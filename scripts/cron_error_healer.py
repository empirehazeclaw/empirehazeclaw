#!/usr/bin/env python3
"""
cron_error_healer.py - Auto-heals failed cron deliveries
Sir HazeClaw - 2026-04-11 v2

Based on Industry Best Practice: 4-Stage Recovery Loop
    Detect → Diagnose → Heal → Verify

NEW in v2:
- Circuit breaker for gateway restart loops
- 4-Stage loop with Verify phase
- Better error categorization
- Prevention of feedback loops
"""

import json
import subprocess
import sys
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List

# Paths
CRON_STATE_PATH = Path("/home/clawbot/.openclaw/cron/jobs.json")
HEAL_LOG = Path("/home/clawbot/.openclaw/workspace/logs/cron_healer.log")
BACKUP_DIR = Path("/home/clawbot/.openclaw/backups")
STATE_FILE = Path("/home/clawbot/.openclaw/workspace/data/healer_state.json")

# Circuit breaker config
MAX_GATEWAY_RESTARTS_PER_HOUR = 4
CIRCUIT_BREAKER_COOLDOWN = 300  # 5 minutes

# Retry with backoff config
RETRY_BASE_DELAY = 2.0  # seconds
RETRY_MAX_DELAY = 30.0  # seconds
RETRY_JITTER = 0.5

# Error categories (from Claude Lab Self-Healing research)
ERROR_CATEGORIES = {
    "transient_api": ["429:", "500:", "503:", "timeout", "ECONNREFUSED", "Connection refused"],
    "context_overflow": ["token limit", "context window", "max_tokens", "too many tokens"],
    "tool_failure": ["Cannot find module", "ENOENT", "Script not found", "path doesn't exist", "Module not found"],
    "malformed_output": ["JSON parse", "schema mismatch", "Invalid JSON", "JSONDecodeError"],
    "reasoning_error": ["hallucination", "contradiction", "invalid reasoning", "FallbackSummaryError", "All models failed"],
    "cascade_failure": ["GatewayDrainingError", "Gateway shutdown", "Gateway is draining", "Gateway down"],
    "rate_limit": ["429:", "Too Many Requests", "rate limit", "Rate limit exceeded"],
    "auth_error": ["401:", "403:", "Forbidden", "User not found", "Unauthorized", "auth"],
    "delivery_error": ["Message failed", "Delivery failed", "send failed", "Cannot send messages", "non-text channel"],
    "timeout_error": ["timed out", "timeout", "execution timeout", "LLM request timed out"],
}

