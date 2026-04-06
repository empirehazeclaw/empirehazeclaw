#!/usr/bin/env python3
"""
Proactive Agent - Event-Driven Automation
Monitors for triggers and acts proactively
"""

import json
import os
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
LOG_FILE = "/home/clawbot/.openclaw/logs/proactive_agent.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProactiveAgent")

class ProactiveAgent:
    def __init__(self):
        self.memory_file = "/home/clawbot/.openclaw/workspace/memory/proactive_learning.json"
        self.feedback_file = "/home/clawbot/.openclaw/workspace/memory/proactive_feedback.json"
        self.triggers_file = "/home/clawbot/.openclaw/workspace/memory/proactive_triggers.json"
        self.load_memory()
        self.load_triggers()
        
    def load_memory(self):
        """Load learned patterns and outcomes"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                "successful_actions": [],
                "failed_actions": [],
                "pattern_scores": {},  # action -> success_rate
                "learned_triggers": {},  # trigger -> best_response
                "feedback": []
            }
            
    def save_memory(self):
        """Save learned patterns"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
            
    def load_triggers(self):
        """Load defined triggers"""
        if os.path.exists(self.triggers_file):
            with open(self.triggers_file, 'r') as f:
                self.triggers = json.load(f)
        else:
            # Default triggers
            self.triggers = {
                "triggers": [
                    {
                        "name": "morning_greeting",
                        "condition": "time",
                        "value": "08:00",
                        "action": "send_greeting",
                        "enabled": True
                    },
                    {
                        "name": "low_engagement",
                        "condition": "social",
                        "metric": "engagement_rate",
                        "threshold": 0.02,
                        "action": "suggest_content",
                        "enabled": True
                    },
                    {
                        "name": "error_detected",
                        "condition": "system",
                        "metric": "error_count",
                        "threshold": 5,
                        "action": "run_auto_repair",
                        "enabled": True
                    },
                    {
                        "name": "opportunity_detected",
                        "condition": "market",
                        "metric": "trend_score",
                        "threshold": 0.8,
                        "action": "notify_trending",
                        "enabled": True
                    },
                    {
                        "name": "follower_milestone",
                        "condition": "social",
                        "metric": "follower_count",
                        "milestone": 50,
                        "action": "celebrate_milestone",
                        "enabled": True
                    }
                ]
            }
            self.save_triggers()
            
    def save_triggers(self):
        """Save triggers config"""
        with open(self.triggers_file, 'w') as f:
            json.dump(self.triggers, f, indent=2)
            
    def evaluate_trigger(self, trigger):
        """Evaluate if a trigger condition is met"""
        condition = trigger.get("condition")
        
        if condition == "time":
            current_time = datetime.now().strftime("%H:%M")
            return current_time == trigger.get("value")
            
        elif condition == "system":
            # Check system metrics
            try:
                error_log = "/tmp/openclaw/openclaw-" + datetime.now().strftime('%Y-%m-%d') + ".log"
                if os.path.exists(error_log):
                    with open(error_log, 'r') as f:
                        errors = f.read().count('"logLevelName":"ERROR"')
                    return errors > trigger.get("threshold", 5)
            except:
                pass
            return False
            
        elif condition == "social":
            # Could check Twitter/social metrics
            # For now, return False - would need API integration
            return False
            
        elif condition == "market":
            # Could check market/trend data
            return False
            
        return False
        
    def execute_action(self, action_name):
        """Execute the appropriate action"""
        logger.info(f"Executing action: {action_name}")
        
        if action_name == "send_greeting":
            return {"status": "success", "action": "greeting_sent"}
            
        elif action_name == "suggest_content":
            return {"status": "success", "action": "content_suggested"}
            
        elif action_name == "run_auto_repair":
            os.system("python3 /home/clawbot/.openclaw/workspace/scripts/auto_repair.py > /dev/null 2>&1")
            return {"status": "success", "action": "auto_repair_run"}
            
        elif action_name == "notify_trending":
            return {"status": "success", "action": "notification_sent"}
            
        elif action_name == "celebrate_milestone":
            return {"status": "success", "action": "milestone_celebrated"}
            
        return {"status": "unknown_action"}
        
    def learn(self, trigger_name, action_name, outcome):
        """Learn from action outcomes"""
        entry = {
            "trigger": trigger_name,
            "action": action_name,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        }
        
        if outcome.get("status") == "success":
            self.memory["successful_actions"].append(entry)
            # Update pattern score
            if action_name not in self.memory["pattern_scores"]:
                self.memory["pattern_scores"][action_name] = []
            self.memory["pattern_scores"][action_name].append(1)
        else:
            self.memory["failed_actions"].append(entry)
            if action_name not in self.memory["pattern_scores"]:
                self.memory["pattern_scores"][action_name] = []
            self.memory["pattern_scores"][action_name].append(0)
            
        # Keep only last 100 entries
        for key in ["successful_actions", "failed_actions"]:
            self.memory[key] = self.memory[key][-100:]
            
        # Update learned triggers
        if outcome.get("status") == "success":
            self.memory["learned_triggers"][trigger_name] = action_name
            
        self.save_memory()
        logger.info(f"Learned: {trigger_name} -> {action_name} = {outcome.get('status')}")
        
    def get_best_action(self, trigger_name):
        """Get the best performing action for a trigger"""
        if trigger_name in self.memory["learned_triggers"]:
            return self.memory["learned_triggers"][trigger_name]
        return None
        
    def run(self):
        """Main loop - check triggers and act"""
        logger.info("Proactive Agent checking triggers...")
        
        for trigger in self.triggers.get("triggers", []):
            if not trigger.get("enabled", True):
                continue
                
            if self.evaluate_trigger(trigger):
                trigger_name = trigger.get("name")
                action_name = trigger.get("action")
                
                # Check if we learned a better action
                learned_action = self.get_best_action(trigger_name)
                if learned_action:
                    action_name = learned_action
                    
                logger.info(f"Trigger activated: {trigger_name}")
                outcome = self.execute_action(action_name)
                self.learn(trigger_name, action_name, outcome)
                
        logger.info("Proactive Agent cycle complete")
        
    def add_feedback(self, trigger_name, action_name, helpful):
        """Add human feedback to improve learning"""
        feedback_entry = {
            "trigger": trigger_name,
            "action": action_name,
            "helpful": helpful,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["feedback"].append(feedback_entry)
        
        # Adjust pattern score based on feedback
        if action_name in self.memory["pattern_scores"]:
            scores = self.memory["pattern_scores"][action_name]
            if helpful:
                scores.append(1)
            else:
                scores.append(0)
            self.memory["pattern_scores"][action_name] = scores[-20:]
            
        self.save_memory()
        logger.info(f"Feedback received: {trigger_name} -> {action_name} = {helpful}")
        
    def get_stats(self):
        """Get learning statistics"""
        stats = {}
        for action, scores in self.memory["pattern_scores"].items():
            if scores:
                success_rate = sum(scores) / len(scores)
                stats[action] = {
                    "success_rate": round(success_rate * 100, 1),
                    "total_runs": len(scores)
                }
        return stats

if __name__ == "__main__":
    agent = ProactiveAgent()
    agent.run()
    
    # Print stats
    stats = agent.get_stats()
    print("\n📊 Proactive Agent Stats:")
    for action, data in stats.items():
        print(f"  {action}: {data['success_rate']}% success ({data['total_runs']} runs)")
