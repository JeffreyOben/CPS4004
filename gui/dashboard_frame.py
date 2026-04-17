# Northshore Logistics System - Operational Dashboard Component
import tkinter as tk
from gui.components import ScrollableFrame

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        self.CLR_TEXT = "#2d3436"
        self.CLR_ACCENT_BLUE = "#3498db"
        self.CLR_ACCENT_YLW = "#f1c40f"
        self.CLR_ACCENT_RED = "#e74c3c"
        self.CLR_ACCENT_GRN = "#2ecc71"
        
        # Stats Container
        stats_frame = tk.Frame(self, bg="white")
        stats_frame.pack(fill="x", pady=(0, 50))
        self.load_stats(stats_frame)

        # Activity Stream Section
        act_header = tk.Frame(self, bg="white")
        act_header.pack(fill="x", pady=(20, 15))
        tk.Label(act_header, text="SYSTEM ACTIVITY STREAM (AUTO-SCROLLING)", 
                 font=("Arial", 9, "bold"), bg="white", fg="#636e72").pack(side="left")
        tk.Frame(act_header, bg="#f1f2f6", height=2).pack(side="left", fill="x", expand=True, padx=(20, 0))
        
        # Scrollable Feed
        self.scroll_outer = tk.Frame(self, bg="white", highlightbackground="#f1f2f6", highlightthickness=1)
        self.scroll_outer.pack(fill="both", expand=True)
        
        self.feed = ScrollableFrame(self.scroll_outer, bg="white")
        self.feed.pack(fill="both", expand=True)
        
        self.refresh_logs()

    def load_stats(self, parent):
        parent.columnconfigure((0,1,2,3), weight=1)
        
        shipment_count = self.controller.db.fetch_one("SELECT COUNT(*) FROM shipments")[0]
        pending_count = self.controller.db.fetch_one("SELECT COUNT(*) FROM shipments WHERE status = 'Pending'")[0]
        low_stock_count = self.controller.db.fetch_one("SELECT COUNT(*) FROM inventory WHERE quantity <= reorder_level")[0]
        vehicle_count = self.controller.db.fetch_one("SELECT COUNT(*) FROM vehicles WHERE is_available = 1")[0]

        stats = [
            ("TOTAL SHIPMENTS", shipment_count, self.CLR_ACCENT_BLUE),
            ("PENDING DELIVERIES", pending_count, self.CLR_ACCENT_YLW),
            ("LOW STOCK ALERTS", low_stock_count, self.CLR_ACCENT_RED),
            ("AVAILABLE FLEET", vehicle_count, self.CLR_ACCENT_GRN)
        ]

        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(parent, bg="white", height=160, 
                            highlightbackground="#f1f2f6", highlightthickness=1)
            card.grid(row=0, column=i, padx=8, pady=10, sticky="nsew")
            card.pack_propagate(False)
            
            tk.Frame(card, bg=color, height=5).pack(fill="x", side="top")
            tk.Label(card, text=label, bg="white", fg="#b2bec3", font=("Arial", 7, "bold")).pack(pady=(30, 5))
            tk.Label(card, text=str(value), bg="white", fg=self.CLR_TEXT, font=("Arial", 18, "bold")).pack()

    def refresh_logs(self):
        for widget in self.feed.scroll_content.winfo_children(): widget.destroy()
        
        role = self.controller.current_user[3]
        user_id = self.controller.current_user[0]
        
        # Privacy Implementation: Admin/Manager see global, other users see personal work
        if role in ["Admin", "Manager"]:
            query = "SELECT action, details, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 30"
            params = ()
        else:
            query = "SELECT action, details, timestamp FROM audit_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 30"
            params = (user_id,)
            
        recent_logs = self.controller.db.fetch_all(query, params)
        
        if not recent_logs:
            tk.Label(self.feed.scroll_content, text="No events recorded for this account.", bg="white", fg="#dfe6e9", pady=60).pack()
        else:
            for action, details, ts in recent_logs:
                row = tk.Frame(self.feed.scroll_content, bg="white", pady=12)
                row.pack(fill="x", padx=25)
                
                tk.Label(row, text=f"{ts[5:16]}", bg="#f8f9fa", fg="#95a5a6", 
                         font=("Consolas", 8), padx=8, pady=3).pack(side="left")
                
                text_frame = tk.Frame(row, bg="white")
                text_frame.pack(side="left", padx=20)
                
                tk.Label(text_frame, text=f"{action}", bg="white", fg=self.CLR_ACCENT_BLUE, 
                         font=("Arial", 8, "bold")).pack(anchor="w")
                tk.Label(text_frame, text=f"{details}", bg="white", fg=self.CLR_TEXT, 
                         font=("Arial", 9)).pack(anchor="w")
                
                tk.Frame(self.feed.scroll_content, bg="#f1f2f6", height=1).pack(fill="x", padx=25)

        self.feed.canvas.yview_moveto(0)
