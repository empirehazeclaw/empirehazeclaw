#!/usr/bin/env python3
"""
Structured Logging - Better debugging
"""
import json
from datetime import datetime

def log_event(event_type, data):
    """Log in structured format"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": data
    }
    with open("logs/structured.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def log_metric(metric, value):
    """Log a metric"""
    log_event("metric", {"metric": metric, "value": value})
