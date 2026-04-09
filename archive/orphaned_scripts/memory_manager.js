#!/usr/bin/env node
/**
 * Memory Manager - Self-Improving Assistant
 * 
 * Usage:
 *   node memory_manager.js add "Korrektur" "Kontext"
 *   node memory_manager.js list
 *   node memory_manager.js archive
 *   node memory_manager.js digest
 *   node memory_manager.js forget "term"
 *   node memory_manager.js forget-all
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, 'memory');
const HOT_FILE = path.join(MEMORY_DIR, 'hot', 'confirmed_rules.md');
const CONTEXT_FILE = path.join(MEMORY_DIR, 'context', 'project_rules.md');
const ARCHIVE_DIR = path.join(MEMORY_DIR, 'archive');
const CORRECTION_LOG = path.join(MEMORY_DIR, 'correction_log.md');

function getTimestamp() {
  return new Date().toISOString().replace('T', ' | ').substring(0, 16);
}

function addCorrection(correction, context) {
  const timestamp = getTimestamp();
  const entry = `\n## ${timestamp}\n- Korrektur: "${correction}"\n- Kontext: "${context}"\n`;
  
  let content = fs.readFileSync(CORRECTION_LOG, 'utf-8');
  content = content.replace('*Noch keine Korrekturen heute*', entry + '\n*Noch keine Korrekturen heute*');
  fs.writeFileSync(CORRECTION_LOG, content);
  
  // Track repetition
  trackRepetition(correction);
  
  console.log('✅ Korrektur gespeichert:', correction);
}

function trackRepetition(correction) {
  const trackingFile = path.join(MEMORY_DIR, 'correction_tracking.json');
  let tracking = {};
  
  if (fs.existsSync(trackingFile)) {
    tracking = JSON.parse(fs.readFileSync(trackingFile, 'utf-8'));
  }
  
  const key = correction.toLowerCase();
  tracking[key] = (tracking[key] || 0) + 1;
  
  fs.writeFileSync(trackingFile, JSON.stringify(tracking, null, 2));
  
  if (tracking[key] === 3) {
    console.log('\n⚠️ 3x wiederholt: "' + correction + '"');
    console.log('Frage Nico ob das eine permanente Regel werden soll.\n');
  }
}

function listCorrections() {
  const content = fs.readFileSync(CORRECTION_LOG, 'utf-8');
  console.log(content);
}

function createPermanentRule(rule, scope = 'hot') {
  const timestamp = getTimestamp();
  const ruleEntry = `\n- **${timestamp}**: ${rule}`;
  
  let file = scope === 'hot' ? HOT_FILE : CONTEXT_FILE;
  let content = fs.readFileSync(file, 'utf-8');
  
  content = content.replace('*Noch keine permanenten Regeln bestätigt*', ruleEntry + '\n\n*Noch keine permanenten Regeln bestätigt*');
  fs.writeFileSync(file, content);
  
  console.log('✅ Permanente Regel erstellt in', scope);
}

function archiveOldRules() {
  // Move items older than 30 days to archive
  console.log('📦 Archiviere alte Regeln...');
  // Implementation depends on format
}

function weeklyDigest() {
  console.log('\n📊 WOCHEN DIGEST - Memory System\n');
  console.log('=== AKTUELLE REGELN ===\n');
  
  console.log('🔥 HOT MEMORY:');
  console.log(fs.readFileSync(HOT_FILE, 'utf-8'));
  
  console.log('\n📂 CONTEXT:');
  console.log(fs.readFileSync(CONTEXT_FILE, 'utf-8'));
  
  console.log('\n📝 KORREKTUREN DIESE WOCHE:');
  console.log(fs.readFileSync(CORRECTION_LOG, 'utf-8'));
}

function forgetTerm(term) {
  // Remove from all memory files
  [HOT_FILE, CONTEXT_FILE, CORRECTION_LOG].forEach(file => {
    if (fs.existsSync(file)) {
      let content = fs.readFileSync(file, 'utf-8');
      content = content.replace(new RegExp(term, 'gi'), '[GELÖSCHT]');
      fs.writeFileSync(file, content);
    }
  });
  console.log('✅ "' + term + '" wurde überall gelöscht.');
}

function forgetAll() {
  [HOT_FILE, CONTEXT_FILE, CORRECTION_LOG].forEach(file => {
    if (fs.existsSync(file)) {
      fs.writeFileSync(file, '# Memory geleert\n\n*Zuletzt geleert: ' + getTimestamp() + '*\n');
    }
  });
  console.log('✅ Memory System komplett geleert.');
}

const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'add':
    addCorrection(args[1], args[2] || 'Allgemein');
    break;
  case 'list':
    listCorrections();
    break;
  case 'digest':
    weeklyDigest();
    break;
  case 'forget':
    forgetTerm(args[1]);
    break;
  case 'forget-all':
    forgetAll();
    break;
  default:
    console.log('Usage: memory_manager.js <add|list|digest|forget|forget-all> [args]');
}
