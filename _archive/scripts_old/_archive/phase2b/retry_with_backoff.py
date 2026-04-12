#!/usr/bin/env python3
"""
retry_with_backoff.py — Exponential Backoff with Jitter Pattern
================================================================
Fuer transiente API Errors (429, 500, 503).

Usage:
    from retry_with_backoff import retry_with_backoff, is_retryable
    
    result = retry_with_backoff(
        lambda: api_call(),
        max_retries=3,
        base_delay=1.0
    )

Pattern:
    - Attempt 1: wait 1s + jitter
    - Attempt 2: wait 2s + jitter
    - Attempt 3: wait 4s + jitter
    - Attempt 4: wait 8s + jitter
"""

import time
import random
from functools import wraps
from typing import Callable, Any, Optional, Set

# Retryable HTTP status codes
RETRYABLE_CODES = {
    429,  # Rate Limit
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}

# Retryable error types
RETRYABLE_ERRORS = {
    "timeout",
    "connection",
    "temporarily unavailable",
    "rate limit",
    "service unavailable",
    "too many requests",
}

def is_retryable(error: Exception) -> bool:
    """Check if an error is retryable."""
    error_str = str(error).lower()
    
    # Check for retryable HTTP codes
    if hasattr(error, 'status_code'):
        if error.status_code in RETRYABLE_CODES:
            return True
    
    # Check for retryable error messages
    for retryable in RETRYABLE_ERRORS:
        if retryable in error_str:
            return True
    
    return False


def calculate_delay(attempt: int, base_delay: float = 1.0, 
                    max_delay: float = 30.0, 
                    jitter_factor: float = 0.5) -> float:
    """
    Calculate delay with exponential backoff and jitter.
    
    Formula: min(base_delay * 2^attempt + random * jitter, max_delay)
    """
    # Exponential backoff
    exponential_delay = base_delay * pow(2, attempt)
    
    # Cap at max delay
    capped_delay = min(exponential_delay, max_delay)
    
    # Add jitter
    jitter = capped_delay * jitter_factor * random.random()
    
    return capped_delay + jitter


def retry_with_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter_factor: float = 0.5,
    retryable_check: Optional[Callable[[Exception], bool]] = None,
    on_retry: Optional[Callable[[Exception, int, float], None]] = None
) -> Any:
    """
    Execute a function with exponential backoff and jitter retry logic.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 30.0)
        jitter_factor: Jitter factor 0-1 (default: 0.5)
        retryable_check: Custom function to check if error is retryable
        on_retry: Callback function(error, attempt, delay) called before each retry
    
    Returns:
        Result of the function call
    
    Raises:
        Last exception if all retries fail
    """
    last_error: Optional[Exception] = None
    
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            return func()
        except Exception as e:
            last_error = e
            
            # Check if we should retry
            if attempt >= max_retries:
                break
                
            # Check if error is retryable
            if retryable_check and not retryable_check(e):
                break
            elif retryable_check is None and not is_retryable(e):
                break
            
            # Calculate delay
            delay = calculate_delay(attempt, base_delay, max_delay, jitter_factor)
            
            # Call on_retry callback if provided
            if on_retry:
                on_retry(e, attempt + 1, delay)
            
            # Sleep before retry
            time.sleep(delay)
    
    # All retries exhausted, raise last error
    raise last_error


def retry_decorator(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter_factor: float = 0.5
):
    """
    Decorator version of retry_with_backoff.
    
    Usage:
        @retry_decorator(max_retries=3, base_delay=1.0)
        def api_call():
            return some_api()
    """
    def decorator(func: Callable[[], Any]) -> Callable[[], Any]:
        @wraps(func)
        def wrapper() -> Any:
            return retry_with_backoff(
                func,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                jitter_factor=jitter_factor
            )
        return wrapper
    return decorator


# ============ CLI Interface ============

if __name__ == "__main__":
    import sys
    import json
    
    print("Retry with Backoff - Exponential Backoff Pattern")
    print("=" * 50)
    print()
    print("Usage:")
    print("  from retry_with_backoff import retry_with_backoff")
    print("  result = retry_with_backoff(lambda: api_call())")
    print()
    print("Pattern:")
    print("  Attempt 1: wait ~1s + jitter")
    print("  Attempt 2: wait ~2s + jitter")
    print("  Attempt 3: wait ~4s + jitter")
    print("  Attempt 4: wait ~8s + jitter")
    print()
    print("Retryable Errors:")
    print("  HTTP Codes: %s" % sorted(RETRYABLE_CODES))
    print("  Error Types: %s" % sorted(RETRYABLE_ERRORS))
    print()
    
    # Demo calculation
    print("Example Delays (base=1s, jitter=0.5):")
    for attempt in range(5):
        delay = calculate_delay(attempt, base_delay=1.0, max_delay=30.0, jitter_factor=0.5)
        print("  Attempt %d: %.2fs" % (attempt + 1, delay))
