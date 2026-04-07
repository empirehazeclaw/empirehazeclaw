#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          PREDICTIVE TASK SYSTEM                          ║
║          Antizipiert was als nächstes kommt               ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Time-based Predictions (cron patterns)
  - Pattern-based Predictions
  - Proactive Task Execution
  - Context Awareness
"""

import asyncio
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PREDICT] %(message)s")
log = logging.getLogger("openclaw.predictive")

try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
except Exception:
    pass


class PredictiveTaskSystem:
    """
    Prediktives System - weiß was als nächstes kommt!
    
    Antizipiert:
    - Tägliche Routinen (Morgen/Abend)
    - Wöchentliche Patterns (Content Days)
    - Trend-basierte Tasks
    - Kunden-bezogene Tasks
    """
    
    def __init__(self):
        self.predictions = []
        self.time_patterns = defaultdict(list)
        self.context_history = []
        
        # Load known patterns
        self._load_patterns()
        
        log.info("🔮 Predictive Task System initialisiert")
    
    def _load_patterns(self):
        """Lade bekannte Patterns"""
        
        # Time-based predictions
        self.time_patterns = {
            "morning": [
                {"task": "Morning Research", "time": "08:00", "weight": 0.9},
                {"task": "Analytics Check", "time": "07:00", "weight": 0.8},
                {"task": "Content Plan", "time": "09:00", "weight": 0.7}
            ],
            "midday": [
                {"task": "Outreach Emails", "time": "14:00", "weight": 0.8},
                {"task": "Social Posts", "time": "12:00", "weight": 0.6}
            ],
            "evening": [
                {"task": "Growth Posts", "time": "20:00", "weight": 0.9},
                {"task": "Daily Summary", "time": "20:00", "weight": 0.8}
            ],
            "weekly": [
                {"task": "Content Post", "days": [1, 3, 5], "weight": 0.9},  # Mo, Mi, Fr
                {"task": "Weekly Report", "days": [0], "weight": 0.9}  # Sonntag
            ]
        }
    
    def predict(self, context: Optional[Dict] = None) -> List[Dict]:
        """
        Prediziere was als nächstes kommt!
        
        Args:
            context: Aktueller Kontext (Zeit, User, etc.)
            
        Returns:
            List von vorhergesagten Tasks mit Wahrscheinlichkeit
        """
        
        now = datetime.now()
        predictions = []
        
        # 1. Time-based predictions
        hour = now.hour
        
        if 6 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 18:
            period = "midday"
        else:
            period = "evening"
        
        # Add time-based predictions
        for pattern in self.time_patterns.get(period, []):
            predictions.append({
                "task": pattern["task"],
                "reason": f"Time-based ({period})",
                "confidence": pattern.get("weight", 0.5),
                "suggested_time": pattern.get("time", ""),
                "type": "scheduled"
            })
        
        # 2. Weekly patterns
        weekday = now.weekday()
        for pattern in self.time_patterns.get("weekly", []):
            if weekday in pattern.get("days", []):
                predictions.append({
                    "task": pattern["task"],
                    "reason": f"Weekly pattern ({now.strftime('%A')})",
                    "confidence": pattern.get("weight", 0.5),
                    "type": "scheduled"
                })
        
        # 3. Context-based predictions
        if context:
            self.context_history.append(context)
            
            # Analyze context for patterns
            recent = self.context_history[-10:]
            
            # Example: If user asked about "Content" recently, suggest more content
            content_mentions = sum(1 for c in recent if "content" in str(c).lower())
            if content_mentions >= 2:
                predictions.append({
                    "task": "Create Content",
                    "reason": "User mentioned content multiple times",
                    "confidence": 0.7,
                    "type": "contextual"
                })
        
        # Sort by confidence
        predictions.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return predictions[:5]  # Top 5
    
    def get_next_task(self) -> Optional[Dict]:
        """Gib die wahrscheinlichste nächste Task"""
        
        predictions = self.predict()
        
        if predictions:
            return predictions[0]
        
        return None
    
    def suggest_related(self, current_task: str) -> List[Dict]:
        """Schlage verwandte Tasks vor basierend auf aktueller Task"""
        
        suggestions = []
        
        # Task chains
        chains = {
            "research": ["content", "outreach"],
            "content": ["social", "email"],
            "outreach": ["follow-up", "content"],
            "email": ["follow-up", "analytics"],
            "analytics": ["report", "optimization"]
        }
        
        current_lower = current_task.lower()
        
        for key, values in chains.items():
            if key in current_lower:
                for v in values:
                    suggestions.append({
                        "task": v.title(),
                        "reason": f"Often follows '{key}'",
                        "confidence": 0.6,
                        "type": "chain"
                    })
        
        return suggestions
    
    def learn_from_execution(self, task: str, success: bool, duration: float):
        """Lerne aus ausgeführten Tasks"""
        
        # Track execution patterns
        self.predictions.append({
            "task": task,
            "success": success,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent
        if len(self.predictions) > 100:
            self.predictions = self.predictions[-100:]
    
    def get_recommended_actions(self) -> List[str]:
        """Gib empfohlene Aktionen basierend auf Predictions"""
        
        now = datetime.now()
        actions = []
        
        # Check what should happen now
        predictions = self.predict()
        
        for p in predictions[:3]:
            if p.get("type") == "scheduled":
                actions.append(f"📅 {p['task']} - scheduled for {p.get('suggested_time', 'now')}")
            else:
                actions.append(f"💡 {p['task']} - {p.get('reason', '')}")
        
        return actions


# Global instance
_predictive_system = None


def get_predictive_system() -> PredictiveTaskSystem:
    """Hol das globale Predictive System"""
    global _predictive_system
    if _predictive_system is None:
        _predictive_system = PredictiveTaskSystem()
    return _predictive_system


if __name__ == "__main__":
    # Test
    p = PredictiveTaskSystem()
    
    print("=== PREDICTIONS ===")
    predictions = p.predict()
    
    for pred in predictions:
        print(f"  {pred['task']} ({pred['confidence']:.0%}) - {pred['reason']}")
    
    print("\n=== RECOMMENDED ACTIONS ===")
    for action in p.get_recommended_actions():
        print(f"  {action}")
    
    print("\n=== RELATED TO 'research' ===")
    related = p.suggest_related("research")
    for r in related:
        print(f"  {r['task']} - {r['reason']}")
