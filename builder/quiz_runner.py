#!/usr/bin/env python3
"""
Quiz Runner für OpenClaw University
Liest Quiz-Markdown-Files und stellt interaktive Fragen.
"""

import re
import os
from pathlib import Path

# === KONFIGURATION ===
UNIVERSITY_DIR = "/home/clawbot/.openclaw/workspace/ceo/university"

# === PARSER ===

def parse_quiz(filepath: str) -> list[dict]:
    """Parse ein Quiz-Markdown-File und extrahiert Fragen."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    questions = []
    
    # Split in Teile (TEIL A, B, C, D)
    # TEIL A: Multiple Choice
    part_a = re.search(r'# TEIL A — Multiple Choice.*?(?=# TEIL B|$)', content, re.DOTALL)
    if part_a:
        questions.extend(parse_multiple_choice(part_a.group()))
    
    # TEIL B: True/False
    part_b = re.search(r'# TEIL B — True/False.*?(?=# TEIL C|# TEIL D|$)', content, re.DOTALL)
    if part_b:
        questions.extend(parse_true_false(part_b.group()))
    
    # TEIL C: Zuordnung
    part_c = re.search(r'# TEIL C — Zuordnungsfrage.*?(?=# TEIL D|$)', content, re.DOTALL)
    if part_c:
        questions.extend(parse_matching(part_c.group()))
    
    # TEIL D: Praxisfragen
    part_d = re.search(r'# TEIL D — Praxisfragen.*?(?=Ende der Prüfung|$)', content, re.DOTALL)
    if part_d:
        questions.extend(parse_praxisfragen(part_d.group()))
    
    return questions


def parse_multiple_choice(text: str) -> list[dict]:
    """Parse Multiple Choice Fragen (a/b/c/d)."""
    questions = []
    # Match Fragen im Format: ## Frage X [Y Punkte] ... a) ... b) ... c) ... d)
    pattern = r'## Frage (\d+) \[(\d+) Punkte\]\s*\n+(.*?)(?=\n+## Frage |\n+# TEIL B|\n*$)'
    
    for match in re.finditer(pattern, text, re.DOTALL):
        q_num = match.group(1)
        points = match.group(2)
        q_body = match.group(3).strip()
        
        # Extrahiere Fragetext und Optionen
        lines = q_body.split('\n')
        question_text = ""
        options = []
        
        for line in lines:
            line = line.strip()
            if re.match(r'^[a-d]\)', line):
                options.append(line)
            elif not question_text and len(line) > 10:
                # Erste lange Zeile ist der Fragetext
                question_text = line
        
        if question_text and len(options) == 4:
            questions.append({
                "id": f"q{q_num}",
                "type": "multiple_choice",
                "text": question_text,
                "options": options,
                "points": int(points)
            })
    
    return questions


def parse_true_false(text: str) -> list[dict]:
    """Parse True/False Fragen."""
    questions = []
    pattern = r'## Frage (\d+) \[(\d+) Punkte\]\s*\n+\*\*Aussage:\*\* "(.*?)"\s*\n+Wahr oder Falsch\?'
    
    for match in re.finditer(pattern, text, re.DOTALL):
        q_num = match.group(1)
        points = match.group(2)
        statement = match.group(3).strip()
        
        questions.append({
            "id": f"q{q_num}",
            "type": "true_false",
            "text": f'Aussage: "{statement}"',
            "points": int(points)
        })
    
    return questions


def parse_matching(text: str) -> list[dict]:
    """Parse Zuordnungsfrage (PART C)."""
    questions = []
    pattern = r'## Frage (\d+) \[(\d+) Punkte\]\s*\n+Ordne die folgenden.*?(?=\n+# TEIL D|Ende der Prüfung|$)'
    
    for match in re.finditer(pattern, text, re.DOTALL):
        q_num = match.group(1)
        points = match.group(2)
        
        questions.append({
            "id": f"q{q_num}",
            "type": "matching",
            "text": "Ordne die OWASP ML-Kategorien den richtigen Beschreibungen zu (siehe Quiz-Datei).",
            "points": int(points)
        })
    
    return questions


def parse_praxisfragen(text: str) -> list[dict]:
    """Parse offene Praxisfragen (PART D)."""
    questions = []
    pattern = r'## Frage (\d+) \[(\d+) Punkte\](.*?)(?=\n+## Frage |\n*Ende|$)'
    
    for match in re.finditer(pattern, text, re.DOTALL):
        q_num = match.group(1)
        points = match.group(2)
        q_body = match.group(3).strip()
        
        # Extrahiere ersten Satz als Fragetext
        first_line = q_body.split('\n')[0].strip()
        
        questions.append({
            "id": f"q{q_num}",
            "type": "praxis",
            "text": first_line,
            "points": int(points)
        })
    
    return questions


def parse_solutions(filepath: str) -> dict:
    """Parse Lösungsschlüssel und extrahiere Antworten."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    solutions = {}
    
    # TEIL A: Multiple Choice Lösungen
    # Pattern: ## Frage X — Lösung ... Richtige Antwort: Y
    mc_pattern = r'## Frage (\d+) — Lösung\s*\n+\*\*Richtige Antwort: (.)\*\*'
    for match in re.finditer(mc_pattern, content):
        q_num = f"q{match.group(1)}"
        answer = match.group(2).lower()
        solutions[q_num] = answer
    
    # TEIL B: True/False Lösungen
    tf_pattern = r'## Frage (\d+) — Lösung\s*\n+\*\*Richtige Antwort: (Wahr|Falsch)\*\*'
    for match in re.finditer(tf_pattern, content):
        q_num = f"q{match.group(1)}"
        answer = match.group(2)
        solutions[q_num] = answer
    
    # TEIL C: Matching (keine automatische Auswertung)
    # TEIL D: Praxisfragen (keine automatische Auswertung)
    
    return solutions


