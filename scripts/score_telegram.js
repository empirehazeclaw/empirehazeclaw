#!/usr/bin/env node
/**
 * AI-powered Telegram Message Filter v3
 * Scores 634 messages for importance, relevance, uniqueness
 */

const fs = require('fs');

// Load the messages
const data = JSON.parse(fs.readFileSync('/home/clawbot/.openclaw/workspace/data/telegram_important.json', 'utf8'));
const messages = data.messages;

console.log(`Loaded ${messages.length} messages`);

// ─── DATE THRESHOLDS ─────────────────────────────────────────────────────────
const RECENT_CUTOFF = new Date('2026-03-25');  // Last 2 weeks (most important)
const MID_CUTOFF = new Date('2026-03-10');     // Last month (still relevant)
const OLD_CUTOFF = new Date('2026-03-01');     // Before March = potentially outdated

// ─── TEXT HELPERS ───────────────────────────────────────────────────────────
function normalize(text) {
  return text.toLowerCase().replace(/[^\w\s]/g, ' ').substring(0, 200);
}

function getFingerprint(text) {
  return normalize(text).replace(/\s+/g, ' ').trim();
}

function wordCount(text) {
  return text.split(/\s+/).filter(w => w.length > 2).length;
}

function isOutdated(timestamp) {
  try {
    return new Date(timestamp.replace(' ', 'T')) < OLD_CUTOFF;
  } catch {
    return false;
  }
}

function isRecent(timestamp) {
  try {
    return new Date(timestamp.replace(' ', 'T')) >= RECENT_CUTOFF;
  } catch {
    return false;
  }
}

// ─── DUPLICATE DETECTION ────────────────────────────────────────────────────
const fpMap = new Map();
messages.forEach((msg, idx) => {
  const fp = getFingerprint(msg.text);
  if (!fpMap.has(fp)) fpMap.set(fp, []);
  fpMap.get(fp).push(idx);
});

// ─── AGE SCORE ──────────────────────────────────────────────────────────────
function getAgeScore(timestamp) {
  try {
    const msgDate = new Date(timestamp.replace(' ', 'T'));
    if (msgDate >= RECENT_CUTOFF) return 3;   // Very recent
    if (msgDate >= MID_CUTOFF) return 1;       // Recent enough
    if (msgDate >= OLD_CUTOFF) return 0;       // Getting old
    return -2;                                  // Old (before March)
  } catch {
    return 0;
  }
}

