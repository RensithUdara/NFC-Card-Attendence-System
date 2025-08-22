import sqlite3
import os

DB_FILE = "attendance_system.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        card_uid TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        timestamp TEXT,
        employee_id TEXT,
        name TEXT,
        card_uid TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS blacklist (
        card_uid TEXT PRIMARY KEY
    )''')
    conn.commit()
    conn.close()


def add_employee(employee_id, name, card_uid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO employees (id, name, card_uid) VALUES (?, ?, ?)", (employee_id, name, card_uid))
    conn.commit()
    conn.close()


def log_attendance(timestamp, employee_id, name, card_uid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO attendance (timestamp, employee_id, name, card_uid) VALUES (?, ?, ?, ?)", (timestamp, employee_id, name, card_uid))
    conn.commit()
    conn.close()


def blacklist_card(card_uid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO blacklist (card_uid) VALUES (?)", (card_uid,))
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
    c.execute("SELECT id, name FROM employees WHERE card_uid = ?", (card_uid,))
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
    c.execute("SELECT card_uid FROM blacklist")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_all_employees():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, card_uid FROM employees")
    rows = c.fetchall()
    conn.close()
    return rows
