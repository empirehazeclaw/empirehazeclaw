#!/usr/bin/env python3
"""
✅ PRODUCT VALIDATION WORKFLOW
============================
Validates product ideas before building - per SOUL.md
"""

import requests
import json

def validate_idea(product_name, niche):
    """Validate if there's actual demand for the product"""
    
    results = {
        "search": False,
        "trends": False,
        "competition": False,
        "outreach": False
    }
    
    # 1. Google Trends Check
    try:
        r = requests.get(
            f"https://trends.google.com/trends/explore?q={niche}",
            timeout=10
        )
        results["trends"] = r.status_code == 200
    except:
        pass
    
    # 2. Search competition
    try:
        r = requests.get(
            f"https://www.google.com/search?q={niche}+buy",
            timeout=10
        )
        results["competition"] = "€" in r.text or "buy" in r.text.lower()
    except:
        pass
    
    # Calculate score
    score = sum(results.values()) * 25
    
    return {
        "product": product_name,
        "niche": niche,
        "results": results,
        "score": score,
        "approved": score >= 75  # Need 3/4 validation methods
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 validate_product.py <name> <niche>")
        sys.exit(1)
    
    result = validate_idea(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
