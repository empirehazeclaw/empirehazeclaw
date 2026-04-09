#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          EXTERNAL TRIGGER SYSTEM                        ║
║          Reagiert auf Webhooks, API Events, CRM          ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Webhook Receiver (HTTP)
  - Event Listeners (GitHub, Etsy, Shopify, etc.)
  - Trigger Rules
  - Auto-Action Execution
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TRIGGER] %(message)s")
log = logging.getLogger("openclaw.triggers")

sys.path.insert(0, str(Path(__file__).parent.parent))


class TriggerType(str, Enum):
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    EVENT = "event"
    MANUAL = "manual"


class TriggerEvent(str, Enum):
    # GitHub
    PUSH = "push"
    PR = "pull_request"
    ISSUE = "issues"
    
    # E-Commerce
    ORDER_CREATED = "order_created"
    ORDER_PAID = "order_paid"
    CUSTOMER_NEW = "customer_new"
    
    # General
    FORM_SUBMIT = "form_submit"
    NEWSLETTER_SIGNUP = "newsletter_signup"
    PAYMENT_SUCCESS = "payment_success"
    
    # Internal
    TASK_COMPLETED = "task_completed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Trigger:
    """Ein Trigger"""
    id: str
    type: TriggerType
    event: TriggerEvent
    action: str  # Task to execute
    conditions: Dict  # When to trigger
    enabled: bool = True