# 7 Error categories with recovery strategies
HEALING_RULES = {
    # ===== Gateway/Cascade Failure - CIRCUIT BREAKER! =====
    "GatewayDrainingError": {
        "action": "circuit_breaker_gateway",
        "category": "cascade_failure",
        "note": "Gateway cascade - circuit breaker to prevent restart loop"
    },
    "Gateway shutdown": {
        "action": "circuit_breaker_gateway",
        "category": "cascade_failure",
        "note": "Gateway cascade - circuit breaker"
    },
    "Gateway is draining": {
        "action": "circuit_breaker_gateway",
        "category": "cascade_failure",
        "note": "Gateway draining is caused by restarts - STOP"
    },
    "ECONNREFUSED": {
        "action": "retry_with_backoff",
        "category": "transient_api",
        "note": "Connection refused - retry with backoff first, then restart"
    },

    # ===== Discord/Message errors =====
    "Outbound not configured for channel: discord": {
        "action": "disable_channel",
        "channel": "discord",
        "category": "tool_failure",
        "note": "Discord not configured - disable channel"
    },
    "Error: Outbound not configured": {
        "action": "disable_channel",
        "channel": "discord",
        "category": "tool_failure",
        "note": "Channel not configured - disable"
    },
    "Cannot send messages in a non-text channel": {
        "action": "disable_channel",
        "channel": "discord",
        "category": "tool_failure",
        "note": "Discord channel issue - disable"
    },
    "Error: Cannot send messages": {
        "action": "disable_channel",
        "channel": "discord",
        "category": "tool_failure",
        "note": "Cannot send messages - check channel"
    },

    # ===== Message delivery (Telegram, not Discord!) =====
    "Message failed": {
        "action": "check_delivery",
        "category": "delivery_error",
        "note": "Message failed - verify if actually delivered"
    },
    "⚠️ ✉️ Message failed": {
        "action": "check_delivery",
        "category": "delivery_error",
        "note": "Telegram delivery issue - verify first"
    },
    "Delivery failed": {
        "action": "check_delivery",
        "category": "delivery_error",
        "note": "Delivery failed - check status"
    },
    "send failed": {
        "action": "check_delivery",
        "category": "delivery_error",
        "note": "Send failed - verify"
    },

    # ===== Timeout errors =====
    "cron: job execution timed out": {
        "action": "increase_timeout_or_disable",
        "timeout_increase": 300,
        "max_consecutive": 3,
        "category": "transient_api",
        "note": "Timeout - increase timeout, disable after 3 consecutive"
    },
    "timeout": {
        "action": "increase_timeout_or_disable",
        "timeout_increase": 300,
        "max_consecutive": 3,
        "category": "transient_api",
        "note": "Timeout - increase timeout or disable"
    },
    "LLM request timed out": {
        "action": "increase_timeout_or_disable",
        "timeout_increase": 300,
        "max_consecutive": 3,
        "category": "transient_api",
        "note": "LLM timeout - increase timeout"
    },

    # ===== Auth/API errors =====
    "401: User not found": {
        "action": "disable_cron",
        "category": "auth_error",
        "note": "OpenRouter auth failed - disable cron"
    },
    "403: Forbidden": {
        "action": "disable_cron",
        "category": "auth_error",
        "note": "API forbidden - likely auth issue"
    },
    "429: Too Many Requests": {
        "action": "wait_and_retry",
        "category": "rate_limit",
        "note": "Rate limited - wait before retry"
    },

    # ===== Telegram errors =====
    "Telegram recipient": {
        "action": "disable_cron",
        "category": "delivery_error",
        "note": "Telegram recipient not found - disable cron"
    },
    "could not be resolved to a numeric chat ID": {
        "action": "disable_cron",
        "category": "delivery_error",
        "note": "Telegram username not resolvable - disable cron"
    },

    # ===== Edit failures =====
    "Edit: `": {
        "action": "disable_cron",
        "category": "tool_failure",
        "note": "Edit operation failed - script issue, disable cron"
    },
    "Edit failed": {
        "action": "disable_cron",
        "category": "tool_failure",
        "note": "Edit failed - disable cron"
    },

    # ===== Fallback/Model errors =====
    "FallbackSummaryError": {
        "action": "model_failover",
        "category": "reasoning_error",
        "note": "All models failed - try failover to healthy model"
    },
    "All models failed": {
        "action": "model_failover",
        "category": "reasoning_error",
        "note": "All models failed - try failover to healthy model"
    },

    # ===== Script/Module errors =====
    "Cannot find module": {
        "action": "disable_cron",
        "category": "tool_failure",
        "note": "Missing module - cron broken, disable"
    },
    "ENOENT": {
        "action": "disable_cron",
        "category": "tool_failure",
        "note": "File not found - script missing, disable"
    },
    "Script not found": {
        "action": "disable_cron",
        "category": "tool_failure",
        "note": "Script missing - disable cron"
    },
}

def log(msg, level="INFO"):
    """Log to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    print(log_line)

    with open(HEAL_LOG, "a") as f:
        f.write(log_line + "\n")

def load_state():
    """Load healer state for circuit breaker."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"gateway_restarts": [], "disabled_channels": [], "circuit_breaker": {}}

