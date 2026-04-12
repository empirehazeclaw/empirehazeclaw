#!/usr/bin/env python3
"""
Discord Bot Routing - Konfiguriert wer in welchen Channel postet
"""

import json
import os
from pathlib import Path

# Config File
CONFIG_FILE = Path('/home/clawbot/.openclaw/workspace/memory/discord_routing.json')

# Bot zu Channel Mapping
ROUTING = {
    'trading': {
        'channel': 'trading-signals',
        'channel_id': None,  # Wird automatisch gefüllt
        'script': '/home/clawbot/.openclaw/workspace/scripts/trading_signals.py',
        'cron': '0 8,12,16,20 * * *',  # 4x täglich
        'enabled': True
    },
    'social': {
        'channel': 'social-analytics',
        'channel_id': None,
        'script': '/home/clawbot/.openclaw/workspace/scripts/social_auto_poster.py',
        'cron': '0 6,12,18 * * *',  # 3x täglich
        'enabled': True
    },
    'health': {
        'channel': 'system-health',
        'channel_id': None,
        'script': '/home/clawbot/.openclaw/workspace/scripts/health_monitor.py',
        'cron': '*/15 * * * *',  # Alle 15 min
        'enabled': True
    },
    'ebook': {
        'channel': 'ebook-chatbot',
        'channel_id': None,
        'script': '/home/clawbot/.openclaw/workspace/scripts/ebook_generator.py',
        'cron': '0 9 * * *',  # Täglich
        'enabled': False  # Noch nicht aktiv
    },
    'dialekt': {
        'channel': 'chat-bot-dialekt',
        'channel_id': None,
        'script': '/home/clawbot/.openclaw/workspace/scripts/chatbot_dialekt.py',
        'cron': '0 10,15,20 * * *',  # 3x täglich
        'enabled': True
    },
    'coder': {
        'channel': 'code-reviews',
        'channel_id': None,
        'script': '/home/clawbot/.openclaw/workspace/scripts/code_reviewer.py',
        'cron': '0 8 * * *',  # Täglich morgens
        'enabled': False
    },
    'memory': {
        'channel': 'memory',
        'channel_id': None,
        'script': '/home/clawbot/.openclaw/workspace/scripts/memory_updater.sh',
        'cron': '0 4 * * *',  # Täglich
        'enabled': True
    }
}

# Discord Channel IDs (aus previous scan)
CHANNEL_IDS = {
    'trading-signals': '1479515300222472202',  # trading-bot
    'social-analytics': '1478833343326978059',  # social-agent
    'system-health': '1478831287698460725',    # summary
    'todo': '1478675903977623633',            # tasks
    'ebook-chatbot': '1479486398552739941',    # ebooks
    'chat-bot-dialekt': '1480249786090131497',
    'code-reviews': '1478506849941590149',    # coder
    'memory': '1479011082256253031',           # librarian
    'daily-summary': '1478831287698460725'    # summary
}

def save_routing():
    """Speichere Routing Config"""
    # IDs eintragen
    for bot, config in ROUTING.items():
        channel_name = config['channel']
        if channel_name in CHANNEL_IDS:
            config['channel_id'] = CHANNEL_IDS[channel_name]
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            'routing': ROUTING,
            'channel_ids': CHANNEL_IDS
        }, f, indent=2)
    
    print(f"✅ Routing gespeichert: {CONFIG_FILE}")

def generate_cron_jobs():
    """Generiere Crons für alle Bots"""
    crons = []
    
    for bot, config in ROUTING.items():
        if not config.get('enabled', False):
            continue
            
        cron = config.get('cron', '')
        script = config.get('script', '')
        channel = config.get('channel', '')
        
        if cron and script:
            # Cron Job erstellen
            job = f"{cron} cd /home/clawbot/.openclaw/workspace && python3 {script} >> logs/{bot}_output.log 2>&1"
            crons.append((bot, job, channel))
    
    return crons

def main():
    print("🎛 Discord Bot Routing Setup")
    print("=" * 40)
    
    # Routing speichern
    save_routing()
    
    # Crons generieren
    crons = generate_cron_jobs()
    
    print("\n📋 Bot Routing:")
    for bot, cron, channel in crons:
        print(f"\n🤖 {bot.title()}")
        print(f"   Channel: #{channel}")
        print(f"   Cron: {cron}")
    
    # Routing Tabelle
    print("\n" + "=" * 40)
    print("📊 Routing Übersicht:")
    print("| Bot | Channel | Cron | Status |")
    print("|-----|---------|------|--------|")
    for bot, config in ROUTING.items():
        channel = config.get('channel', '-')
        cron = config.get('cron', '-')
        status = '✅' if config.get('enabled', False) else '❌'
        print(f"| {bot} | #{channel} | {cron} | {status} |")
    
    return ROUTING

if __name__ == '__main__':
    main()
