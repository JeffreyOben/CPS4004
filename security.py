import hashlib
import os
import secrets

def load_encryption_key():
    """
    Manually parses the .env file to retrieve the XOR_KEY.
    Raises an error if the key is missing.
    """
    env_path = ".env"
    if not os.path.exists(env_path):
        raise FileNotFoundError("Security Error: .env file missing. System cannot start.")
    
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("XOR_KEY="):
                return line.split("=")[1].strip()
    
    raise ValueError("Security Error: XOR_KEY not found in .env file.")

# Global key for XOR encryption
ENCRYPTION_KEY = load_encryption_key()

def hash_password(password):
    """
    Hashes a password using SHA-256 via hashlib.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
    """
    Generates a secure, cryptographically strong unique token for 
    the current session using the secrets module.
    """
    return secrets.token_hex(24)

def xor_cipher(data):
    """
    Simple XOR-based encryption/decryption for sensitive data.
    Uses the key from the .env file.
    """
    if not data:
        return ""
    
    key = ENCRYPTION_KEY
    output = []
    for i in range(len(data)):
        # XOR each character with a character from the key (cycling the key)
        output_char = chr(ord(data[i]) ^ ord(key[i % len(key)]))
        output.append(output_char)
    
    return "".join(output)
