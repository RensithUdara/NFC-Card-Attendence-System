import tkinter as tk
from tkinter import messagebox, simpledialog
import db_utils
import nfc
import time
import threading

SECRET_KEY = "Attendance_v1"
BLOCK_ADDRESS = 4

class CardProgrammerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NFC Card Programmer")
        self.root.geometry("400x300")
        db_utils.init_db()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        tk.Label(root, text="NFC Card Programmer", font=("Arial", 16)).pack(pady=10)
        tk.Button(root, text="Program New Card", command=self.program_card, width=25).pack(pady=5)
        tk.Button(root, text="Reprogram Card", command=self.reprogram_card, width=25).pack(pady=5)
        tk.Button(root, text="Revoke (Blacklist) Card", command=self.revoke_card, width=25).pack(pady=5)
        tk.Button(root, text="View Blacklist", command=self.view_blacklist, width=25).pack(pady=5)
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

    def program_card(self):
        employee_id = simpledialog.askstring("Employee ID", "Enter Employee ID (e.g., EMP123):")
        if not employee_id:
            return
        name = simpledialog.askstring("Employee Name", "Enter Employee Name:")
        if not name:
            return
        def on_connect(tag):
            if not hasattr(tag, 'identifier'):
                self.status_var.set("Not a valid card.")
                return False
            card_uid = tag.identifier.hex()
            data_to_write = f"{SECRET_KEY}:{employee_id}:{name}"
            try:
                tag.load_key_a(block_address=BLOCK_ADDRESS, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
                data_bytes = bytearray(data_to_write, 'utf-8')
                padded_data = data_bytes.ljust(16, b'\x00')
                tag.write(block_address=BLOCK_ADDRESS, data=padded_data)
                db_utils.add_employee(employee_id, name, card_uid)
                self.status_var.set(f"Card programmed for {employee_id}.")
                messagebox.showinfo("Success", f"Card programmed for {employee_id} ({name})!")
            except Exception as e:
                self.status_var.set(f"Error: {e}")
            return False
        threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()

    def reprogram_card(self):
        def on_connect(tag):
            if not hasattr(tag, 'identifier'):
                self.status_var.set("Not a valid card.")
                return False
            card_uid = tag.identifier.hex()
            emp = db_utils.get_employee_by_uid(card_uid)
            if not emp:
                self.status_var.set("Card not registered.")
                return False
            current_id, current_name = emp
            employee_id = simpledialog.askstring("Employee ID", "Enter new Employee ID (leave blank to keep current):") or current_id
            name = simpledialog.askstring("Employee Name", "Enter new Employee Name (leave blank to keep current):") or current_name
            data_to_write = f"{SECRET_KEY}:{employee_id}:{name}"
            try:
                tag.load_key_a(block_address=BLOCK_ADDRESS, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
                data_bytes = bytearray(data_to_write, 'utf-8')
                padded_data = data_bytes.ljust(16, b'\x00')
                tag.write(block_address=BLOCK_ADDRESS, data=padded_data)
                db_utils.add_employee(employee_id, name, card_uid)
                self.status_var.set(f"Card reprogrammed for {employee_id}.")
                messagebox.showinfo("Success", f"Card reprogrammed for {employee_id} ({name})!")
            except Exception as e:
                self.status_var.set(f"Error: {e}")
            return False
        threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()

    def revoke_card(self):
        def on_connect(tag):
            if not hasattr(tag, 'identifier'):
                self.status_var.set("Not a valid card.")
                return False
            card_uid = tag.identifier.hex()
            db_utils.blacklist_card(card_uid)
            self.status_var.set(f"Card {card_uid} blacklisted.")
            messagebox.showinfo("Blacklisted", f"Card UID {card_uid} has been blacklisted.")
            return False
        threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()

    def view_blacklist(self):
        bl = db_utils.get_all_blacklisted()
        msg = "Blacklisted Card UIDs:\n" + ("\n".join(bl) if bl else "None")
        messagebox.showinfo("Blacklist", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = CardProgrammerGUI(root)
    root.mainloop()
