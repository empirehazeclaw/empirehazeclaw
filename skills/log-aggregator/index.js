#!/usr/bin/env node

/**
 * 📊 Log Aggregator - Centralized log collection and analysis
 * 
 * Usage:
 *   node index.js --errors [--today|--yesterday|--date YYYY-MM-DD]
 *   node index.js --report [daily|weekly|monthly]
 *   node index.js --trend <days>
 *   node index.js --sources
 *   node index.js --export [learning_loop|debug]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const readline = require('readline');

// Configuration
const HOME = process.env.HOME || '/home/clawbot';
const OPENCLAW_LOGS = path.join(HOME, '.openclaw/logs');
const WORKSPACE = path.join(HOME, '.openclaw/workspace');
const AGGREGATED_DIR = path.join(WORKSPACE, 'memory/logs/aggregated');
const DATA_DIR = path.join(WORKSPACE, 'data');
const LEARNING_LOOP_ERRORS = path.join(DATA_DIR, 'learning_loop/errors_for_analysis.json');

// Error patterns to track
const ERROR_PATTERNS = [
  { pattern: /ECONNREFUSED/, name: 'ECONNREFUSED', description: 'Connection refused - service not running' },
  { pattern: /ENOENT/, name: 'ENOENT', description: 'File or path not found' },
  { pattern: /EACCES/, name: 'EACCES', description: 'Permission denied' },
  { pattern: /ETIMEDOUT|TIMEOUT/i, name: 'TIMEOUT', description: 'Operation timed out' },
  { pattern: /JSON\.parse|JSONError/i, name: 'JSON_PARSE', description: 'Malformed JSON' },
  { pattern: /Permission denied.*socket|socket.*Permission/i, name: 'SOCKET_PERMISSION', description: 'Socket ownership issue' },
  { pattern: /spawn.*ENOENT|Cannot find module/i, name: 'MODULE_NOT_FOUND', description: 'Missing module or command' },
  { pattern: /Cron list timeout/i, name: 'CRON_TIMEOUT', description: 'Cron operation timeout' },
  { pattern: /Error:|Exception|FAILED/i, name: 'GENERAL_ERROR', description: 'General error' }
];

/**
 * Get all log sources
 */
function getLogSources() {
  const sources = [];
  
  // OpenClaw logs
  if (fs.existsSync(OPENCLAW_LOGS)) {
    const files = fs.readdirSync(OPENCLAW_LOGS).filter(f => f.endsWith('.log'));
    for (const file of files) {
      sources.push({ path: path.join(OPENCLAW_LOGS, file), source: 'openclaw', name: file });
    }
  }
  
  // Workspace memory logs
  const memLogs = path.join(WORKSPACE, 'memory/logs');
  if (fs.existsSync(memLogs)) {
    const files = fs.readdirSync(memLogs).filter(f => f.endsWith('.log'));
    for (const file of files) {
      sources.push({ path: path.join(memLogs, file), source: 'memory', name: file });
    }
  }
  
  return sources;
}

/**
 * Read log file and extract entries
 */
function readLogFile(filePath, options = {}) {
  const { from, to, level, limit } = options;
  const entries = [];
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n').filter(l => l.trim());
    
    for (const line of lines) {
      // Try to parse as JSON first
      let entry = { raw: line, message: line };
      
      try {
        const parsed = JSON.parse(line);
        entry = { ...entry, ...parsed, message: parsed.message || parsed.msg || line };
      } catch {
        // Not JSON, extract timestamp and message manually
        const tsMatch = line.match(/^\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})/);
        if (tsMatch) {
          entry.timestamp = tsMatch[1];
        }
        entry.message = line;
      }
      
      // Filter by date range
      if (from && entry.timestamp && entry.timestamp < from) continue;
      if (to && entry.timestamp && entry.timestamp > to) continue;
      
      // Filter by level
      if (level && !line.toLowerCase().includes(level.toLowerCase())) continue;
      
      entries.push(entry);
      
      if (limit && entries.length >= limit) break;
    }
  } catch (e) {
    // File doesn't exist or can't be read
  }
  
  return entries;
}

/**
 * Extract error information from entries
 */
function extractErrors(entries) {
  const errors = [];
  
  for (const entry of entries) {
    const raw = entry.raw || entry.message || '';
    
    for (const { pattern, name, description } of ERROR_PATTERNS) {
      if (pattern.test(raw)) {
        errors.push({
          timestamp: entry.timestamp || new Date().toISOString(),
          pattern: name,
          description: description,
          source: entry.source || 'unknown',
          raw: raw.substring(0, 500)
        });
        break;
      }
    }
  }
  
  return errors;
}

/**
 * Aggregate errors by pattern and source
 */
function aggregateErrors(errors) {
  const byPattern = {};
  const bySource = {};
  const byDate = {};
  
  for (const error of errors) {
    // By pattern
    byPattern[error.pattern] = (byPattern[error.pattern] || 0) + 1;
    
    // By source
    bySource[error.source] = (bySource[error.source] || 0) + 1;
    
    // By date
    const date = error.timestamp ? error.timestamp.split('T')[0] : 'unknown';
    byDate[date] = (byDate[date] || 0) + 1;
  }
  
  return { byPattern, bySource, byDate, total: errors.length };
}

/**
 * Get errors for specific date(s)
 */
function getErrors(options = {}) {
  const { date, days = 1 } = options;
  let sources = getLogSources();
  const errors = [];
  
  const targetDate = date || new Date().toISOString().split('T')[0];
  
  for (const source of sources) {
    const entries = readLogFile(source.path, { limit: 1000 });
    const sourceErrors = extractErrors(entries).map(e => ({ ...e, source: source.name }));
    
    // Filter by date
    const filtered = sourceErrors.filter(e => 
      e.timestamp && e.timestamp.startsWith(targetDate)
    );
    
    errors.push(...filtered);
  }
  
  return errors;
}

