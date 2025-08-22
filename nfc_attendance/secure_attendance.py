import nfc
from datetime import datetime
import time
import os

SECRET_KEY = "KDJay_Attendance_v1"  # Our secret key
BLOCK_ADDRESS = 4
LOG_FILE = "secure_attendance_log.csv"


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

try:
    clf = nfc.ContactlessFrontend('usb')
    print("Secure Attendance System is ready!")
except IOError:
    print("NFC Reader not found.")
    exit()

print("To log attendance, place your ID card on the reader...")

def on_connect(tag):
    if not isinstance(tag, nfc.tag.mifare.MifareClassic):
        print("Rejected! Not a MIFARE Classic card.")
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

def main():
    clear_console()
    print("=== Secure NFC Attendance System ===")
    while True:
        clf.connect(rdwr={'on-connect': on_connect})
        time.sleep(0.1)

if __name__ == "__main__":
    main()
