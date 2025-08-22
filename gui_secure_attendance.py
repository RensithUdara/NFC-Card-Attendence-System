
import tkinter as tk
from tkinter import messagebox
import db_utils
import nfc
import time
import threading
from datetime import datetime
import os

SECRET_KEY = "Attendance_v1"
BLOCK_ADDRESS = 4

class AttendanceScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NFC Attendance Scanner")
        self.root.geometry("400x300")
        db_utils.init_db()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        tk.Label(root, text="NFC Attendance Scanner", font=("Arial", 16)).pack(pady=10)
        tk.Button(root, text="Start Attendance Scan", command=self.scan_card, width=25).pack(pady=5)
        tk.Button(root, text="View Daily Report", command=lambda: self.show_report("daily"), width=25).pack(pady=5)
        tk.Button(root, text="View Monthly Report", command=lambda: self.show_report("monthly"), width=25).pack(pady=5)
        tk.Button(root, text="Exit", command=root.destroy, width=25).pack(pady=20)
        tk.Label(root, textvariable=self.status_var, fg="blue").pack(pady=5)

    def _wait_for_card(self, callback):
        try:
            clf = nfc.ContactlessFrontend('usb')
        except IOError:
            self.status_var.set("NFC Reader not found.")
            return
        self.status_var.set("Waiting for card...")
        clf.connect(rdwr={'on-connect': callback})
        clf.close()

    def scan_card(self):
        def on_connect(tag):
            if not hasattr(tag, 'identifier'):
                self.status_var.set("Not a valid card.")
                return False
            card_uid = tag.identifier.hex()
            if db_utils.is_blacklisted(card_uid):
                self.status_var.set("Card is blacklisted.")
                messagebox.showerror("Blacklisted", "This card is blacklisted!")
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
                    db_utils.log_attendance(timestamp, employee_id, name, card_uid)
                    # Show employee photo and info
                    emp = db_utils.get_employee_by_uid(card_uid)
                    if emp:
                        _, _, department, role, photo_path = emp
                        info = f"ID: {employee_id}\nName: {name}\nDepartment: {department or ''}\nRole: {role or ''}"
                        if photo_path and os.path.exists(photo_path):
                            from PIL import Image, ImageTk
                            img = Image.open(photo_path)
                            img = img.resize((120, 120))
                            img_tk = ImageTk.PhotoImage(img)
                            top = tk.Toplevel(self.root)
                            top.title("Employee Info")
                            tk.Label(top, image=img_tk).pack()
                            tk.Label(top, text=info, font=("Arial", 12)).pack()
                            top.after(3000, top.destroy)
                            top.mainloop()
                        else:
                            messagebox.showinfo("Success", f"Attendance logged!\n{info}")
                    else:
                        messagebox.showinfo("Success", f"Attendance logged for {employee_id} ({name})!")
                    self.status_var.set(f"Attendance logged for {employee_id}.")
                else:
                    self.status_var.set("Card not authorized.")
                    messagebox.showerror("Unauthorized", "This card is not authorized!")
            except Exception as e:
                self.status_var.set(f"Error: {e}")
            return False
        threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()

    def show_report(self, period):
        rows = db_utils.get_attendance_report(period)
        msg = f"{period.capitalize()} Attendance Report:\n" + "\n".join([f"{r[0]}: {r[1]} unique employees" for r in rows])
        messagebox.showinfo(f"{period.capitalize()} Report", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceScannerGUI(root)
    root.mainloop()