# === QUIZ LOOP ===

def run_quiz(module_num: int):
    """Führe das Quiz für ein bestimmtes Modul aus."""
    quiz_file = os.path.join(UNIVERSITY_DIR, f"quiz_module_{module_num}.md")
    solution_file = os.path.join(UNIVERSITY_DIR, f"solutions_quiz_module_{module_num}.md")
    
    if not os.path.exists(quiz_file):
        print(f"❌ Quiz-Datei nicht gefunden: {quiz_file}")
        return
    
    if not os.path.exists(solution_file):
        print(f"❌ Lösung-Datei nicht gefunden: {solution_file}")
        return
    
    print(f"\n{'='*60}")
    print(f"📚 OpenClaw University — Modul {module_num}")
    print(f"{'='*60}\n")
    
    # Parse
    questions = parse_quiz(quiz_file)
    solutions = parse_solutions(solution_file)
    
    if not questions:
        print("❌ Keine Fragen gefunden. Format möglicherweise unbekannt.")
        return
    
    print(f"Gefundene Fragen: {len(questions)}")
    print(f"Automatisch auswertbar: {len(solutions)}")
    print()
    
    score = 0
    auto_score = 0
    auto_total = len(solutions)
    question_num = 1
    
    for q in questions:
        print(f"\n--- Frage {question_num} ---")
        print(f"[{q['type']}] {q['text']}")
        
        if q["type"] == "multiple_choice":
            for opt in q["options"]:
                print(f"  {opt}")
            print()
            user_answer = input("Deine Antwort (a/b/c/d): ").strip().lower()
            correct = solutions.get(q["id"], "")
            
            if user_answer == correct:
                print("✅ Richtig!")
                score += q["points"]
                auto_score += 1
            else:
                print(f"❌ Falsch. Richtige Antwort: {correct}")
        
        elif q["type"] == "true_false":
            print()
            user_answer = input("Wahr oder Falsch? ").strip()
            correct = solutions.get(q["id"], "")
            
            # Normalisiere
            if user_answer.lower() in ['w', 'true', 't', '1', 'wahr']:
                user_answer = "Wahr"
            else:
                user_answer = "Falsch"
            
            if user_answer == correct:
                print("✅ Richtig!")
                score += q["points"]
                auto_score += 1
            else:
                print(f"❌ Falsch. Richtige Antwort: {correct}")
        
        elif q["type"] == "matching":
            print("📋 Diese Frage bitte manuell mit dem Lösungsschlüssel vergleichen.")
            print("   (Zuordnungen: ML01-ML10 → Beschreibungen A-J)")
        
        elif q["type"] == "praxis":
            print("📝 Bitte selbst beantworten und mit Lösungsschlüssel vergleichen.")
            print("   Tipp: Siehe solutions_quiz_module_X.md für Musterlösungen.")
        
        question_num += 1
    
    # === ERGEBNIS ===
    print(f"\n{'='*60}")
    print(f"📊 ERGEBNIS")
    print(f"{'='*60}")
    
    if auto_total > 0:
        pct = (auto_score / auto_total) * 100
        print(f"Automatischer Score: {auto_score}/{auto_total} ({pct:.0f}%)")
    
    print(f"Manuelle Teile (TEIL C & D): Bitte selbst prüfen")
    print(f"\nLösungen: {solution_file}")
    print(f"{'='*60}\n")


def list_modules():
    """Liste alle verfügbaren Module."""
    print("\n📚 Verfügbare Module:")
    print("-" * 40)
    
    for f in sorted(Path(UNIVERSITY_DIR).glob("quiz_module_*.md")):
        num = re.search(r'quiz_module_(\d+)', f.name)
        if num:
            print(f"  Modul {num.group(1)}: {f.name}")
    
    print()


def main():
    """Hauptmenü."""
    while True:
        print("\n🎓 OpenClaw University — Quiz Runner")
        print("=" * 40)
        print("1. Modul auswählen")
        print("2. Alle Module anzeigen")
        print("0. Beenden")
        
        choice = input("\nWähle: ").strip()
        
        if choice == "1":
            list_modules()
            mod = input("Modul-Nummer: ").strip()
            if mod.isdigit():
                run_quiz(int(mod))
        elif choice == "2":
            list_modules()
        elif choice == "0":
            print("👋 Bis bald!")
            break
        else:
            print("Ungültige Eingabe.")


if __name__ == "__main__":
    main()
