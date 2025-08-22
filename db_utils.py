import sqlite3
import os


DB_FILE = "attendance_system.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        role TEXT,
        photo_path TEXT,
        date_joined TEXT,
        card_uid TEXT UNIQUE,
        card_issued TEXT,
        card_revoked TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        timestamp TEXT,
        employee_id TEXT,
        name TEXT,
        card_uid TEXT,
        event_type TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS blacklist (
        card_uid TEXT PRIMARY KEY,
        revoked_on TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()



def add_employee(employee_id, name, card_uid, department=None, role=None, photo_path=None, date_joined=None, card_issued=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO employees (id, name, department, role, photo_path, date_joined, card_uid, card_issued)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (employee_id, name, department, role, photo_path, date_joined, card_uid, card_issued))
    conn.commit()
    conn.close()



def log_attendance(timestamp, employee_id, name, card_uid, event_type="IN"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO attendance (timestamp, employee_id, name, card_uid, event_type) VALUES (?, ?, ?, ?, ?)", (timestamp, employee_id, name, card_uid, event_type))
    conn.commit()
    conn.close()



def blacklist_card(card_uid, revoked_on=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO blacklist (card_uid, revoked_on) VALUES (?, ?)", (card_uid, revoked_on))
    c.execute("UPDATE employees SET card_revoked = ? WHERE card_uid = ?", (revoked_on, card_uid))
    conn.commit()
    conn.close()



def is_blacklisted(card_uid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM blacklist WHERE card_uid = ?", (card_uid,))
    result = c.fetchone()
    conn.close()
    return result is not None



def get_employee_by_uid(card_uid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, department, role, photo_path FROM employees WHERE card_uid = ?", (card_uid,))
    result = c.fetchone()
    conn.close()
    return result



def get_attendance_report(period="daily"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if period == "daily":
        c.execute("SELECT substr(timestamp, 1, 10) as day, COUNT(DISTINCT employee_id) FROM attendance GROUP BY day")
    elif period == "monthly":
        c.execute("SELECT substr(timestamp, 1, 7) as month, COUNT(DISTINCT employee_id) FROM attendance GROUP BY month")
    rows = c.fetchall()
    conn.close()
    return rows



def get_all_blacklisted():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT card_uid, revoked_on FROM blacklist")
    rows = c.fetchall()
    conn.close()
    return rows



def get_all_employees():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, department, role, photo_path, date_joined, card_uid, card_issued, card_revoked FROM employees")
    rows = c.fetchall()
    conn.close()
    return rows

def add_admin(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO admins (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def check_admin(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM admins WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None
