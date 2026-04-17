# Northshore Logistics System - Login & Security Access Component
import tkinter as tk
from tkinter import messagebox
from security import hash_password

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2c3e50")
        self.controller = controller
        
        self.CLR_TEXT = "#2d3436"
        self.CLR_BLUE = "#3498db"
        self.CLR_BORDER = "black"
        
        card = tk.Frame(self, bg="white", padx=80, pady=80)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(card, text="Northshore Logistics", 
                 font=("Arial", 18, "bold"), bg="white", fg=self.CLR_TEXT).pack(pady=(0, 5))
        tk.Label(card, text="SYSTEM ACCESS PORTAL", 
                 font=("Arial", 8, "bold"), bg="white", fg="#95a5a6").pack(pady=(0, 30))
        
        self.create_input(card, "USERNAME / STAFF ID", "username_entry")
        self.create_input(card, "SECURE PASSWORD", "password_entry", is_pwd=True)
        
        self.btn_container = tk.Frame(card, bg=self.CLR_BLUE)
        self.btn_container.pack(pady=(20, 0), fill="x")
        
        self.login_btn_lbl = tk.Label(self.btn_container, text="SIGN IN", 
                                      bg=self.CLR_BLUE, fg="white", font=("Arial", 12, "bold"), 
                                      pady=20, cursor="hand2")
        self.login_btn_lbl.pack(fill="both", expand=True)
        
        for w in [self.btn_container, self.login_btn_lbl]:
            w.bind("<Button-1>", lambda e: self.attempt_login())
            w.bind("<Enter>", lambda e: self.on_btn_hover(True))
            w.bind("<Leave>", lambda e: self.on_btn_hover(False))
        
        self.username_entry.focus_set()
        self.controller.bind('<Return>', lambda event: self.attempt_login())

    def on_btn_hover(self, is_hover):
        color = "#2980b9" if is_hover else self.CLR_BLUE
        self.btn_container.config(bg=color)
        self.login_btn_lbl.config(bg=color)

    def create_input(self, parent, label_text, attr_name, is_pwd=False):
        tk.Label(parent, text=label_text, bg="white", fg="#b2bec3", font=("Arial", 9, "bold")).pack(anchor="w")
        
        # Consistent minimalist line and font
        entry = tk.Entry(parent, width=45, bg="white", fg="black", 
                         insertbackground="black", font=("Arial", 11),
                         relief="flat", borderwidth=0, 
                         highlightthickness=1,
                         highlightbackground=self.CLR_BORDER,
                         highlightcolor=self.CLR_BLUE)
        
        entry.pack(fill="x", pady=(5, 25), ipady=1)
        if is_pwd: entry.config(show="*")
        setattr(self, attr_name, entry)

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password: return
        
        pw_hash = hash_password(password)
        user = self.controller.db.fetch_one("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
        
        if user:
            self.controller.db.execute_query("INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)", (user[0], "LOGIN", f"User {username} logged in."))
            self.controller.unbind('<Return>')
            self.controller.login_success(user)
        else:
            messagebox.showerror("Access Denied", "Invalid credentials.")
