# Northshore Logistics System - Inventory & Fleet Management Component
import tkinter as tk
from tkinter import ttk, messagebox
from gui.components import ControlButton, BaseDialog

class InventoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.CLR_STRIPE = "#f9f9f9"
        
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", pady=(0, 20))
        
        ControlButton(header, text="ADD NEW PRODUCT", command=self.add_item).pack(side="left")
        ControlButton(header, text="STOCK ADJUSTMENT", command=self.edit_item, bg="#f1c40f").pack(side="left", padx=15)
        ControlButton(header, text="REMOVE ITEM", command=self.delete_item, bg="#e74c3c").pack(side="left")

        # Table
        tree_container = tk.Frame(self, bg="white")
        tree_container.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 9), rowheight=30)
        
        self.tree = ttk.Treeview(tree_container, columns=("ID", "Warehouse", "Item", "Quantity", "Reorder"), show="headings")
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.tag_configure('oddrow', background="white")
        self.tree.tag_configure('evenrow', background=self.CLR_STRIPE)
        
        self.tree.heading("ID", text="SKU")
        self.tree.heading("Warehouse", text="FACILITY")
        self.tree.heading("Item", text="PRODUCT NAME")
        self.tree.heading("Quantity", text="ON HAND")
        self.tree.heading("Reorder", text="THRESHOLD")
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        query = """
            SELECT i.id, w.location_name, i.item_name, i.quantity, i.reorder_level 
            FROM inventory i
            JOIN warehouses w ON i.warehouse_id = w.id
        """
        items = self.controller.db.fetch_all(query)
        for i, item in enumerate(items):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=item, tags=(tag,))

    def add_item(self):
        InventoryDialog(self, self.controller)

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product from the list to perform a stock adjustment.")
            return
        item_data = self.tree.item(selected[0])['values']
        InventoryDialog(self, self.controller, item_id=item_data[0], initial_data=item_data)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product from the list first to remove it.")
            return
        item_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete this product? This will remove the record permanently."):
            self.controller.db.execute_query("DELETE FROM inventory WHERE id = ?", (item_id,))
            self.refresh_list()

class FleetFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.CLR_STRIPE = "#f9f9f9"
        
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", pady=(0, 20))
        
        ControlButton(header, text="REGISTER VEHICLE", command=self.add_vehicle).pack(side="left")
        ControlButton(header, text="UPDATE STATUS", command=self.edit_vehicle, bg="#f1c40f").pack(side="left", padx=15)
        ControlButton(header, text="DECOMMISSION", command=self.delete_vehicle, bg="#e74c3c").pack(side="left")

        # Vehicle List
        v_container = tk.Frame(self, bg="white")
        v_container.pack(fill="x", pady=(0, 30))
        
        self.fleet_tree = ttk.Treeview(v_container, columns=("ID", "License", "Capacity", "Status"), show="headings", height=8)
        vsb_v = ttk.Scrollbar(v_container, orient="vertical", command=self.fleet_tree.yview)
        self.fleet_tree.configure(yscrollcommand=vsb_v.set)
        
        self.fleet_tree.heading("ID", text="VEHICLE ID")
        self.fleet_tree.heading("License", text="LICENSE PLATE")
        self.fleet_tree.heading("Capacity", text="LIMIT (KG)")
        self.fleet_tree.heading("Status", text="CURRENT STATUS")
        
        self.fleet_tree.tag_configure('evenrow', background=self.CLR_STRIPE)
        self.fleet_tree.tag_configure('oddrow', background="white")
        
        self.fleet_tree.pack(side="left", fill="x", expand=True)
        vsb_v.pack(side="right", fill="y")
        
        # Driver List
        tk.Label(self, text="AUTHORIZED DRIVER REGISTRY", font=("Arial", 9, "bold"), 
                 bg="white", fg="#2d3436").pack(anchor="w", pady=(10,5))
        
        d_container = tk.Frame(self, bg="white")
        d_container.pack(fill="x")
        
        self.driver_tree = ttk.Treeview(d_container, columns=("Name", "License #", "Status"), show="headings", height=5)
        vsb_d = ttk.Scrollbar(d_container, orient="vertical", command=self.driver_tree.yview)
        self.driver_tree.configure(yscrollcommand=vsb_d.set)
        
        self.driver_tree.heading("Name", text="FULL LEGAL NAME")
        self.driver_tree.heading("License #", text="DRIVER LICENSE")
        self.driver_tree.heading("Status", text="WORK STATUS")
        
        self.driver_tree.pack(side="left", fill="x", expand=True)
        vsb_d.pack(side="right", fill="y")
        
        self.refresh_list()

    def refresh_list(self):
        for item in self.fleet_tree.get_children(): self.fleet_tree.delete(item)
        vehicles = self.controller.db.fetch_all("SELECT id, license_plate, capacity_kg, is_available FROM vehicles")
        for i, v in enumerate(vehicles):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            status = "Ready / Available" if v[3] else "In Maintenance"
            self.fleet_tree.insert("", "end", values=(v[0], v[1], v[2], status), tags=(tag,))
            
        for item in self.driver_tree.get_children(): self.driver_tree.delete(item)
        drivers = self.controller.db.fetch_all("""
            SELECT u.full_name, d.license_number, d.employment_status 
            FROM drivers d 
            JOIN users u ON d.user_id = u.id
        """)
        for d in drivers: self.driver_tree.insert("", "end", values=d)

    def add_vehicle(self): FleetDialog(self, self.controller)
    def edit_vehicle(self):
        selected = self.fleet_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a vehicle from the fleet registry to update its status.")
            return
        v_data = self.fleet_tree.item(selected[0])['values']
        FleetDialog(self, self.controller, v_id=v_data[0], initial_data=v_data)
    def delete_vehicle(self):
        selected = self.fleet_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a vehicle to decommission.")
            return
        v_id = self.fleet_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Decommission this vehicle? This will remove it from operational availability."):
            self.controller.db.execute_query("DELETE FROM vehicles WHERE id = ?", (v_id,))
            self.refresh_list()

