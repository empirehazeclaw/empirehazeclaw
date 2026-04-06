#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SMART DELEGATE - SELF-HEALING VERSION         ║
║          Mit eingebautem Self-Healing System            ║
╚══════════════════════════════════════════════════════════════╝

Der Delegate heilt sich selbst bei Fehlern!
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.agents.orchestrator import Orchestrator
from scripts.self_learning_system import get_learning_system
from scripts.self_healing_system import get_healing_system

logging.basicConfig(level=logging.INFO, format="%(asctime)s [DELEGATE] %(message)s")
log = logging.getLogger("openclaw.delegate_healing")


class ResilientDelegate:
    """
    Smart Delegate mit Self-Healing!
    
    - Lernt aus Fehlern
    - Heilt sich automatisch
    - Benachrichtigt bei kritischen Problemen
    """
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.learning = get_learning_system()
        self.healing = get_healing_system()
        
        self.stats = {
            "total_tasks": 0,
            "successful": 0,
            "healed": 0,
            "failed": 0
        }
        
        log.info("🧠 Resilient Delegate mit Self-Healing initialisiert")
    
    async def process_task(self, task: str, auto_execute: bool = True) -> dict:
        """Verarbeite Task mit Healing"""
        
        self.stats["total_tasks"] += 1
        start_time = time.time()
        
        log.info(f"📥 Task: {task}")
        
        # Analyze
        analysis = self.orchestrator.analyze_task(task)
        log.info(f"   → Agent: {analysis.get('primary_agent')}")
        
        # Create Workflow
        workflow = self.orchestrator.create_workflow(task)
        log.info(f"   → Steps: {len(workflow)}")
        
        if not auto_execute:
            return {"analysis": analysis, "workflow": workflow}
        
        # Execute with Healing
        result = await self._execute_with_healing(task, workflow)
        
        # Learn from result
        success = result.get("success", False)
        duration = time.time() - start_time
        
        self.learning.learn_task(task, success)
        
        if success:
            self.stats["successful"] += 1
            if result.get("healed", False):
                self.stats["healed"] += 1
        else:
            self.stats["failed"] += 1
        
        return {
            "task": task,
            "analysis": analysis,
            "workflow": workflow,
            "result": result,
            "success": success,
            "duration": duration
        }
    
    async def _execute_with_healing(self, task: str, workflow: list) -> dict:
        """Führe Workflow aus mit Self-Healing"""
        
        results = []
        
        for step in workflow:
            agent = step.get("agent")
            action = step.get("action")
            
            log.info(f"   ▶ {agent} → {action}")
            
            # Define the work function
            async def do_work():
                # Simulate agent execution
                await asyncio.sleep(0.1)
                
                # Simulate occasional errors for testing
                # In real: call actual agent
                return {"success": True, "result": f"{agent} done"}
            
            # Execute with healing
            try:
                result = await do_work()
                results.append(result)
                
                # Learn success
                self.learning.learn_agent(agent, action, True)
                
            except Exception as e:
                log.warning(f"   ❌ Fehler: {e}")
                
                # Try to heal
                healing_result = await self.healing.heal(
                    error=e,
                    context={"task": task, "agent": agent, "action": action},
                    retry_func=do_work
                )
                
                if healing_result.success:
                    log.info(f"   ✅ Geheilt: {healing_result.solution}")
                    results.append({"success": True, "healed": True})
                    self.stats["healed"] += 1
                else:
                    log.error(f"   ❌ Konnte nicht heilen")
                    results.append({"success": False, "error": str(e)})
                    
                    # Learn failure
                    self.learning.learn_agent(agent, action, False)
                    
                    # Stop if critical
                    if healing_result.notification_sent:
                        log.error("🆘 Kritischer Fehler - Stoppe Workflow")
                        break
        
        # Check overall success
        all_success = all(r.get("success", False) for r in results)
        
        return {
            "success": all_success,
            "healed": any(r.get("healed", False) for r in results),
            "results": results
        }
    
    def get_stats(self) -> dict:
        """Gib Statistiken"""
        
        healing_stats = self.healing.get_stats()
        
        return {
            **self.stats,
            "healing": healing_stats,
            "learning": self.learning.get_stats()
        }


async def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("task", nargs="?", help="Task")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()
    
    delegate = ResilientDelegate()
    
    if args.stats:
        print("\n📊 STATS:")
        import json
        print(json.dumps(delegate.get_stats(), indent=2))
        return
    
    if args.task:
        result = await delegate.process_task(args.task)
        print(f"\n✅ Ergebnis:")
        print(f"   Success: {result['success']}")
        print(f"   Healed: {result.get('result', {}).get('healed', False)}")
    else:
        print("Usage: resilient_delegate.py <task> --stats")


if __name__ == "__main__":
    asyncio.run(main())
