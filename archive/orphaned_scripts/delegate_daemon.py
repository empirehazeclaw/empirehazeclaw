#!/usr/bin/env python3
"""
Smart Delegate - Background Service
Läuft permanent und verteilt Tasks an Agenten
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.smart_delegate import SmartDelegate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [DELEGATE] %(message)s")
log = logging.getLogger("openclaw.delegate_daemon")


class DelegateDaemon:
    """Hintergrund-Service für Smart Delegate"""
    
    def __init__(self):
        self.delegate = SmartDelegate()
        self.running = False
        self.task_queue = []
        
    async def start(self):
        """Start den Daemon"""
        log.info("🚀 Delegate Daemon gestartet")
        self.running = True
        
        while self.running:
            try:
                # Check for new tasks
                await self.check_tasks()
                
                # Process queued tasks
                await self.process_queue()
                
                # Periodic optimization
                await self.optimize()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                log.error(f"❌ Daemon Fehler: {e}")
                await asyncio.sleep(60)
    
    async def check_tasks(self):
        """Prüfe auf neue Tasks"""
        
        # Check various sources for tasks
        # 1. Cron-triggered tasks (from logs)
        # 2. API tasks (from queue)
        # 3. Manual tasks
        
        # For now, just log
        log.debug("Prüfe auf Tasks...")
    
    async def process_queue(self):
        """Verarbeite Task-Queue"""
        
        while self.task_queue:
            task = self.task_queue.pop(0)
            log.info(f"📥 Verarbeite: {task}")
            
            result = await self.delegate.process_task(task)
            log.info(f"✅ Erledigt: {result['analysis'].get('primary_agent')}")
    
    async def optimize(self):
        """Periodische Optimierung"""
        
        stats = self.delegate.get_stats()
        
        # Log stats every hour
        if datetime.now().minute == 0:
            log.info(f"📊 Stats: {stats['total_tasks']} Tasks, {stats['successful']} erfolgreich")
    
    def add_task(self, task: str):
        """Task zur Queue hinzufügen"""
        self.task_queue.append(task)
        log.info(f"📝 Task hinzugefügt: {task}")
    
    def stop(self):
        """Stoppe den Daemon"""
        self.running = False
        log.info("🛑 Daemon gestoppt")


async def main():
    """Main entry point"""
    daemon = DelegateDaemon()
    await daemon.start()


if __name__ == "__main__":
    asyncio.run(main())
