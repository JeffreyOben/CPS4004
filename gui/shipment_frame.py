# Northshore Logistics System - Shipment Lifecycle Management Component
import tkinter as tk
from tkinter import ttk, messagebox
from gui.components import BaseDialog, ControlButton, ScrollableFrame
from security import xor_cipher

class ShipmentFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.CLR_STRIPE = "#f9f9f9"
        
        # UI Panels
        self.left_panel = tk.Frame(self, bg="white")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=10)
        
        self.right_panel = tk.Frame(self, bg="#fafafa", width=460, highlightbackground="#f1f2f6", highlightthickness=1)
        self.right_panel.pack(side="right", fill="both", padx=(20, 0))
        self.right_panel.pack_propagate(False)
        
        self.create_list_view()
        self.create_details_view()

    def create_list_view(self):
        ctrl = tk.Frame(self.left_panel, bg="white")
        ctrl.pack(fill="x", pady=(0, 25))
        
        role = self.controller.current_user[3]
        if role in ["Admin", "Warehouse Staff"]:
            ControlButton(ctrl, text="CREATE ORDER", command=self.add_shipment_dialog).pack(side="left")
        
        ControlButton(ctrl, text="REFRESH SYSTEM", command=self.refresh_list, bg="#95a5a6").pack(side="right")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 11), rowheight=40)
        
        tree_container = tk.Frame(self.left_panel, bg="white")
        tree_container.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_container, columns=("ID", "Order", "Receiver", "Status"), show="headings")
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.tag_configure('oddrow', background="white")
        self.tree.tag_configure('evenrow', background=self.CLR_STRIPE)
        self.tree.tag_configure('cancelled', foreground="#95a5a6")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Order", text="ORDER NO.")
        self.tree.heading("Receiver", text="RECIPIENT")
        self.tree.heading("Status", text="LIFECYCLE STATUS")
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_shipment_select)
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        role = self.controller.current_user[3]
        user_id = self.controller.current_user[0]
        
        if role == "Driver":
            driver_info = self.controller.db.fetch_one("SELECT id FROM drivers WHERE user_id = ?", (user_id,))
            if driver_info:
                query = "SELECT id, order_number, receiver_name, status FROM shipments WHERE assigned_driver_id = ? ORDER BY id DESC"
                params = (driver_info[0],)
            else: return
        else:
            query = "SELECT id, order_number, receiver_name, status FROM shipments ORDER BY id DESC"
            params = ()

        shipments = self.controller.db.fetch_all(query, params)
        for i, s in enumerate(shipments):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            if s[3] == "Cancelled": tag = 'cancelled'
            self.tree.insert("", "end", values=s, tags=(tag,))

    def create_details_view(self):
        """Shows the Logistics Lifecycle Guide when no order is selected."""
        for widget in self.right_panel.winfo_children(): widget.destroy()
        
        wrapper = tk.Frame(self.right_panel, bg="#fafafa", padx=35, pady=40)
        wrapper.pack(fill="both", expand=True)
        
        tk.Label(wrapper, text="LOGISTICS LIFECYCLE GUIDE", font=("Arial", 14, "bold"), 
                 bg="#fafafa", fg="#2d3436").pack(anchor="w", pady=(0, 30))
        
        guide_steps = [
            ("1. PENDING", "staff1", "Order details registered. Product inventory reserved immediately.", "#95a5a6"),
            ("2. CONFIRMED", "manager1", "Review complete. Transportation cost and assets approved.", "#f1c40f"),
            ("3. PICKED UP", "staff1", "Item retrieved. Specific Driver & Vehicle assigned to load.", "#0984e3"),
            ("4. IN TRANSIT", "driver1", "Vehicle is out for delivery. Real-time route tracking active.", "#e67e22"),
            ("5. DELIVERED", "driver1", "Final delivery confirmed. Order lifecycle closed.", "#2ecc71")
        ]
        
        for step, user, desc, color in guide_steps:
            f = tk.Frame(wrapper, bg="white", highlightbackground="#f1f2f6", highlightthickness=1, pady=15, padx=20)
            f.pack(fill="x", pady=6)
            
            tk.Label(f, text=step, font=("Arial", 9, "bold"), bg="white", fg=color).pack(anchor="w")
            tk.Label(f, text=f"Actor: {user}", font=("Arial", 8), bg="white", fg="#95a5a6").pack(anchor="w", pady=(2, 5))
            tk.Label(f, text=desc, font=("Arial", 9), bg="white", fg="#2d3436", wraplength=350, justify="left").pack(anchor="w")

    def on_shipment_select(self, event):
        selected = self.tree.selection()
        if not selected: 
            self.create_details_view()
            return
        ship_id = self.tree.item(selected[0])['values'][0]
        shipment = self.controller.db.fetch_one("SELECT * FROM shipments WHERE id = ?", (ship_id,))
        if shipment: self.show_shipment_details(shipment)

    def show_shipment_details(self, shipment):
        for widget in self.right_panel.winfo_children(): widget.destroy()
        
        role = self.controller.current_user[3]
        status = shipment[7]
            
        header = tk.Frame(self.right_panel, bg="#fafafa", padx=35, pady=30)
        header.pack(fill="x")
        
        tk.Label(header, text=f"ORDER RD-{shipment[1]}", font=("Arial", 16, "bold"), 
                 bg="#fafafa", fg="#2d3436").pack(anchor="w")
        
        progress = tk.Frame(self.right_panel, bg="#dfe6e9", height=4)
        progress.pack(fill="x", padx=35, pady=(0, 20))
        
        states = ["Pending", "Confirmed", "Picked Up", "In Transit", "Delivered"]
        if status in states:
            idx = states.index(status) + 1
            fill = tk.Frame(progress, bg="#2ecc71", width=(idx/len(states))*390, height=4)
            fill.pack(side="left")

        info_scroll = ScrollableFrame(self.right_panel, bg="#fafafa")
        info_scroll.pack(fill="both", expand=True, padx=35)
        
        driver_name, vehicle_info = "UNASSIGNED", "NO ASSET"
        if shipment[9]:
            d = self.controller.db.fetch_one("SELECT u.full_name FROM drivers d JOIN users u ON d.user_id = u.id WHERE d.id = ?", (shipment[9],))
            if d: driver_name = d[0]
        if shipment[10]:
            v = self.controller.db.fetch_one("SELECT license_plate FROM vehicles WHERE id = ?", (shipment[10],))
            if v: vehicle_info = v[0]

        fields = [
            ("SENDER", shipment[2]),
            ("ORIGIN", f"{xor_cipher(shipment[3])}"),
            ("RECEIVER", shipment[4]),
            ("DESTINATION", f"{xor_cipher(shipment[5])}"),
            ("STATUS", status),
            ("ASSIGNED DRIVER", driver_name),
            ("VEHICLE ASSET", vehicle_info)
        ]
        
        for lbl, val in fields:
            f = tk.Frame(info_scroll.scroll_content, bg="#fafafa")
            f.pack(fill="x", pady=8)
            tk.Label(f, text=lbl, font=("Arial", 8, "bold"), bg="#fafafa", fg="#b2bec3", width=15, anchor="w").pack(side="left")
            tk.Label(f, text=val, font=("Arial", 11, "bold"), bg="#fafafa", fg="#2d3436").pack(side="left")

        # Item List
        tk.Label(info_scroll.scroll_content, text="ORDER MANIFEST", font=("Arial", 8, "bold"), bg="#fafafa", fg="#b2bec3").pack(anchor="w", pady=(20, 10))
        items = self.controller.db.fetch_all("""
            SELECT i.item_name, si.quantity, w.location_name 
            FROM shipment_items si 
            JOIN inventory i ON si.inventory_id = i.id 
            JOIN warehouses w ON i.warehouse_id = w.id
            WHERE si.shipment_id = ?
        """, (shipment[0],))
        
        for name, qty, wh in items:
            item_f = tk.Frame(info_scroll.scroll_content, bg="white", pady=10, padx=15, highlightbackground="#f1f2f6", highlightthickness=1)
            item_f.pack(fill="x", pady=2)
            tk.Label(item_f, text=f"{qty}x {name}", font=("Arial", 10, "bold"), bg="white", fg="#2d3436").pack(side="left")
            tk.Label(item_f, text=f"[{wh}]", font=("Arial", 8), bg="white", fg="#95a5a6").pack(side="right")

        btn_box = tk.Frame(self.right_panel, bg="#fafafa", pady=25)
        btn_box.pack(fill="x", side="bottom")

        if status != "Cancelled" and status != "Delivered":
            if role in ["Admin", "Manager"]:
                ControlButton(btn_box, text="CANCEL ORDER", command=lambda: self.update_status(shipment[0], "Cancelled"), bg="#e74c3c").pack(fill="x", padx=35, pady=5)
            
            is_admin = (role == "Admin")
            if status == "Pending" and (role == "Manager" or is_admin):
                ControlButton(btn_box, text="APPROVE & CONFIRM", command=lambda: self.update_status(shipment[0], "Confirmed"), bg="#2ecc71").pack(fill="x", padx=35, pady=5)
            if status == "Confirmed" and (role == "Warehouse Staff" or is_admin):
                ControlButton(btn_box, text="PROCESS PICKUP", command=lambda: self.assign_driver_dialog(shipment[0]), bg="#0984e3").pack(fill="x", padx=35, pady=5)
            if status == "Picked Up" and (role == "Driver" or is_admin):
                ControlButton(btn_box, text="OUT FOR DELIVERY", command=lambda: self.update_status(shipment[0], "In Transit"), bg="#e67e22").pack(fill="x", padx=35, pady=5)
            if status == "In Transit" and (role == "Driver" or is_admin):
                ControlButton(btn_box, text="COMPLETE DELIVERY", command=lambda: self.update_status(shipment[0], "Delivered"), bg="#2ecc71").pack(fill="x", padx=35, pady=5)

    def update_status(self, ship_id, new_status):
        # Restoration Logic
        if new_status == "Cancelled":
            items = self.controller.db.fetch_all("SELECT inventory_id, quantity FROM shipment_items WHERE shipment_id = ?", (ship_id,))
            for inv_id, qty in items:
                self.controller.db.execute_query("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, inv_id))
            messagebox.showinfo("Stock Restored", "All order items have been returned to warehouse inventory.")

        self.controller.db.execute_query("UPDATE shipments SET status = ? WHERE id = ?", (new_status, ship_id))
        self.controller.db.execute_query("INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)", 
                                         (self.controller.current_user[0], "LIVECYCLE_CHANGE", f"Order {ship_id} ~ {new_status}"))
        self.refresh_list()
        messagebox.showinfo("Success", f"Order moved to {new_status}")
        self.show_shipment_details(self.controller.db.fetch_one("SELECT * FROM shipments WHERE id = ?", (ship_id,)))

    def assign_driver_dialog(self, ship_id):
        DriverAssignDialog(self, self.controller, ship_id)

    def add_shipment_dialog(self, ship_id=None, initial_data=None):
        if ship_id: return # Editing of complex multi-item orders is restricted to prevent stock sync errors
        AddShipmentDialog(self, self.controller)

class DriverAssignDialog(BaseDialog):
    def __init__(self, parent_frame, controller, ship_id):
        super().__init__(parent_frame.winfo_toplevel(), title="Dispatch Assignment", width=450, height=550)
        self.parent_frame, self.controller, self.ship_id = parent_frame, controller, ship_id
        
        tk.Label(self.content_frame, text="SELECT AVAILABLE DRIVER", bg="white", fg="#95a5a6", font=("Arial", 8, "bold")).pack(anchor="w")
        self.driver_var = tk.StringVar()
        drivers = self.controller.db.fetch_all("SELECT d.id, u.full_name FROM drivers d JOIN users u ON d.user_id = u.id")
        self.driver_map = {name: id for id, name in drivers}
        ttk.Combobox(self.content_frame, textvariable=self.driver_var, values=list(self.driver_map.keys()), state="readonly").pack(fill="x", pady=(10, 25))
        
        tk.Label(self.content_frame, text="SELECT AVAILABLE VEHICLE", bg="white", fg="#95a5a6", font=("Arial", 8, "bold")).pack(anchor="w")
        self.vehicle_var = tk.StringVar()
        vehicles = self.controller.db.fetch_all("SELECT id, license_plate FROM vehicles WHERE is_available = 1")
        self.vehicle_map = {f"{lp} (ID:{id})": id for id, lp in vehicles}
        ttk.Combobox(self.content_frame, textvariable=self.vehicle_var, values=list(self.vehicle_map.keys()), state="readonly").pack(fill="x", pady=(10, 25))

        ControlButton(self.content_frame, text="CONFIRM DISPATCH", command=self.save).pack(fill="x", pady=20)

    def save(self):
        d_name, v_info = self.driver_var.get(), self.vehicle_var.get()
        if d_name and v_info:
            d_id = self.driver_map[d_name]
            v_id = self.vehicle_map[v_info]
            self.controller.db.execute_query("UPDATE shipments SET assigned_driver_id = ?, assigned_vehicle_id = ?, status = 'Picked Up' WHERE id = ?", (d_id, v_id, self.ship_id))
            self.parent_frame.refresh_list(); self.destroy()

class AddShipmentDialog(BaseDialog):
    def __init__(self, parent_frame, controller):
        super().__init__(parent_frame.winfo_toplevel(), title="Create Multi-Product Order", width=650, height=850)
        self.parent_frame, self.controller = parent_frame, controller
        
        # Header Info
        header_f = tk.Frame(self.content_frame, bg="white")
        header_f.pack(fill="x", pady=(0, 20))
        self.create_field(header_f, "ORDER REFERENCE", "order_no")
        self.create_field(header_f, "SENDER NAME", "sender_name")
        self.create_field(header_f, "ORIGIN ADDRESS", "sender_addr")
        self.create_field(header_f, "RECEIVER NAME", "receiver_name")
        self.create_field(header_f, "DESTINATION ADDRESS", "receiver_addr")
        
        # Dynamic Product List
        tk.Label(self.content_frame, text="ORDER MANIFEST (PRODUCTS)", font=("Arial", 10, "bold"), bg="white", fg="#2d3436").pack(anchor="w", pady=(10, 10))
        self.items_container = tk.Frame(self.content_frame, bg="white")
        self.items_container.pack(fill="x")
        
        self.item_rows = []
        self.add_item_row()
        
        ControlButton(self.content_frame, text="+ ADD ANOTHER PRODUCT", command=self.add_item_row, bg="#95a5a6").pack(anchor="w", pady=10)
        ControlButton(self.content_frame, text="PLACE ORDER & RESERVE STOCK", command=self.save).pack(fill="x", pady=25)

    def add_item_row(self):
        row_f = tk.Frame(self.items_container, bg="white", pady=5)
        row_f.pack(fill="x")
        
        inv_data = self.controller.db.fetch_all("SELECT i.id, i.item_name, w.location_name FROM inventory i JOIN warehouses w ON i.warehouse_id = w.id")
        inv_map = {f"{item} [{wh}]": id for id, item, wh in inv_data}
        
        prod_var = tk.StringVar()
        combo = ttk.Combobox(row_f, textvariable=prod_var, values=list(inv_map.keys()), state="readonly", width=40)
        combo.pack(side="left", padx=(0, 10))
        
        qty_entry = tk.Entry(row_f, width=10, highlightbackground="black", highlightthickness=1)
        qty_entry.pack(side="left")
        qty_entry.insert(0, "1")
        
        remove_btn = tk.Label(row_f, text="X", fg="red", bg="white", cursor="hand2", font=("Arial", 10, "bold"))
        remove_btn.pack(side="left", padx=10)
        remove_btn.bind("<Button-1>", lambda e: self.remove_row(row_f, row_data))
        
        row_data = {"frame": row_f, "combo": combo, "qty": qty_entry, "map": inv_map}
        self.item_rows.append(row_data)

    def remove_row(self, frame, data):
        if len(self.item_rows) > 1:
            frame.destroy()
            self.item_rows.remove(data)

    def save(self):
        # 1. Basic Validation
        header = [self.order_no.get(), self.sender_name.get(), xor_cipher(self.sender_addr.get()), 
                  self.receiver_name.get(), xor_cipher(self.receiver_addr.get())]
        if not all(header):
            messagebox.showwarning("Incomplete", "All delivery details are required.")
            return

        # 2. Manifest Validation & Stock Check
        manifest = []
        errors = []
        for row in self.item_rows:
            prod_str = row["combo"].get()
            qty_str = row["qty"].get()
            if not prod_str or not qty_str: continue
            
            p_id = row["map"][prod_str]
            try:
                requested_qty = int(qty_str)
            except: continue
            
            # CHECK STOCK
            stock = self.controller.db.fetch_one("SELECT quantity, item_name, (SELECT location_name FROM warehouses WHERE id=warehouse_id) FROM inventory WHERE id=?", (p_id,))
            if stock[0] < requested_qty:
                errors.append(f"Insufficient Stock: '{stock[1]}' only has {stock[0]} units available in {stock[2]}.")
            else:
                manifest.append((p_id, requested_qty))
        
        if errors:
            messagebox.showerror("Inventory Alert", "\n".join(errors))
            return
        
        if not manifest:
            messagebox.showwarning("Empty", "Please add at least one product to the order.")
            return

        # 3. COMMIT ORDER & DEDUCT
        try:
            self.controller.db.execute_query("INSERT INTO shipments (order_number, sender_name, sender_address, receiver_name, receiver_address, status) VALUES (?,?,?,?,?,'Pending')", header)
            ship_id = self.controller.db.fetch_one("SELECT last_insert_rowid()")[0]
            
            for p_id, q in manifest:
                self.controller.db.execute_query("INSERT INTO shipment_items (shipment_id, inventory_id, quantity) VALUES (?,?,?)", (ship_id, p_id, q))
                self.controller.db.execute_query("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (q, p_id))
            
            self.parent_frame.refresh_list()
            messagebox.showinfo("Success", f"Order {header[0]} created. Stock has been reserved.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {e}")
