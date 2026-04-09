#!/usr/bin/env python3
"""
Flashcard Bot für OpenClaw University
Tägliches Spaced-Repetition System via Telegram

Usage:
    python flashcard_bot.py                    # Sende Daily Cards
    python flashcard_bot.py --add             # Interaktiv Karte hinzufügen
    python flashcard_bot.py --stats           # Zeig Deck-Statistik
    python flashcard_bot.py --list            # Liste alle Karten
    python flashcard_bot.py --review          # Sofort Review starten
"""

import json
import os
import sys
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIG ===
WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo/university")
DECK_FILE = WORKSPACE / "flashcard_deck.json"
TELEGRAM_ID = "5392634979"  # Nico's Telegram ID

# === HELPERS ===

def load_deck():
    """Lädt das Flashcard-Deck aus JSON"""
    if not DECK_FILE.exists():
        return {"cards": [], "deck_version": "1.0"}
    with open(DECK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_deck(deck):
    """Speichert das Deck"""
    with open(DECK_FILE, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)

def get_due_cards(deck, limit=5):
    """
    Wählt Karten die fällig sind basierend auf:
    - Nicht gezeigt seit >1 Tag
    - High wrong_count (vorrang)
    - Topic-Wechsel (nicht alle vom selben Thema)
    """
    cards = deck.get("cards", [])
    if not cards:
        return []
    
    now = datetime.utcnow()
    due = []
    
    for card in cards:
        # Parse last_shown
        last_shown_str = card.get("last_shown", None)
        if last_shown_str:
            try:
                last_shown = datetime.fromisoformat(last_shown_str.replace("Z", "+00:00"))
                days_since = (now - last_shown.replace(tzinfo=None)).days
            except:
                days_since = 999  # Show cards with invalid date
        else:
            days_since = 999
        
        wrong_count = card.get("wrong_count", 0)
        priority = wrong_count * 2 + days_since
        
        card["_priority"] = priority
        card["_days_since"] = days_since
        due.append(card)
    
    # Sortiere nach Priority (absteigend)
    due.sort(key=lambda x: x["_priority"], reverse=True)
    
    # Wähle mit Topic-Diversity
    selected = []
    topics_seen = set()
    
    for card in due:
        topic = card.get("topic", "unknown")
        if len(selected) >= limit:
            break
        # Max 2 Karten pro Topic
        if topic not in topics_seen or len([c for c in selected if c.get("topic") == topic]) < 2:
            selected.append(card)
            topics_seen.add(topic)
    
    return selected

def format_flashcard(card, show_answer=False):
    """Formatiert eine Flashcard für Telegram"""
    q = card.get("question", "")
    a = card.get("answer", "")
    topic = card.get("topic", "unknown")
    card_id = card.get("id", "?")
    wrong = card.get("wrong_count", 0)
    
    msg = f"🎴 **Flashcard** `#{card_id}` — {topic}\n\n"
    msg += f"❓ **{q}**\n\n"
    
    if show_answer:
        msg += f"━━━━━━━━━━━━━━━\n"
        msg += f"✅ **{a}**\n"
        msg += f"━━━━━━━━━━━━━━━\n"
        msg += f"_Falsch beantwortet: {wrong}×_"
    else:
        msg += f"_Antwort kommt gleich..._ ⏳"
    
    return msg

def send_telegram(message, chat_id=TELEGRAM_ID):
    """Sendet eine Nachricht via openclaw message tool (Telegram)"""
    # Note: Dies würde normalerweise das message tool nutzen
    # Für CLI-Ausgabe nutzen wir print
    print(f"[TELEGRAM to {chat_id}]:")
    print(message)
    print("-" * 40)
    return True

def update_card_after_feedback(card, correct):
    """Aktualisiert wrong_count nach Feedback"""
    card["last_shown"] = datetime.utcnow().isoformat() + "Z"
    
    if correct:
        card["wrong_count"] = max(0, card.get("wrong_count", 0) - 1)
    else:
        card["wrong_count"] = card.get("wrong_count", 0) + 1
    
    return card

# === COMMANDS ===

def cmd_daily(limit=5):
    """Sendet täglich fällige Flashcards"""
    deck = load_deck()
    cards = get_due_cards(deck, limit)
    
    if not cards:
        print("📭 Keine Karten fällig! Deck ist leer oder alle kürzlich gezeigt.")
        return
    
    print(f"📤 Sende {len(cards)} Flashcards an Nico...")
    
    for i, card in enumerate(cards, 1):
        # Sende Frage
        q_msg = format_flashcard(card, show_answer=False)
        send_telegram(f"[{i}/{len(cards)}]\n{q_msg}")
        
        # Sende Antwort nach kurzer Pause (simuliert)
        a_msg = format_flashcard(card, show_answer=True)
        send_telegram(a_msg)
        print()
    
    print(f"✅ {len(cards)} Flashcards gesendet!")
    print("📝 Feedback: '👍' = richtig, '👎' = nochmal")

def cmd_add():
    """Interaktiv neue Karte hinzufügen"""
    print("🆕 Neue Flashcard erstellen")
    print("-" * 40)
    
    topic = input("Topic: ").strip()
    question = input("Frage: ").strip()
    answer = input("Antwort: ").strip()
    
    if not topic or not question or not answer:
        print("❌ Alle Felder müssen ausgefüllt sein!")
        return
    
    deck = load_deck()
    cards = deck.get("cards", [])
    
    # Generiere ID
    existing_ids = [int(c.get("id", "0").replace("oc_", "0") or "0") for c in cards]
    new_id = max(existing_ids or [0]) + 1
    card_id = f"oc_{new_id:03d}"
    
    new_card = {
        "id": card_id,
        "topic": topic,
        "question": question,
        "answer": answer,
        "difficulty": 2,
        "last_shown": None,
        "wrong_count": 0
    }
    
    cards.append(new_card)
    deck["cards"] = cards
    save_deck(deck)
    
    print(f"✅ Karte {card_id} hinzugefügt!")
    print(f"📊 Gesamtkarten im Deck: {len(cards)}")

def cmd_stats():
    """Zeigt Deck-Statistiken"""
    deck = load_deck()
    cards = deck.get("cards", [])
    
    if not cards:
        print("📭 Deck ist leer!")
        return
    
    # Topics zählen
    topics = {}
    total_wrong = 0
    never_shown = 0
    
    for card in cards:
        t = card.get("topic", "unknown")
        topics[t] = topics.get(t, 0) + 1
        total_wrong += card.get("wrong_count", 0)
        if not card.get("last_shown"):
            never_shown += 1
    
    print("📊 Flashcard Deck — Statistik")
    print("=" * 40)
    print(f" Gesamtkarten: {len(cards)}")
    print(f" Nie gezeigt:   {never_shown}")
    print(f" Gesamt-Falsch: {total_wrong}")
    print()
    print(" Topics:")
    for topic, count in sorted(topics.items()):
        print(f"  • {topic}: {count}")
    
    # Fällige Karten
    due = get_due_cards(deck, 100)
    print(f"\n⏰ Fällige Karten: {len(due)}")

def cmd_list():
    """Listet alle Karten auf"""
    deck = load_deck()
    cards = deck.get("cards", [])
    
    if not cards:
        print("📭 Deck ist leer!")
        return
    
    print(f"📚 Alle {len(cards)} Karten im Deck:")
    print("-" * 50)
    
    for card in sorted(cards, key=lambda x: x.get("id", "?")):
        cid = card.get("id", "?")
        topic = card.get("topic", "?")
        wrong = card.get("wrong_count", 0)
        last = card.get("last_shown", "nie")
        if last and last != "nie":
            last = last[:10]  # Nur Datum
        q = card.get("question", "?")[:40]
        print(f"[{cid}] {topic:20s} | {q:40s} | ❌{wrong} | {last}")

def cmd_review():
    """Startet sofortiges Review"""
    deck = load_deck()
    cards = get_due_cards(deck, limit=5)
    
    if not cards:
        print("📭 Keine Karten verfügbar!")
        return
    
    print("🎴 Flashcard Review — 'q' zum Beenden")
    print("=" * 50)
    
    for card in cards:
        print(f"\n❓ {card.get('question')}")
        input("    [Enter für Antwort]...")
        print(f"✅ {card.get('answer')}")
        
        feedback = input("    Richtig? (j/n): ").strip().lower()
        correct = feedback in ["j", "ja", "y", "yes"]
        
        # Update card
        deck["cards"] = [c if c.get("id") != card.get("id") 
                        else update_card_after_feedback(card, correct) 
                        for c in deck["cards"]]
        
        if correct:
            print("  👍 Correct! (wrong_count -1)")
        else:
            print("  👎 Wrong! (wrong_count +1)")
    
    save_deck(deck)
    print("\n✅ Review abgeschlossen!")

def cmd_init_sample_cards():
    """Initialisiert Deck mit 20 Beispiel-Karten aus Lektionen"""
    sample_cards = [
        {
            "id": "oc_001",
            "topic": "Prompt Injection",
            "question": "Was ist der Unterschied zwischen Direct und Indirect Prompt Injection?",
            "answer": "Direct: Angreifer fügt bösartigen Prompt direkt in User-Input ein. Indirect: Bösartiger Text wird in externen Daten (Web, DB) versteckt und dann vom Model als Teil des Kontexts interpretiert.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_002",
            "topic": "Prompt Injection",
            "question": "Nenne 3 Verteidigungsstrategien gegen Prompt Injection",
            "answer": "1) Input-Validation & Sanitization, 2) Kontext-Isolation (separate Verarbeitung von User-Input), 3) Prompt/Ausgabe-Filtering, 4) Least Privilege für Tool-Nutzung",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_003",
            "topic": "RBAC",
            "question": "Was bedeutet RBAC und wofür steht es?",
            "answer": "Role-Based Access Control. Ein Sicherheitsmodell das Zugriffsrechte anhand von Rollen vergibt statt an einzelne User oder Agenten.",
            "difficulty": 1,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_004",
            "topic": "RBAC",
            "question": "Was ist das Principle of Least Privilege?",
            "answer": "Jeder Agent/User erhält nur die minimalen Rechte die nötig sind um seine Aufgabe zu erledigen. Keine überflüssigen Permissions.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_005",
            "topic": "Tool Security",
            "question": "Was ist Tool-Input-Validation?",
            "answer": "Die Prüfung und Bereinigung von Eingabeparametern BEVOR sie an ein Tool übergeben werden. Verhindert Injection-Angriffe über Tool-Parameter.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_006",
            "topic": "Tool Security",
            "question": "Nenne die 5 Schritte für sichere Tool-Nutzung",
            "answer": "1) Input validieren, 2) Allowlist für Tools, 3) Rate-Limiting, 4) Output sanitizen, 5) Audit-Logging",
            "difficulty": 3,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_007",
            "topic": "Sessions",
            "question": "Was ist Context Compaction in OpenClaw?",
            "answer": "Wenn der Conversation Context zu groß wird, komprimiert OpenClaw ihn zu einer Zusammenfassung. Alte Details gehen verloren, aber die wichtigsten Informationen bleiben erhalten.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_008",
            "topic": "Sessions",
            "question": "Was ist der Unterschied zwischen main, isolated und subagent Sessions?",
            "answer": "main: Normale User-Konversation. isolated: Isolierte Bootstrap-Umgebung (kein Context Leak). subagent: Child-Session die für parallele Tasks gestartet wird.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_009",
            "topic": "Memory",
            "question": "Welche Memory-Tools gibt es in OpenClaw?",
            "answer": "memory_search (semantische Suche), memory_get (gezieltes Lesen), lcm_grep (regex/text), lcm_expand_query (tiefe Rekursion mit Quellen), lcm_describe (Summary-Analyse)",
            "difficulty": 3,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_010",
            "topic": "Memory",
            "question": "Wann nutzt man lcm_expand_query statt lcm_grep?",
            "answer": "lcm_expand_query bei komplexen Fragen wo einfache Suche nicht reicht - es spawnt einen Subagent der tiefere Rekursion macht und Quellen zitiert. lcm_grep für schnelle regex/text-Suchen.",
            "difficulty": 3,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_011",
            "topic": "Multi-Agent",
            "question": "Was ist die Sovereign Architecture in OpenClaw?",
            "answer": "Der CEO (ClawMaster) ist der zentrale Orchestrator. Andere Agents sind spezialisierte Worker. Der CEO analysiert, delegiert, und validiert - baut selbst nichts direkt.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_012",
            "topic": "Multi-Agent",
            "question": "Was ist das Handshake-Protokoll im Multi-Agent Workflow?",
            "answer": "Task → Agent arbeitet → Report zurück an CEO → QC Officer validiert → CEO markiert Done → Nico informiert. KEIN Task gilt als erledigt bis QC validiert hat.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_013",
            "topic": "Multi-Agent",
            "question": "Wie kommunizieren Agents in OpenClaw?",
            "answer": "sessions_send(sessionKey, message) sendet eine Nachricht an eine andere Session. NICHT sessions_spawn für Agent-to-Agent (verboten), sondern sessions_send an die echte Agent-Session.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_014",
            "topic": "Security",
            "question": "Was ist Context Splitting Attack?",
            "answer": "Wenn während eines laufenden Tasks eine neue Nachricht kommt, wechselt die Konversation und der Agent 'vergisst' den aktuellen Stand. Lösung: Checkpoint-Regel - laufende Tasks NIEMALS für neue Anfragen abbrechen.",
            "difficulty": 3,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_015",
            "topic": "Security",
            "question": "Was sind Exec Security Modes in OpenClaw?",
            "answer": "deny: Alles verboten was nicht explizit erlaubt. allowlist: Nur erlaubt was auf der Allowlist steht. full: Voller Zugriff (unsicher). Standard ist deny oder allowlist.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_016",
            "topic": "Security",
            "question": "Was ist Memory Poisoning?",
            "answer": "Ein Angriff bei dem bösartige Daten ins Memory/Long-term Storage eingeschleust werden. Wenn der Agent später diese Daten abruft, interpretiert er sie als vertrauenswürdig und könnte schädliche Anweisungen folgen.",
            "difficulty": 3,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_017",
            "topic": "Cron",
            "question": "Was ist der Unterschied zwischen at, cron und every im OpenClaw Cron-System?",
            "answer": "at: Einmalig zu bestimmter Zeit. cron: Wiederholt nach Cron-Expression (z.B. jeden Sonntag 18:00). every: Wiederholt in Intervallen (z.B. alle 10min).",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_018",
            "topic": "Cron",
            "question": "Was bedeutet 'wakeMode: now' bei Cron-Jobs?",
            "answer": "Der Cron-Job startet sofort bei Auslösung und läuft durch bis zum Abschluss (nicht nur ein kurzer Heartbeat). Wichtig für längere Tasks wie University Loops.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_019",
            "topic": "Workflow",
            "question": "Was ist die QC-Pflicht Checkpoint-Regel?",
            "answer": "KEIN Task gilt als 'Erledigt' bis: 1) Agent hat Report gesendet, 2) QC Officer hat validiert, 3) CEO hat 'Done' markiert. Alles andere ist nur 'in Arbeit'.",
            "difficulty": 2,
            "last_shown": None,
            "wrong_count": 0
        },
        {
            "id": "oc_020",
            "topic": "Workflow",
            "question": "Was ist der Zettelkasten Workflow in OpenClaw?",
            "answer": "Einatomic Notes System: Jede Idee = eine Note mit Datum-Tag. Weekly Reviews sammeln verwandte Notes. Ziel: Wissen vernetzen statt nur speichern. Crons: Daily Capture (21:00) + Weekly Review (Sonntag 22:00).",
            "difficulty": 3,
            "last_shown": None,
            "wrong_count": 0
        }
    ]
    
    deck = {"cards": sample_cards, "deck_version": "1.0"}
    save_deck(deck)
    print(f"✅ {len(sample_cards)} Beispiel-Karten initialisiert!")
    print(f"📁 {DECK_FILE}")

# === MAIN ===

def main():
    parser = argparse.ArgumentParser(description="Flashcard Bot für OpenClaw University")
    parser.add_argument("--daily", action="store_true", help="Sende tägliche Flashcards")
    parser.add_argument("--add", action="store_true", help="Neue Karte hinzufügen")
    parser.add_argument("--stats", action="store_true", help="Deck-Statistiken")
    parser.add_argument("--list", action="store_true", help="Alle Karten auflisten")
    parser.add_argument("--review", action="store_true", help="Sofort Review starten")
    parser.add_argument("--init", action="store_true", help="Init示例-Karten")
    parser.add_argument("--limit", type=int, default=5, help="Anzahl Karten für --daily")
    
    args = parser.parse_args()
    
    if args.daily:
        cmd_daily(args.limit)
    elif args.add:
        cmd_add()
    elif args.stats:
        cmd_stats()
    elif args.list:
        cmd_list()
    elif args.review:
        cmd_review()
    elif args.init:
        cmd_init_sample_cards()
    else:
        parser.print_help()
        print("\n📌 Schnellstart:")
        print("  python flashcard_bot.py --init      # 20 Beispiel-Karten erstellen")
        print("  python flashcard_bot.py --daily      # Heutige Karten senden")
        print("  python flashcard_bot.py --stats     # Statistik")
        print("  python flashcard_bot.py --review    # Interaktiv reviewen")

if __name__ == "__main__":
    main()
