import tkinter as tk
from tkinter import messagebox
import db_utils

def launch_admin_login(on_success):
    def try_login():
        username = username_var.get()
        password = password_var.get()
        if db_utils.check_admin(username, password):
            login_win.destroy()
            on_success(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_win = tk.Tk()
    login_win.title("Admin Login")
    login_win.geometry("300x180")
    tk.Label(login_win, text="Admin Login", font=("Arial", 14)).pack(pady=10)
    tk.Label(login_win, text="Username:").pack()
    username_var = tk.StringVar()
    tk.Entry(login_win, textvariable=username_var).pack()
    tk.Label(login_win, text="Password:").pack()
    password_var = tk.StringVar()
    tk.Entry(login_win, textvariable=password_var, show="*").pack()
    tk.Button(login_win, text="Login", command=try_login).pack(pady=10)
    login_win.mainloop()

if __name__ == "__main__":
    def after_login(user):
        messagebox.showinfo("Welcome", f"Welcome, {user}!")
    launch_admin_login(after_login)
