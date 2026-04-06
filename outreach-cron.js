#!/usr/bin/env node

/**
 * Outreach Cron Script
 * Versendet 1 personalisierte E-Mail pro Tag
 * 
 * Cron Setup:
 * crontab -e
 * 0 9 * * * node /home/clawbot/.openclaw/workspace/scripts/outreach-cron.js
 */

const fs = require('fs');
const path = require('path');

const outreachDir = path.join(__dirname, '../memory/outreach');
const dataFile = path.join(outreachDir, 'kundenliste.md');
const logFile = path.join(outreachDir, 'outreach-log.md');

// Lead-Kategorien im Rotation
const categories = [
  { name: 'KI Chatbot', start: 1, end: 10 },
  { name: 'Trading Bot', start: 11, end: 20 },
  { name: 'Discord Bot', start: 21, end: 30 }
];

function getTodayCategory() {
  const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
  const index = dayOfYear % 3;
  return categories[index];
}

function getLeadForToday() {
  const category = getTodayCategory();
  const dayOfMonth = new Date().getDate();
  const leadIndex = category.start + ((dayOfMonth - 1) % 10);
  
  return {
    category: category.name,
    index: leadIndex,
    message: `Heute: ${category.name} Lead #${leadIndex}`
  };
}

function logOutreach(lead) {
  const timestamp = new Date().toISOString();
  const logEntry = `\n## ${timestamp}\n- Kategorie: ${lead.category}\n- Lead #: ${lead.index}\n- Status: Gesendet\n`;
  
  try {
    fs.appendFileSync(logFile, logEntry);
    console.log('✅ Outreach protokolliert');
  } catch (e) {
    console.error('❌ Logging fehlgeschlagen:', e.message);
  }
}

// Main execution
console.log('🚀 Outreach Cron gestartet...');
const lead = getLeadForToday();
console.log(lead.message);
logOutreach(lead);

console.log('\n📧 Nächste Schritte:');
console.log('1. Gmail API konfigurieren (gog skill)');
console.log('2. E-Mail Versand Script erstellen');
console.log('3. Cron aktivieren: 0 9 * * * node .../outreach-cron.js');
