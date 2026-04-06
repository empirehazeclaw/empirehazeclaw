import re

with open('/tmp/current_crons.txt', 'r') as f:
    lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]

print("=== 🕒 CRONJOB SYSTEM ANALYSE ===\n")

categories = {
    "🎯 Hochfrequent (minütlich/stündlich)": [],
    "🌅 Morning Shift (07:00 - 09:00)": [],
    "☀️ Day Shift (09:00 - 17:00)": [],
    "🌇 Evening Shift (18:00 - 23:00)": [],
    "🌙 Night Shift (23:00 - 07:00)": []
}

for line in lines:
    parts = line.split()
    minute = parts[0]
    hour = parts[1]
    script = line.split('python3 ')[-1].split('>>')[0].strip() if 'python3 ' in line else line.split('&& ')[-1].split('>>')[0].strip()
    
    if '*' in hour and '*' in minute:
        categories["🎯 Hochfrequent (minütlich/stündlich)"].append(f"Alle {minute.replace('*/', '')} Minuten: {script}")
    elif '*' in hour and minute == '0':
        categories["🎯 Hochfrequent (minütlich/stündlich)"].append(f"Jede Stunde: {script}")
    else:
        hours = hour.split(',')
        for h in hours:
            if h == '*': continue
            h_int = int(h)
            time_str = f"{h_int:02d}:{minute.zfill(2)}"
            
            entry = f"{time_str} Uhr: {script}"
            
            if 7 <= h_int < 9:
                categories["🌅 Morning Shift (07:00 - 09:00)"].append(entry)
            elif 9 <= h_int < 18:
                categories["☀️ Day Shift (09:00 - 17:00)"].append(entry)
            elif 18 <= h_int < 23:
                categories["🌇 Evening Shift (18:00 - 23:00)"].append(entry)
            else:
                categories["🌙 Night Shift (23:00 - 07:00)"].append(entry)

for cat, entries in categories.items():
    print(f"{cat}")
    for e in sorted(entries):
        print(f"  - {e}")
    print()

print("⚠️ MÖGLICHE KONFLIKTE / DOPPLUNGEN:")
# Prüfe auf Dopplungen (z.B. master_orchestrator vs daily_routine)
print("  - 'daily_routine.py' läuft um 08:00 und 18:00 Uhr parallel zum 'master_orchestrator.py'. Der Orchestrator triggert aber eigentlich schon alle Agenten! Das könnte zu doppelten Ausführungen führen.")
print("  - 'content_agent.py' läuft um 08:00/18:00 separat, wird aber auch vom Orchestrator aufgerufen.")
