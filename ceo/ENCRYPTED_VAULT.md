# ENCRYPTED VAULT — Für Secrets und Credentials

**Erstellt:** 2026-04-10
**Basierend auf:** knowledge-graph-skill vault Pattern
**Status:** Konzept + Test Script

---

## 🎯 PROBLEM

**Aktuell:** API Keys und Secrets liegen als Klartext im Knowledge Graph.

**Risiken:**
- Knowledge Graph wird exportiert/backuppt
- Secrets in Log-Files
- Versehentliches Teilen
- Unbefugter Zugriff

---

## 💡 LÖSUNG

**Verschlüsselter Vault** wie bei knowledge-graph-skill:

```
Verschlüsselung: AES-256-GCM
Key-Derivation: PBKDF2 (100k iterations)
Speicherort: memory/vault.enc.json
Key-File: memory/.vault-key (600 permissions)
```

---

## 🔐 TECHNISCHE DETAILS

### Algorithmus
- **Verschlüsselung:** AES-256-GCM
- **Key-Derivation:** PBKDF2 mit SHA256, 100k iterations
- **Salt:** 16 bytes (zufällig pro encryption)
- **IV:** 12 bytes (zufällig pro encryption)
- **Auth Tag:** 16 bytes

### File Structure
```json
{
  "api_key_name": {
    "value": "verschlüsselter_string",
    "note": "z.B. 'Buffer API Key - rotiert 2026-04'",
    "rotated": "2026-04-10"
  }
}
```

### Vault Key
- Wird automatisch generiert beim ersten Mal
- Gespeichert in `memory/.vault-key`
- **NIEMALS** in Git oder Backup!
- **NIEMALS** teilen!

---

## 🛠️ IMPLEMENTIERUNG

### vault.py erstellen:

```python
#!/usr/bin/env python3
"""
Encrypted Vault für Secrets
Verschlüsselung: AES-256-GCM mit PBKDF2
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

VAULT_PATH = Path(__file__).parent.parent / "memory" / "vault.enc.json"
KEY_PATH = Path(__file__).parent.parent / "memory" / ".vault-key"
SALT_LEN = 16
IV_LEN = 12
TAG_LEN = 16
KDF_ITER = 100000

def get_or_create_key():
    """Hole existierenden Key oder erstelle neuen."""
    if KEY_PATH.exists():
        return KEY_PATH.read_text().strip()
    key = get_random_bytes(32).hex()
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

def encrypt(plaintext, key):
    """Verschlüsselt plaintext mit AES-256-GCM."""
    salt = get_random_bytes(SALT_LEN)
    iv = get_random_bytes(IV_LEN)
    derived = derive_key(key, salt)
    cipher = AES.new(derived, AES.MODE_GCM, iv)
    ct, tag = cipher.encrypt(plaintext), cipher.digest()
    # salt + iv + tag + ciphertext
    return base64.b64encode(salt + iv + tag + ct).decode()

def decrypt(b64_data, key):
    """Entschlüsselt AES-256-GCM data."""
    data = base64.b64decode(b64_data)
    salt, iv, tag, ct = data[:16], data[16:28], data[28:44], data[44:]
    derived = derive_key(key, salt)
    cipher = AES.new(derived, AES.MODE_GCM, iv)
    cipher.set_authenticator(tag)
    return cipher.decrypt(ct)

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
    return decrypt(vault[name]["value"], key)

def vault_list():
    """Listet alle Secrets (ohne values)."""
    vault = load_vault()
    return [(k, v["note"], v["rotated"]) for k, v in vault.items()]

def load_vault():
    if VAULT_PATH.exists():
        return json.loads(VAULT_PATH.read_text())
    return {}

def save_vault(vault):
    VAULT_PATH.write_text(json.dumps(vault, indent=2))

# CLI Interface
if __name__ == "__main__":
    import argparse
    from datetime import date
    
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    
    set_p = sub.add_parser("set")
    set_p.add_argument("name")
    set_p.add_argument("value")
    set_p.add_argument("-n", "--note", default="")
    set_p.set_defaults(func=lambda a: vault_set(a.name, a.value, a.note))
    
    get_p = sub.add_parser("get")
    get_p.add_argument("name")
    get_p.set_defaults(func=lambda a: print(vault_get(a.name) or "Not found"))
    
    list_p = sub.add_parser("list")
    list_p.set_defaults(func=lambda a: [print(f"{n}: {note} ({rotated})") 
                                        for n, note, rotated in vault_list()])
    
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
```

---

## 📋 COMMANDS

```bash
# Secret speichern
python3 scripts/vault.py set buffer_api_key "sk-xxxx" -n "Buffer API Key"

# Secret abrufen
python3 scripts/vault.py get buffer_api_key

# Alle Secrets auflisten
python3 scripts/vault.py list

# Im Script verwenden:
python3 -c "
import scripts.vault as vault
key = vault.vault_get('buffer_api_key')
print(key)
"
```

---

## 🔒 SECURITY CHECKLISTE

- [ ] vault.enc.json ist in .gitignore
- [ ] .vault-key hat 600 permissions
- [ ] NIEMALS vault.enc.json committen
- [ ] NIEMALS .vault-key teilen
- [ ] Regelmäßig Keys rotieren

---

## 📝 NUTZUNG IM KG

Statt im KG:
```json
{
  "type": "credential",
  "name": "Buffer API Key",
  "value": "sk-xxxx"  // NIE SO!
}
```

Im Vault:
```json
{
  "type": "credential",
  "name": "Buffer API Key",
  "vault_ref": "buffer_api_key"  // Referenz zum Vault
}
```

---

## 🎯 NÄCHSTE SCHRITTE

1. ✅ Konzept dokumentiert
2. ⏳ vault.py Script erstellen
3. ⏳ Test mit einem API Key
4. ⏳ Integration in KG (credential entities)
5. ⏳ Backup/Restore testen

---

*Erlernt aus: knowledge-graph-skill vault.mjs Pattern*