// ─── MAIN SCORING ───────────────────────────────────────────────────────────
function scoreMessage(msg) {
  let importance = 5;
  let relevance = 5;
  let uniqueness = 5;
  
  const text = msg.text;
  const fp = getFingerprint(msg.text);
  const isJson = text.trim().startsWith('{');
  const isLong = text.length > 600;
  const isVeryLong = text.length > 1500;
  const categories = msg.categories || [];
  const timestamp = msg.timestamp || '';
  const fpDupCount = fpMap.get(fp).length - 1;
  const msgDate = new Date(timestamp.replace(' ', 'T'));
  
  // ════════════════════════════════════════════════════════════
  // IMPORTANCE (0-10)
  // ════════════════════════════════════════════════════════════
  {
    let score = 5;
    
    // ── JSON / Structured Configs ──
    if (isJson) {
      if (/system_name|design_principles|core_components/i.test(text)) {
        score = 9.5;  // Core architecture
      } else if (/godmode|trading_stack|market_scan|black_swan/i.test(text)) {
        score = 9.0;  // Trading system spec
      } else if (/"api_key"|"token"|"secret"|environment/i.test(text)) {
        score = 8.5;  // Credentials config
      } else if (/"skill"|"agent"|"memory"/i.test(text)) {
        score = 8.0;  // Skill/agent config
      } else {
        score = 7.0;  // Other JSON
      }
    }
    
    // ── Non-JSON Text ──
    else {
      // Very short (< 25 chars) → rarely important
      if (text.length < 25) {
        score = 2.5;
        if (/^(action|decision|task):/i.test(text)) score = 6;
      }
      // Short (25-100 chars)
      else if (text.length < 100) {
        score = 4.5;
        if (/entscheidung|beschlossen|architecture/i.test(text)) score += 2;
        if (/^(action|decision|task):/i.test(text)) score += 1.5;
        if (/kosten|€|budget|pricing/i.test(text)) score += 1;
        if (/^danke( schon)?$|^mach ich$|^erledigt$/i.test(text)) score = 2;
      }
      // Medium (100-500 chars)
      else if (text.length < 500) {
        score = 5.5;
        if (/entscheidung|beschlossen|strategy|roadmap/i.test(text)) score += 2;
        if (/revenue|kunde|lead|sales|umsatz/i.test(text)) score += 2;
        if (/architecture|system|agent|skill/i.test(text)) score += 1.5;
        if (/server|vps|docker|nginx|hosting/i.test(text)) score += 1;
        if (/learned|lesson|pattern|insight/i.test(text)) score += 1;
        if (/error|bug|fix|issue|problem/i.test(text)) score += 0.5;
      }
      // Long (500-1500 chars)
      else if (text.length < 1500) {
        score = 6.5;
        if (/revenue|business|kunde|sales/i.test(text)) score += 2.5;
        if (/strategy|roadmap|plan|vision/i.test(text)) score += 2;
        if (/architecture|system|design|agent|skill/i.test(text)) score += 2;
        if (/learned|lesson|pattern|insight|erkenntnis/i.test(text)) score += 1.5;
        if (/error|bug|fix|issue/i.test(text)) score += 0.5;
      }
      // Very long (> 1500 chars)
      else {
        score = 7.0;
        // Long content about business = very important
        if (/revenue|kunde|lead|business/i.test(text)) score += 2;
        if (/strategy|vision|goal/i.test(text)) score += 1.5;
        if (/learned|insight|pattern|erkenntnis/i.test(text)) score += 1;
      }
    }
    
    // Category boosts
    if (categories.includes('decision')) score += 0.3;
    
    importance = Math.max(0, Math.min(10, score));
  }
  
  // ════════════════════════════════════════════════════════════
  // RELEVANCE (0-10) — is it still current?
  // ════════════════════════════════════════════════════════════
  {
    let score = 5;
    
    // Age factor
    score += getAgeScore(timestamp);
    
    // Very recent gets extra boost
    if (isRecent(timestamp)) {
      score += 1;
      if (/heute|jetzt|gerade|sofort|gerade eben/i.test(text)) score += 0.5;
    }
    
    // Old (pre-March) gets penalty
    if (isOutdated(timestamp)) {
      // Architectural decisions from old times might still matter
      if (isJson && /architecture|design_principles|core_components/i.test(text)) {
        score = 5; // Architectural decisions age well
      }
      // GodMode trading spec - still relevant
      else if (isJson && /godmode|trading/i.test(text)) {
        score = 4.5;
      }
      // Otherwise old = less relevant
      else {
        score = Math.max(2, score);
      }
    }
    
    // API key contexts
    if (categories.includes('api_key')) {
      if (/expired|revoked|old version/i.test(text)) score -= 2;
    }
    
    relevance = Math.max(0, Math.min(10, score));
  }
  
  // ════════════════════════════════════════════════════════════
  // UNIQUENESS (0-10) — is it new info?
  // ════════════════════════════════════════════════════════════
  {
    let score = 7;
    
    // Exact duplicates
    if (fpDupCount > 0) {
      score -= fpDupCount * 2;
    }
    
    // Very short → usually not unique
    if (text.length < 25) score -= 1.5;
    else if (text.length < 50) score -= 0.5;
    
    // Long substantive content
    if (isVeryLong) score += 0.5;
    
    // Contains specific data
    if (/\bhttps?:\/\/\S{10,}/i.test(text)) score += 0.3;
    if (/\b\d{20,}\b/.test(text)) score += 0.3;  // long numbers = IDs, tokens
    if (/€\d+|\$\d+|\d+€/.test(text)) score += 0.3;
    
    uniqueness = Math.max(0, Math.min(10, score));
  }
  
  // ── TOTAL ──
  const total = (
    importance * 0.40 +
    relevance * 0.35 +
    uniqueness * 0.25
  );
  
  return {
    importance: Math.round(importance * 10) / 10,
    relevance: Math.round(relevance * 10) / 10,
    uniqueness: Math.round(uniqueness * 10) / 10,
    total: Math.round(total * 10) / 10
  };
}

