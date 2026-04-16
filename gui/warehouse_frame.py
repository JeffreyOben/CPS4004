import tkinter as tk
from tkinter import ttk, messagebox
from gui.components import ControlButton, BaseDialog

class WarehouseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.CLR_STRIPE = "#f9f9f9"
        
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", pady=(0, 25))
        
        ControlButton(header, text="REGISTER NEW FACILITY", command=self.add_warehouse).pack(side="left")
        ControlButton(header, text="EDIT FACILITY DATA", command=self.edit_warehouse, bg="#f1c40f").pack(side="left", padx=15)
        ControlButton(header, text="DECOMMISSION FACILITY", command=self.delete_warehouse, bg="#eb4d4b").pack(side="left")

        # Table
        tree_container = tk.Frame(self, bg="white")
        tree_container.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 11), rowheight=40)
        
        self.tree = ttk.Treeview(tree_container, columns=("ID", "Name", "Address"), show="headings")
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.tag_configure('oddrow', background="white")
        self.tree.tag_configure('evenrow', background=self.CLR_STRIPE)
        
        self.tree.heading("ID", text="FID")
        self.tree.heading("Name", text="FACILITY NAME")
        self.tree.heading("Address", text="LOCATION ADDRESS")
        
        # Column widths
        self.tree.column("ID", width=70, anchor="center")
        self.tree.column("Name", width=250)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        warehouses = self.controller.db.fetch_all("SELECT id, location_name, address FROM warehouses")
        for i, wh in enumerate(warehouses):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=wh, tags=(tag,))

    def add_warehouse(self):
        WarehouseDialog(self, self.controller)

    def edit_warehouse(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a warehouse facility to modify.")
            return
        wh_data = self.tree.item(selected[0])['values']
        WarehouseDialog(self, self.controller, wh_id=wh_data[0], initial_data=wh_data)

    def delete_warehouse(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a warehouse to decommission.")
            return
        wh_id = self.tree.item(selected[0])['values'][0]
        
        # Check if warehouse has inventory
        count = self.controller.db.fetch_one("SELECT COUNT(*) FROM inventory WHERE warehouse_id = ?", (wh_id,))[0]
        if count > 0:
            messagebox.showerror("Error", f"Cannot delete facility while it still contains {count} items in stock.")
            return

        if messagebox.askyesno("Confirm Decommission", "Are you sure? This facility will be permanently removed from the logistics registry."):
            self.controller.db.execute_query("DELETE FROM warehouses WHERE id = ?", (wh_id,))
            self.refresh_list()

class WarehouseDialog(BaseDialog):
    def __init__(self, parent_frame, controller, wh_id=None, initial_data=None):
        title = "Edit Facility" if wh_id else "Register Facility"
        super().__init__(parent_frame.winfo_toplevel(), title=title, width=500, height=500)
        self.parent_frame, self.controller, self.wh_id = parent_frame, controller, wh_id
        
        self.create_field(self.content_frame, "FACILITY NAME", "name")
        self.create_field(self.content_frame, "LOCATION ADDRESS", "address")
        
        if initial_data:
            self.name.insert(0, initial_data[1])
            self.address.insert(0, initial_data[2])

        ControlButton(self.content_frame, text="SAVE RECORD", command=self.save).pack(fill="x", pady=25)

    def save(self):
        n, a = self.name.get(), self.address.get()
        if not all([n, a]):
            messagebox.showwarning("Fields Required", "Both Name and Address are mandatory.")
            return
            
        if self.wh_id:
            self.controller.db.execute_query("UPDATE warehouses SET location_name = ?, address = ? WHERE id = ?", (n, a, self.wh_id))
        else:
            self.controller.db.execute_query("INSERT INTO warehouses (location_name, address) VALUES (?, ?)", (n, a))
            
        self.parent_frame.refresh_list()
        self.destroy()
