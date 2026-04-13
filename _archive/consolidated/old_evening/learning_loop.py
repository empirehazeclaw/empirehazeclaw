#!/usr/bin/env python3
"""
🔄 Learning Loop
Automatischer Lernzyklus: Problem → Lösung → Skill
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from creator import learn_from_problem, get_relevant_learnings
from persistent_memory import get_memory

LEARNING_LOG = Path("/home/clawbot/.openclaw/workspace/logs/learning_loop.log")
DECISION_LOG = Path("/home/clawbot/.openclaw/workspace/memory/decisions")

class LearningLoop:
    def __init__(self):
        self.memory = get_memory()
        self.log_file = LEARNING_LOG
        self.decision_log = DECISION_LOG
        DECISION_LOG.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str):
        """Loggt Aktion"""
        timestamp = datetime.now().isoformat()
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"📝 {message}")
    
    def analyze_error(self, error: str, context: str = "") -> dict:
        """Analysiert einen Fehler und findet/schreibt Lösung"""
        self.log(f"Analysiere Error: {error[:50]}...")
        
        # Check ob wir ähnliches Problem schon gelöst haben
        relevant = get_relevant_learnings(error)
        
        if relevant:
            self.log(f"✅ Ähnliches Problem gefunden: {len(relevant)} Treffer")
            return {
                "found": True,
                "solutions": relevant,
                "new_solution_needed": False
            }
        
        # Speichere für später
        self.log(f"❌ Keine Lösung gefunden - speichere für später")
        return {
            "found": False,
            "solutions": [],
            "new_solution_needed": True
        }
    
    def record_solution(self, problem: str, solution: str, context: str = ""):
        """Zeichnet Lösung auf und erstellt ggf. Skill"""
        self.log(f"Speichere Lösung für: {problem[:50]}...")
        
        # Lernt aus Problem
        entry = learn_from_problem(problem, solution, context)
        
        # Speichert in Persistent Memory
        self.memory.add_learning(f"problem_{datetime.now().timestamp()}", {
            "problem": problem,
            "solution": solution,
            "context": context
        }, category="error_fix")
        
        if entry.get("skill_created"):
            self.log(f"🧠 Neuer Skill automatisch erstellt!")
        
        return entry
    
    def make_decision(self, context: str, options: list, choice: str, reason: str):
        """Speichert wichtige Entscheidung"""
        decision = {
            "context": context,
            "options": options,
            "choice": choice,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # Speichern
        filename = DECISION_LOG / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(decision, f, indent=2)
        
        # Auch in memory
        self.memory.add_learning(f"decision_{datetime.now().timestamp()}", decision, "decision")
        
        self.log(f"✅ Entscheidung gespeichert: {choice}")
        return decision
    
    def get_historical_decisions(self, query: str = "") -> list:
        """Holt vergangene Entscheidungen"""
        decisions = []
        
        for f in DECISION_LOG.glob("*.json"):
            with open(f) as fp:
                decisions.append(json.load(fp))
        
        if query:
            query_lower = query.lower()
            decisions = [d for d in decisions if query_lower in d.get("context", "").lower()]
        
        return sorted(decisions, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def weekly_review(self) -> dict:
        """Wöchentlicher Review - was haben wir gelernt?"""
        self.log("🗓️ Weekly Review starten...")
        
        learnings = get_relevant_learnings("")
        decisions = self.get_historical_decisions()
        
        review = {
            "date": datetime.now().isoformat(),
            "total_learnings": len(learnings),
            "total_decisions": len(decisions),
            "recent_learnings": learnings[-5:],
            "recent_decisions": decisions[:5]
        }
        
        self.log(f"📊 Review: {len(learnings)} Learnings, {len(decisions)} Decisions")
        
        return review

if __name__ == "__main__":
    loop = LearningLoop()
    
    if len(sys.argv) < 2:
        print("🔄 Learning Loop")
        print("")
        print("Usage:")
        print("  python3 learning_loop.py analyze <error> [context]")
        print("  python3 learning_loop.py record <problem> <solution> [context]")
        print("  python3 learning_loop.py decide <context> <choice> <reason>")
        print("  python3 learning_loop.py decisions [query]")
        print("  python3 learning_loop.py review")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "analyze" and len(sys.argv) >= 3:
        error = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        result = loop.analyze_error(error, context)
        print(json.dumps(result, indent=2))
    
    elif cmd == "record" and len(sys.argv) >= 4:
        problem = sys.argv[2]
        solution = sys.argv[3]
        context = sys.argv[4] if len(sys.argv) > 4 else ""
        loop.record_solution(problem, solution, context)
    
    elif cmd == "decide" and len(sys.argv) >= 5:
        context = sys.argv[2]
        choice = sys.argv[3]
        reason = sys.argv[4]
        loop.make_decision(context, [], choice, reason)
    
    elif cmd == "decisions":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        decisions = loop.get_historical_decisions(query)
        for d in decisions:
            print(f"📌 {d.get('timestamp')}: {d.get('choice')}")
            print(f"   → {d.get('reason')}")
            print()
    
    elif cmd == "review":
        review = loop.weekly_review()
        print(json.dumps(review, indent=2))
