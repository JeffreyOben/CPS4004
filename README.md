# Northshore Logistics: Centralised Database System

![Status](https://img.shields.io/badge/Status-Production--Ready-success)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite%203-blueviolet)

Northshore Logistics Ltd is a modern, high-DPI Enterprise Resource Planning (ERP) platform designed to streamline distribution operations. By unifying warehouse inventory, multi-product manifests, and asset-linked dispatching into a single interface, this system eliminates the fragmentation of legacy spreadsheet-based workflows.

---

## 🔥 Professional Features

### 📦 Relational Shipment & Manifest Hub
Manage complex orders through a rigorous 5-stage state machine:
- **Multi-Product Manifests**: Add multiple products and quantities to a single order via a dynamic line-item interface.
- **Automated Stock Reservation**: Inventory is **immediately deducted** upon order creation to "lock" stock and prevent phantom inventory.
- **Fail-Safe Inventory Guard**: The system blocks orders that exceed available stock and provides specific warehouse-location feedback.

### 📊 Operational Insights (Pandas-Powered)
- **Fleet Analytics**: Real-time calculation of vehicle utilization rates and availability.
- **Inventory Risk Profiles**: automated identification of products below reorder thresholds.
- **Lifecycle Visualization**: Distribution analysis of order statuses across the entire logistics chain.
- **Export Capabilities**: Generate professional CSV reports for offline auditing.

### 🔐 Enterprise-Grade Security
- **Role-Based Access Control (RBAC)**: Customised interfaces for Admins, Managers, Staff, and Drivers.
- **Sensitive Data Obfuscation**: Personal addresses protected using a character-wise XOR cipher.
- **Credential Safety**: SHA-256 salted hashing and `secrets`-generated session tokenization.
- **Immutable Auditing**: Comprehensive dual-layer logging (Database + `app.log` file).

---

## 🛠️ Technology Stack & Compliance
This software adheres 100% to the permitted Python standard libraries:
- **Data Handling**: `pandas`, `sqlite3`
- **Security**: `hashlib`, `secrets`, `os`
- **Core Engine**: `tkinter`, `logging`, `datetime`

---

## 📥 Installation & Setup

1. **Clone & Initialize**:
   ```bash
   python main.py
   ```
   *Note: The database is auto-migrated on the first launch. Default Admin: `admin` / `admin123`.*

2. **Run Tests**:
   ```bash
   python tests/test_suite.py
   ```

---

## 📋 System Workflow Guide
The system is designed with a **"Logic First"** approach. The **Logistics Lifecycle Guide** (visible in the Shipment Hub when no order is selected) provides a real-time manual for role responsibilities at each stage of the delivery pipeline.

---

## ⚖️ License
This project is developed for academic purposes as part of the **CPS4004 Database Systems** assessment. All rights reserved.
