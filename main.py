import sys
import logging
from database_manager import DatabaseManager
from security import hash_password, xor_cipher
from gui.app import NorthshoreApp

# Configure standard logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def seed_database(db):
    """Populates the database with initial data for demonstration."""
    
    # 1. Seed Users (if not exists)
    if not db.fetch_one("SELECT id FROM users WHERE username = ?", ("admin",)):
        db.execute_query(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Admin", "System Administrator")
        )
        db.execute_query(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            ("staff1", hash_password("staff123"), "Warehouse Staff", "John Doe")
        )
        db.execute_query(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            ("driver1", hash_password("driver123"), "Driver", "Robert Swift")
        )

    # 2. Seed Warehouses
    if not db.fetch_one("SELECT id FROM warehouses"):
        db.execute_query(
            "INSERT INTO warehouses (location_name, address) VALUES (?, ?)",
            ("London Hub", "12 Industrial Way, London")
        )
        db.execute_query(
            "INSERT INTO warehouses (location_name, address) VALUES (?, ?)",
            ("Manchester Depot", "45 Canal Street, Manchester")
        )

    # 3. Seed Inventory
    if not db.fetch_one("SELECT id FROM inventory"):
        db.execute_query(
            "INSERT INTO inventory (warehouse_id, item_name, quantity, reorder_level) VALUES (?, ?, ?, ?)",
            (1, "Standard Pallets", 150, 50)
        )
        db.execute_query(
            "INSERT INTO inventory (warehouse_id, item_name, quantity, reorder_level) VALUES (?, ?, ?, ?)",
            (1, "Packaging Tape", 10, 20)  # Low stock
        )

    # 4. Seed Vehicles & Drivers
    if not db.fetch_one("SELECT id FROM vehicles"):
        db.execute_query(
            "INSERT INTO vehicles (license_plate, capacity_kg) VALUES (?, ?)",
            ("LN75 ABC", 3500)
        )
        db.execute_query(
            "INSERT INTO drivers (user_id, license_number, employment_status) VALUES (?, ?, ?)",
            (3, "ABC123456D", "Active")
        )

    # 5. Seed Shipments (Relational Manifest System)
    if not db.fetch_one("SELECT id FROM shipments"):
        db.execute_query(
            """INSERT INTO shipments (order_number, sender_name, sender_address, 
               receiver_name, receiver_address, status) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("ORD001", "Global Tech", xor_cipher("10 Tech Park, Reading"), 
             "Alice Smith", xor_cipher("22 High St, Bristol"), "Pending")
        )
        
        ship_id = db.fetch_one("SELECT id FROM shipments WHERE order_number = 'ORD001'")[0]
        db.execute_query("INSERT INTO shipment_items (shipment_id, inventory_id, quantity) VALUES (?, ?, ?)", (ship_id, 1, 5))
        db.execute_query("INSERT INTO shipment_items (shipment_id, inventory_id, quantity) VALUES (?, ?, ?)", (ship_id, 2, 2))

def main():
    logging.info("Starting Northshore Logistics System...")
    # Initialise the DB
    db = DatabaseManager()
    
    # Seed data for demo purposes
    logging.info("Validating database state...")
    seed_database(db)
    
    # Launch the GUI
    logging.info("Launching Northshore Logistics GUI...")
    app = NorthshoreApp()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)
