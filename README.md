# NFC Card Attendance System

A secure, professional attendance system using NFC cards and a USB NFC reader (e.g., ACR122U) on Windows. This project prevents card cloning by embedding a secret key and employee info on each card.

## Features
- **Admin Card Programming**: Securely program cards with employee ID and name, protected by admin password.
- **Secure Attendance Logging**: Only cards with the correct secret key are accepted. Logs employee ID, name, and timestamp.
- **CSV Log Export**: Attendance is saved in a CSV file for easy viewing in Excel.
- **Simple Console UI**: Clear instructions and feedback for users and admins.

## Requirements
- Windows PC
- USB NFC Reader (e.g., ACR122U)
- MIFARE Classic 1K NFC cards
- Python 3.x
- Python packages: `nfcpy`

## Setup
1. **Install Python**: [Download Python](https://www.python.org/downloads/) and check "Add Python to PATH" during install.
2. **Install NFC Reader Driver**: Download from your reader's official website.
3. **Install Python Library**:
   ```sh
   pip install nfcpy
   ```

## Usage
### 1. Program a Card (Admin)
Run:
```sh
python program_card.py
```
- Authenticate as admin.
- Place a blank card on the reader.
- Enter employee ID and name.

### 2. Log Attendance (Reception)
Run:
```sh
python secure_attendance.py
```
- Employees tap their programmed cards to log attendance.
- Logs are saved in `secure_attendance_log.csv`.

## Security Notes
- The system uses a secret key and employee info written to a protected block on the card.
- Only cards with the correct secret key are accepted.
- Change the admin password and secret key in the scripts for your organization.

## Extending the System
- Add card revocation/blacklist.
- Integrate with a database or cloud service.
- Add a GUI for easier management.

---
**Author:** Your Name
