#!/usr/bin/env python3
"""
Stripe Auto-Invoice System
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
INVOICE_DIR = WORKSPACE / "data" / "invoices"

def generate_invoice_number():
    """RE-2026-0001"""
    INVOICE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(INVOICE_DIR.glob("RE-*.txt"))
    if files:
        try:
            last_num = int(files[-1].name.split("-")[-1].split(".")[0])
            return f"RE-{datetime.now().year}-{last_num + 1:04d}"
        except:
            pass
    return f"RE-{datetime.now().year}-0001"

def handle_payment(email, name, product, amount):
    inv_num = generate_invoice_number()
    date = datetime.now().strftime("%Y-%m-%d")
    net = amount / 1.19
    vat = amount - net
    
    text = f"""
╔═══════════════════════════════════════════════════════════╗
║                      RECHNUNG                              ║
╠═══════════════════════════════════════════════════════════╣
║  Nr: {inv_num:<48} ║
║  Datum: {date:<47} ║
╠═══════════════════════════════════════════════════════════╣
║  Kunde: {name:<48} ║
║  Email: {email:<48} ║
╠═══════════════════════════════════════════════════════════╣
║  {product:<50} ║
║  Netto:     {net:>10.2f} €                               ║
║  MwSt 19%:  {vat:>10.2f} €                               ║
║  ─────────────────────────────────────────               ║
║  BRUTTO:    {amount:>10.2f} €                               ║
╠═══════════════════════════════════════════════════════════╣
║  EmpireHazeClaw GmbH | Germany | DE123456789               ║
╚═══════════════════════════════════════════════════════════╝
"""
    # Save
    with open(INVOICE_DIR / f"{inv_num}.txt", 'w') as f:
        f.write(text)
    
    # Metadata
    meta = {"invoice": inv_num, "date": date, "email": email, "name": name, "product": product, "amount": amount}
    with open(INVOICE_DIR / f"{inv_num}.json", 'w') as f:
        json.dump(meta, f, indent=2)
    
    print(f"✅ Invoice {inv_num} saved for {email}")
    return inv_num

if __name__ == "__main__":
    handle_payment("kunde@beispiel.de", "Max Mustermann", "Managed AI Web Hosting Basic", 49.00)
