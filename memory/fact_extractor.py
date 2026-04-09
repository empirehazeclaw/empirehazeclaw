#!/usr/bin/env python3
"""
Fact Extractor - Automatic extraction from conversations
"""

import re
from datetime import datetime
from typing import List, Dict

class FactExtractor:
    """Extract facts from text automatically"""
    
    # Patterns for different categories
    FACT_PATTERNS = {
        "preference": [
            r"Ich (?:heiße|bin|mag|nutze|liebe|hasse|will|nicht)",
            r"prefer|prefers?|like|likes|love|hate|want|don't like",
            r"german|deutsch|english|short|detailed|concise",
            r"call me|nenn mich|mein name ist",
        ],
        "goal": [
            r"Ziel|goal|target|will erreichen|aim for",
            r"€\d+|dollar \d+|verdienen|machen",
            r"per month|pro monat|per week|pro woche",
            r"my objective|mein ziel",
        ],
        "learning": [
            r"gelernt|learned|entdeckt|found out|new|neu",
            r"lesson|erkenntnis|insight",
            r"fand heraus|research",
        ],
        "pattern": [
            r"immer|always|often|usually|typically",
            r"wenn|whenever|if",
            r"normalerweise|typically",
        ],
        "project": [
            r"project|projekt|Business|POD|Shopify|Etsy",
            r"starten|start|begin|launch",
        ],
        "skill": [
            r"skill|können|can|ability|fähig",
            r"experience|erfahrung|experienced",
        ]
    }
    
    # Priority mapping
    PRIORITY_MAP = {
        "goal": "HIGH",
        "preference": "CRITICAL",
        "project": "HIGH",
        "pattern": "MEDIUM",
        "learning": "MEDIUM",
        "skill": "LOW"
    }
    
    def extract(self, text: str) -> List[Dict]:
        """Extract facts from text"""
        facts = []
        
        for category, patterns in self.FACT_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Extract context around match
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end]
                    
                    facts.append({
                        "category": category,
                        "content": context.strip(),
                        "extracted_at": datetime.now().isoformat(),
                        "confidence": self._calculate_confidence(category, context),
                        "priority": self.PRIORITY_MAP.get(category, "MEDIUM"),
                        "match": match.group()
                    })
        
        return facts
    
    def _calculate_confidence(self, category: str, text: str) -> float:
        """Calculate confidence score"""
        # Direct statements are higher confidence
        direct_indicators = [
            "ich bin", "ich will", "ich mag", "ich heiße",
            "i am", "i will", "i want", "i like", "my name"
        ]
        
        text_lower = text.lower()
        
        for indicator in direct_indicators:
            if indicator in text_lower:
                return 0.9
        
        return 0.6
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract named entities"""
        entities = []
        
        # Project/Brand names
        projects = ["POD", "Etsy", "Printify", "Shopify", "Felix", "ClawBot", "OpenClaw"]
        for project in projects:
            if project.lower() in text.lower():
                entities.append(project)
        
        # Money amounts
        money = re.findall(r"€\d+|\$\d+|\d+\s*(?:euro|dollar)", text, re.IGNORECASE)
        entities.extend(money)
        
        return entities
    
    def summarize(self, facts: List[Dict]) -> str:
        """Summarize extracted facts"""
        if not facts:
            return "No facts extracted."
        
        by_category = {}
        for fact in facts:
            cat = fact["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(fact["content"])
        
        summary = "Extracted Facts:\n"
        for cat, contents in by_category.items():
            summary += f"\n{cat.upper()} ({len(contents)}):\n"
            for c in contents[:3]:  # Max 3 per category
                summary += f"  - {c[:80]}\n"
        
        return summary

# CLI
if __name__ == "__main__":
    import sys
    
    extractor = FactExtractor()
    
    if len(sys.argv) < 2:
        print("Fact Extractor CLI")
        print("Usage:")
        print("  python3 fact_extractor.py extract <text>")
        print("  python3 fact_extractor.py entities <text>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "extract":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Ich heiße Nico und will €100 pro Monat verdienen"
        facts = extractor.extract(text)
        print(extractor.summarize(facts))
    
    elif action == "entities":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Mein POD Business auf Etsy wird €100 pro Monat machen"
        entities = extractor.extract_entities(text)
        print(f"Entities: {entities}")