class InventoryDialog(BaseDialog):
    def __init__(self, parent_frame, controller, item_id=None, initial_data=None):
        super().__init__(parent_frame.winfo_toplevel(), title="Product Record", width=500, height=650)
        self.parent_frame, self.controller, self.item_id = parent_frame, controller, item_id
        self.create_field(self.content_frame, "PRODUCT NAME", "name")
        self.create_field(self.content_frame, "QUANTITY", "qty")
        self.create_field(self.content_frame, "REORDER LEVEL", "reorder")
        tk.Label(self.content_frame, text="FACILITY", bg="white", fg="#95a5a6", font=("Arial", 8, "bold")).pack(anchor="w")
        self.wh_var = tk.StringVar()
        warehouses = self.controller.db.fetch_all("SELECT id, location_name FROM warehouses")
        self.wh_map = {name: id for id, name in warehouses}
        self.wh_menu = ttk.Combobox(self.content_frame, textvariable=self.wh_var, values=list(self.wh_map.keys()), state="readonly")
        self.wh_menu.pack(fill="x", pady=(5, 25))
        if initial_data:
            self.name.insert(0, initial_data[2]); self.qty.insert(0, initial_data[3])
            self.reorder.insert(0, initial_data[4]); self.wh_var.set(initial_data[1])
        ControlButton(self.content_frame, text="COMMIT DATA", command=self.save).pack(fill="x", pady=20)
    def save(self):
        n, q, r, w = self.name.get(), self.qty.get(), self.reorder.get(), self.wh_var.get()
        if not all([n, q, r, w]): return
        w_id = self.wh_map[w]
        if self.item_id: self.controller.db.execute_query("UPDATE inventory SET item_name=?, quantity=?, reorder_level=?, warehouse_id=? WHERE id=?", (n, q, r, w_id, self.item_id))
        else: self.controller.db.execute_query("INSERT INTO inventory (item_name, quantity, reorder_level, warehouse_id) VALUES (?,?,?,?)", (n, q, r, w_id))
        self.parent_frame.refresh_list(); self.destroy()

class FleetDialog(BaseDialog):
    def __init__(self, parent_frame, controller, v_id=None, initial_data=None):
        super().__init__(parent_frame.winfo_toplevel(), title="Vehicle Entry", width=450, height=550)
        self.parent_frame, self.controller, self.v_id = parent_frame, controller, v_id
        self.create_field(self.content_frame, "LICENSE", "license")
        self.create_field(self.content_frame, "CAPACITY (KG)", "capacity")
        self.status_var = tk.StringVar(value="Available")
        ttk.Combobox(self.content_frame, textvariable=self.status_var, values=["Available", "In Maintenance"], state="readonly").pack(fill="x", pady=10)
        if initial_data:
            self.license.insert(0, initial_data[1]); self.capacity.insert(0, initial_data[2])
            self.status_var.set("Available" if "Available" in initial_data[3] else "In Maintenance")
        ControlButton(self.content_frame, text="SAVE RECORD", command=self.save).pack(fill="x", pady=20)
    def save(self):
        l, c, s = self.license.get(), self.capacity.get(), self.status_var.get()
        a = 1 if s == "Available" else 0
        if self.v_id: self.controller.db.execute_query("UPDATE vehicles SET license_plate=?, capacity_kg=?, is_available=? WHERE id=?", (l, c, a, self.v_id))
        else: self.controller.db.execute_query("INSERT INTO vehicles (license_plate, capacity_kg, is_available) VALUES (?,?,?)", (l, c, a))
        self.parent_frame.refresh_list(); self.destroy()

class LogsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        tree_container = tk.Frame(self, bg="white")
        tree_container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container, columns=("Time", "User", "Action", "Details"), show="headings")
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.heading("Time", text="EVENT TIMESTAMP")
        self.tree.heading("User", text="UID")
        self.tree.heading("Action", text="OPERATION")
        self.tree.heading("Details", text="ENTITY DETAILS")
        
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 9), rowheight=30)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        self.load_data()
    def load_data(self):
        logs = self.controller.db.fetch_all("SELECT timestamp, user_id, action, details FROM audit_logs ORDER BY timestamp DESC")
        for log in logs: self.tree.insert("", "end", values=log)
