#!/usr/bin/env python3
"""
Knee Exercise Bundle - Tägliche Erinnerungen
Prüft ob Training heute nötig + erinnert stündlich
"""

import subprocess
import sys
from datetime import datetime

def check_and_remind():
    """Prüfe ob Knie-Training heute"""
    # Trainingstage: Mo(0), Mi(2), Fr(4)
    today = datetime.now().weekday()
    training_days = [0, 2, 4]  # Monday, Wednesday, Friday
    
    if today in training_days:
        print("🦵 Heute ist Knie-Trainingstag!")
        print("\n📋 Übungen:")
        print("  1. Kniebeugen (3x12)")
        print("  2. Ausfallschritte (3x10)")
        print("  3. Plank (3x30s)")
        print("  4. Wand-Winkelhocke (3x45s)")
        
        # Dann Reminder alle Stunde bis 13:00
        hour = datetime.now().hour
        if hour < 13:
            return f"🦵 Knie-Training jetzt machen! Du hast noch bis {13-hour}h."
        else:
            return "🦵 Training heute nicht vergessen!"
    else:
        day_names = ["Montag", "Dienstag", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        next_training = [d for d in training_days if d > today]
        next_day = next_training[0] if next_training else training_days[0]
        return f"🦵 Nächster Trainingstag: {day_names[next_day]}"

def main():
    msg = check_and_remind()
    print(msg)
    return 0

if __name__ == "__main__":
    sys.exit(main())