// ─── WHY EXPLANATION ────────────────────────────────────────────────────────
function explainWhy(msg, scores) {
  const text = msg.text;
  const cats = msg.categories || [];
  const isJson = text.trim().startsWith('{');
  const t = msg.timestamp || '';
  const isOld = isOutdated(t);
  
  if (scores.total >= 9) {
    if (isJson && /system_name|design_principles|core_components/i.test(text))
      return 'CORE ARCHITECTURE: System design defining agent types, memory, security, data pipeline';
    if (isJson && /godmode|trading_stack/i.test(text))
      return 'TRADING SYSTEM: GodMode architecture spec with €120/month budget, risk settings, components';
    if (/revenue|kunde|lead|sales/i.test(text))
      return 'REVENUE CRITICAL: Content directly about customer acquisition or revenue generation';
    if (/identity|persona|role/i.test(text))
      return 'IDENTITY DEFINITION: ClawMaster persona/role definition with values and rules';
    return 'HIGHEST VALUE: Critical system content, recent and unique';
  }
  
  if (scores.total >= 8) {
    if (isJson) return 'STRUCTURED CONFIG: JSON system configuration with active parameters';
    if (cats.includes('decision')) return 'DECISION: Specific choice affecting current operations';
    if (/learned|lesson|pattern|insight|erkenntnis/i.test(text)) return 'LEARNING: Key insight or pattern affecting our approach';
    if (/server|vps|docker|nginx|hosting/i.test(text)) return 'INFRASTRUCTURE: Server/deployment config (check if still current)';
    if (/skill|agent|memory/i.test(text)) return 'AGENTIC SYSTEM: Skill or agent configuration';
    if (isOld) return `⚠️ OLD but important: ${summarizeTopic(text)}`;
    return 'HIGH VALUE: Important content, still relevant';
  }
  
  if (scores.total >= 7) {
    if (isOld) return `⚠️ OLD: ${summarizeTopic(text)}`;
    if (cats.includes('task')) return `TASK: ${summarizeTopic(text)}`;
    if (cats.includes('learning')) return `LEARNING: ${summarizeTopic(text)}`;
    if (cats.includes('api_key')) return `CONFIG: ${summarizeTopic(text)}`;
    return summarizeTopic(text);
  }
  
  return 'ROUTINE: Lower priority, reference only';
}

function summarizeTopic(text) {
  const cleaned = text.substring(0, 200).replace(/\n+/g, ' ').replace(/\s+/g, ' ').trim();
  return cleaned.length < 150 ? cleaned : cleaned.substring(0, 150) + '...';
}

// ─── MAIN ───────────────────────────────────────────────────────────────────
console.log('\nProcessing messages...\n');

const scored = messages.map(msg => {
  const scores = scoreMessage(msg);
  return {
    ...msg,
    scores,
    score_total: scores.total,
    why: explainWhy(msg, scores)
  };
});

// Filter: truly important (total >= 7)
const IMPORTANT_THRESHOLD = 7;

const topMessages = scored
  .filter(m => m.score_total >= IMPORTANT_THRESHOLD)
  .sort((a, b) => b.score_total - a.score_total);

const importantByCategory = {};
topMessages.forEach(m => {
  (m.categories || []).forEach(cat => {
    if (!importantByCategory[cat]) importantByCategory[cat] = 0;
    importantByCategory[cat]++;
  });
});

const dist = scored.reduce((acc, m) => {
  const t = m.score_total;
  if (t >= 9) acc['9-10']++;
  else if (t >= 8) acc['8-9']++;
  else if (t >= 7) acc['7-8']++;
  else if (t >= 6) acc['6-7']++;
  else if (t >= 5) acc['5-6']++;
  else acc['<5']++;
  return acc;
}, {'9-10':0,'8-9':0,'7-8':0,'6-7':0,'5-6':0,'<5':0});

// Build output
const output = {
  generated_at: new Date().toISOString(),
  top_messages: topMessages.map(m => ({
    id: m.id,
    timestamp: m.timestamp,
    sender: m.sender,
    text: m.text.length > 1200 ? m.text.substring(0, 1200) + '\n...[truncated]' : m.text,
    category: m.categories,
    scores: {
      importance: m.scores.importance,
      relevance: m.scores.relevance,
      uniqueness: m.scores.uniqueness
    },
    score_total: m.score_total,
    why: m.why
  })),
  summary: {
    total_reviewed: messages.length,
    truly_important: topMessages.length,
    threshold: IMPORTANT_THRESHOLD,
    by_category: importantByCategory,
    score_distribution: dist,
    outdated_messages: messages.filter(m => isOutdated(m.timestamp)).length,
    unique_signatures: fpMap.size
  }
};

