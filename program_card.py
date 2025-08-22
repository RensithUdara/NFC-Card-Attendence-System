
import nfc
import time
import getpass
import os
import json

SECRET_KEY = "Attendance_v1"  # Our secret key
BLOCK_ADDRESS = 4
BLACKLIST_FILE = "blacklist.json"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def admin_auth():
    password = getpass.getpass("Enter admin password to continue: ")
    return password == "admin123"  # Change this to your own admin password

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return set()
    with open(BLACKLIST_FILE, "r") as f:
        return set(json.load(f))

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(list(blacklist), f)

def get_card_uid(tag):
    return getattr(tag, 'identifier', b'').hex()

def program_card(tag):
    print("Card found!", tag)
    if not isinstance(tag, nfc.tag.mifare.MifareClassic):
        print("Sorry, this card cannot be written to. (A MIFARE Classic card is required)")
        return False
    try:
        employee_id = input("Enter the Employee ID (e.g., EMP123): ")
        name = input("Enter Employee Name: ")
        data_to_write = f"{SECRET_KEY}:{employee_id}:{name}"
        tag.load_key_a(block_address=BLOCK_ADDRESS, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
        data_bytes = bytearray(data_to_write, 'utf-8')
        padded_data = data_bytes.ljust(16, b'\x00')
        tag.write(block_address=BLOCK_ADDRESS, data=padded_data)
        print(f"\nSuccess! The message '{data_to_write}' has been written to the card.")
        print("You can now remove the card.")
    except Exception as e:
        print(f"Error: An error occurred while writing! - {e}")
    return False

def reprogram_card(tag):
    print("Card found!", tag)
    if not isinstance(tag, nfc.tag.mifare.MifareClassic):
        print("Sorry, this card cannot be written to. (A MIFARE Classic card is required)")
        return False
    try:
        tag.load_key_a(block_address=BLOCK_ADDRESS, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
        read_data_bytes = tag.read(block_address=BLOCK_ADDRESS)
        read_data = read_data_bytes.decode('utf-8').strip('\x00')
        if read_data.startswith(SECRET_KEY):
            print(f"Current data: {read_data}")
            employee_id = input("Enter new Employee ID (leave blank to keep current): ")
            name = input("Enter new Employee Name (leave blank to keep current): ")
            parts = read_data.split(":")
            if not employee_id:
                employee_id = parts[1] if len(parts) > 1 else "UNKNOWN"
            if not name:
                name = parts[2] if len(parts) > 2 else "UNKNOWN"
            data_to_write = f"{SECRET_KEY}:{employee_id}:{name}"
            data_bytes = bytearray(data_to_write, 'utf-8')
            padded_data = data_bytes.ljust(16, b'\x00')
            tag.write(block_address=BLOCK_ADDRESS, data=padded_data)
            print(f"\nSuccess! The message '{data_to_write}' has been written to the card.")
        else:
            print("This card does not contain a valid attendance record.")
    except Exception as e:
        print(f"Error: {e}")
    return False

def revoke_card(tag):
    print("Card found!", tag)
    uid = get_card_uid(tag)
    blacklist = load_blacklist()
    blacklist.add(uid)
    save_blacklist(blacklist)
    print(f"Card UID {uid} has been revoked and added to the blacklist.")
    return False

def menu():
    print("\n=== NFC Card Admin Menu ===")
    print("1. Program new card")
    print("2. Reprogram existing card")
    print("3. Revoke (blacklist) card")
    print("4. View blacklist")
    print("5. Exit")
    return input("Select an option: ")

def view_blacklist():
    blacklist = load_blacklist()
    if not blacklist:
        print("Blacklist is empty.")
    else:
        print("Blacklisted Card UIDs:")
        for uid in blacklist:
            print(uid)

def main():
    clear_console()
    print("=== NFC Card Programming Utility ===")
    if not admin_auth():
        print("Authentication failed. Exiting.")
        return
    try:
        clf = nfc.ContactlessFrontend('usb')
    except IOError:
        print("NFC Reader not found. Check the connection.")
        return
    while True:
        choice = menu()
        if choice == "1":
            print("Place a card on the reader to program it...")
            clf.connect(rdwr={'on-connect': program_card})
        elif choice == "2":
            print("Place a card on the reader to reprogram it...")
            clf.connect(rdwr={'on-connect': reprogram_card})
        elif choice == "3":
            print("Place a card on the reader to revoke it...")
            clf.connect(rdwr={'on-connect': revoke_card})
        elif choice == "4":
            view_blacklist()
        elif choice == "5":
            print("Exiting admin menu.")
            break
        else:
            print("Invalid option. Try again.")
        time.sleep(1)

if __name__ == "__main__":
    main()
