import tkinter as tk
from tkinter import messagebox, simpledialog
import db_utils
import os

def start_gui():
    db_utils.init_db()
    root = tk.Tk()
    root.title("NFC Attendance System")
    root.geometry("400x300")

    def show_employees():
        employees = db_utils.get_all_employees()
        msg = "Registered Employees:\n" + "\n".join([f"{e[0]} - {e[1]} (UID: {e[2]})" for e in employees])
        messagebox.showinfo("Employees", msg)

    def show_blacklist():
        bl = db_utils.get_all_blacklisted()
        msg = "Blacklisted Card UIDs:\n" + ("\n".join(bl) if bl else "None")
        messagebox.showinfo("Blacklist", msg)

    def show_report(period):
        rows = db_utils.get_attendance_report(period)
        msg = f"{period.capitalize()} Attendance Report:\n" + "\n".join([f"{r[0]}: {r[1]} unique employees" for r in rows])
        messagebox.showinfo(f"{period.capitalize()} Report", msg)

    tk.Label(root, text="NFC Attendance System", font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Show Employees", command=show_employees, width=25).pack(pady=5)
    tk.Button(root, text="Show Blacklist", command=show_blacklist, width=25).pack(pady=5)
    tk.Button(root, text="Daily Report", command=lambda: show_report("daily"), width=25).pack(pady=5)
    tk.Button(root, text="Monthly Report", command=lambda: show_report("monthly"), width=25).pack(pady=5)
    tk.Button(root, text="Exit", command=root.destroy, width=25).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
