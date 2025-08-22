
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import db_utils
import nfc
import time
import threading
import os

SECRET_KEY = "Attendance_v1"
BLOCK_ADDRESS = 4


class CardProgrammerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NFC Card Programmer")
        self.root.geometry("500x420")
        db_utils.init_db()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        self.photo_path = None

        main_frame = tk.Frame(root)
        main_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        tk.Label(main_frame, text="NFC Card Programmer", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=5)
        tk.Button(main_frame, text="Program New Card", command=self.program_card, width=25).grid(row=1, column=0, pady=5)
        tk.Button(main_frame, text="Reprogram Card", command=self.reprogram_card, width=25).grid(row=1, column=1, pady=5)
        tk.Button(main_frame, text="Revoke (Blacklist) Card", command=self.revoke_card, width=25).grid(row=2, column=0, pady=5)
        tk.Button(main_frame, text="View Blacklist", command=self.view_blacklist, width=25).grid(row=2, column=1, pady=5)
        tk.Button(main_frame, text="Exit", command=root.destroy, width=25).grid(row=3, column=0, columnspan=2, pady=20)
        tk.Label(main_frame, textvariable=self.status_var, fg="blue").grid(row=4, column=0, columnspan=2, pady=5)

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
        win = tk.Toplevel(self.root)
        win.title("Program New Card")
        win.geometry("350x350")
        vars = {k: tk.StringVar() for k in ["id", "name", "dept", "role"]}
        tk.Label(win, text="Employee ID:").pack()
        tk.Entry(win, textvariable=vars["id"]).pack()
        tk.Label(win, text="Name:").pack()
        tk.Entry(win, textvariable=vars["name"]).pack()
        tk.Label(win, text="Department:").pack()
        tk.Entry(win, textvariable=vars["dept"]).pack()
        tk.Label(win, text="Role:").pack()
        tk.Entry(win, textvariable=vars["role"]).pack()
        photo_label = tk.Label(win, text="No photo selected.")
        photo_label.pack()
        def upload_photo():
            file_path = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
            if file_path:
                self.photo_path = file_path
                photo_label.config(text=os.path.basename(file_path))
        tk.Button(win, text="Upload Photo", command=upload_photo).pack(pady=5)
        def do_program():
            employee_id = vars["id"].get()
            name = vars["name"].get()
            dept = vars["dept"].get()
            role = vars["role"].get()
            photo = self.photo_path
            if not employee_id or not name:
                messagebox.showerror("Error", "Employee ID and Name are required.")
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
                    db_utils.add_employee(employee_id, name, card_uid, dept, role, photo)
                    self.status_var.set(f"Card programmed for {employee_id}.")
                    messagebox.showinfo("Success", f"Card programmed for {employee_id} ({name})!")
                except Exception as e:
                    self.status_var.set(f"Error: {e}")
                return False
            threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()
            win.destroy()
        tk.Button(win, text="Program Card", command=do_program).pack(pady=10)

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
            current_id, current_name, dept, role, photo = emp
            win = tk.Toplevel(self.root)
            win.title("Reprogram Card")
            win.geometry("350x400")
            tk.Label(win, text=f"Current ID: {current_id}").pack()
            tk.Label(win, text=f"Current Name: {current_name}").pack()
            tk.Label(win, text=f"Department: {dept or ''}").pack()
            tk.Label(win, text=f"Role: {role or ''}").pack()
            if photo and os.path.exists(photo):
                img = Image.open(photo)
                img = img.resize((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(win, image=img_tk)
                img_label.image = img_tk
                img_label.pack()
            new_id = tk.StringVar(value=current_id)
            new_name = tk.StringVar(value=current_name)
            new_dept = tk.StringVar(value=dept)
            new_role = tk.StringVar(value=role)
            tk.Label(win, text="New Employee ID:").pack()
            tk.Entry(win, textvariable=new_id).pack()
            tk.Label(win, text="New Name:").pack()
            tk.Entry(win, textvariable=new_name).pack()
            tk.Label(win, text="New Department:").pack()
            tk.Entry(win, textvariable=new_dept).pack()
            tk.Label(win, text="New Role:").pack()
            tk.Entry(win, textvariable=new_role).pack()
            def do_reprogram():
                employee_id = new_id.get()
                name = new_name.get()
                dept = new_dept.get()
                role = new_role.get()
                data_to_write = f"{SECRET_KEY}:{employee_id}:{name}"
                try:
                    tag.load_key_a(block_address=BLOCK_ADDRESS, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
                    data_bytes = bytearray(data_to_write, 'utf-8')
                    padded_data = data_bytes.ljust(16, b'\x00')
                    tag.write(block_address=BLOCK_ADDRESS, data=padded_data)
                    db_utils.add_employee(employee_id, name, card_uid, dept, role, photo)
                    self.status_var.set(f"Card reprogrammed for {employee_id}.")
                    messagebox.showinfo("Success", f"Card reprogrammed for {employee_id} ({name})!")
                except Exception as e:
                    self.status_var.set(f"Error: {e}")
                win.destroy()
                return False
            tk.Button(win, text="Reprogram Card", command=do_reprogram).pack(pady=10)
            return False
        threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()

    def revoke_card(self):
        def on_connect(tag):
            if not hasattr(tag, 'identifier'):
                self.status_var.set("Not a valid card.")
                return False
            card_uid = tag.identifier.hex()
            emp = db_utils.get_employee_by_uid(card_uid)
            info = ""
            if emp:
                current_id, current_name, dept, role, photo = emp
                info = f"ID: {current_id}\nName: {current_name}\nDepartment: {dept or ''}\nRole: {role or ''}"
                if photo and os.path.exists(photo):
                    img = Image.open(photo)
                    img = img.resize((100, 100))
                    img_tk = ImageTk.PhotoImage(img)
                    top = tk.Toplevel(self.root)
                    top.title("Employee Info")
                    tk.Label(top, image=img_tk).pack()
                    tk.Label(top, text=info, font=("Arial", 12)).pack()
                    top.after(2500, top.destroy)
                    top.mainloop()
                else:
                    messagebox.showinfo("Employee Info", info)
            db_utils.blacklist_card(card_uid)
            self.status_var.set(f"Card {card_uid} blacklisted.")
            messagebox.showinfo("Blacklisted", f"Card UID {card_uid} has been blacklisted.")
            return False
        threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()

    def view_blacklist(self):
        bl = db_utils.get_all_blacklisted()
        win = tk.Toplevel(self.root)
        win.title("Blacklisted Cards")
        win.geometry("400x300")
        from tkinter import ttk
        tree = ttk.Treeview(win, columns=("uid", "revoked", "info"), show="headings")
        tree.heading("uid", text="Card UID")
        tree.heading("revoked", text="Revoked On")
        tree.heading("info", text="Employee Info")
        tree.pack(fill=tk.BOTH, expand=True)
        for uid, revoked_on in bl:
            emp = db_utils.get_employee_by_uid(uid)
            if emp:
                current_id, current_name, dept, role, _ = emp
                info = f"{current_id} - {current_name} ({dept or ''}, {role or ''})"
            else:
                info = "-"
            tree.insert("", tk.END, values=(uid, revoked_on or "", info))
        tk.Button(win, text="Close", command=win.destroy).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = CardProgrammerGUI(root)
    root.mainloop()
