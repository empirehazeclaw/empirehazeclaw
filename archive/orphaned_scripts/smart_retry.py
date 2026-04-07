#!/usr/bin/env python3
"""
Smart Retry System - Automatic retry with exponential backoff
"""
import time
import logging

def retry(max_attempts=3, base_delay=1):
    """Decorator for automatic retry"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    delay = base_delay * (2 ** attempt)
                    logging.warning(f"Retry {attempt+1}/{max_attempts} in {delay}s: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

# Usage example
@retry(max_attempts=3, base_delay=2)
def api_call():
    # Your API call here
    pass