def save_state(state):
    """Save healer state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def calculate_backoff_delay(attempt: int) -> float:
    """Calculate delay with exponential backoff and jitter.
    
    Formula: min(base_delay * 2^attempt + random * jitter, max_delay)
    """
    import random
    exponential_delay = RETRY_BASE_DELAY * pow(2, attempt)
    capped_delay = min(exponential_delay, RETRY_MAX_DELAY)
    jitter = capped_delay * RETRY_JITTER * random.random()
    return capped_delay + jitter

def get_cron_state(job_id: str = None) -> Optional[Dict]:
    """Get cron state from openclaw."""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if job_id:
                for job in data.get("jobs", []):
                    if job.get("id") == job_id:
                        return job
            return data
    except Exception as e:
        log(f"Failed to get cron state: {e}", "ERROR")
    return None

def get_last_run_status(job_id: str) -> Optional[Dict]:
    """Get last run status for a cron job."""
    state = get_cron_state(job_id)
    if state:
        return state.get("state", {})
    return None

def check_gateway_restart_loop(state: Dict) -> bool:
    """Circuit breaker: Check if we're in a gateway restart loop.

    If we've restarted gateway more than MAX_GATEWAY_RESTARTS_PER_HOUR in the
    last hour, we have a cascade failure and should NOT restart again.
    """
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)

    # Clean old entries
    state["gateway_restarts"] = [
        t for t in state.get("gateway_restarts", [])
        if datetime.fromisoformat(t) > one_hour_ago
    ]

    restart_count = len(state["gateway_restarts"])

    if restart_count >= MAX_GATEWAY_RESTARTS_PER_HOUR:
        log(f"CIRCUIT BREAKER: {restart_count} gateway restarts in last hour - STOP!", "WARN")
        return True  # Circuit is open - don't restart

    return False  # Circuit is closed - safe to restart

def record_gateway_restart(state: Dict):
    """Record a gateway restart for circuit breaker."""
    state.setdefault("gateway_restarts", []).append(datetime.now().isoformat())
    save_state(state)

def check_false_positive(job_id: str, error: str) -> bool:
    """Check if this is a false positive - don't heal."""
    # Message failed but actually delivered = false positive
    if "Message failed" in error or "✉" in error:
        status = get_last_run_status(job_id)
        if status and status.get("lastDelivered"):
            log(f"FALSE POSITIVE: {job_id} actually delivered", "INFO")
            return True
    return False

def categorize_error(error: str) -> str:
    """Categorize error based on patterns."""
    for category, patterns in ERROR_CATEGORIES.items():
        for pattern in patterns:
            if pattern.lower() in error.lower():
                return category
    return "unknown"

