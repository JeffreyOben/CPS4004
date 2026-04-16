import tkinter as tk
from tkinter import ttk, messagebox
from gui.components import BaseDialog, ControlButton
from security import hash_password

class UserRegistryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", pady=(0, 25))
        
        ControlButton(header, text="PROVISION ACCOUNT", command=self.add_user_dialog).pack(side="left")
        ControlButton(header, text="EDIT USER DATA", command=self.edit_user_dialog, bg="#f1c40f").pack(side="left", padx=15)
        ControlButton(header, text="DEACTIVATE USER", command=self.delete_user, bg="#e74c3c").pack(side="left")
        
        # Table Container with Scrollbar
        tree_container = tk.Frame(self, bg="white")
        tree_container.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 11), rowheight=40)
        
        self.tree = ttk.Treeview(tree_container, columns=("ID", "Username", "Role", "Name"), show="headings")
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.heading("ID", text="UID")
        self.tree.heading("Username", text="STAFF USERNAME")
        self.tree.heading("Role", text="ACCESS ROLE")
        self.tree.heading("Name", text="LEGAL FULL NAME")
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        users = self.controller.db.fetch_all("SELECT id, username, role, full_name FROM users")
        for u in users: self.tree.insert("", "end", values=u)

    def add_user_dialog(self):
        UserEditDialog(self, self.controller)

    def edit_user_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user account from the list to modify their credentials.")
            return
        u_data = self.tree.item(selected[0])['values']
        UserEditDialog(self, self.controller, user_id=u_data[0], initial_data=u_data)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user account to deactivate.")
            return
        u_id = self.tree.item(selected[0])['values'][0]
        if u_id == 1:
            messagebox.showerror("Error", "Primary Admin account cannot be deactivated for system safety.")
            return
        if messagebox.askyesno("Confirm", "Deactivate this account? This will revoke all system access for this user."):
            self.controller.db.execute_query("DELETE FROM users WHERE id = ?", (u_id,))
            self.refresh_list()

class UserEditDialog(BaseDialog):
    def __init__(self, parent_frame, controller, user_id=None, initial_data=None):
        title = "Edit User" if user_id else "Provision Account"
        super().__init__(parent_frame.winfo_toplevel(), title=title, width=450, height=700)
        self.parent_frame, self.controller, self.user_id = parent_frame, controller, user_id
        
        self.create_field(self.content_frame, "STAFF ID", "username")
        self.create_field(self.content_frame, "Password (BLANK = NO CHANGE)", "password", is_pwd=True)
        self.create_field(self.content_frame, "FULL NAME", "fullname")
        
        tk.Label(self.content_frame, text="ACCESS ROLE", bg="white", fg="#95a5a6", font=("Arial", 8, "bold")).pack(anchor="w")
        self.role_var = tk.StringVar(value="Warehouse Staff")
        roles = ["Admin", "Manager", "Warehouse Staff", "Driver"]
        self.role_menu = ttk.Combobox(self.content_frame, textvariable=self.role_var, values=roles, state="readonly")
        self.role_menu.pack(fill="x", pady=(10, 30))
        
        if initial_data:
            self.username.insert(0, initial_data[1]); self.fullname.insert(0, initial_data[3])
            self.role_var.set(initial_data[2])

        ControlButton(self.content_frame, text="SAVE PROFILE", command=self.save).pack(fill="x", pady=20)

    def save(self):
        u, p, f, r = self.username.get(), self.password.get(), self.fullname.get(), self.role_var.get()
        if not all([u, f, r]): 
            messagebox.showwarning("Missing Fields", "Username, Full Name, and Role are mandatory.")
            return
        if self.user_id:
            if p: self.controller.db.execute_query("UPDATE users SET username=?, password_hash=?, role=?, full_name=? WHERE id=?", (u, hash_password(p), r, f, self.user_id))
            else: self.controller.db.execute_query("UPDATE users SET username=?, role=?, full_name=? WHERE id=?", (u, r, f, self.user_id))
        else:
            if not p:
                messagebox.showwarning("Password Required", "A security password must be set for new accounts.")
                return
            self.controller.db.execute_query("INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)", (u, hash_password(p), r, f))
        self.parent_frame.refresh_list(); self.destroy()