/**
 * Generate daily report
 */
function generateDailyReport(date) {
  const errors = getErrors({ date });
  const aggregated = aggregateErrors(errors);
  
  // Get sources
  const sources = getLogSources();
  
  let report = `## 📊 Log Summary - ${date}\n\n`;
  report += `### Errors: ${aggregated.total}\n\n`;
  
  if (aggregated.total === 0) {
    report += `✅ No errors detected!\n`;
    return report;
  }
  
  // Top patterns
  const sortedPatterns = Object.entries(aggregated.byPattern)
    .sort((a, b) => b[1] - a[1]);
  
  report += `### Top Patterns\n`;
  for (const [pattern, count] of sortedPatterns.slice(0, 5)) {
    report += `- ${pattern}: ${count}\n`;
  }
  
  // Top sources
  report += `\n### By Source\n`;
  for (const [source, count] of Object.entries(aggregated.bySource)) {
    report += `- ${source}: ${count}\n`;
  }
  
  // New patterns (simple heuristic: errors with general_error that have unique messages)
  const generalErrors = errors.filter(e => e.pattern === 'GENERAL_ERROR');
  const uniqueMessages = [...new Set(generalErrors.map(e => e.raw.substring(0, 100)))];
  
  if (uniqueMessages.length > 0) {
    report += `\n### Notable Errors\n`;
    for (const msg of uniqueMessages.slice(0, 3)) {
      report += `\`\`\`\n${msg}\n\`\`\`\n`;
    }
  }
  
  return report;
}

/**
 * Export errors for learning loop
 */
function exportForLearningLoop() {
  const today = new Date().toISOString().split('T')[0];
  const errors = getErrors({ date: today });
  
  const exportData = {
    date: today,
    total: errors.length,
    by_pattern: aggregateErrors(errors).byPattern,
    errors: errors.slice(0, 50), // Limit to 50 most recent
    exported_at: new Date().toISOString()
  };
  
  // Ensure directory exists
  fs.mkdirSync(path.dirname(LEARNING_LOOP_ERRORS), { recursive: true });
  fs.writeFileSync(LEARNING_LOOP_ERRORS, JSON.stringify(exportData, null, 2));
  
  console.log(`📤 Exported ${errors.length} errors to ${LEARNING_LOOP_ERRORS}`);
  return exportData;
}

/**
 * Show log sources
 */
function showSources() {
  const sources = getLogSources();
  
  let report = `## 📁 Log Sources\n\n`;
  report += `| Source | File | Size | Modified |\n|--------|------|------|----------|\n`;
  
  for (const source of sources) {
    try {
      const stat = fs.statSync(source.path);
      const size = formatBytes(stat.size);
      const mtime = stat.mtime.toISOString().split('T')[0];
      report += `| ${source.source} | ${source.name} | ${size} | ${mtime} |\n`;
    } catch {
      report += `| ${source.source} | ${source.name} | ? | ? |\n`;
    }
  }
  
  return report;
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
  return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
📊 Log Aggregator - Centralized log analysis

Usage:
  node index.js --sources           Show all log sources
  node index.js --errors [--today]  Show errors (default: today)
  node index.js --report [daily]    Generate daily summary
  node index.js --trend <days>      Show error trends
  node index.js --export [learning_loop]  Export for learning loop

Examples:
  node index.js --sources
  node index.js --errors --today
  node index.js --report daily
  node index.js --trend 7
  node index.js --export learning_loop
`);
    process.exit(0);
  }
  
  if (args.includes('--sources')) {
    console.log(showSources());
    process.exit(0);
  }
  
  if (args.includes('--errors')) {
    const today = new Date().toISOString().split('T')[0];
    const errors = getErrors({ date: today });
    const aggregated = aggregateErrors(errors);
    
    console.log(`\n## 🐛 Errors for ${today}\n`);
    console.log(`Total: ${aggregated.total}\n`);
    
    if (aggregated.total > 0) {
      console.log('By Pattern:');
      for (const [p, c] of Object.entries(aggregated.byPattern)) {
        console.log(`  ${p}: ${c}`);
      }
      console.log('\nBy Source:');
      for (const [s, c] of Object.entries(aggregated.bySource)) {
        console.log(`  ${s}: ${c}`);
      }
    }
    process.exit(0);
  }
  
  if (args.includes('--report')) {
    const today = new Date().toISOString().split('T')[0];
    console.log(generateDailyReport(today));
    process.exit(0);
  }
  
  if (args.includes('--trend')) {
    const idx = args.indexOf('--trend');
    const days = parseInt(args[idx + 1] || '7');
    
    console.log(`\n## 📈 Error Trends (Last ${days} days)\n`);
    
    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const errors = getErrors({ date: dateStr });
      const total = errors.length;
      
      const bar = '█'.repeat(Math.min(total, 20)) + '░'.repeat(Math.max(0, 20 - total));
      console.log(`${dateStr}: ${total.toString().padStart(3)} ${bar}`);
    }
    process.exit(0);
  }
  
  if (args.includes('--export')) {
    const idx = args.indexOf('--export');
    const target = args[idx + 1] || 'learning_loop';
    
    if (target === 'learning_loop') {
      exportForLearningLoop();
    } else {
      console.error(`Unknown export target: ${target}`);
      process.exit(1);
    }
    process.exit(0);
  }
  
  // Default: show summary
  const today = new Date().toISOString().split('T')[0];
  console.log(showSources());
  console.log('\n' + generateDailyReport(today));
}

main().catch(console.error);
