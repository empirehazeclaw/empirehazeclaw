#!/usr/bin/env python3
"""
✅ QUALITY CHECK ENGINE - STRICT VERSION
=========================================
Strenge Quality Checks - Produkte MÜSSEN bestehen!
"""

import json
import re
import os
from datetime import datetime

# Minimale Anforderungen (STRENG)
MIN_REQUIREMENTS = {
    "ebook": {
        "min_length": 5000,      # Mindestens 5000 Zeichen
        "min_sections": 5,        # Mindestens 5 Kapitel
        "min_placeholder_score": 100,  # 0 Placeholder erlaubt
        "passing_score": 80       # Mindestens 80% für Verkauf
    },
    "notion": {
        "min_properties": 3,       # Mindestens 3 Properties
        "min_content_items": 10,  # Mindestens 10 Content Items
        "passing_score": 80
    },
    "saas": {
        "has_ui": True,           # MUSS eine UI haben
        "has_api": True,          # MUSS eine API haben
        "passing_score": 85       # Mindestens 85% für SaaS
    },
    "pod": {
        "has_description": True,
        "has_tags": True,
        "min_tags": 5,
        "passing_score": 80
    }
}

class QualityEngine:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
    
    def check_saas(self, project_path):
        """STRENGER Quality Check für SaaS"""
        
        results = {
            "checks": [],
            "score": 0,
            "passed": False,
            "blocker": []
        }
        
        # STRENG: Check for UI (HTML template)
        has_ui = False
        ui_path = f"{project_path}/templates"
        if os.path.exists(ui_path):
            ui_files = os.listdir(ui_path)
            has_ui = len(ui_files) > 0 and any(f.endswith('.html') for f in ui_files)
        
        results["checks"].append({
            "name": "Has UI (HTML Templates)",
            "passed": has_ui,
            "weight": 25,
            "required": True
        })
        
        if not has_ui:
            results["blocker"].append("KEINE UI - Produkt nicht verkaufbar!")
        
        # Check for app.py
        app_exists = self.check_file_exists(f"{project_path}/app.py")
        results["checks"].append({
            "name": "Code File Exists",
            "passed": app_exists,
            "weight": 15,
            "required": True
        })
        
        if not app_exists:
            results["blocker"].append("Keine app.py gefunden!")
        
        # Syntax Check
        if app_exists:
            syntax_ok = self.check_python_syntax(f"{project_path}/app.py")
            results["checks"].append({
                "name": "Python Syntax Valid",
                "passed": syntax_ok,
                "weight": 20,
                "required": True
            })
            
            if not syntax_ok:
                results["blocker"].append("Syntax Fehler im Code!")
        
        # API Check
        has_api = False
        if app_exists:
            with open(f"{project_path}/app.py") as f:
                content = f.read()
                has_api = "@app.route" in content or "API" in content
        
        results["checks"].append({
            "name": "Has API Routes",
            "passed": has_api,
            "weight": 20,
            "required": True
        })
        
        if not has_api:
            results["blocker"].append("KEINE API Routes - kein echtes SaaS!")
        
        # Calculate score
        total_weight = sum(c["weight"] for c in results["checks"])
        passed_weight = sum(c["weight"] for c in results["checks"] if c["passed"])
        
        results["score"] = int((passed_weight / total_weight) * 100) if total_weight > 0 else 0
        results["passed"] = results["score"] >= MIN_REQUIREMENTS["saas"]["passing_score"] and len(results["blocker"]) == 0
        
        return results
    
    def check_ebook(self, filepath):
        """STRENGER Quality Check für eBooks"""
        
        results = {
            "checks": [],
            "score": 0,
            "passed": False,
            "blocker": []
        }
        
        # Check 1: File exists
        file_exists = self.check_file_exists(filepath)
        results["checks"].append({
            "name": "File Exists",
            "passed": file_exists,
            "weight": 10,
            "required": True
        })
        
        if not file_exists:
            results["blocker"].append("Datei existiert nicht!")
            return results
        
        # Check 2: Minimum length (STRENG: 5000 chars)
        length_ok = self.check_min_length(filepath, MIN_REQUIREMENTS["ebook"]["min_length"])
        results["checks"].append({
            "name": f"Minimum Length ({MIN_REQUIREMENTS['ebook']['min_length']} chars)",
            "passed": length_ok,
            "weight": 25,
            "required": True
        })
        
        if not length_ok:
            results["blocker"].append(f"Zu kurz! Mindestens {MIN_REQUIREMENTS['ebook']['min_length']} Zeichen nötig.")
        
        # Check 3: Structure (min 5 sections)
        structure_ok = self.check_structure(filepath, MIN_REQUIREMENTS["ebook"]["min_sections"])
        results["checks"].append({
            "name": f"Has Structure ({MIN_REQUIREMENTS['ebook']['min_sections']}+ Kapitel)",
            "passed": structure_ok,
            "weight": 20,
            "required": True
        })
        
        if not structure_ok:
            results["blocker"].append("Zu wenig Struktur! Mindestens 5 Kapitel nötig.")
        
        # Check 4: No placeholder
        no_placeholder = self.check_no_placeholder(filepath)
        results["checks"].append({
            "name": "No Placeholder Text",
            "passed": no_placeholder,
            "weight": 20,
            "required": True
        })
        
        if not no_placeholder:
            results["blocker"].append("Placeholder Text gefunden - nicht verkaufsreif!")
        
        # Check 5: Has conclusion
        has_conclusion = self.check_conclusion(filepath)
        results["checks"].append({
            "name": "Has Conclusion/Fazit",
            "passed": has_conclusion,
            "weight": 15,
            "required": True
        })
        
        if not has_conclusion:
            results["blocker"].append("Kein Fazit/Conclusion - unvollständig!")
        
        # Check 6: Unique content (not generic)
        unique_ok = self.check_unique_content(filepath)
        results["checks"].append({
            "name": "Has Unique Insights",
            "passed": unique_ok,
            "weight": 10,
            "required": False
        })
        
        # Calculate score
        total_weight = sum(c["weight"] for c in results["checks"])
        passed_weight = sum(c["weight"] for c in results["checks"] if c["passed"])
        
        results["score"] = int((passed_weight / total_weight) * 100) if total_weight > 0 else 0
        results["passed"] = results["score"] >= MIN_REQUIREMENTS["ebook"]["passing_score"] and len(results["blocker"]) == 0
        
        return results
    
    def check_notion(self, filepath):
        """STRENGER Quality Check für Notion Templates"""
        
        results = {
            "checks": [],
            "score": 0,
            "passed": False,
            "blocker": []
        }
        
        # Check file exists
        file_exists = self.check_file_exists(filepath)
        results["checks"].append({
            "name": "File Exists",
            "passed": file_exists,
            "weight": 10,
            "required": True
        })
        
        if not file_exists:
            results["blocker"].append("Datei existiert nicht!")
            return results
        
        # Check valid JSON
        valid_json = self.check_valid_json(filepath)
        results["checks"].append({
            "name": "Valid JSON",
            "passed": valid_json,
            "weight": 20,
            "required": True
        })
        
        if not valid_json:
            results["blocker"].append("Kein valides JSON!")
            return results
        
        # Check properties (min 3)
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            properties = data.get("properties", [])
            has_enough_props = len(properties) >= MIN_REQUIREMENTS["notion"]["min_properties"]
            
            results["checks"].append({
                "name": f"Has Properties ({MIN_REQUIREMENTS['notion']['min_properties']}+)",
                "passed": has_enough_props,
                "weight": 25,
                "required": True
            })
            
            if not has_enough_props:
                results["blocker"].append(f"Zu wenig Properties! Mindestens {MIN_REQUIREMENTS['notion']['min_properties']} nötig.")
            
            # Check content items (min 10)
            content = data.get("database_content", [])
            has_content = len(content) >= MIN_REQUIREMENTS["notion"]["min_content_items"]
            
            results["checks"].append({
                "name": f"Has Content ({MIN_REQUIREMENTS['notion']['min_content_items']}+ Items)",
                "passed": has_content,
                "weight": 25,
                "required": True
            })
            
            if not has_content:
                results["blocker"].append(f"Zu wenig Content! Mindestens {MIN_REQUIREMENTS['notion']['min_content_items']} Items nötig.")
            
            # Check title
            has_title = "title" in data
            results["checks"].append({
                "name": "Has Title",
                "passed": has_title,
                "weight": 10,
                "required": True
            })
            
            if not has_title:
                results["blocker"].append("Kein Titel definiert!")
            
            # Check icon
            has_icon = "icon" in data
            results["checks"].append({
                "name": "Has Icon/Emoji",
                "passed": has_icon,
                "weight": 10,
                "required": False
            })
            
        except Exception as e:
            results["blocker"].append(f"Fehler beim Lesen: {e}")
        
        # Calculate score
        total_weight = sum(c["weight"] for c in results["checks"])
        passed_weight = sum(c["weight"] for c in results["checks"] if c["passed"])
        
        results["score"] = int((passed_weight / total_weight) * 100) if total_weight > 0 else 0
        results["passed"] = results["score"] >= MIN_REQUIREMENTS["notion"]["passing_score"] and len(results["blocker"]) == 0
        
        return results
    
    # Helper methods
    def check_file_exists(self, path):
        import os
        return os.path.exists(path)
    
    def check_min_length(self, filepath, min_chars):
        try:
            with open(filepath) as f:
                content = f.read()
            return len(content) >= min_chars
        except:
            return False
    
    def check_structure(self, filepath, min_sections):
        try:
            with open(filepath) as f:
                content = f.read()
            # Count ## headings
            sections = len(re.findall(r'^##\s+', content, re.MULTILINE))
            return sections >= min_sections
        except:
            return False
    
    def check_no_placeholder(self, filepath):
        try:
            with open(filepath) as f:
                content = f.read().lower()
            placeholders = ["placeholder", "todo", "fixme", "xxx", "tbd", "insert here", "add your", "replace this"]
            return not any(p in content for p in placeholders)
        except:
            return False
    
    def check_conclusion(self, filepath):
        try:
            with open(filepath) as f:
                content = f.read().lower()
            return "fazit" in content or "conclusion" in content or "zusammenfassung" in content
        except:
            return False
    
    def check_unique_content(self, filepath):
        """Check if content is not just generic AI text"""
        try:
            with open(filepath) as f:
                content = f.read().lower()
            
            # Generic phrases that indicate low quality
            generic_phrases = [
                "in der heutigen zeit",
                "wie bereits erwähnt",
                "es ist wichtig zu erwähnen",
                "zusammenfassend lässt sich sagen"
            ]
            
            generic_count = sum(1 for p in generic_phrases if p in content)
            return generic_count < 3
        except:
            return True
    
    def check_python_syntax(self, filepath):
        import ast
        try:
            with open(filepath) as f:
                code = f.read()
            ast.parse(code)
            return True
        except:
            return False
    
    def check_imports(self, filepath):
        try:
            with open(filepath) as f:
                content = f.read()
            required = ["flask", "request"]
            return any(r in content.lower() for r in required)
        except:
            return False
    
    def check_valid_json(self, filepath):
        try:
            with open(filepath) as f:
                json.load(f)
            return True
        except:
            return False


def run_quality_check(product_type, filepath):
    """Main entry point - BLOCKS if not passing!"""
    
    engine = QualityEngine()
    
    if product_type == "ebook":
        result = engine.check_ebook(filepath)
    elif product_type == "notion":
        result = engine.check_notion(filepath)
    elif product_type == "saas":
        result = engine.check_saas(filepath)
    else:
        result = {"score": 100, "passed": True, "blocker": []}
    
    # STRENG: Add warning if not passing
    if not result["passed"]:
        result["message"] = "❌ PRODUKT BLOCKIERT - Qualität nicht ausreichend!"
        if result.get("blocker"):
            result["message"] += "\nGründe:\n" + "\n".join(f"  - {b}" for b in result["blocker"])
    else:
        result["message"] = "✅ Produkt verkaufsreif!"
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python3 quality_check.py <type> <path>")
        print("Types: ebook, notion, saas")
        sys.exit(1)
    
    result = run_quality_check(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