const outPath = '/home/clawbot/.openclaw/workspace/data/telegram_filtered.json';
fs.writeFileSync(outPath, JSON.stringify(output, null, 2));

// ─── PRINT REPORT ───────────────────────────────────────────────────────────
console.log('╔══════════════════════════════════════════════════════════╗');
console.log('║       TELEGRAM MESSAGE FILTER — FINAL REPORT             ║');
console.log('╚══════════════════════════════════════════════════════════╝\n');
console.log(`Total reviewed:        ${messages.length}`);
console.log(`Truly important:        ${topMessages.length} (score >= ${IMPORTANT_THRESHOLD})`);
console.log(`Outdated (pre-Mar 1):    ${output.summary.outdated_messages}`);
console.log(`Unique fingerprints:     ${fpMap.size}\n`);

console.log('Score Distribution:');
const maxBar = Math.max(...Object.values(dist));
Object.entries(dist).forEach(([range, count]) => {
  const barLen = Math.round((count / maxBar) * 30);
  const bar = '█'.repeat(barLen) + '░'.repeat(30 - barLen);
  console.log(`  ${range.padEnd(6)} │ ${String(count).padStart(4)} │ ${bar} ${Math.round(count/messages.length*100)}%`);
});

console.log('\nBy Category (important messages):');
const totalImp = topMessages.length;
Object.entries(importantByCategory).sort((a,b) => b[1]-a[1]).forEach(([cat, count]) => {
  const pct = Math.round(count / totalImp * 100);
  const bar = '█'.repeat(Math.round(pct/5)) + '░'.repeat(20 - Math.round(pct/5));
  console.log(`  ${cat.padEnd(10)} │ ${String(count).padStart(3)} (${String(pct).padStart(3)}%) │ ${bar}`);
});

// Top 10
console.log('\n╔══════════════════════════════════════════════════════════╗');
console.log('║              TOP 10 MOST IMPORTANT MESSAGES              ║');
console.log('╚══════════════════════════════════════════════════════════╝');
topMessages.slice(0, 10).forEach((m, i) => {
  const date = m.timestamp.split(' ')[0];
  console.log(`\n${String(i+1)+'.'.padEnd(3)} [${m.score_total}/10] ${date} ${(m.categories||[]).map(c=>c.padEnd(10)).join('')}`);
  console.log(`    "${m.text.substring(0, 180).replace(/\n/g, ' ')}"`);
  console.log(`    → ${m.why}`);
});

// Notable patterns
console.log('\n╔══════════════════════════════════════════════════════════╗');
console.log('║                   INTERESTING PATTERNS                    ║');
console.log('╚══════════════════════════════════════════════════════════╝');

// Old but important
const oldImportant = topMessages.filter(m => isOutdated(m.timestamp));
console.log(`\n🔴 Old but important (pre-March, score>=7): ${oldImportant.length}`);
oldImportant.slice(0, 3).forEach(m => {
  console.log(`   [${m.score_total}] ${m.timestamp} - ${m.categories.join(',')}`);
  console.log(`   ${m.text.substring(0,120).replace(/\n/g,' ')}`);
});

// JSON configs
const jsonMsgs = topMessages.filter(m => m.text.trim().startsWith('{'));
console.log(`\n📋 JSON/Structured configs (score>=7): ${jsonMsgs.length}`);
jsonMsgs.slice(0,3).forEach(m => {
  console.log(`   [${m.score_total}] ${m.timestamp}`);
  const preview = m.text.substring(0,80).replace(/\n/g,' ');
  console.log(`   ${preview}...`);
});

// Revenue-related
const revenueMsgs = topMessages.filter(m => /revenue|kunde|lead|sales/i.test(m.text));
console.log(`\n💰 Revenue-related (score>=7): ${revenueMsgs.length}`);

// Decisions
const decisionMsgs = topMessages.filter(m => (m.categories||[]).includes('decision'));
console.log(`\n⚖️ Decisions (score>=7): ${decisionMsgs.length}`);
decisionMsgs.slice(0,5).forEach(m => {
  console.log(`   [${m.score_total}] ${m.timestamp}: ${m.text.substring(0,100).replace(/\n/g,' ')}`);
});

console.log(`\n✅ Output: ${outPath}`);
console.log(`   Contains ${topMessages.length} important messages`);
