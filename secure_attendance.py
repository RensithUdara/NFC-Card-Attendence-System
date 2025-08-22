import nfc
from datetime import datetime
import time
import os
import json
import csv

SECRET_KEY = "KDJay_Attendance_v1"  # Our secret key
BLOCK_ADDRESS = 4
LOG_FILE = "secure_attendance_log.csv"
BLACKLIST_FILE = "blacklist.json"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_log():
    if not os.path.exists(LOG_FILE):
        print("No attendance log found.")
        return
    with open(LOG_FILE, "r") as f:
        print(f.read())

def export_log(filename):
    if not os.path.exists(LOG_FILE):
        print("No attendance log found.")
        return
    with open(LOG_FILE, "r") as src, open(filename, "w") as dst:
        dst.write(src.read())
    print(f"Log exported to {filename}")

def generate_report(period="daily"):
    if not os.path.exists(LOG_FILE):
        print("No attendance log found.")
        return
    report = {}
    with open(LOG_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            date = row[0][:10]
            emp = row[1]
            if period == "daily":
                report.setdefault(date, set()).add(emp)
            elif period == "monthly":
                month = date[:7]
                report.setdefault(month, set()).add(emp)
    print(f"\nAttendance {period.capitalize()} Report:")
    for k, v in report.items():
        print(f"{k}: {len(v)} unique employees")

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return set()
    with open(BLACKLIST_FILE, "r") as f:
        return set(json.load(f))

def get_card_uid(tag):
    return getattr(tag, 'identifier', b'').hex()

def on_connect(tag):
    if not isinstance(tag, nfc.tag.mifare.MifareClassic):
        print("Rejected! Not a MIFARE Classic card.")
        time.sleep(2)
        return False
    uid = get_card_uid(tag)
    blacklist = load_blacklist()
    if uid in blacklist:
        print("Rejected! This card is blacklisted.")
        time.sleep(2)
        return False
    try:
        tag.load_key_a(block_address=BLOCK_ADDRESS, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
        read_data_bytes = tag.read(block_address=BLOCK_ADDRESS)
        read_data = read_data_bytes.decode('utf-8').strip('\x00')
        if read_data.startswith(SECRET_KEY):
            parts = read_data.split(":")
            employee_id = parts[1] if len(parts) > 1 else "UNKNOWN"
            name = parts[2] if len(parts) > 2 else "UNKNOWN"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Accepted! ID: {employee_id} | Name: {name} | Time: {timestamp}")
            with open(LOG_FILE, "a") as f:
                f.write(f"{timestamp},{employee_id},{name}\n")
            time.sleep(2)
        else:
            print("Rejected! This card is not authorized.")
            time.sleep(2)
    except Exception as e:
        print(f"Error reading card! ({e})")
        time.sleep(2)
    return True

def menu():
    print("\n=== Secure Attendance Menu ===")
    print("1. Start attendance scan")
    print("2. View attendance log")
    print("3. Export log to file")
    print("4. Generate daily report")
    print("5. Generate monthly report")
    print("6. Exit")
    return input("Select an option: ")

def main():
    clear_console()
    print("=== Secure NFC Attendance System ===")
    try:
        clf = nfc.ContactlessFrontend('usb')
    except IOError:
        print("NFC Reader not found.")
        return
    while True:
        choice = menu()
        if choice == "1":
            print("To log attendance, place your ID card on the reader...")
            while True:
                clf.connect(rdwr={'on-connect': on_connect})
                time.sleep(0.1)
                again = input("Press Enter to scan another card, or type 'q' to return to menu: ")
                if again.lower() == 'q':
                    break
        elif choice == "2":
            print_log()
        elif choice == "3":
            filename = input("Enter filename to export log (e.g., export.csv): ")
            export_log(filename)
        elif choice == "4":
            generate_report("daily")
        elif choice == "5":
            generate_report("monthly")
        elif choice == "6":
            print("Exiting.")
            break
        else:
            print("Invalid option. Try again.")
        time.sleep(1)

if __name__ == "__main__":
    main()
