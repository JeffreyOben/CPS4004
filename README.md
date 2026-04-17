# Northshore Logistics: Centralised Database System

![Status](https://img.shields.io/badge/Status-Production--Ready-success)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite%203-blueviolet)

Northshore Logistics Ltd is a modern, high-DPI Enterprise Resource Planning (ERP) platform designed to streamline distribution operations. By unifying warehouse inventory, multi-product manifests, and asset-linked dispatching into a single interface, this system eliminates the fragmentation of legacy spreadsheet-based workflows.

---

## Professional Features

### Relational Shipment & Manifest Hub
Manage complex orders through a rigorous 5-stage state machine:
- **Multi-Product Manifests**: Add multiple products and quantities to a single order via a dynamic line-item interface.
- **Automated Stock Reservation**: Inventory is **immediately deducted** upon order creation to "lock" stock and prevent phantom inventory.
- **Fail-Safe Inventory Guard**: The system blocks orders that exceed available stock and provides specific warehouse-location feedback.

### Operational Reports (Pandas-Powered)
- **Fleet Analytics**: Real-time calculation of vehicle utilization rates and availability.
- **Inventory Risk Profiles**: automated identification of products below reorder thresholds.
- **Lifecycle Visualization**: Distribution analysis of order statuses across the entire logistics chain.
- **Export Capabilities**: Generate professional CSV reports for offline auditing.

### Enterprise-Grade Security
- **Role-Based Access Control (RBAC)**: Customised interfaces for Admins, Managers, Staff, and Drivers.
- **Sensitive Data Obfuscation**: Personal addresses protected using a character-wise XOR cipher.
- **Credential Safety**: SHA-256 salted hashing and `secrets`-generated session tokenization.
- **Immutable Auditing**: Comprehensive dual-layer logging (Database + `app.log` file).

---

## Technology Stack & Compliance
This software adheres 100% to the permitted Python standard libraries:
- **Data Handling**: `pandas`, `sqlite3`
- **Security**: `hashlib`, `secrets`, `os`
- **Core Engine**: `tkinter`, `logging`, `datetime`

---

## Installation & Setup

1. **Clone & Initialize**:
   ```bash
   python main.py
   ```

2. **Verify Setup (Optional)**:
   Run the core logic and security test suite to ensure your environment is configured correctly:
   ```bash
   python tests/test_suite.py
   ```

   *Note: The database is auto-migrated on the first launch. Default Admin: `admin` / `admin123`.*
   
---

## Troubleshooting & Technical Resolutions

If you encounter issues during setup, check the following professional resolutions:

### 1. Tkinter Missing (Python Setup)
On some Linux distributions or custom Python installs, the GUI library (`tkinter`) is not included by default.
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS/Windows**: Re-run the official Python installer and ensure "tcl/tk and IDLE" is checked.

### 2. Operational Reports (Pandas Dependency)
The Advanced Analytics module requires the `pandas` library. If the "Operational Reports" page shows a dependency warning:
```bash
pip install pandas
```

### 3. Windows UI Scaling
If the interface appears oversized or blurry on Windows laptops, ensure you are running the latest version of the code. We have implemented **Windows-Specific DPI Awareness** (via `SetProcessDpiAwareness`) to fix this automatically.

### 4. Database Initialization
If you see a "Database Locked" error, ensure only one instance of the application is running at a time.

---

## System Workflow Guide
The system is designed with a **"Logic First"** approach. The **Logistics Lifecycle Guide** (visible in the Shipment Hub when no order is selected) provides a real-time manual for role responsibilities at each stage of the delivery pipeline.

---

## License
This project is developed for academic purposes as part of the **CPS4004 Database Systems** assessment. All rights reserved.
