#!/usr/bin/env python3
"""
Autonomy Supervisor — Sir HazeClaw Autonomy Engine
VIGIL-inspired sibling agent that watches and proposes fixes
Runs on cron every 5 minutes
"""

import os
import re
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
AUTONOMY_DIR = WORKSPACE / "memory" / "autonomy"
ACTION_LOG = AUTONOMY_DIR / "action_log.md"
ERROR_LOG = AUTONOMY_DIR / "error_log.md"
AFFECTIVE_STATE = AUTONOMY_DIR / "affective_state.json"
PROPOSALS_DIR = AUTONOMY_DIR / "proposals"

# Transaction ID pattern
TX_PATTERN = re.compile(r'AUTONOMY-(\d{8})-(\d{4})-(\w+)-(\d+)')

class AutonomySupervisor:
    """
    VIGIL-inspired supervisor agent.
    Watches the primary agent from outside.
    NEVER touches live system - only proposes fixes.
    """
    
    def __init__(self):
        self.proposals_dir = PROPOSALS_DIR
        self.proposals_dir.mkdir(exist_ok=True)
        self.last_check = self._load_last_check_time()
    
    def _load_last_check_time(self) -> datetime:
        """Load last check timestamp"""
        state_file = AUTONOMY_DIR / "supervisor_state.json"
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text())
                ts = state.get("last_check")
                if ts:
                    return datetime.fromisoformat(ts)
            except:
                pass
        return datetime.now(timezone.utc) - timedelta(minutes=5)
    
    def _save_last_check_time(self):
        """Save last check timestamp"""
        state_file = AUTONOMY_DIR / "supervisor_state.json"
        state = {"last_check": datetime.now(timezone.utc).isoformat()}
        state_file.write_text(json.dumps(state))
    
    def analyze_actions(self) -> Dict:
        """
        Analyze recent actions for patterns.
        Returns analysis with recommendations.
        """
        if not ACTION_LOG.exists():
            return {"status": "no_actions_yet", "recommendations": []}
        
        content = ACTION_LOG.read_text()
        transactions = self._extract_transactions(content)
        
        if not transactions:
            return {"status": "no_transactions", "recommendations": []}
        
        # Analyze by category
        by_category = {}
        for tx in transactions:
            cat = tx["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tx)
        
        # Calculate stats
        stats = {
            "total": len(transactions),
            "by_category": {cat: len(txs) for cat, txs in by_category.items()},
            "success_rate": self._calc_success_rate(transactions),
            "avg_duration": self._calc_avg_duration(transactions),
            "recent_failures": self._find_recent_failures(transactions)
        }
        
        # Generate recommendations
        recommendations = []
        
        # Check for patterns
        if stats["recent_failures"]:
            recommendations.append({
                "type": "INVESTIGATE_FAILURES",
                "priority": "HIGH",
                "details": f"Found {len(stats['recent_failures'])} recent failures"
            })
        
        if stats["success_rate"] < 0.8:
            recommendations.append({
                "type": "SUCCESS_RATE_LOW",
                "priority": "MEDIUM",
                "details": f"Success rate {stats['success_rate']:.1%} below target"
            })
        
        # Check for repetitive SMALL actions that could be automated
        small_actions = by_category.get("SMALL", [])
        if len(small_actions) > 10:
            recommendations.append({
                "type": "AUTOMATE_REPETITIVE",
                "priority": "LOW",
                "details": f"{len(small_actions)} SMALL actions - consider automating"
            })
        
        return {
            "status": "analyzed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stats": stats,
            "recommendations": recommendations
        }
    
    def analyze_errors(self) -> Dict:
        """
        Analyze error patterns.
        Returns errors with proposed fixes.
        """
        if not ERROR_LOG.exists():
            return {"status": "no_errors", "proposals": []}
        
        content = ERROR_LOG.read_text()
        errors = self._extract_errors(content)
        
        if not errors:
            return {"status": "no_errors", "proposals": []}
        
        proposals = []
        
        # Group by error type
        by_type = {}
        for err in errors:
            err_type = err["type"]
            if err_type not in by_type:
                by_type[err_type] = []
            by_type[err_type].append(err)
        
        # Generate proposals for errors (any count, priority scales with frequency)
        for err_type, type_errors in by_type.items():
            priority = "HIGH" if len(type_errors) >= 5 else "MEDIUM" if len(type_errors) >= 3 else "LOW"
            proposals.append({
                "id": f"PROPOSAL-{datetime.utcnow().strftime('%Y%m%d%H%M')}-{err_type}",
                "type": "FIX_REPETITIVE_ERROR",
                "error_type": err_type,
                "count": len(type_errors),
                "priority": priority,
                "proposed_fix": self._propose_fix(err_type, type_errors),
                "artifacts": self._generate_artifacts(err_type, type_errors)
            })
        
        return {
            "status": "analyzed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_errors": len(errors),
            "proposals": proposals
        }
    
    def analyze_affective_state(self) -> Dict:
        """
        Analyze affective state for soft failures.
        Deterministic rules - NOT LLM.
        """
        if not AFFECTIVE_STATE.exists():
            return {"status": "no_state", "alerts": []}
        
        state = json.loads(AFFECTIVE_STATE.read_text())
        rules = state.get("rules", {})
        affective = state.get("affectiveScores", {})
        
        alerts = []
        
        # Check deterministic rules
        metrics = state.get("metrics", {})
        
        # Error rate check
        error_rate = metrics.get("errorRate", {}).get("current", 0)
        if error_rate > 0.10:
            alerts.append({
                "type": "ERROR_RATE_CRITICAL",
                "severity": "CRITICAL",
                "value": error_rate,
                "threshold": 0.10,
                "action": "ALERT"
            })
        elif error_rate > 0.05:
            alerts.append({
                "type": "ERROR_RATE_WARNING",
                "severity": "WARNING",
                "value": error_rate,
                "threshold": 0.05,
                "action": "WARN"
            })
        
        # Gateway response check
        gateway_ms = metrics.get("gatewayResponseMs", {}).get("current", 0)
        if gateway_ms > 1000:
            alerts.append({
                "type": "GATEWAY_SLOW",
                "severity": "CRITICAL",
                "value": gateway_ms,
                "threshold": 1000,
                "action": "ALERT"
            })
        elif gateway_ms > 500:
            alerts.append({
                "type": "GATEWAY_DEGRADED",
                "severity": "WARNING",
                "value": gateway_ms,
                "threshold": 500,
                "action": "WARN"
            })
        
        # Lost tasks check
        lost_tasks = metrics.get("lostTasks", {}).get("current", 0)
        threshold = metrics.get("lostTasks", {}).get("threshold", 70)
        if lost_tasks > threshold:
            alerts.append({
                "type": "LOST_TASKS_ESCALATING",
                "severity": "CRITICAL",
                "value": lost_tasks,
                "threshold": threshold,
                "action": "ALERT"
            })
        
        # Affective scores
        for score_name, score_data in affective.items():
            if score_data.get("value", 0) > 0.7:
                alerts.append({
                    "type": f"AFFECTIVE_{score_name.upper()}",
                    "severity": "WARNING",
                    "value": score_data["value"],
                    "description": score_data.get("description", ""),
                    "action": "INVESTIGATE"
                })
        
        return {
            "status": "analyzed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "alerts": alerts,
            "active_alert_count": len([a for a in alerts if a["severity"] == "CRITICAL"])
        }
    
    def create_proposal(self, proposal_type: str, details: Dict) -> str:
        """
        Create a proposal artifact.
        Proposals are read-only suggestions - supervisor NEVER touches live system.
        """
        proposal_id = f"PROPOSAL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        proposal = {
            "id": proposal_id,
            "type": proposal_type,
            "created": datetime.now(timezone.utc).isoformat(),
            "status": "PENDING",
            "details": details,
            "supervisor": "Sir HazeClaw Supervisor (VIGIL pattern)",
            "note": "This is a READ-ONLY proposal. Supervisor cannot modify live system."
        }
        
        # Write proposal file
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        proposal_file.write_text(json.dumps(proposal, indent=2))
        
        return proposal_id
    
    def _extract_transactions(self, content: str) -> List[Dict]:
        """Extract transaction entries from action log"""
        transactions = []
        
        # Find all ### AUTONOMY-... blocks
        blocks = re.split(r'^### AUTONOMY-', content, flags=re.MULTILINE)[1:]
        
        for block in blocks:
            lines = block.strip().split('\n')
            if not lines:
                continue
            
            # Parse first line for ID
            first_line = lines[0].strip()
            match = TX_PATTERN.search(first_line)
            if not match:
                continue
            
            tx = {
                "id": f"AUTONOMY-{match.group(0)}",
                "date": match.group(1),
                "time": match.group(2),
                "category": match.group(3),
                "seq": int(match.group(4))
            }
            
            # Parse fields
            for line in lines[1:]:
                if '**Timestamp:**' in line:
                    tx["timestamp"] = line.split('**Timestamp:**')[1].strip()
                elif '**Result:**' in line:
                    tx["result"] = line.split('**Result:**')[1].strip()
                elif '**Action:**' in line:
                    tx["action"] = line.split('**Action:**')[1].strip()
            
            transactions.append(tx)
        
        return transactions
    
    def _extract_errors(self, content: str) -> List[Dict]:
        """Extract error entries from error log"""
        errors = []
        
        blocks = re.split(r'^### ERR-', content, flags=re.MULTILINE)[1:]
        
        for block in blocks:
            lines = block.strip().split('\n')
            if not lines:
                continue
            
            err = {"id": f"ERR-{lines[0].strip()}"}
            
            for line in lines[1:]:
                if '**Type:**' in line:
                    err["type"] = line.split('**Type:**')[1].strip()
                elif '**Result:**' in line:
                    err["result"] = line.split('**Result:**')[1].strip()
            
            # Only count if has type AND a real Result (not template/example)
            # Template entries have placeholders like "RESOLVED / ESCALATED / ROLLED_BACK"
            if "type" in err and "result" in err:
                # Filter out template/example text
                if err["result"] not in ["RESOLVED / ESCALATED / ROLLED_BACK", 
                                           "RESOLVED", "ESCALATED", "ROLLED_BACK",
                                           "RESOLVED / ", " / "]:
                    errors.append(err)
        
        return errors
    
    def _calc_success_rate(self, transactions: List[Dict]) -> float:
        """Calculate success rate"""
        if not transactions:
            return 1.0
        
        successful = sum(1 for tx in transactions if tx.get("result") == "SUCCESS")
        return successful / len(transactions)
    
    def _calc_avg_duration(self, transactions: List[Dict]) -> Optional[float]:
        """Calculate average duration (if tracked)"""
        # This would need duration tracking in action log
        return None
    
    def _find_recent_failures(self, transactions: List[Dict]) -> List[Dict]:
        """Find recent failures"""
        return [tx for tx in transactions if tx.get("result") in ["FAILED", "ROLLED_BACK"]]
    
    def _propose_fix(self, error_type: str, errors: List[Dict]) -> str:
        """Propose a fix for error type"""
        fixes = {
            "RUNTIME": "Check syntax and imports. Run py_compile on affected scripts.",
            "TIMEOUT": "Increase timeout value or optimize script performance.",
            "CONFIG": "Review configuration file syntax and values.",
            "PERMISSION": "Check file permissions and ownership.",
            "NETWORK": "Verify network connectivity and DNS resolution.",
            "MEMORY": "Check memory usage and optimize resource consumption."
        }
        return fixes.get(error_type, f"Investigate {error_type} errors")
    
    def _generate_artifacts(self, error_type: str, errors: List[Dict]) -> List[Dict]:
        """Generate fix artifacts (code/config patches)"""
        # Return placeholder - actual implementation would analyze errors and create patches
        return [{
            "type": "analysis",
            "error_type": error_type,
            "count": len(errors),
            "recommendation": "Create diagnostic script for this error type"
        }]
    
    def run_monitoring_cycle(self) -> Dict:
        """
        Run one monitoring cycle.
        This is what gets called by cron.
        """
        self._save_last_check_time()
        
        results = {
            "cycle_timestamp": datetime.now(timezone.utc).isoformat(),
            "actions_analysis": self.analyze_actions(),
            "errors_analysis": self.analyze_errors(),
            "affective_analysis": self.analyze_affective_state(),
            "kg_pattern_analysis": self.analyze_kg_patterns(),
            "proposals_created": []
        }
        
        # Create proposals for high-priority items
        for rec in results["actions_analysis"].get("recommendations", []):
            if rec["priority"] == "HIGH":
                proposal_id = self.create_proposal("ACTION_RECOMMENDATION", rec)
                results["proposals_created"].append(proposal_id)
        
        for prop in results["errors_analysis"].get("proposals", []):
            # Create proposals for MEDIUM and HIGH priority errors
            if prop["priority"] in ["HIGH", "MEDIUM"]:
                proposal_id = self.create_proposal("ERROR_FIX", prop)
                results["proposals_created"].append(proposal_id)
        
        # KG pattern proposals
        for pattern in results["kg_pattern_analysis"].get("patterns", []):
            if pattern["priority"] == "HIGH":
                proposal_id = self.create_proposal("KG_PATTERN", pattern)
                results["proposals_created"].append(proposal_id)
        
        # Alert if critical issues found
        critical_alerts = [a for a in results["affective_analysis"].get("alerts", []) 
                          if a["severity"] == "CRITICAL"]
        
        if critical_alerts:
            results["alert_needed"] = True
            results["alert_type"] = "CRITICAL"
            results["critical_alerts"] = critical_alerts
        else:
            results["alert_needed"] = False
        
        return results
    
    def get_proposals(self, status: str = "PENDING") -> List[Dict]:
        """Get all proposals with given status"""
        proposals = []
        for f in self.proposals_dir.glob("*.json"):
            try:
                p = json.loads(f.read_text())
                if p.get("status") == status:
                    proposals.append(p)
            except:
                pass
        return proposals

    def analyze_kg_patterns(self) -> Dict:
        """
        Analyze Knowledge Graph for patterns.
        Looks for:
        - Issues mentioned across multiple entities
        - Error patterns in entity facts
        - Trending topics (high access_count)
        """
        kg_path = Path("/home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json")
        if not kg_path.exists():
            return {"status": "no_kg", "patterns": []}
        
        try:
            kg = json.loads(kg_path.read_text())
        except:
            return {"status": "kg_unreadable", "patterns": []}
        
        entities_raw = kg.get("entities", [])
        # Support both old dict format and new list format
        if isinstance(entities_raw, dict):
            entities_list = [(name, entity) for name, entity in entities_raw.items()]
        else:
            entities_list = [(e.get("id", "unknown"), e) for e in entities_raw]
        
        patterns = []
        
        # Keywords that indicate issues/problems
        issue_keywords = ["error", "problem", "issue", "bug", "fail", "timeout", "crash", "broken"]
        
        # Find entities with issue-related facts
        entities_with_issues = []
        for name, entity in entities_list:
            for fact in entity.get("facts", []):
                content = fact.get("content", "").lower()
                if any(kw in content for kw in issue_keywords):
                    entities_with_issues.append({
                        "entity": name,
                        "fact": fact.get("content", "")[:100],
                        "access_count": entity.get("access_count", 0)
                    })
                    break  # Only count entity once
        
        if entities_with_issues:
            patterns.append({
                "type": "ISSUES_IN_KG",
                "description": f"{len(entities_with_issues)} entities contain issue-related facts",
                "entities": entities_with_issues[:5],  # Top 5
                "priority": "MEDIUM"
            })
        
        # Find high-access entities (potential hotspots)
        trending = sorted(entities_list, key=lambda x: x[1].get("access_count", 0), reverse=True)[:5]
        if trending:
            patterns.append({
                "type": "TRENDING_ENTITIES",
                "description": "Entities with highest recent access",
                "entities": [{"name": n, "access_count": e.get("access_count", 0)} for n, e in trending],
                "priority": "LOW"
            })
        
        return {
            "status": "analyzed",
            "total_entities": len(entities_list),
            "patterns": patterns
        }

    def validate_action(self, action: Dict, result: Dict) -> Dict:
        """
        Actor-Critic validation of an autonomous action.
        Uses Learning Loop as the critic.
        
        Returns: {"approved": bool, "feedback": str, "retry": bool}
        """
        validation = {
            "approved": True,
            "feedback": "",
            "retry": False,
            "checks": {}
        }
        
        # Check 1: Did the action succeed?
        if result.get("status") == "error":
            validation["approved"] = False
            validation["feedback"] = f"Action failed: {result.get('error', 'unknown')}"
            validation["retry"] = True
            validation["checks"]["success"] = False
        else:
            validation["checks"]["success"] = True
        
        # Check 2: Did it complete within expected time?
        duration_ms = result.get("duration_ms", 0)
        expected_max_ms = result.get("expected_duration_ms", 60000)
        if duration_ms > expected_max_ms:
            validation["feedback"] += f" Warning: Took {duration_ms/1000:.1f}s (expected <{expected_max_ms/1000}s)"
            validation["checks"]["timing"] = "slow"
        else:
            validation["checks"]["timing"] = "ok"
        
        # Check 3: Invoke Learning Loop validation for code/config changes
        action_type = action.get("type", "")
        if action_type in ["script_modification", "config_change", "new_system"]:
            # Run Learning Loop validation
            try:
                import subprocess
                ll_result = subprocess.run(
                    ["python3", "/home/clawbot/.openclaw/workspace/scripts/learning_loop_v3.py", "--validate"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if ll_result.returncode != 0:
                    validation["approved"] = False
                    validation["feedback"] += f" Learning Loop validation failed."
                    validation["retry"] = True
            except Exception as e:
                validation["feedback"] += f" Could not run Learning Loop: {e}"
        
        return validation

    def create_action_log_entry(self, transaction_id: str, category: str, action: str, 
                                 trigger: str, result: str, notes: str = "") -> None:
        """Log an autonomous action to the action log."""
        if not ACTION_LOG.exists():
            ACTION_LOG.write_text("# ACTION LOG — Sir HazeClaw Autonomy Engine\n\n")
        
        entry = f"""
### {transaction_id}
- **Timestamp:** {datetime.now(timezone.utc).isoformat()}
- **Category:** {category}
- **Action:** {action}
- **Trigger:** {trigger}
- **Result:** {result}
- **Notes:** {notes}

"""
        with open(ACTION_LOG, "a") as f:
            f.write(entry)


# CLI interface
if __name__ == "__main__":
    import sys
    
    supervisor = AutonomySupervisor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # Called by cron - run monitoring cycle
        results = supervisor.run_monitoring_cycle()
        
        # Output summary (for logging)
        print(f"Supervisor cycle: {results['cycle_timestamp']}")
        print(f"Actions analyzed: {results['actions_analysis'].get('status')}")
        print(f"Errors analyzed: {results['errors_analysis'].get('status')}")
        print(f"Alerts: {len(results['affective_analysis'].get('alerts', []))}")
        print(f"Proposals created: {len(results['proposals_created'])}")
        
        if results.get("alert_needed"):
            print(f"\n⚠️  ALERT: {len(results.get('critical_alerts', []))} CRITICAL issues")
            for alert in results.get("critical_alerts", []):
                print(f"  - {alert['type']}: {alert.get('value')}")
        
        # Save results
        results_file = AUTONOMY_DIR / "supervisor_latest.json"
        results_file.write_text(json.dumps(results, indent=2))
    else:
        # Interactive or analysis mode
        print("=== Autonomy Supervisor ===")
        print(f"Last check: {supervisor.last_check}")
        print()
        
        results = supervisor.run_monitoring_cycle()
        
        print("Actions Analysis:")
        print(json.dumps(results["actions_analysis"], indent=2))
        print()
        
        print("Errors Analysis:")
        print(json.dumps(results["errors_analysis"], indent=2))
        print()
        
        print("Affective State:")
        print(json.dumps(results["affective_analysis"], indent=2))