def determine_healing_action(job_id: str, job_name: str, error: str, consecutive_errors: int = 0, dry_run: bool = False) -> bool:
    """Determine and execute healing action for an error.

    4-Stage Loop:
    1. DETECT - We already know there's an error
    2. DIAGNOSE - Categorize the error
    3. HEAL - Execute the healing action
    4. VERIFY - Check if healing worked (done in next cycle)
    """

    # Load state for circuit breaker
    state = load_state()

    # STAGE 1: DETECT (already done - we have an error)
    log(f"", "INFO")
    log(f"=== DETECT ===", "INFO")
    log(f"Job: {job_name}", "INFO")
    log(f"Error: {error[:100]}...", "INFO")
    log(f"Consecutive: {consecutive_errors}", "INFO")

    # STAGE 2: DIAGNOSE
    log(f"", "INFO")
    log(f"=== DIAGNOSE ===", "INFO")
    category = categorize_error(error)
    log(f"Category: {category}", "INFO")

    # CRITICAL CHECK: If message was delivered, this is a false positive - don't heal!
    # Even if error text contains patterns like "Telegram recipient" or "Message failed",
    # if lastDelivered is True, the message got through and we should ignore the error.
    status = get_last_run_status(job_id)
    if status and status.get("lastDelivered"):
        log(f"FALSE POSITIVE: Job {job_name} has lastDelivered=True - message actually delivered", "INFO")
        log(f"Error text '{error[:50]}...' is misleading - skipping healing", "INFO")
        return True

    # Check false positive patterns (text-based)
    if check_false_positive(job_id, error):
        log(f"Action: FALSE POSITIVE - no healing needed", "INFO")
        return True

    # Find matching error pattern
    action_taken = False
    for pattern, rule in HEALING_RULES.items():
        if pattern in error:
            log(f"MATCH: '{pattern}' -> {rule.get('action')}", "INFO")
            log(f"Category: {rule.get('category', 'unknown')}", "INFO")

            action = rule['action']

            # ===== CIRCUIT BREAKER for Gateway =====
            if action == "circuit_breaker_gateway":
                if check_gateway_restart_loop(state):
                    log(f"Action: CIRCUIT BREAKER OPEN - skip gateway restart", "WARN")
                    log(f"Reason: Too many restarts in last hour (cascade failure)", "WARN")
                    log(f"Action: ALERT_MASTER instead", "WARN")
                    action = "alert_master"  # Fall through to alert
                else:
                    log(f"Action: RESTART_GATEWAY (circuit breaker allows)", "INFO")
                    record_gateway_restart(state)
                    if not dry_run:
                        try:
                            subprocess.Popen(
                                ["openclaw", "gateway", "restart"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            log(f"Gateway restart initiated", "INFO")
                        except Exception as e:
                            log(f"Gateway restart failed: {e}", "ERROR")
                    action_taken = True
                    # VERIFY will happen in next cycle
                    continue

            # ===== RESTART GATEWAY =====
            elif action == "restart_gateway":
                if check_gateway_restart_loop(state):
                    log(f"CIRCUIT BREAKER: Skipping restart, alerting master", "WARN")
                    action = "alert_master"
                else:
                    log(f"Action: RESTART_GATEWAY", "INFO")
                    record_gateway_restart(state)
                    if not dry_run:
                        try:
                            subprocess.Popen(
                                ["openclaw", "gateway", "restart"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            log(f"Gateway restart initiated", "INFO")
                        except Exception as e:
                            log(f"Gateway restart failed: {e}", "ERROR")
                    action_taken = True
                    continue

            # ===== RETRY WITH BACKOFF (EXPONENTIAL BACKOFF) =====
            elif action == "retry_with_backoff":
                retry_count_key = f"retry_count_{job_id}"
                retry_count = state.get(retry_count_key, 0)
                
                if retry_count >= 3:
                    log(f"RETRY: Max retries ({retry_count}) exceeded - escalating to gateway restart", "WARN")
                    state[retry_count_key] = 0  # Reset
                    save_state(state)
                    # Escalate to gateway restart
                    if not check_gateway_restart_loop(state):
                        log(f"Action: ESCALATE -> RESTART_GATEWAY", "INFO")
                        record_gateway_restart(state)
                        if not dry_run:
                            try:
                                subprocess.Popen(
                                    ["openclaw", "gateway", "restart"],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL
                                )
                                log(f"Gateway restart initiated after retry exhaustion", "INFO")
                            except Exception as e:
                                log(f"Gateway restart failed: {e}", "ERROR")
                    else:
                        log(f"CIRCUIT BREAKER: Can't restart, alerting master", "WARN")
                        action = "alert_master"
                else:
                    delay = calculate_backoff_delay(retry_count)
                    log(f"Action: RETRY_WITH_BACKOFF (attempt {retry_count + 1}/3, wait {delay:.1f}s)", "INFO")
                    
                    if not dry_run:
                        # Wait with exponential backoff
                        time.sleep(delay)
                        
                        # Trigger immediate retry of the cron job
                        try:
                            subprocess.run(
                                ["openclaw", "cron", "run", job_id],
                                capture_output=True, timeout=60
                            )
                            log(f"Cron job re-triggered: {job_name}", "INFO")
                            state[retry_count_key] = retry_count + 1
                            save_state(state)
                        except Exception as e:
                            log(f"Retry trigger failed: {e}", "ERROR")
                            state[retry_count_key] = retry_count + 1
                            save_state(state)
                    action_taken = True
                    continue  # VERIFY will happen in next cycle

            # ===== DISABLE CHANNEL =====
            elif action == "disable_channel":
                channel = rule.get("channel", "discord")
                log(f"Action: DISABLE_CHANNEL ({channel})", "INFO")
                if not dry_run:
                    try:
                        subprocess.run([
                            "openclaw", "cron", "edit",
                            job_id, "--delivery", "none"
                        ], check=True, capture_output=True)
                        log(f"Channel {channel} disabled for {job_name}", "INFO")
                    except Exception as e:
                        log(f"Failed to disable channel: {e}", "ERROR")
                action_taken = True

            # ===== CHECK DELIVERY (VERIFY PHASE!) =====
            elif action == "check_delivery":
                log(f"Action: CHECK_DELIVERY (Verify phase)", "INFO")
                status = get_last_run_status(job_id)
                if status and status.get("delivered"):
                    log(f"VERIFIED: {job_name} actually delivered - false positive", "INFO")
                    action_taken = True
                elif status and status.get("lastDelivered"):
                    log(f"VERIFIED: {job_name} delivered={status.get('lastDelivered')}", "INFO")
                    action_taken = True
                else:
                    log(f"UNVERIFIED: {job_name} may need manual check", "WARN")
                    # Don't mark as healed - needs verification
                # Don't continue - we're done

            # ===== INCREASE TIMEOUT OR DISABLE =====
            elif action == "increase_timeout_or_disable":
                timeout_inc = rule.get('timeout_increase', 300)
                max_cons = rule.get('max_consecutive', 3)

                if consecutive_errors >= max_cons:
                    log(f"Action: DISABLE_CRON (max consecutive errors)", "WARN")
                    if not dry_run:
                        try:
                            subprocess.run(["openclaw", "cron", "disable", job_id], check=True)
                            log(f"Cron disabled after {consecutive_errors} errors", "INFO")
                        except Exception as e:
                            log(f"Failed to disable cron: {e}", "ERROR")
                    action_taken = True
                else:
                    log(f"Action: TIMEOUT_INCREASE (will disable after {max_cons} errors)", "INFO")
                    action_taken = True  # Will retry next cycle
                # Note: Timeout increase requires manual edit for now

            # ===== DISABLE CRON =====
            elif action == "disable_cron":
                log(f"Action: DISABLE_CRON", "WARN")
                if not dry_run:
                    # Auto-backup config before changes
                    try:
                        sys.path.insert(0, str(Path(__file__).parent))
                        from config_backup_manager import auto_backup
                        auto_backup(f"before_disable_cron_{job_name}")
                    except Exception as e:
                        log(f"Config backup failed: {e}", "WARN")
                    
                    # Disable the cron
                    try:
                        subprocess.run(["openclaw", "cron", "disable", job_id], check=True)
                        log(f"Cron disabled: {job_name}", "INFO")
                    except Exception as e:
                        log(f"Failed to disable cron: {e}", "ERROR")
                    
                    # Create GitHub issue for persistent failures
                    if consecutive >= 3:
                        try:
                            from github_issue_creator import create_cron_failure_issue
                            issue_url = create_cron_failure_issue(
                                job_name, job_id, error, consecutive
                            )
                            if issue_url:
                                log(f"GitHub issue created: {issue_url}", "INFO")
                        except Exception as e:
                            log(f"GitHub issue creation failed: {e}", "WARN")
                action_taken = True

            # ===== WAIT AND RETRY =====
            elif action == "wait_and_retry":
                log(f"Action: WAIT_AND_RETRY (will retry next cycle)", "INFO")
                action_taken = True

            # ===== ALERT MASTER =====
            elif action == "alert_master":
                log(f"Action: ALERT_MASTER - needs human attention", "WARN")
                # This would trigger Telegram notification
                action_taken = False  # Needs manual intervention

            # ===== MODEL FAILOVER =====
            elif action == "model_failover":
                log(f"Action: MODEL_FAILOVER - trying to switch to healthy model", "INFO")
                if not dry_run:
                    try:
                        # Import session pin manager
                        sys.path.insert(0, str(Path(__file__).parent))
                        from session_pin_manager import failover_all_from_model, get_available_models, DEFAULT_MODEL_CHAIN
                        
                        # Get current model from error context
                        # For now, try to failover all sessions from failed models
                        available = get_available_models(DEFAULT_MODEL_CHAIN)
                        if available:
                            healthy_model = available[0]
                            log(f"Found healthy model: {healthy_model}", "INFO")
                            # Note: Full session failover requires session ID tracking
                            # For now, just log the suggestion
                            log(f"Suggestion: Pin sessions to {healthy_model}", "INFO")
                        else:
                            log(f"No healthy models available - would disable cron", "WARN")
                            # Fallback to disable
                            subprocess.run(["openclaw", "cron", "disable", job_id], check=True)
                            log(f"Cron disabled: {job_name}", "INFO")
                    except Exception as e:
                        log(f"Model failover failed: {e}", "ERROR")
                        action_taken = False
                action_taken = True

            break  # Only handle first matching pattern

    # STAGE 4: VERIFY
    log(f"", "INFO")
    log(f"=== VERIFY (next cycle) ===", "INFO")
    log(f"Next run will check if healing worked", "INFO")

    if not action_taken and not check_false_positive(job_id, error):
        log(f"NO HEALING RULE for: {error[:80]}", "WARN")
        log(f"Category: {category} - needs rule update", "WARN")

    return action_taken

def check_model_health_and_record():
    """Check model health and record failures."""
    try:
        # Import model health checker functions
        sys.path.insert(0, str(Path(__file__).parent))
        from model_health_checker import probe_model, get_configured_models, load_state as load_health_state
        from model_cooldown_manager import record_failure, is_in_cooldown, get_available_models
        
        # Get configured models
        models = get_configured_models()
        
        # Probe each model
        for model_id in models:
            result = probe_model(model_id)
            
            if result.get("status") == "error":
                error_msg = result.get("error", "unknown")
                # Determine reason
                if "429" in error_msg or "rate" in error_msg.lower():
                    reason = "rate_limit"
                elif "401" in error_msg or "403" in error_msg:
                    reason = "auth_error"
                elif "timeout" in error_msg.lower():
                    reason = "timeout"
                else:
                    reason = "unknown"
                
                record_failure(model_id, reason)
                log(f"Model {model_id} failed: {error_msg} -> recorded as {reason}", "WARN")
        
        # Check for available models
        available = get_available_models(models)
        if len(available) < len(models):
            unavailable = set(models) - set(available)
            log(f"Models in cooldown: {unavailable}", "WARN")
        
    except Exception as e:
        log(f"Model health check failed: {e}", "WARN")


def heal_all_errors(dry_run: bool = False) -> Dict[str, int]:
    """Heale alle Crons mit Errors - full 4-Stage loop."""
    stats = {
        'checked': 0,
        'healed': 0,
        'false_positives': 0,
        'failed': 0,
        'needs_manual': 0,
        'circuit_breaker': 0
    }

    log(f"", "INFO")
    log(f"=== MODEL HEALTH CHECK ===", "INFO")
    check_model_health_and_record()
    
    log(f"", "INFO")
    log(f"=== FULL 4-STAGE LOOP ===", "INFO")

    # Get all cron jobs
    data = get_cron_state()
    if not data:
        log("Failed to get cron state", "ERROR")
        return stats

    total_jobs = data.get("total", 0)
    stats['total_jobs'] = total_jobs
    log(f"Total cron jobs: {total_jobs}", "INFO")

    for job in data.get("jobs", []):
        job_id = job.get("id")
        job_name = job.get("name", "unknown")
        state = job.get("state", {})

        # Check if job has errors
        if state.get("lastRunStatus") != "error":
            continue

        stats['checked'] += 1
        error = state.get("lastError", "unknown")
        consecutive = state.get("consecutiveErrors", 0)

        log(f"", "INFO")
        log(f"--- Processing: {job_name} ---", "INFO")

        # Run full 4-stage loop
        healed = determine_healing_action(
            job_id, job_name, error, consecutive, dry_run
        )

        if healed:
            stats['healed'] += 1
        elif check_false_positive(job_id, error):
            stats['false_positives'] += 1
        else:
            stats['needs_manual'] += 1

    return stats

def main():
    global HEAL_LOG

    import argparse
    parser = argparse.ArgumentParser(description='Cron Error Healer v2 - 4-Stage Self-Healing')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t make changes')
    parser.add_argument('--job-id', help='Specific job ID to heal')
    parser.add_argument('--reset-state', action='store_true', help='Reset healer state')
    args = parser.parse_args()

    # Reset state if requested
    if args.reset_state:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        print("Healer state reset")
        return

    print("=" * 60)
    print("🦞 CRON ERROR HEALER v2 - 4-Stage Self-Healing")
    print("=" * 60)
    print()
    print("4-Stage Loop: Detect → Diagnose → Heal → Verify")
    print()

    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made\n")

    # Ensure log directory exists
    HEAL_LOG.parent.mkdir(parents=True, exist_ok=True)

    log("=" * 50, "INFO")
    log("Cron Error Healer v2 started", "INFO")
    log(f"Dry run: {args.dry_run}", "INFO")
    log(f"Circuit breaker: {MAX_GATEWAY_RESTARTS_PER_HOUR} restarts/hour max", "INFO")

    if args.job_id:
        # Single job healing
        job = get_cron_state(args.job_id)
        if job:
            error = job.get('state', {}).get('lastError', 'unknown')
            determine_healing_action(
                args.job_id,
                job.get('name'),
                error,
                job.get('state', {}).get('consecutiveErrors', 0),
                args.dry_run
            )
        else:
            print(f"Job not found: {args.job_id}")
    else:
        # Heal all errors
        stats = heal_all_errors(args.dry_run)

        print()
        print("=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        print(f"Total Jobs:      {stats.get('total_jobs', '?')}")
        print(f"Checked:         {stats['checked']}")
        print(f"Healed:          {stats['healed']}")
        print(f"False Positives: {stats['false_positives']}")
        print(f"Needs Manual:    {stats['needs_manual']}")
        print(f"Circuit Breaker: {stats['circuit_breaker']}")

        log(f"Results: {stats}", "INFO")

        if stats['needs_manual'] > 0:
            print(f"\n⚠️  {stats['needs_manual']} jobs need manual intervention")
            print("Run with --dry-run=false to see details")

    print()
    print(f"Done. Check logs at: {HEAL_LOG}")
    print()
    print("4-Stage Loop complete. Next cycle will VERIFY healing.")


if __name__ == '__main__':
    main()
