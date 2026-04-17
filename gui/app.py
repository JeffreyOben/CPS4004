# Northshore Logistics System - Application Controller Component
import tkinter as tk
from tkinter import messagebox
from database_manager import DatabaseManager

class NorthshoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Northshore Logistics Ltd - Centralised Database System")
        
        # 1. Window Maximization
        try:
            self.state('zoomed')
        except:
            self.attributes('-fullscreen', True)
        
        # 2. Global Typography (Optimized for Windows/Cross-platform)
        self.FONT_BASE = ("Arial", 10)
        self.FONT_BOLD = ("Arial", 10, "bold")
        self.FONT_TITLE = ("Arial", 18, "bold")
        self.FONT_HEADER = ("Arial", 14, "bold")
        
        # 3. Design Tokens
        self.CLR_SIDEBAR = "#1e272e"
        self.CLR_SIDEBAR_ACTIVE = "#0984e3"
        self.CLR_BG = "#f5f6fa"
        self.CLR_WHITE = "#ffffff"
        self.CLR_TEXT_DARK = "#2d3436"
        self.CLR_TEXT_LIGHT = "#dcdde1"
        self.CLR_RED = "#eb4d4b"
        
        self.db = DatabaseManager()
        self.current_user = None
        
        self.container = tk.Frame(self, bg=self.CLR_BG)
        self.container.pack(side="top", fill="both", expand=True)
        self.show_login()

    def show_login(self):
        from gui.login_frame import LoginFrame
        for widget in self.container.winfo_children(): widget.destroy()
        LoginFrame(self.container, self).pack(fill="both", expand=True)

    def login_success(self, user_data):
        from security import generate_session_token
        import logging
        self.current_user = user_data
        self.session_token = generate_session_token()
        logging.info(f"User {user_data[1]} authenticated. Active session token: {self.session_token[:8]}...")
        self.show_main_interface()

    def show_main_interface(self):
        for widget in self.container.winfo_children(): widget.destroy()
            
        header = tk.Frame(self.container, bg="#2c3e50", height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="NORTHSHORE LOGISTICS", fg="white", bg="#2c3e50", 
                 font=self.FONT_HEADER).pack(side="left", padx=40)
        
        right_header = tk.Frame(header, bg="#2c3e50")
        right_header.pack(side="right", padx=40)
        
        name_info = f"{self.current_user[4]} ({self.current_user[3]})"
        tk.Label(right_header, text=name_info, fg="#95a5a6", bg="#2c3e50", 
                 font=self.FONT_BASE).pack(side="left", padx=20)
        
        from gui.components import ControlButton
        ControlButton(right_header, text="SIGN OUT", command=self.show_login, 
                      bg=self.CLR_RED, font=self.FONT_BOLD, padx=25).pack(side="left")

        main_body = tk.Frame(self.container, bg=self.CLR_BG)
        main_body.pack(side="top", fill="both", expand=True)
        
        self.sidebar = tk.Frame(main_body, bg=self.CLR_SIDEBAR, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self.content_container = tk.Frame(main_body, bg=self.CLR_BG, padx=40, pady=40)
        self.content_container.pack(side="right", fill="both", expand=True)
        
        self.content_area = tk.Frame(self.content_container, bg=self.CLR_WHITE, 
                                     highlightbackground="#dfe6e9", highlightthickness=1)
        self.content_area.pack(fill="both", expand=True)
        
        self.create_nav_menu()
        self.show_dashboard()

    def create_nav_menu(self):
        role = self.current_user[3]
        nav_items = [("Dashboard", self.show_dashboard)]
        
        # Drivers now visit the Shipment Hub to see their assigned work
        if role in ["Admin", "Manager", "Warehouse Staff", "Driver"]:
            nav_items.append(("Shipment Hub", self.show_shipments))
            
        if role in ["Admin", "Manager", "Warehouse Staff"]:
            nav_items.append(("Inventory Control", self.show_inventory))
            
        if role in ["Admin", "Manager"]:
            nav_items.append(("Fleet Management", self.show_fleet))
            nav_items.append(("Facility Control", self.show_warehouses))
            nav_items.append(("Operational Reports", self.show_insights))
            
        if role == "Admin":
            nav_items.append(("User Registry", self.show_users))
            nav_items.append(("Security Audit", self.show_logs))

        self.menu_widgets = {}
        for text, command in nav_items:
            item_frame = tk.Frame(self.sidebar, bg=self.CLR_SIDEBAR, height=50)
            item_frame.pack(fill="x")
            item_frame.pack_propagate(False)
            
            indicator = tk.Frame(item_frame, bg=self.CLR_SIDEBAR_ACTIVE, width=7)
            indicator.pack(side="left", fill="y")
            indicator.pack_forget()
            
            label = tk.Label(item_frame, text=text.upper(), bg=self.CLR_SIDEBAR, 
                             fg=self.CLR_TEXT_LIGHT, font=self.FONT_BOLD, 
                             padx=35, anchor="w", cursor="hand2")
            label.pack(side="left", fill="both", expand=True)
            
            for widget in [item_frame, label]:
                widget.bind("<Button-1>", lambda e, cmd=command: cmd())
                widget.bind("<Enter>", lambda e, f=item_frame, l=label: self.on_menu_hover(f, l, True))
                widget.bind("<Leave>", lambda e, f=item_frame, l=label: self.on_menu_hover(f, l, False))
            
            self.menu_widgets[text] = {"frame": item_frame, "label": label, "indicator": indicator}

    def on_menu_hover(self, frame, label, is_hover):
        if label.cget("text").title() != self.active_menu:
            color = "#2d3436" if is_hover else self.CLR_SIDEBAR
            frame.config(bg=color)
            label.config(bg=color)

    def switch_frame(self, title):
        for widget in self.content_area.winfo_children(): widget.destroy()
        self.active_menu = title.replace(" Overview", "").replace(" Hub", "").replace(" Control", "").replace(" Management", "").replace(" Registry", "").replace(" Reports", "").title()
        
        for text, widgets in self.menu_widgets.items():
            if text in title:
                widgets["frame"].config(bg="#2d3436")
                widgets["label"].config(bg="#2d3436", fg="white")
                widgets["indicator"].pack(side="left", fill="y")
            else:
                widgets["frame"].config(bg=self.CLR_SIDEBAR)
                widgets["label"].config(bg=self.CLR_SIDEBAR, fg=self.CLR_TEXT_LIGHT)
                widgets["indicator"].pack_forget()

        bc_frame = tk.Frame(self.content_area, bg=self.CLR_WHITE, padx=35, pady=30)
        bc_frame.pack(side="top", fill="x")
        tk.Label(bc_frame, text=title.upper(), font=self.FONT_TITLE, 
                 bg=self.CLR_WHITE, fg=self.CLR_TEXT_DARK).pack(side="left")
        tk.Frame(self.content_area, bg=self.CLR_BG, height=2).pack(fill="x", padx=35)

    def show_dashboard(self):
        from gui.dashboard_frame import DashboardFrame
        self.switch_frame("Dashboard Overview")
        DashboardFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)

    def show_shipments(self):
        from gui.shipment_frame import ShipmentFrame
        self.switch_frame("Shipment Hub")
        ShipmentFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)

    def show_inventory(self):
        from gui.inventory_fleet_frames import InventoryFrame
        self.switch_frame("Inventory Control")
        InventoryFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)

    def show_fleet(self):
        from gui.inventory_fleet_frames import FleetFrame
        self.switch_frame("Fleet Management")
        FleetFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)

    def show_users(self):
        from gui.admin_frame import UserRegistryFrame
        self.switch_frame("User Registry")
        UserRegistryFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)

    def show_logs(self):
        from gui.inventory_fleet_frames import LogsFrame
        self.switch_frame("Security Audit")
        LogsFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)

    def show_warehouses(self):
        from gui.warehouse_frame import WarehouseFrame
        self.switch_frame("Facility Control")
        WarehouseFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)

    def show_insights(self):
        from gui.insights_frame import InsightsFrame
        self.switch_frame("Operational Reports")
        InsightsFrame(self.content_area, self).pack(fill="both", expand=True, padx=35, pady=20)
