import tkinter as tk
from tkinter import messagebox
import db_utils
import gui_admin_login
import gui_employee_register
import gui_today_attendance
import subprocess
import os

def launch_employee_register():
    subprocess.Popen(["python", "gui_employee_register.py"])

def launch_today_attendance():
    subprocess.Popen(["python", "gui_today_attendance.py"])

def launch_program_card():
    subprocess.Popen(["python", "gui_program_card.py"])

def launch_attendance_scanner():
    subprocess.Popen(["python", "gui_secure_attendance.py"])

def export_attendance_to_excel():
    import pandas as pd
    conn = db_utils.sqlite3.connect(db_utils.DB_FILE)
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()
    file_path = tk.filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Exported", f"Attendance exported to {file_path}")

def main_dashboard(admin_user):
    root = tk.Tk()
    root.title(f"NFC Attendance Dashboard - Admin: {admin_user}")
    root.geometry("400x400")
    db_utils.init_db()
    tk.Label(root, text="NFC Attendance System Dashboard", font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Register New Employee", command=launch_employee_register, width=30).pack(pady=5)
    tk.Button(root, text="Program/Reprogram/Blacklist Card", command=launch_program_card, width=30).pack(pady=5)
    tk.Button(root, text="Attendance Scanner", command=launch_attendance_scanner, width=30).pack(pady=5)
    tk.Button(root, text="Today's Attendance", command=launch_today_attendance, width=30).pack(pady=5)
    tk.Button(root, text="Export Attendance to Excel", command=export_attendance_to_excel, width=30).pack(pady=5)
    tk.Button(root, text="Exit", command=root.destroy, width=30).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    def after_login(user):
        main_dashboard(user)
    gui_admin_login.launch_admin_login(after_login)
