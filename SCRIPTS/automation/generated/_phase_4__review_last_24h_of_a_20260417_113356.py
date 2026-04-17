```python
#!/usr/bin/env python3
"""
[PHASE 4] API Call Analyzer - Review last 24h of API calls,
identify 1 specific call that used too many tokens, optimize or cache it.
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import hashlib

# Configuration
SCRIPT_DIR = Path("/workspace/SCRIPTS/automation")
LOG_DIR = Path("/workspace/logs")
CACHE_DIR = Path("/workspace/SCRIPTS/automation/cache")
TOKEN_THRESHOLD_PERCENTILE = 90
CACHE_TTL_HOURS = 24

# Setup logging
def setup_logging(verbose: bool = False) -> logging.Logger:
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{SCRIPT_DIR}/api_analyzer.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Error handling wrapper
def handle_errors(func):
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return None
    return wrapper

@handle_errors
def get_api_logs(last_hours: int = 24) -> list:
    """Get API logs from the last N hours."""
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching API logs from last {last_hours} hours")
    
    # Try to read from log file
    log_file = LOG_DIR / "api_calls.log"
    
    if log_file.exists():
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        # Use subprocess to get system info / simulate log fetch
        result = subprocess.run(
            ['find', str(LOG_DIR), '-name', '*.log', '-mtime', '-1'],
            capture_output=True,
            text=True,
            timeout=30
        )
        logger.info(f"Found log files: {result.stdout}")
        logs = []
        
    # Filter logs for last 24 hours
    cutoff_time = datetime.now() - timedelta(hours=last_hours)
    recent_logs = []
    
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log.get('timestamp', '2024-01-01'))
            if log_time >= cutoff_time:
                recent_logs.append(log)
        except:
            continue
            
    logger.info(f"Found {len(recent_logs)} API calls in last {last_hours}h")
    return recent_logs

@handle_errors
def analyze_token_usage(logs: list) -> dict:
    """Analyze token usage and identify high consumption calls."""
    logger = logging.getLogger(__name__)
    
    if not logs:
        logger.warning("No logs to analyze")
        return {}
    
    token_data = defaultdict(list)
    
    for log in logs:
        endpoint = log.get('endpoint', 'unknown')
        tokens = log.get('tokens', 0)
        request_id = log.get('request_id', '')
        
        token_data[endpoint].append({
            'tokens': tokens,
            'request_id': request_id,
            'timestamp': log.get('timestamp'),
            'parameters': log.get('parameters', {})
        })
    
    # Calculate statistics per endpoint
    endpoint_stats = {}
    for endpoint, calls in token_data.items():
        total_tokens = sum(c['tokens'] for c in calls)
        avg_tokens = total_tokens / len(calls)
        max_call = max(calls, key=lambda x: x['tokens'])
        
        endpoint_stats[endpoint] = {
            'total_calls': len(calls),
            'total_tokens': total_tokens,
            'avg_tokens': avg_tokens,
            'max_tokens': max_call['tokens'],
            'max_call': max_call,
            'requests': calls
        }
    
    # Find the call with most tokens
    worst_call = None
    for endpoint, stats in endpoint_stats.items():
        if not worst_call or stats['max_tokens'] > worst_call['max_tokens']:
            worst_call = {
                'endpoint': endpoint,
                'stats': stats
            }
    
    logger.info(f"Identified high token usage call: {worst_call['endpoint']}")
    logger.info(f"Max tokens used: {worst_call['stats']['max_tokens']}")
    
    return worst_call

@handle_errors
def create_optimization_suggestion(high_token_call: dict) -> str:
    """Generate optimization suggestion for the identified call."""
    logger = logging.getLogger(__name__)
    
    endpoint = high_token_call['endpoint']
    stats = high_token_call['stats']
    max_call = stats['max_call']
    
    suggestions = []
    
    # Analyze parameters to suggest optimization
    params = max_call.get('parameters', {})
    
    if params.get('max_tokens'):
        suggestions.append(f"- Reduce max_tokens parameter: current={params.get('max_tokens')}")
    
    if params.get('temperature'):
        suggestions.append(f"- Adjust temperature: current={params.get('temperature')}")
    
    if params.get('response_format'):
        suggestions.append("- Use simpler response format to reduce token usage")
    
    # Generic optimizations
    suggestions.append("- Implement response caching for identical requests")
    suggestions.append("- Use streaming for large responses")
    suggestions.append("- Batch similar requests where possible")
    suggestions.append("- Consider using a smaller model for simple queries")
    
    suggestion_text = "\n".join(suggestions)
    logger.info(f"Generated optimization suggestions for {endpoint}")
    
    return suggestion_text

@handle_errors
def implement_caching(endpoint: str, max_call: dict):
    """Implement caching for the identified high-token call."""
    logger = logging.getLogger(__name__)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create cache key from endpoint and parameters
    cache_key = hashlib.md5(
        f"{endpoint}:{json.dumps(max_call.get('parameters', {}), sort_keys=True)}".encode()
    ).hexdigest()
    
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    cache_data = {
        'endpoint': endpoint,
        'parameters': max_call.get('parameters', {}),
        'tokens_used': max_call['tokens'],
        'cached_at': datetime.now().isoformat(),
        'ttl_hours': CACHE_TTL_HOURS,
        'optimized': True
    }
    
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    logger.info(f"Caching implemented for {endpoint}")
    logger.debug(f"Cache file created: {cache_file}")
    
    # Use subprocess to set permissions
    subprocess.run(['chmod', '644', str(cache_file)], check=True)

@handle_errors
def create_optimized_wrapper(high_token_call: dict) -> Path:
    """Create an optimized wrapper script for the identified call."""
    logger = logging.getLogger(__name__)
    
    endpoint_name = high_token_call['endpoint'].replace('/', '_').strip('_')
    wrapper_path = SCRIPT_DIR / f"optimized_{endpoint_name}.py"
    
    wrapper_code = f'''#!/usr/bin/env python3
"""
Auto-generated optimized wrapper for {high_token_call['endpoint']}
Created by API Analyzer - Phase 4
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path("{CACHE_DIR}")

def optimized_call(parameters: dict, force_refresh: bool = False):
    """
    Optimized API call with caching for {high_token_call['endpoint']}
    
    Args:
        parameters: API call parameters
        force_refresh: Bypass cache if True
    
    Returns:
        dict: Cached or fresh response
    """
    cache_key = hashlib.md5(
        json.dumps(parameters, sort_keys=True).encode()
    ).hexdigest()
    
    cache_file = CACHE_DIR / f"{{cache_key}}.json"
    
    # Check cache validity
    if not force_refresh and cache_file.exists():
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        
        cached_time = datetime.fromisoformat(cached['cached_at'])
        ttl = timedelta(hours={CACHE_TTL_HOURS})
        
        if datetime.now() - cached