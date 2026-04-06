#!/usr/bin/env python3
"""
Webhook Server - Empfängt HTTP Requests und löst Trigger aus
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.external_trigger_system import (
    get_trigger_system, 
    TriggerEvent, 
    ExternalTriggerSystem
)

try:
    from aiohttp import web
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("⚠️ aiohttp nicht installiert. Nur CLI-Modus verfügbar.")
    print("   Installieren mit: pip install aiohttp")


logging.basicConfig(level=logging.INFO, format="%(asctime)s [WEBHOOK] %(message)s")
log = logging.getLogger("openclaw.webhook")


class WebhookServer:
    """
    Webhook Server - Lauscht auf HTTP Requests
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.trigger_system = get_trigger_system()
        self.app = None
        self.runner = None
    
    def setup_routes(self):
        """Richte Routes ein"""
        
        self.app = web.Application()
        
        # Health check
        self.app.router.add_get('/health', self.health)
        
        # Webhook endpoints
        self.app.router.add_post('/webhook/github', self.webhook_github)
        self.app.router.add_post('/webhook/contact', self.webhook_contact)
        self.app.router.add_post('/webhook/newsletter', self.webhook_newsletter)
        self.app.router.add_post('/webhook/order', self.webhook_order)
        self.app.router.add_post('/webhook/generic', self.webhook_generic)
        
        # Management
        self.app.router.add_get('/triggers', self.list_triggers)
        self.app.router.add_post('/triggers/enable/{id}', self.enable_trigger)
        self.app.router.add_post('/triggers/disable/{id}', self.disable_trigger)
    
    async def health(self, request):
        """Health Check"""
        return web.json_response({
            "status": "ok",
            "triggers": self.trigger_system.get_stats()
        })
    
    async def webhook_github(self, request):
        """GitHub Webhook"""
        
        try:
            data = await request.json()
            
            event = request.headers.get('X-GitHub-Event', 'push')
            
            log.info(f"📥 GitHub Event: {event}")
            
            # Map to trigger event
            event_map = {
                "push": TriggerEvent.PUSH,
                "pull_request": TriggerEvent.PR,
                "issues": TriggerEvent.ISSUE
            }
            
            trigger_event = event_map.get(event, TriggerEvent.PUSH)
            
            result = await self.trigger_system.handle_webhook(trigger_event, data)
            
            return web.json_response(result)
            
        except Exception as e:
            log.error(f"❌ GitHub Webhook Fehler: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def webhook_contact(self, request):
        """Contact Form Webhook"""
        
        try:
            data = await request.json()
            
            log.info("📥 Kontaktformular erhalten")
            
            result = await self.trigger_system.handle_webhook(
                TriggerEvent.FORM_SUBMIT,
                {**data, "form": "contact"}
            )
            
            return web.json_response(result)
            
        except Exception as e:
            log.error(f"❌ Contact Webhook Fehler: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def webhook_newsletter(self, request):
        """Newsletter Webhook"""
        
        try:
            data = await request.json()
            
            log.info(f"📥 Newsletter Signup: {data.get('email')}")
            
            result = await self.trigger_system.handle_webhook(
                TriggerEvent.NEWSLETTER_SIGNUP,
                data
            )
            
            return web.json_response(result)
            
        except Exception as e:
            log.error(f"❌ Newsletter Webhook Fehler: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def webhook_order(self, request):
        """Order Webhook"""
        
        try:
            data = await request.json()
            
            event_type = data.get("event", "order_created")
            
            log.info(f"📥 Order Event: {event_type}")
            
            event_map = {
                "order_created": TriggerEvent.ORDER_CREATED,
                "order_paid": TriggerEvent.ORDER_PAID,
                "customer_new": TriggerEvent.CUSTOMER_NEW
            }
            
            trigger_event = event_map.get(event_type, TriggerEvent.ORDER_CREATED)
            
            result = await self.trigger_system.handle_webhook(trigger_event, data)
            
            return web.json_response(result)
            
        except Exception as e:
            log.error(f"❌ Order Webhook Fehler: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def webhook_generic(self, request):
        """Generic Webhook"""
        
        try:
            data = await request.json()
            event = data.get("event", "generic")
            
            log.info(f"📥 Generic Event: {event}")
            
            # Parse as TriggerEvent if valid
            try:
                trigger_event = TriggerEvent(event)
            except ValueError:
                trigger_event = TriggerEvent.FORM_SUBMIT
            
            result = await self.trigger_system.handle_webhook(trigger_event, data)
            
            return web.json_response(result)
            
        except Exception as e:
            log.error(f"❌ Generic Webhook Fehler: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def list_triggers(self, request):
        """Liste alle Trigger"""
        return web.json_response(self.trigger_system.get_triggers())
    
    async def enable_trigger(self, request):
        """Aktiviere Trigger"""
        trigger_id = request.match_info['id']
        
        if self.trigger_system.enable_trigger(trigger_id):
            return web.json_response({"status": "ok", "trigger": trigger_id})
        
        return web.json_response({"error": "not_found"}, status=404)
    
    async def disable_trigger(self, request):
        """Deaktiviere Trigger"""
        trigger_id = request.match_info['id']
        
        if self.trigger_system.disable_trigger(trigger_id):
            return web.json_response({"status": "ok", "trigger": trigger_id})
        
        return web.json_response({"error": "not_found"}, status=404)
    
    async def start(self):
        """Starte den Server"""
        
        if not AIOHTTP_AVAILABLE:
            log.error("❌ aiohttp nicht verfügbar")
            return
        
        self.setup_routes()
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await site.start()
        
        log.info(f"🚀 Webhook Server gestartet auf Port {self.port}")
        log.info(f"   Endpoints:")
        log.info(f"   - /webhook/github")
        log.info(f"   - /webhook/contact")
        log.info(f"   - /webhook/newsletter")
        log.info(f"   - /webhook/order")
        log.info(f"   - /webhook/generic")
    
    async def stop(self):
        """Stoppe den Server"""
        
        if self.runner:
            await self.runner.cleanup()
            log.info("🛑 Webhook Server gestoppt")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Webhook Server")
    parser.add_argument("--port", type=int, default=8080, help="Port")
    parser.add_argument("--test", action="store_true", help="Test-Modus")
    
    args = parser.parse_args()
    
    if args.test:
        # Just test the trigger system
        t = ExternalTriggerSystem()
        print("✅ Trigger System works!")
        print(f"Triggers: {len(t.triggers)}")
        return
    
    if not AIOHTTP_AVAILABLE:
        print("❌ Bitte installiere aiohttp: pip install aiohttp")
        return
    
    server = WebhookServer(port=args.port)
    
    try:
        await server.start()
        
        # Keep running
        while True:
            await asyncio.sleep(3600)
            
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
