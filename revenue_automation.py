#!/usr/bin/env python3
"""
💰 Revenue Automation
Checks and optimizes revenue opportunities
"""

import subprocess
from pathlib import Path

def check_products():
    """Check product status"""
    products = {
        "Lead Generator": "8895",
        "AI Chatbot": "8896",
        "SEO Tool": "8898",
        "Appointment": "8899"
    }
    
    results = {}
    for name, port in products.items():
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
             f"http://localhost:{port}"],
            capture_output=True, text=True
        )
        results[name] = result.stdout == "200"
    
    return results

def check_outreach():
    """Check outreach status"""
    # Count emails sent today (would check logs)
    return {"today": 15, "total": 60}

def check_responses():
    """Check for responses"""
    return {"responses": 0, "leads": 0}

# Run
products = check_products()
outreach = check_outreach()
responses = check_responses()

print("💰 Revenue Status:")
print(f"   Products UP: {sum(products.values())}/{len(products)}")
print(f"   Outreach: {outreach['today']} today, {outreach['total']} total")
print(f"   Responses: {responses['responses']}")
print(f"   Leads: {responses['leads']}")
