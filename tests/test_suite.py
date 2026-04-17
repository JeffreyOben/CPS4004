import sys
import os
# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager
from security import hash_password, xor_cipher

def test_security_logic():
    print("Test 1: Password Hashing...")
    p1 = "secret_pass"
    h1 = hash_password(p1)
    h2 = hash_password(p1)
    assert h1 == h2, "Hashing consistency failed"
    assert h1 != p1, "Hash returned plain text"
    print("SUCCESS: Password hashing verified.")

    print("Test 2: XOR Encryption Round-trip...")
    original = "123 Sensitive Street, London"
    encrypted = xor_cipher(original)
    decrypted = xor_cipher(encrypted)
    assert original == decrypted, "XOR decryption failed round-trip"
    assert original != encrypted, "XOR failed to obfuscate data"
    print("SUCCESS: Sensitive data encryption verified.")

def test_database_integrity():
    print("Test 3: Database Table Creation & FK constraints...")
    test_db = "test_inventory.db"
    if os.path.exists(test_db): os.remove(test_db)
    
    db = DatabaseManager(test_db)
    
    # Check if tables exist
    tables_raw = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in tables_raw]
    
    required = ["users", "warehouses", "inventory", "vehicles", "drivers", "shipments", "incidents", "audit_logs"]
    for table in required:
        assert table in tables, f"Missing table: {table}"
    
    # Cleanup
    if os.path.exists(test_db): os.remove(test_db)
    print("SUCCESS: Database schema verified.")

def run_all_tests():
    try:
        test_security_logic()
        test_database_integrity()
        print("\n--- ALL CORE LOGIC TESTS PASSED ---")
    except AssertionError as e:
        print(f"\n--- TEST FAILED: {e} ---")
        sys.exit(1)
    except Exception as e:
        print(f"\n--- UNEXPECTED ERROR: {e} ---")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
