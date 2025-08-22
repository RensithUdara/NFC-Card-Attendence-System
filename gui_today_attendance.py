import tkinter as tk
from tkinter import ttk
import db_utils
from datetime import datetime

class TodayAttendanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Today's Attendance")
        self.root.geometry("600x400")
        db_utils.init_db()
        self.build_table()
        self.load_attendance()

    def build_table(self):
        columns = ("timestamp", "employee_id", "name", "event_type")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)
        tk.Button(self.root, text="Refresh", command=self.load_attendance).pack(pady=5)

    def load_attendance(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        today = datetime.now().strftime("%Y-%m-%d")
        conn = db_utils.sqlite3.connect(db_utils.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT timestamp, employee_id, name, event_type FROM attendance WHERE substr(timestamp,1,10)=?", (today,))
        rows = c.fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = TodayAttendanceGUI(root)
    root.mainloop()
