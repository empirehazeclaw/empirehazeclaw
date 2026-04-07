#!/usr/bin/env python3
"""
Customer Feedback System
"""
import json

FEEDBACK_FILE = "data/feedback.json"

def collect_feedback(customer_id, rating, comment):
    """Collect customer feedback"""
    feedback = {
        "customer": customer_id,
        "rating": rating,  # 1-5
        "comment": comment,
        "timestamp": "now"
    }
    
    try:
        with open(FEEDBACK_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    
    data.append(feedback)
    
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    return {"saved": True, "rating": rating}

def get_nps():
    """Calculate NPS score"""
    # Net Promoter Score calculation
    return 50  # placeholder
