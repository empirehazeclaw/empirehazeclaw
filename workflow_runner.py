#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          AUTONOMOUS WORKFLOW RUNNER                       ║
║          Scheduled Execution + Self-Management             ║
╚══════════════════════════════════════════════════════════════╝

Runs workflows on schedule, monitors, and auto-optimizes.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from scripts.autonomous_workflow_manager import (
    AutonomousWorkflowManager,
    init_default_workflows,
    WorkflowStatus
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [RUNNER] %(message)s")
log = logging.getLogger("openclaw.runner")

WORKFLOW_DIR = Path("/home/clawbot/.openclaw/workspace/workflows")
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs/workflows")
LOG_DIR.mkdir(parents=True, exist_ok=True)


class WorkflowRunner:
    """
    Führt Workflows autonom aus - nach Schedule oder Event.
    """
    
    def __init__(self):
        self.manager = None
        self.running = False
        self.schedule_check_interval = 60  # seconds
        
    async def start(self):
        """Start den Workflow Runner"""
        log.info("🚀 Workflow Runner gestartet")
        
        # Initialize workflows
        self.manager = await init_default_workflows()
        
        self.running = True
        
        # Main loop
        while self.running:
            try:
                await self.check_and_run_scheduled()
                await self.check_and_optimize()
                await asyncio.sleep(self.schedule_check_interval)
            except Exception as e:
                log.error(f"❌ Runner Fehler: {e}")
                await asyncio.sleep(60)
    
    async def check_and_run_scheduled(self):
        """Prüfe ob Workflows fällig sind"""
        
        now = datetime.now()
        
        for wf in self.manager.workflows.values():
            if wf.status != WorkflowStatus.ACTIVE:
                continue
            
            # Check if due (simple schedule check)
            if self._is_due(wf):
                log.info(f"🕐 Workflow fällig: {wf.name}")
                await self._run_workflow(wf)
    
    def _is_due(self, workflow) -> bool:
        """Prüfe ob Workflow fällig ist"""
        
        trigger = workflow.trigger
        trigger_type = trigger.get("type", "manual")
        
        if trigger_type == "manual":
            return False
        
        # Check last run
        if not workflow.last_run:
            return True
        
        last = datetime.fromisoformat(workflow.last_run)
        
        # Simple hourly/daily check
        cron = trigger.get("cron", "")
        
        if "0 8" in cron and " * * *" in cron:  # Daily at 8
            return (datetime.now() - last).hours >= 24
        
        if "0 9,14" in cron:  # Twice daily
            return (datetime.now() - last).hours >= 5
        
        if "0 20" in cron:  # Evening
            return (datetime.now() - last).hours >= 12
        
        return False
    
    async def _run_workflow(self, workflow):
        """Führe Workflow aus"""
        
        log.info(f"▶️  Ausführen: {workflow.name}")
        
        try:
            result = await self.manager.execute_workflow(workflow.id)
            
            # Log result
            self._log_result(workflow, result)
            
            # Check if optimization needed
            if workflow.total_runs >= 3 and workflow.failure_count > workflow.success_count:
                log.info(f"🧠 Starte Optimierung für {workflow.name}")
                opt_result = self.manager.optimize_workflow(workflow.id)
                log.info(f"   Optimierung: {opt_result}")
            
            return result
            
        except Exception as e:
            log.error(f"❌ Workflow fehlgeschlagen: {e}")
            return {"error": str(e)}
    
    def _log_result(self, workflow, result):
        """Logge Ergebnis"""
        
        log_file = LOG_DIR / f"{workflow.id}_{datetime.now().strftime('%Y%m%d')}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "workflow": workflow.name,
            "success": result.get("success", False),
            "duration": result.get("duration", 0)
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_data) + "\n")
    
    async def check_and_optimize(self):
        """Prüfe auf Optimierungsmöglichkeiten"""
        
        for wf in self.manager.workflows.values():
            if wf.total_runs >= 5:
                # Auto-optimize every 5 runs
                if wf.failure_count > wf.success_count * 0.5:
                    log.info(f"🧠 Auto-Optimierung: {wf.name}")
                    self.manager.optimize_workflow(wf.id)
    
    async def run_now(self, workflow_id: str):
        """Führe Workflow sofort aus"""
        return await self._run_workflow(
            self.manager.workflows.get(workflow_id)
        )
    
    def stop(self):
        """Stoppe den Runner"""
        self.running = False
        log.info("🛑 Workflow Runner gestoppt")


# CLI
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Workflow Runner")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--workflow", help="Run specific workflow")
    args = parser.parse_args()
    
    runner = WorkflowRunner()
    
    if args.workflow:
        # Run specific workflow
        result = await runner.run_now(args.workflow)
        print(json.dumps(result, indent=2))
    elif args.once:
        # Run once
        runner.manager = await init_default_workflows()
        
        # Run all active workflows
        for wf in runner.manager.workflows.values():
            if wf.status == WorkflowStatus.ACTIVE:
                result = await runner._run_workflow(wf)
                print(f"{wf.name}: {'✅' if result.get('success') else '❌'}")
    else:
        # Run continuously
        await runner.start()


if __name__ == "__main__":
    import sys
    asyncio.run(main())
