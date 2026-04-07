#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SELF-HEALING SYSTEM                            ║
║          Auto-Repair bei Fehlern + Resilience             ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Auto-Retry mit Exponential Backoff
  - Alternative Agenten versuchen
  - Fallback Strategies
  - Error Classification
  - Critical Alert Notifications
"""

import asyncio
import logging
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [HEAL] %(message)s")
log = logging.getLogger("openclaw.healing")

sys.path.insert(0, str(Path(__file__).parent.parent))


class ErrorSeverity(str, Enum):
    LOW = "low"           # Warning, kann ignoriert werden
    MEDIUM = "medium"     # Task fehlgeschlagen, Retry hilft
    HIGH = "high"         # Kritisch, braucht manusia Intervention
    CRITICAL = "critical" # System-Fehler


class ErrorCategory(str, Enum):
    TIMEOUT = "timeout"
    NETWORK = "network"
    AUTH = "auth"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


@dataclass
class HealingResult:
    """Ergebnis einer Heilungs-Aktion"""
    success: bool
    attempts: int
    solution: str
    fallback_used: bool = False
    notification_sent: bool = False


class SelfHealingSystem:
    """
    Selbstheilendes System - wird automatisch besser bei Fehlern!
    
    Strategien:
    1. Retry mit Backoff
    2. Alternative Agenten
    3. Fallback Workflows
    4. Parameter-Anpassung
    5. Human Notification
    """
    
    def __init__(self):
        self.stats = {
            "total_errors": 0,
            "healed": 0,
            "failed_to_heal": 0,
            "by_category": defaultdict(int),
            "by_severity": defaultdict(int)
        }
        
        # Error patterns and solutions
        self.error_patterns = {
            "timeout": {
                "severity": ErrorSeverity.MEDIUM,
                "solutions": ["retry_with_backoff", "use_alternative_agent", "reduce_data"]
            },
            "rate_limit": {
                "severity": ErrorSeverity.MEDIUM,
                "solutions": ["wait_and_retry", "use_alternative_api"]
            },
            "network": {
                "severity": ErrorSeverity.MEDIUM,
                "solutions": ["retry", "use_offline_mode", "skip_step"]
            },
            "auth": {
                "severity": ErrorSeverity.HIGH,
                "solutions": ["refresh_token", "notify_human"]
            },
            "validation": {
                "severity": ErrorSeverity.MEDIUM,
                "solutions": ["fix_parameters", "use_fallback_data"]
            },
            "not_found": {
                "severity": ErrorSeverity.LOW,
                "solutions": ["skip_step", "create_resource"]
            }
        }
        
        log.info("🩺 Self-Healing System initialisiert")
    
    def classify_error(self, error: Exception or str) -> tuple[ErrorCategory, ErrorSeverity]:
        """Klassifiziere einen Fehler"""
        
        error_str = str(error).lower()
        
        # Pattern matching
        if any(w in error_str for w in ["timeout", "timed out", "deadline"]):
            return ErrorCategory.TIMEOUT, self.error_patterns["timeout"]["severity"]
        
        elif any(w in error_str for w in ["rate limit", "too many requests", "429"]):
            return ErrorCategory.RATE_LIMIT, self.error_patterns["rate_limit"]["severity"]
        
        elif any(w in error_str for w in ["network", "connection", "dns", "refused"]):
            return ErrorCategory.NETWORK, self.error_patterns["network"]["severity"]
        
        elif any(w in error_str for w in ["auth", "unauthorized", "401", "token", "forbidden", "403"]):
            return ErrorCategory.AUTH, self.error_patterns["auth"]["severity"]
        
        elif any(w in error_str for w in ["not found", "404", "does not exist"]):
            return ErrorCategory.NOT_FOUND, self.error_patterns["not_found"]["severity"]
        
        elif any(w in error_str for w in ["validation", "invalid", "400", "bad request"]):
            return ErrorCategory.VALIDATION, self.error_patterns["validation"]["severity"]
        
        elif any(w in error_str for w in ["permission", "access denied"]):
            return ErrorCategory.PERMISSION, self.error_patterns["permission"]["severity"]
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    async def heal(
        self,
        error: Exception or str,
        context: Dict,
        retry_func: Callable,
        fallback_func: Optional[Callable] = None
    ) -> HealingResult:
        """
        Versuche einen Fehler zu heilen!
        
        Args:
            error: Der aufgetretene Fehler
            context: Kontext-Informationen
            retry_func: Funktion zum Retry
            fallback_func: Optionaler Fallback
            
        Returns:
            HealingResult
        """
        
        self.stats["total_errors"] += 1
        
        # Classify error
        category, severity = self.classify_error(error)
        
        self.stats["by_category"][category.value] += 1
        self.stats["by_severity"][severity.value] += 1
        
        log.warning(f"🩺 Error erkannt: {category.value} ({severity.value})")
        
        # Get solutions
        solutions = self.error_patterns.get(category.value, {}).get("solutions", ["retry"])
        
        # Try each solution
        attempts = 0
        max_attempts = 3
        
        for solution in solutions:
            if attempts >= max_attempts:
                break
            
            attempts += 1
            
            log.info(f"   Versuche Lösung {attempts}/{max_attempts}: {solution}")
            
            # Execute solution
            success = await self._apply_solution(
                solution, error, context, retry_func
            )
            
            if success:
                self.stats["healed"] += 1
                log.info(f"   ✅ Geheilt mit {solution} nach {attempts} Versuchen!")
                
                return HealingResult(
                    success=True,
                    attempts=attempts,
                    solution=solution
                )
        
        # Try fallback if available
        if fallback_func:
            log.info("   🔄 Versuche Fallback...")
            try:
                result = await fallback_func()
                self.stats["healed"] += 1
                
                return HealingResult(
                    success=True,
                    attempts=attempts,
                    solution="fallback_executed",
                    fallback_used=True
                )
            except Exception as e:
                log.error(f"   ❌ Fallback auch fehlgeschlagen: {e}")
        
        # Critical - notify human
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            await self._notify_human(category, severity, error, context)
            
            return HealingResult(
                success=False,
                attempts=attempts,
                solution="notification_sent",
                notification_sent=True
            )
        
        # Failed to heal
        self.stats["failed_to_heal"] += 1
        
        return HealingResult(
            success=False,
            attempts=attempts,
            solution="failed"
        )
    
    async def _apply_solution(
        self,
        solution: str,
        error: Exception,
        context: Dict,
        retry_func: Callable
    ) -> bool:
        """Wende eine Lösung an"""
        
        if solution == "retry_with_backoff":
            # Exponential backoff
            for i in range(3):
                wait_time = (2 ** i) + 1  # 1, 3, 7 seconds
                log.info(f"      ⏳ Warte {wait_time}s...")
                await asyncio.sleep(wait_time)
                
                try:
                    await retry_func()
                    return True
                except:
                    continue
        
        elif solution == "use_alternative_agent":
            # Try with different agent
            try:
                context["agent"] = context.get("alt_agent", "research")
                await retry_func()
                return True
            except:
                pass
        
        elif solution == "reduce_data":
            # Reduce data size
            if "data" in context and isinstance(context["data"], list):
                context["data"] = context["data"][:len(context["data"]) // 2]
            try:
                await retry_func()
                return True
            except:
                pass
        
        elif solution == "skip_step":
            # Skip this step
            log.info("      ⏭ Step übersprungen")
            return True
        
        elif solution == "wait_and_retry":
            # Wait longer
            await asyncio.sleep(30)
            try:
                await retry_func()
                return True
            except:
                pass
        
        else:
            # Simple retry
            await asyncio.sleep(1)
            try:
                await retry_func()
                return True
            except:
                pass
        
        return False
    
    async def _notify_human(self, category: ErrorCategory, severity: ErrorSeverity, error: Exception, context: Dict):
        """Benachrichtige Mensch bei kritischen Fehlern"""
        
        log.error(f"🆘 KRITISCHER FEHLER - Benachrichtige Mensch!")
        
        # Could send Telegram, Email, etc.
        notification = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity.value,
            "category": category.value,
            "error": str(error)[:200],
            "context": {k: str(v)[:50] for k, v in context.items()}
        }
        
        # Log for now
        log.error(f"   📧 Notification: {notification}")
        
        # Save to file
        Path("/home/clawbot/.openclaw/workspace/logs/critical_errors.log").append_text(
            json.dumps(notification) + "\n"
        )
    
    def get_stats(self) -> Dict:
        """Gib Heilungs-Statistiken"""
        
        heal_rate = 0
        if self.stats["total_errors"] > 0:
            heal_rate = self.stats["healed"] / self.stats["total_errors"]
        
        return {
            **dict(self.stats),
            "heal_rate": heal_rate,
            "success_rate": f"{heal_rate:.1%}"
        }
    
    # Decorator for easy use
    def heal_on_error(self, fallback_return=None):
        """Decorator für Funktionen die geheilt werden sollen"""
        
        def decorator(func):
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    result = await self.heal(
                        error=e,
                        context={"func": func.__name__, "args": str(args)[:100]},
                        retry_func=lambda: func(*args, **kwargs)
                    )
                    
                    if result.success:
                        return result
                    else:
                        return fallback_return
            
            return wrapper
        return decorator


# Global instance
_healing_system = None


def get_healing_system() -> SelfHealingSystem:
    """Hol das globale Healing System"""
    global _healing_system
    if _healing_system is None:
        _healing_system = SelfHealingSystem()
    return _healing_system


if __name__ == "__main__":
    # Test
    import json
    
    async def test_retry():
        """Test function"""
        await asyncio.sleep(0.5)
        return "Success!"
    
    async def test_error():
        """Test that throws error"""
        await asyncio.sleep(0.5)
        raise Exception("Test timeout error")
    
    async def test():
        healing = SelfHealingSystem()
        
        # Test error classification
        category, severity = healing.classify_error("Connection timeout")
        print(f"Classified: {category.value} ({severity.value})")
        
        # Test healing
        result = await healing.heal(
            error="Rate limit exceeded",
            context={"api": "twitter"},
            retry_func=test_retry
        )
        
        print(f"\nHealing Result: {result}")
        print(f"\nStats: {healing.get_stats()}")
    
    asyncio.run(test())
