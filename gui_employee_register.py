import tkinter as tk
from tkinter import filedialog, messagebox
import db_utils
import os
from datetime import datetime

class EmployeeRegisterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Register New Employee")
        self.root.geometry("400x400")
        db_utils.init_db()
        self.photo_path = None
        self.build_form()

    def build_form(self):
        tk.Label(self.root, text="Register New Employee", font=("Arial", 16)).pack(pady=10)
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.dept_var = tk.StringVar()
        self.role_var = tk.StringVar()
        tk.Label(self.root, text="Employee ID:").pack()
        tk.Entry(self.root, textvariable=self.id_var).pack()
        tk.Label(self.root, text="Name:").pack()
        tk.Entry(self.root, textvariable=self.name_var).pack()
        tk.Label(self.root, text="Department:").pack()
        tk.Entry(self.root, textvariable=self.dept_var).pack()
        tk.Label(self.root, text="Role:").pack()
        tk.Entry(self.root, textvariable=self.role_var).pack()
        tk.Button(self.root, text="Upload Photo", command=self.upload_photo).pack(pady=5)
        self.photo_label = tk.Label(self.root, text="No photo selected.")
        self.photo_label.pack()
        tk.Button(self.root, text="Register Employee", command=self.register_employee).pack(pady=20)

    def upload_photo(self):
        file_path = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.photo_path = file_path
            self.photo_label.config(text=os.path.basename(file_path))

    def register_employee(self):
        emp_id = self.id_var.get()
        name = self.name_var.get()
        dept = self.dept_var.get()
        role = self.role_var.get()
        photo = self.photo_path
        date_joined = datetime.now().strftime("%Y-%m-%d")
        if not emp_id or not name:
            messagebox.showerror("Error", "Employee ID and Name are required.")
            return
        db_utils.add_employee(emp_id, name, None, dept, role, photo, date_joined)
        messagebox.showinfo("Success", f"Employee {name} registered!")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeRegisterGUI(root)
    root.mainloop()
