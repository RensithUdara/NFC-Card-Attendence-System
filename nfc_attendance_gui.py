import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import db_utils
import subprocess
import os
import pandas as pd

PRIMARY = "#1976D2"
ACCENT = "#2196F3"
BG = "#F5F5F5"
FG = "#212121"
BTN = "#42A5F5"

class NFCMainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NFC Attendance System")
        self.geometry("700x500")
        self.configure(bg=BG)
        db_utils.init_db()
        self._build_nav()
        self._build_main()
        self.show_dashboard()

    def _build_nav(self):
        nav = tk.Frame(self, bg=PRIMARY)
        nav.pack(side=tk.LEFT, fill=tk.Y)
        btn_style = dict(bg=BTN, fg="white", font=("Arial", 12), relief=tk.FLAT, activebackground=ACCENT)
        tk.Button(nav, text="Dashboard", command=self.show_dashboard, **btn_style).pack(fill=tk.X, pady=2, padx=8)
        tk.Button(nav, text="Register Employee", command=self.show_register, **btn_style).pack(fill=tk.X, pady=2, padx=8)
        tk.Button(nav, text="Program Card", command=self.show_program, **btn_style).pack(fill=tk.X, pady=2, padx=8)
        tk.Button(nav, text="Attendance Scan", command=self.show_scan, **btn_style).pack(fill=tk.X, pady=2, padx=8)
        tk.Button(nav, text="Today's Attendance", command=self.show_today, **btn_style).pack(fill=tk.X, pady=2, padx=8)
        tk.Button(nav, text="Blacklist", command=self.show_blacklist, **btn_style).pack(fill=tk.X, pady=2, padx=8)
        tk.Button(nav, text="Export to Excel", command=self.export_excel, **btn_style).pack(fill=tk.X, pady=2, padx=8)
        tk.Button(nav, text="Exit", command=self.destroy, **btn_style).pack(fill=tk.X, pady=2, padx=8)

    def _build_main(self):
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main()
        tk.Label(self.main, text="NFC Attendance System Dashboard", font=("Arial", 20), bg=BG, fg=PRIMARY).pack(pady=20)
        # --- Dashboard widgets ---
        stats_frame = tk.Frame(self.main, bg=BG)
        stats_frame.pack(pady=10)
        # Get stats
        employees = db_utils.get_all_employees()
        total_employees = len(employees)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        conn = db_utils.sqlite3.connect(db_utils.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(DISTINCT employee_id) FROM attendance WHERE substr(timestamp,1,10)=?", (today,))
        present_today = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM blacklist")
        blacklisted = c.fetchone()[0]
        c.execute("SELECT timestamp, employee_id, name, event_type FROM attendance ORDER BY timestamp DESC LIMIT 5")
        recent = c.fetchall()
        conn.close()
        # Stat cards
        def stat_card(parent, label, value, color, icon=None):
            f = tk.Frame(parent, bg=color, bd=2, relief=tk.RIDGE)
            f.pack(side=tk.LEFT, padx=10)
            if icon:
                tk.Label(f, text=icon, font=("Arial", 24), bg=color, fg="white").pack()
            tk.Label(f, text=label, font=("Arial", 12), bg=color, fg="white").pack()
            tk.Label(f, text=str(value), font=("Arial", 18, "bold"), bg=color, fg="white").pack()
        stat_card(stats_frame, "Employees", total_employees, "#43A047", "👤")
        stat_card(stats_frame, "Present Today", present_today, "#1976D2", "🟢")
        stat_card(stats_frame, "Blacklisted", blacklisted, "#E53935", "⛔")
        # Recent activity
        recent_frame = tk.Frame(self.main, bg=BG)
        recent_frame.pack(pady=20)
        tk.Label(recent_frame, text="Recent Attendance Activity", font=("Arial", 14), bg=BG, fg=ACCENT).pack()
        tree = ttk.Treeview(recent_frame, columns=("time", "id", "name", "event"), show="headings", height=5)
        for col, label in zip(["time", "id", "name", "event"], ["Time", "ID", "Name", "Event"]):
            tree.heading(col, text=label)
            tree.column(col, width=120)
        tree.pack()
        for row in recent:
            tree.insert("", tk.END, values=row)

    def show_register(self):
        self.clear_main()
        RegisterFrame(self.main)

    def show_program(self):
        self.clear_main()
        ProgramCardFrame(self.main)

    def show_scan(self):
        self.clear_main()
        AttendanceScanFrame(self.main)

    def show_today(self):
        self.clear_main()
        TodayAttendanceFrame(self.main)

    def show_blacklist(self):
        self.clear_main()
        BlacklistFrame(self.main)

    def export_excel(self):
        conn = db_utils.sqlite3.connect(db_utils.DB_FILE)
        df = pd.read_sql_query("SELECT * FROM attendance", conn)
        conn.close()
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"Attendance exported to {file_path}")

class RegisterFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill=tk.BOTH, expand=True)
        self.photo_path = None
        tk.Label(self, text="Register New Employee", font=("Arial", 16), bg=BG, fg=PRIMARY).pack(pady=10)
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.dept_var = tk.StringVar()
        self.role_var = tk.StringVar()
        form = tk.Frame(self, bg=BG)
        form.pack(pady=10)
        tk.Label(form, text="Employee ID:", bg=BG, fg=FG).grid(row=0, column=0, sticky=tk.W)
        tk.Entry(form, textvariable=self.id_var).grid(row=0, column=1)
        tk.Label(form, text="Name:", bg=BG, fg=FG).grid(row=1, column=0, sticky=tk.W)
        tk.Entry(form, textvariable=self.name_var).grid(row=1, column=1)
        tk.Label(form, text="Department:", bg=BG, fg=FG).grid(row=2, column=0, sticky=tk.W)
        tk.Entry(form, textvariable=self.dept_var).grid(row=2, column=1)
        tk.Label(form, text="Role:", bg=BG, fg=FG).grid(row=3, column=0, sticky=tk.W)
        tk.Entry(form, textvariable=self.role_var).grid(row=3, column=1)
        self.photo_label = tk.Label(form, text="No photo selected.", bg=BG, fg=FG)
        self.photo_label.grid(row=4, column=0, columnspan=2)
        tk.Button(form, text="Upload Photo", bg=BTN, fg="white", command=self.upload_photo).grid(row=5, column=0, columnspan=2, pady=5)
        tk.Button(self, text="Register Employee", bg=PRIMARY, fg="white", command=self.register_employee).pack(pady=10)

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
        from datetime import datetime
        date_joined = datetime.now().strftime("%Y-%m-%d")
        if not emp_id or not name:
            messagebox.showerror("Error", "Employee ID and Name are required.")
            return
        db_utils.add_employee(emp_id, name, None, dept, role, photo, date_joined)
        messagebox.showinfo("Success", f"Employee {name} registered!")

class ProgramCardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill=tk.BOTH, expand=True)
        tk.Label(self, text="Program/Reprogram/Blacklist Card", font=("Arial", 16), bg=BG, fg=PRIMARY).pack(pady=10)
        tk.Button(self, text="Program New Card", bg=BTN, fg="white", command=self.program_card).pack(pady=5)
        tk.Button(self, text="Reprogram Card", bg=BTN, fg="white", command=self.reprogram_card).pack(pady=5)
        tk.Button(self, text="Revoke (Blacklist) Card", bg=BTN, fg="white", command=self.revoke_card).pack(pady=5)
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, fg=PRIMARY, bg=BG).pack(pady=10)

    def _wait_for_card(self, callback):
        import nfc
        try:
            clf = nfc.ContactlessFrontend('usb')
        except IOError:
            self.status_var.set("NFC Reader not found.")
            return
        self.status_var.set("Waiting for card...")
        clf.connect(rdwr={'on-connect': callback})
        clf.close()

    def program_card(self):
        # ... (reuse improved logic from previous GUI)
        from tkinter import simpledialog
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
            data_to_write = f"Attendance_v1:{employee_id}:{name}"
            try:
                tag.load_key_a(block_address=4, key=b'\xFF\xFF\xFF\xFF\xFF\xFF')
                data_bytes = bytearray(data_to_write, 'utf-8')
                padded_data = data_bytes.ljust(16, b'\x00')
                tag.write(block_address=4, data=padded_data)
                db_utils.add_employee(employee_id, name, card_uid)
                self.status_var.set(f"Card programmed for {employee_id}.")
                messagebox.showinfo("Success", f"Card programmed for {employee_id} ({name})!")
            except Exception as e:
                self.status_var.set(f"Error: {e}")
            return False
        import threading
        threading.Thread(target=self._wait_for_card, args=(on_connect,)).start()

    def reprogram_card(self):
        # ... (reuse improved logic from previous GUI)
        pass
    def revoke_card(self):
        # ... (reuse improved logic from previous GUI)
        pass

class AttendanceScanFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill=tk.BOTH, expand=True)
        tk.Label(self, text="Attendance Scan", font=("Arial", 16), bg=BG, fg=PRIMARY).pack(pady=10)
        # ... (reuse improved logic from previous GUI)

class TodayAttendanceFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill=tk.BOTH, expand=True)
        tk.Label(self, text="Today's Attendance", font=("Arial", 16), bg=BG, fg=PRIMARY).pack(pady=10)
        # ... (reuse improved logic from previous GUI)

class BlacklistFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill=tk.BOTH, expand=True)
        tk.Label(self, text="Blacklisted Cards", font=("Arial", 16), bg=BG, fg=PRIMARY).pack(pady=10)
        # ... (reuse improved logic from previous GUI)

if __name__ == "__main__":
    app = NFCMainApp()
    app.mainloop()
