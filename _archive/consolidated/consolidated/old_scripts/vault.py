#!/usr/bin/env python3
"""
Sir HazeClaw — Encrypted Vault für Secrets
Verschlüsselung: AES-256-GCM mit PBKDF2

Verwendung:
    python3 vault.py set <name> <value> [-n note]
    python3 vault.py get <name>
    python3 vault.py list
"""

import os
import json
import base64
import hashlib
import argparse
from pathlib import Path
from datetime import date

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("WARNING: cryptography library nicht verfügbar. Fallback zu Base64.")
    import base64 as b64

# Config
SCRIPT_DIR = Path(__file__).parent.parent
VAULT_PATH = SCRIPT_DIR / "memory" / "vault.enc.json"
KEY_PATH = SCRIPT_DIR / "memory" / ".vault-key"
SALT_LEN = 16
IV_LEN = 12
KDF_ITER = 100000

def get_or_create_key():
    """Hole existierenden Key oder erstelle neuen."""
    if KEY_PATH.exists():
        return KEY_PATH.read_text().strip()
    # 32 bytes = 256 bits für AES-256
    key = os.urandom(32).hex()
    KEY_PATH.write_text(key + "\n")
    os.chmod(KEY_PATH, 0o600)
    return key

def derive_key(passphrase, salt):
    """PBKDF2 Key Derivation."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        passphrase.encode(),
        salt,
        KDF_ITER,
        dklen=32
    )

def encrypt(plaintext, key_hex):
    """Verschlüsselt plaintext mit AES-256-GCM."""
    if HAS_CRYPTO:
        salt = os.urandom(SALT_LEN)
        iv = os.urandom(IV_LEN)
        derived = derive_key(key_hex, salt)
        aesgcm = AESGCM(derived)
        ct = aesgcm.encrypt(iv, plaintext.encode(), None)
        # salt + iv + ciphertext
        return base64.b64encode(salt + iv + ct).decode()
    else:
        # Fallback: nur base64
        return base64.b64encode(plaintext.encode()).decode()

def decrypt(data, key_hex):
    """Entschlüsselt AES-256-GCM data."""
    if HAS_CRYPTO:
        raw = base64.b64decode(data)
        salt, iv, ct = raw[:SALT_LEN], raw[SALT_LEN:SALT_LEN+IV_LEN], raw[SALT_LEN+IV_LEN:]
        derived = derive_key(key_hex, salt)
        aesgcm = AESGCM(derived)
        return aesgcm.decrypt(iv, ct, None).decode()
    else:
        return base64.b64decode(data).decode()

def vault_set(name, value, note=""):
    """Speichert einen Secret."""
    key = get_or_create_key()
    vault = load_vault()
    vault[name] = {
        "value": encrypt(value, key),
        "note": note,
        "rotated": str(date.today())
    }
    save_vault(vault)
    return {"ok": True, "name": name}

def vault_get(name):
    """Holt einen Secret."""
    key = get_or_create_key()
    vault = load_vault()
    if name not in vault:
        return None
    try:
        return decrypt(vault[name]["value"], key)
    except Exception as e:
        return f"ERROR: {e}"

def vault_list():
    """Listet alle Secrets (ohne values)."""
    vault = load_vault()
    return [(k, v.get("note", ""), v.get("rotated", "?")) 
            for k, v in vault.items()]

def load_vault():
    if VAULT_PATH.exists():
        return json.loads(VAULT_PATH.read_text())
    return {}

def save_vault(vault):
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VAULT_PATH.write_text(json.dumps(vault, indent=2))

def cmd_set(args):
    result = vault_set(args.name, args.value, args.note)
    if result["ok"]:
        print(f"✅ Secret '{args.name}' gespeichert.")

def cmd_get(args):
    value = vault_get(args.name)
    if value:
        print(value)
    else:
        print(f"Secret '{args.name}' nicht gefunden.")

def cmd_list(args):
    secrets = vault_list()
    if not secrets:
        print("Vault ist leer.")
        return
    print(f"{'Name':<30} {'Note':<30} {'Rotated':<12}")
    print("-" * 75)
    for name, note, rotated in sorted(secrets):
        print(f"{name:<30} {note:<30} {rotated:<12}")

def cmd_delete(args):
    vault = load_vault()
    if args.name in vault:
        del vault[args.name]
        save_vault(vault)
        print(f"✅ Secret '{args.name}' gelöscht.")
    else:
        print(f"Secret '{args.name}' nicht gefunden.")

def main():
    parser = argparse.ArgumentParser(description="Sir HazeClaw Vault")
    sub = parser.add_subparsers(dest="cmd")
    
    # set
    p_set = sub.add_parser("set", help="Secret speichern")
    p_set.add_argument("name", help="Name des Secrets")
    p_set.add_argument("value", help="Wert des Secrets")
    p_set.add_argument("-n", "--note", default="", help="Notiz")
    p_set.set_defaults(func=cmd_set)
    
    # get
    p_get = sub.add_parser("get", help="Secret abrufen")
    p_get.add_argument("name", help="Name des Secrets")
    p_get.set_defaults(func=cmd_get)
    
    # list
    p_list = sub.add_parser("list", help="Alle Secrets auflisten")
    p_list.set_defaults(func=cmd_list)
    
    # delete
    p_del = sub.add_parser("delete", help="Secret löschen")
    p_del.add_argument("name", help="Name des Secrets")
    p_del.set_defaults(func=cmd_delete)
    
    args = parser.parse_args()
    
    if not args.cmd:
        parser.print_help()
        return
    
    args.func(args)

if __name__ == "__main__":
    main()