class ExternalTriggerSystem:
    """
    External Trigger System - Reagiert auf die Aussenwelt!
    
    Hört auf:
    - Webhooks (HTTP)
    - GitHub Events
    - E-Commerce Events (Etsy, Shopify)
    - Form Submissions
    - Scheduled Events
    """
    
    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}
        self.listeners: Dict[str, Callable] = {}
        self.event_history: List[Dict] = []
        
        # Load default triggers
        self._load_default_triggers()
        
        log.info("🎯 External Trigger System initialisiert")
    
    def _load_default_triggers(self):
        """Lade Standard-Trigger"""
        
        defaults = [
            # Webhook triggers
            Trigger(
                id="webhook_contact",
                type=TriggerType.WEBHOOK,
                event=TriggerEvent.FORM_SUBMIT,
                action="process_contact_form",
                conditions={"form": "contact"}
            ),
            Trigger(
                id="webhook_newsletter",
                type=TriggerType.WEBHOOK,
                event=TriggerEvent.NEWSLETTER_SIGNUP,
                action="send_welcome_email",
                conditions={"source": "website"}
            ),
            
            # E-Commerce triggers
            Trigger(
                id="order_created",
                type=TriggerType.EVENT,
                event=TriggerEvent.ORDER_CREATED,
                action="process_order",
                conditions={}
            ),
            Trigger(
                id="order_paid",
                type=TriggerType.EVENT,
                event=TriggerEvent.ORDER_PAID,
                action="send_order_confirmation",
                conditions={}
            ),
            
            # GitHub triggers
            Trigger(
                id="github_push",
                type=TriggerType.EVENT,
                event=TriggerEvent.PUSH,
                action="deploy_website",
                conditions={"branch": "main"}
            ),
        ]
        
        for t in defaults:
            self.triggers[t.id] = t
    
    def add_trigger(
        self,
        trigger_id: str,
        event: TriggerEvent,
        action: str,
        conditions: Dict = None,
        trigger_type: TriggerType = TriggerType.WEBHOOK
    ) -> str:
        """Füge einen neuen Trigger hinzu"""
        
        trigger = Trigger(
            id=trigger_id,
            type=trigger_type,
            event=event,
            action=action,
            conditions=conditions or {}
        )
        
        self.triggers[trigger_id] = trigger
        
        log.info(f"➕ Trigger hinzugefügt: {trigger_id} → {action}")
        
        return trigger_id
    
    def remove_trigger(self, trigger_id: str) -> bool:
        """Entferne einen Trigger"""
        
        if trigger_id in self.triggers:
            del self.triggers[trigger_id]
            log.info(f"➖ Trigger entfernt: {trigger_id}")
            return True
        
        return False
    
    def enable_trigger(self, trigger_id: str) -> bool:
        """Aktiviere einen Trigger"""
        
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = True
            log.info(f"✅ Trigger aktiviert: {trigger_id}")
            return True
        
        return False
    
    def disable_trigger(self, trigger_id: str) -> bool:
        """Deaktiviere einen Trigger"""
        
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = False
            log.info(f"⏸ Trigger deaktiviert: {trigger_id}")
            return True
        
        return False
    
    async def handle_webhook(self, event: TriggerEvent, data: Dict) -> Dict:
        """
        Verarbeite einen Webhook!
        
        Args:
            event: Der Event-Typ
            data: Payload Data
            
        Returns:
            Dict mit Ergebnissen
        """
        
        log.info(f"📥 Webhook erhalten: {event.value}")
        
        # Find matching triggers
        matching = self._find_matching_triggers(event, data)
        
        if not matching:
            log.info("   Keine passenden Trigger gefunden")
            return {"status": "no_trigger", "matched": 0}
        
        # Execute actions
        results = []
        
        for trigger in matching:
            if not trigger.enabled:
                continue
            
            log.info(f"   ▶ Trigger: {trigger.id} → {trigger.action}")
            
            result = await self._execute_action(trigger.action, data)
            
            results.append({
                "trigger_id": trigger.id,
                "action": trigger.action,
                "success": result.get("success", False)
            })
            
            # Log to history
            self.event_history.append({
                "timestamp": datetime.now().isoformat(),
                "event": event.value,
                "trigger_id": trigger.id,
                "action": trigger.action,
                "data": data
            })
        
        return {
            "status": "processed",
            "matched": len(results),
            "results": results
        }
    
    def _find_matching_triggers(self, event: TriggerEvent, data: Dict) -> List[Trigger]:
        """Finde passende Trigger für einen Event"""
        
        matching = []
        
        for trigger in self.triggers.values():
            if not trigger.enabled:
                continue
            
            if trigger.event != event:
                continue
            
            # Check conditions
            matches = True
            
            for key, expected in trigger.conditions.items():
                actual = data.get(key)
                
                if actual != expected:
                    matches = False
                    break
            
            if matches:
                matching.append(trigger)
        
        return matching
    
    async def _execute_action(self, action: str, data: Dict) -> Dict:
        """Führe die Aktion aus"""
        
        # Map actions to actual handlers
        handlers = {
            "process_contact_form": self._handle_contact_form,
            "send_welcome_email": self._handle_newsletter_signup,
            "process_order": self._handle_order,
            "send_order_confirmation": self._handle_order_paid,
            "deploy_website": self._handle_github_push
        }
        
        handler = handlers.get(action)
        
        if handler:
            try:
                return await handler(data)
            except Exception as e:
                log.error(f"   ❌ Action fehlgeschlagen: {e}")
                return {"success": False, "error": str(e)}
        
        log.warning(f"   ⚠️ Kein Handler für Action: {action}")
        return {"success": False, "error": "no_handler"}
    
    async def _handle_contact_form(self, data: Dict) -> Dict:
        """Kontaktformular verarbeiten"""
        
        log.info("   📧 Kontaktformular erhalten")
        
        # In real: send notification
        return {"success": True, "action": "contact_processed"}
    
    async def _handle_newsletter_signup(self, data: Dict) -> Dict:
        """Newsletter Anmeldung"""
        
        log.info("   📧 Willkommens-Email gesendet")
        
        return {"success": True, "action": "welcome_email_sent"}
    
    async def _handle_order(self, data: Dict) -> Dict:
        """Bestellung verarbeiten"""
        
        order_id = data.get("order_id", "unknown")
        log.info(f"   📦 Bestellung verarbeitet: {order_id}")
        
        return {"success": True, "action": "order_processed"}
    
    async def _handle_order_paid(self, data: Dict) -> Dict:
        """Bestellung bezahlt"""
        
        order_id = data.get("order_id", "unknown")
        log.info(f"   ✅ Bestellung bezahlt: {order_id}")
        
        return {"success": True, "action": "confirmation_sent"}
    
    async def _handle_github_push(self, data: Dict) -> Dict:
        """GitHub Push - Deploy"""
        
        branch = data.get("ref", "").split("/")[-1]
        log.info(f"   🚀 Deploy auf {branch}")
        
        return {"success": True, "action": "deployed"}
    
    def get_triggers(self) -> List[Dict]:
        """Gib alle Trigger"""
        
        return [
            {
                "id": t.id,
                "type": t.type.value,
                "event": t.event.value,
                "action": t.action,
                "enabled": t.enabled
            }
            for t in self.triggers.values()
        ]
    
    def get_stats(self) -> Dict:
        """Gib Statistiken"""
        
        return {
            "total_triggers": len(self.triggers),
            "enabled": sum(1 for t in self.triggers.values() if t.enabled),
            "disabled": sum(1 for t in self.triggers.values() if not t.enabled),
            "events_processed": len(self.event_history)
        }


# Global instance
_trigger_system = None


def get_trigger_system() -> ExternalTriggerSystem:
    """Hol das globale Trigger System"""
    global _trigger_system
    if _trigger_system is None:
        _trigger_system = ExternalTriggerSystem()
    return _trigger_system


if __name__ == "__main__":
    async def test():
        t = ExternalTriggerSystem()
        
        print("=== AVAILABLE TRIGGERS ===")
        for tr in t.get_triggers():
            print(f"  {tr['id']}: {tr['event']} → {tr['action']} ({'✅' if tr['enabled'] else '⏸'})")
        
        print("\n=== TEST WEBHOOK ===")
        
        # Test contact form
        result = await t.handle_webhook(
            TriggerEvent.FORM_SUBMIT,
            {"form": "contact", "name": "Max", "email": "max@test.de"}
        )
        
        print(f"Result: {result}")
        
        print("\n=== STATS ===")
        print(t.get_stats())
    
    asyncio.run(test())
