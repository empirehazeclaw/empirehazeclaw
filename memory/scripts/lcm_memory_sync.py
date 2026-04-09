#!/usr/bin/env python3
"""
LCM ↔ MEMORY.md Sync Script v2
Extracts key decisions from LosslessClaw summaries and syncs to MEMORY.md
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_PATH = Path("/home/clawbot/.openclaw/workspace/memory/MEMORY.md")
LCM_DB = Path("/home/clawbot/.openclaw/lcm.db")
STATE_FILE = Path("/home/clawbot/.openclaw/workspace/memory/.sync_state.json")

def get_all_summaries():
    """Get all summaries, sorted by created_at desc"""
    conn = sqlite3.connect(str(LCM_DB))
    c = conn.cursor()
    c.execute("""
        SELECT summary_id, content, created_at, conversation_id, kind
        FROM summaries
        ORDER BY created_at DESC
    """)
    return c.fetchall()

def extract_key_decisions(content):
    """Extract lines that look like decisions/actions"""
    decisions = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if any(marker in line for marker in ['✅', '🔴', '⚠️', '**', 'Decision:', 'Action:', '→', '✔']):
            clean = line.replace('**', '').replace('✅', '').replace('🔴', '').replace('⚠️', '').replace('✔', '').strip()
            if len(clean) > 10 and len(clean) < 300:
                decisions.append(clean)
    return decisions[:3]  # Max 3 per summary

def get_last_sync_id():
    """Get last synced summary_id from state file"""
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            return state.get('last_summary_id', None)
        except:
            return None
    return None

def save_sync_state(last_id, count):
    """Save sync state"""
    state = {
        'last_summary_id': last_id,
        'synced_count': count,
        'last_sync': datetime.now().isoformat()
    }
    STATE_FILE.write_text(json.dumps(state, indent=2))

def sync_to_memory():
    """Main sync function"""
    print(f"🔄 LCM → MEMORY sync starting...")
    
    summaries = get_all_summaries()
    print(f"📊 Found {len(summaries)} total summaries in LCM DB")
    
    last_synced = get_last_sync_id()
    print(f"📍 Last synced summary_id: {last_synced}")
    
    # Find index of last synced
    start_idx = 0
    if last_synced:
        for i, (sid, *_) in enumerate(summaries):
            if sid == last_synced:
                start_idx = i + 1
                break
    
    # Get new summaries since last sync
    new_summaries = summaries[start_idx:]
    print(f"📥 {len(new_summaries)} new summaries to process")
    
    all_decisions = []
    for summary_id, content, created, conv_id, kind in new_summaries:
        decisions = extract_key_decisions(content)
        for d in decisions:
            all_decisions.append((created[:10], d))
    
    if not all_decisions:
        print("ℹ️ No new decisions to sync")
        return 0
    
    # Read existing MEMORY.md or create new
    if MEMORY_PATH.exists():
        memory_content = MEMORY_PATH.read_text()
    else:
        memory_content = "# MEMORY.md - Fleet Central Memory\n\n"
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    decisions_section = f"\n## 📌 Recent Decisions ({now})\n\n"
    decisions_section += f"*(Synced from {len(new_summaries)} LCM summaries)*\n\n"
    
    for date_short, decision in all_decisions[:20]:  # Max 20 decisions
        decisions_section += f"- [{date_short}] {decision}\n"
    
    decisions_section += "\n---\n"
    
    # Prepend to memory (not append - newest first)
    memory_content = memory_content + decisions_section
    MEMORY_PATH.write_text(memory_content)
    
    # Save state
    if new_summaries:
        save_sync_state(new_summaries[0][0], len(all_decisions))
    
    print(f"✅ Synced {len(all_decisions)} decisions to MEMORY.md")
    return len(all_decisions)

if __name__ == "__main__":
    count = sync_to_memory()
    print(f"🎯 Sync complete: {count} items")