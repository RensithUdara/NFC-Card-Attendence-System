import nfc
import time
import getpass
import os

SECRET_KEY = "KDJay_Attendance_v1"  # Our secret key
BLOCK_ADDRESS = 4


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def admin_auth():
    password = getpass.getpass("Enter admin password to continue: ")
    return password == "admin123"  # Change this to your own admin password

try:
    clf = nfc.ContactlessFrontend('usb')
    print("NFC Reader connected successfully!")
    print("Place a card on the reader to program it...")
except IOError:
    print("NFC Reader not found. Check the connection.")
    exit()

def on_connect(tag):
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

def main():
    clear_console()
    print("=== NFC Card Programming Utility ===")
    if not admin_auth():
        print("Authentication failed. Exiting.")
        return
    while True:
        clf.connect(rdwr={'on-connect': on_connect})
        time.sleep(1)

if __name__ == "__main__":
    main()
