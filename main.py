import os
from database_manager import DatabaseManager
from security import hash_password, xor_cipher, ENCRYPTION_KEY

def run_basic_tests():
    print("--- Northshore Logistics System: Phase 3 Verification ---")
    
    # 1. Verify .env and Encryption Key
    print(f"Encryption Key Loaded: {'[SECRET]' if ENCRYPTION_KEY else 'FAILED'}")
    
    # 2. Database Initialisation
    db = DatabaseManager()
    print("Database initialised and tables created successfully.")
    
    # 3. Test Security Features
    test_pass = "admin123"
    hashed = hash_password(test_pass)
    print(f"Hashing Test: Input '{test_pass}' -> {hashed[:15]}...")
    
    sensitive_data = "123 Northshore Lane, Hub 1"
    encrypted = xor_cipher(sensitive_data)
    decrypted = xor_cipher(encrypted)
    print(f"Encryption Test: Original: '{sensitive_data}'")
    print(f"Encryption Test: Decrypted: '{decrypted}'")
    
    if sensitive_data == decrypted:
        print("Security Verification: SUCCESS")
    else:
        print("Security Verification: FAILED")

    # 4. Seed Initial Admin User (if not exists)
    admin_exists = db.fetch_one("SELECT id FROM users WHERE username = ?", ("admin",))
    if not admin_exists:
        db.execute_query(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Admin", "System Administrator")
        )
        print("Initial Admin user created (admin / admin123).")
    else:
        print("Admin user already exists.")

    print("-------------------------------------------------------")

if __name__ == "__main__":
    try:
        run_basic_tests()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
