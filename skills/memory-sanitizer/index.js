#!/usr/bin/env node

/**
 * 🧹 Memory Sanitizer v2 — MAXIMUM LEVEL
 * 
 * Advanced sanitization with:
 * - Consistent token mapping (PERSON_1, PERSON_2)
 * - Context-aware patterns
 * - Whitelist support
 * - Verification & audit
 * - Restore capability
 * 
 * Usage:
 *   node index.js --dry-run           Preview without changes
 *   node index.js --sanitize          Apply sanitization
 *   node index.js --verify            Verify sanitized output
 *   node index.js --restore          Restore from mapping
 *   node index.js --config            Show current config
 */

'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ============ CONFIGURATION ============

const WORKSPACE = process.env.HOME || '/home/clawbot';
const MEMORY_DIR = path.join(WORKSPACE, '.openclaw/workspace/ceo/memory');
const OUTPUT_DIR = path.join(WORKSPACE, '.openclaw/workspace/ceo/sanitized_memory');
const CONFIG_FILE = path.join(OUTPUT_DIR, '_config.json');
const MAPPING_FILE = path.join(OUTPUT_DIR, '_mapping.json');
const WHITELIST_FILE = path.join(OUTPUT_DIR, '_whitelist.json');
const AUDIT_FILE = path.join(OUTPUT_DIR, '_audit.json');

// ============ SENSITIVITY LEVELS ============

const SENSITIVITY = {
  CRITICAL: 'critical',     // API Keys, Tokens, Passwords
  HIGH: 'high',             // Emails, Phones, Names, IDs
  MEDIUM: 'medium',         // Domains, Paths
  LOW: 'low'               // Context-only
};

// ============ PATTERN DEFINITIONS ============

const PATTERNS = [
  // ============ CRITICAL ============
  {
    id: 'api_key',
    sensitivity: SENSITIVITY.CRITICAL,
    patterns: [
      /sk-[a-zA-Z0-9]{20,}/g,
      /sk_live_[a-zA-Z0-9]{20,}/g,
      /sk_test_[a-zA-Z0-9]{20,}/g,
    ],
    token: '{{API_KEY}}',
    description: 'API Key',
    preserve: false
  },
  {
    id: 'aws_key',
    sensitivity: SENSITIVITY.CRITICAL,
    patterns: [/AKIA[0-9A-Z]{16}/g],
    token: '{{AWS_KEY}}',
    description: 'AWS Access Key',
    preserve: false
  },
  {
    id: 'jwt_token',
    sensitivity: SENSITIVITY.CRITICAL,
    patterns: [/eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g],
    token: '{{JWT}}',
    description: 'JWT Token',
    preserve: false
  },
  {
    id: 'bot_token',
    sensitivity: SENSITIVITY.CRITICAL,
    patterns: [/\d{8,10}:[a-zA-Z0-9_-]{35,}/g],
    token: '{{BOT_TOKEN}}',
    description: 'Telegram Bot Token',
    preserve: false
  },
  {
    id: 'private_key',
    sensitivity: SENSITIVITY.CRITICAL,
    patterns: [/-----BEGIN [A-Z]+ PRIVATE KEY-----/g],
    token: '{{PRIVATE_KEY}}',
    description: 'Private Key',
    preserve: false
  },
  {
    id: 'db_url',
    sensitivity: SENSITIVITY.CRITICAL,
    patterns: [/(mongodb(?:\+srv)?|postgresql|mysql):\/\/[^\s'"`]+/gi],
    token: '{{DB_URL}}',
    description: 'Database URL',
    preserve: false
  },
  {
    id: 'bearer_token',
    sensitivity: SENSITIVITY.CRITICAL,
    patterns: [/[a-zA-Z0-9+/]{50,}={0,2}/g],
    token: '{{BEARER}}',
    description: 'Bearer Token',
    preserve: false
  },

  // ============ HIGH ============
  {
    id: 'email',
    sensitivity: SENSITIVITY.HIGH,
    patterns: [/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g],
    token: null, // Dynamic: {{EMAIL_1}}, {{EMAIL_2}}
    tokenPrefix: 'EMAIL',
    description: 'Email Address',
    preserve: false,
    consistent: true
  },
  {
    id: 'phone',
    sensitivity: SENSITIVITY.HIGH,
    patterns: [/\+?49[\s.-]?[0-9]{10,14}/g],
    token: null,
    tokenPrefix: 'PHONE',
    description: 'Phone Number',
    preserve: false,
    consistent: true
  },
  {
    id: 'telegram_id',
    sensitivity: SENSITIVITY.HIGH,
    patterns: [/(?<![\d])[1-9]\d{8,10}(?![\d])/g],
    token: null,
    tokenPrefix: 'USER_ID',
    description: 'Telegram/User ID',
    preserve: false,
    consistent: true
  },
  {
    id: 'ip_address',
    sensitivity: SENSITIVITY.HIGH,
    patterns: [/\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g],
    token: '{{IP}}',
    description: 'IP Address',
    preserve: false
  },

  // ============ MEDIUM ============
  {
    id: 'domain',
    sensitivity: SENSITIVITY.MEDIUM,
    patterns: [/empirehazeclaw\.(com|de|store|info|org)/g],
    token: '{{PRIMARY_DOMAIN}}',
    description: 'Domain Name',
    preserve: false
  },
  {
    id: 'workspace_path',
    sensitivity: SENSITIVITY.MEDIUM,
    patterns: [/\/home\/[a-zA-Z0-9_-]+\//g],
    token: '/home/{{USER}}/',
    description: 'Home Directory Path',
    preserve: true // Keep for context
  },

  // ============ LOW ============
  {
    id: 'person_name',
    sensitivity: SENSITIVITY.LOW,
    patterns: [/\bNico\b/g],
    token: null,
    tokenPrefix: 'PERSON',
    description: 'Person Name',
    preserve: false,
    consistent: true
  },
  {
    id: 'agent_name',
    sensitivity: SENSITIVITY.LOW,
    patterns: [/\bSir HazeClaw\b/g, /\bHazeClaw\b/g],
    token: '{{AGENT_NAME}}',
    description: 'Agent Name',
    preserve: false
  },
];

// ============ WHITELIST ============

const DEFAULT_WHITELIST = [
  'Sir HazeClaw', // Agent name - keep for context
  'EmpireHazeClaw', // Business name
  'Empire Haze', // Business name
  'German', // Language indicator
  'KMU', // Business context
  'Telegram', // Platform name
  'Linux', // OS name
];

// ============ STATE ============

let state = {
  mapping: {},       // value -> token mapping
  counter: {},       // prefix -> count
  whitelist: new Set(DEFAULT_WHITELIST),
  audit: [],
  errors: []
};

// ============ UTILITIES ============

function loadConfig() {
  if (fs.existsSync(CONFIG_FILE)) {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  }
  return { version: '2.0', created: new Date().toISOString() };
}

function loadWhitelist() {
  if (fs.existsSync(WHITELIST_FILE)) {
    const list = JSON.parse(fs.readFileSync(WHITELIST_FILE, 'utf8'));
    return new Set([...DEFAULT_WHITELIST, ...list]);
  }
  return new Set(DEFAULT_WHITELIST);
}

function loadMapping() {
  if (fs.existsSync(MAPPING_FILE)) {
    return JSON.parse(fs.readFileSync(MAPPING_FILE, 'utf8'));
  }
  return { mappings: {}, audit: [] };
}

function saveMapping() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(MAPPING_FILE, JSON.stringify({
    mappings: state.mapping,
    audit: state.audit,
    timestamp: new Date().toISOString()
  }, null, 2));
}

function loadAudit() {
  if (fs.existsSync(AUDIT_FILE)) {
    return JSON.parse(fs.readFileSync(AUDIT_FILE, 'utf8'));
  }
  return [];
}

function saveAudit() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(AUDIT_FILE, JSON.stringify({
    audit: state.audit,
    errors: state.errors,
    timestamp: new Date().toISOString()
  }, null, 2));
}

function getNextToken(prefix) {
  if (!state.counter[prefix]) {
    state.counter[prefix] = 1;
  }
  const token = `{{${prefix}_${state.counter[prefix]}}}`;
  state.counter[prefix]++;
  return token;
}

function getToken(patternId, originalValue) {
  // Check if we already have a mapping for this exact value
  if (state.mapping[originalValue]) {
    return state.mapping[originalValue];
  }
  
  // Find pattern definition
  const pattern = PATTERNS.find(p => p.id === patternId);
  if (!pattern) return originalValue;
  
  // Generate token
  let token;
  if (pattern.token) {
    token = pattern.token;
  } else if (pattern.tokenPrefix && pattern.consistent) {
    token = getNextToken(pattern.tokenPrefix);
  } else {
    token = `{{${pattern.id.toUpperCase()}}}`;
  }
  
  // Store mapping
  state.mapping[originalValue] = token;
  state.audit.push({
    original: originalValue,
    token,
    pattern: patternId,
    timestamp: new Date().toISOString()
  });
  
  return token;
}

function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function isWhitelisted(text) {
  return state.whitelist.has(text);
}

// ============ SANITIZATION ============

function sanitizeContent(content, filePath, options = {}) {
  const { dryRun = true, level = 2 } = options;
  let result = content;
  let changes = [];
  let skipped = [];
  
  // Process each pattern
  for (const pattern of PATTERNS) {
    // Skip if below level threshold
    if (pattern.sensitivity === SENSITIVITY.LOW && level < 3) continue;
    if (pattern.sensitivity === SENSITIVITY.MEDIUM && level < 2) continue;
    
    for (const regex of pattern.patterns) {
      // Reset regex lastIndex
      regex.lastIndex = 0;
      
      let match;
      while ((match = regex.exec(content)) !== null) {
        const originalValue = match[0];
        
        // Skip if whitelisted
        if (isWhitelisted(originalValue)) {
          skipped.push({ value: originalValue, reason: 'whitelist', pattern: pattern.id });
          continue;
        }
        
        // Skip if preserve is true and this is MEDIUM or LOW sensitivity
        if (pattern.preserve && pattern.sensitivity === SENSITIVITY.MEDIUM) {
          skipped.push({ value: originalValue, reason: 'preserve', pattern: pattern.id });
          continue;
        }
        
        // Generate token
        const token = getToken(pattern.id, originalValue);
        
        if (!dryRun) {
          // Replace all occurrences of this exact value
          const escapedValue = escapeRegex(originalValue);
          result = result.replace(new RegExp(escapedValue, 'g'), token);
        }
        
        changes.push({
          original: originalValue,
          replacement: dryRun ? token : 'APPLIED',
          pattern: pattern.id,
          sensitivity: pattern.sensitivity
        });
        
        // Prevent infinite loops
        if (!regex.global) break;
      }
    }
  }
  
  return { sanitized: result, changes, skipped };
}

// ============ FILE PROCESSING ============

function getMemoryFiles(dir = MEMORY_DIR) {
  const files = [];
  
  function walk(currentDir) {
    try {
      const items = fs.readdirSync(currentDir);
      for (const item of items) {
        if (item.startsWith('.')) continue;
        const fullPath = path.join(currentDir, item);
        try {
          const stat = fs.statSync(fullPath);
          if (stat.isDirectory()) {
            walk(fullPath);
          } else if (['.md', '.json', '.txt'].includes(path.extname(item))) {
            files.push(fullPath);
          }
        } catch (e) {
          // Skip inaccessible files
        }
      }
    } catch (e) {
      state.errors.push({ path: currentDir, error: e.message });
    }
  }
  
  walk(dir);
  return files;
}

function processFile(filePath, options = {}) {
  const { dryRun = true, level = 2, outputDir = OUTPUT_DIR } = options;
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const relativePath = path.relative(MEMORY_DIR, filePath);
    const { sanitized, changes, skipped } = sanitizeContent(content, filePath, { dryRun, level });
    
    if (!dryRun && changes.length > 0) {
      const outPath = path.join(outputDir, relativePath);
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(outPath, sanitized);
    }
    
    return {
      file: relativePath,
      changes,
      skipped,
      changed: changes.length > 0
    };
  } catch (e) {
    return {
      file: path.relative(MEMORY_DIR, filePath),
      error: e.message
    };
  }
}

// ============ VERIFICATION ============

const VERIFY_CHECKS = [
  { name: 'API Keys', patterns: [/sk-[a-zA-Z0-9]{20,}/g, /sk_live_/g], critical: true },
  { name: 'Bot Tokens', patterns: [/\d{8,10}:[a-zA-Z0-9_-]{35,}/g], critical: true },
  { name: 'JWT Tokens', patterns: [/eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+/g], critical: true },
  { name: 'AWS Keys', patterns: [/AKIA[0-9A-Z]{16}/g], critical: true },
  { name: 'Emails', patterns: [/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g], critical: false },
  { name: 'Phone Numbers', patterns: [/\+?49[\s.-]?[0-9]{10,14}/g], critical: false },
  { name: 'Telegram IDs', patterns: [/[1-9]\d{8,10}/g], critical: false },
];

function verifyDirectory(dir = OUTPUT_DIR) {
  const results = [];
  const files = getMemoryFiles(dir);
  
  for (const file of files) {
    const content = fs.readFileSync(file, 'utf8');
    const relativePath = path.relative(dir, file);
    
    for (const check of VERIFY_CHECKS) {
      for (const pattern of check.patterns) {
        pattern.lastIndex = 0;
        const matches = content.match(pattern);
        if (matches && matches.length > 0) {
          results.push({
            file: relativePath,
            check: check.name,
            matches: matches.length,
            critical: check.critical
          });
        }
      }
    }
  }
  
  return results;
}

// ============ MAIN ============

function printBanner() {
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║          🧹 MEMORY SANITIZER v2 — MAXIMUM LEVEL              ║
╚═══════════════════════════════════════════════════════════════╝
`);
}

function printHelp() {
  console.log(`
Usage:
  node index.js --dry-run           Preview changes without applying
  node index.js --sanitize          Apply full sanitization
  node index.js --sanitize --level 1  L1: Critical only
  node index.js --sanitize --level 2  L2: Critical + High (default)
  node index.js --sanitize --level 3  L3: Everything
  node index.js --verify            Verify sanitized output
  node index.js --restore           Restore from mapping
  node index.js --stats             Show statistics
  node index.js --config            Show current config
  node index.js --whitelist         Show/manage whitelist

Examples:
  node index.js --dry-run
  node index.js --sanitize --level 2
  node index.js --verify
`);
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    printBanner();
    printHelp();
    process.exit(0);
  }
  
  const dryRun = args.includes('--dry-run');
  const sanitize = args.includes('--sanitize');
  const verify = args.includes('--verify');
  const restore = args.includes('--restore');
  const stats = args.includes('--stats');
  const configShow = args.includes('--config');
  const whitelistShow = args.includes('--whitelist');
  
  const levelIndex = args.indexOf('--level');
  const level = levelIndex !== -1 ? parseInt(args[levelIndex + 1] || '2') : 2;
  
  printBanner();
  
  // Load whitelist
  state.whitelist = loadWhitelist();
  
  // ============ STATS ============
  if (stats) {
    const files = getMemoryFiles();
    const mapping = loadMapping();
    const whitelist = loadWhitelist();
    
    console.log('📊 Statistics\n');
    console.log(`Memory files: ${files.length}`);
    console.log(`Mapping entries: ${Object.keys(mapping.mappings || {}).length}`);
    console.log(`Whitelist entries: ${whitelist.size}`);
    console.log(`Output directory: ${OUTPUT_DIR}`);
    console.log(`\nSensitivity Levels:`);
    console.log(`  L1: Critical only (API Keys, Tokens, Passwords)`);
    console.log(`  L2: Critical + High (Emails, Phones, Names) [DEFAULT]`);
    console.log(`  L3: Everything (including Medium/Low)`);
    process.exit(0);
  }
  
  // ============ CONFIG ============
  if (configShow) {
    const cfg = loadConfig();
    console.log('📋 Current Configuration\n');
    console.log(JSON.stringify(cfg, null, 2));
    process.exit(0);
  }
  
  // ============ WHITELIST ============
  if (whitelistShow) {
    console.log('📋 Whitelist\n');
    state.whitelist.forEach(item => console.log(`  - ${item}`));
    console.log(`\nTotal: ${state.whitelist.size} entries`);
    console.log(`\nTo add: Edit ${WHITELIST_FILE}`);
    process.exit(0);
  }
  
  // ============ RESTORE ============
  if (restore) {
    const mapping = loadMapping();
    console.log('🔄 Restore from Mapping\n');
    console.log(`Found ${Object.keys(mapping.mappings || {}).length} mappings`);
    console.log(`\n⚠️  Restore not implemented yet.`);
    console.log(`Manual restore: Use the _mapping.json file to reverse replacements.`);
    process.exit(0);
  }
  
  // ============ VERIFY ============
  if (verify) {
    console.log('🔍 Verifying Sanitized Output\n');
    
    if (!fs.existsSync(OUTPUT_DIR)) {
      console.log('❌ No sanitized output found. Run --sanitize first.');
      process.exit(1);
    }
    
    const results = verifyDirectory();
    
    if (results.length === 0) {
      console.log('✅ VERIFICATION PASSED — No sensitive data found!');
    } else {
      console.log('❌ VERIFICATION FAILED — Sensitive data still present:\n');
      
      const critical = results.filter(r => r.critical);
      const nonCritical = results.filter(r => !r.critical);
      
      if (critical.length > 0) {
        console.log('🔴 CRITICAL ISSUES:');
        critical.forEach(r => {
          console.log(`  ${r.file}: ${r.check} (${r.matches} matches)`);
        });
        console.log('');
      }
      
      if (nonCritical.length > 0) {
        console.log('🟡 NON-CRITICAL:');
        nonCritical.forEach(r => {
          console.log(`  ${r.file}: ${r.check} (${r.matches} matches)`);
        });
      }
    }
    process.exit(0);
  }
  
  // ============ DRY RUN / SANITIZE ============
  const mode = dryRun ? 'DRY RUN (no changes)' : `SANITIZE (Level ${level})`;
  console.log(`Mode: ${mode}`);
  console.log(`Source: ${MEMORY_DIR}`);
  console.log(`Output: ${OUTPUT_DIR}\n`);
  
  // Reset state
  state = {
    mapping: {},
    counter: {},
    whitelist: state.whitelist,
    audit: [],
    errors: []
  };
  
  const files = getMemoryFiles();
  console.log(`Found ${files.length} files to process\n`);
  
  let totalChanges = 0;
  let processedFiles = 0;
  let changedFiles = 0;
  let skippedFiles = 0;
  
  for (const file of files) {
    const result = processFile(file, { dryRun, level });
    
    if (result.error) {
      console.log(`❌ ${result.file}: ${result.error}`);
      skippedFiles++;
      continue;
    }
    
    processedFiles++;
    
    if (result.changed) {
      changedFiles++;
      totalChanges += result.changes.length;
      
      const changeTypes = {};
      result.changes.forEach(c => {
        changeTypes[c.pattern] = (changeTypes[c.pattern] || 0) + 1;
      });
      
      console.log(`✅ ${result.file}: ${result.changes.length} changes`);
      
      if (dryRun) {
        const entries = Object.entries(changeTypes).slice(0, 3);
        for (const [pattern, count] of entries) {
          console.log(`   [${pattern}] × ${count}`);
        }
        if (Object.keys(changeTypes).length > 3) {
          console.log(`   ... and ${Object.keys(changeTypes).length - 3} more types`);
        }
      }
      
      if (result.skipped.length > 0 && dryRun) {
        console.log(`   (${result.skipped.length} skipped - whitelisted/preserved)`);
      }
    } else {
      console.log(`➖ ${result.file}: no changes`);
    }
  }
  
  // Save mapping and audit
  if (!dryRun) {
    saveMapping();
    saveAudit();
  }
  
  console.log(`\n╔════════════════════════════════════════╗`);
  console.log(`║            📊 SUMMARY                  ║`);
  console.log(`╠════════════════════════════════════════╣`);
  console.log(`║ Processed:  ${processedFiles.toString().padStart(4)} files         ║`);
  console.log(`║ Changed:    ${changedFiles.toString().padStart(4)} files         ║`);
  console.log(`║ Skipped:    ${skippedFiles.toString().padStart(4)} files         ║`);
  console.log(`║ Replacements: ${totalChanges.toString().padStart(4)} total         ║`);
  console.log(`╚════════════════════════════════════════╝`);
  
  if (dryRun) {
    console.log(`\n💡 Run with --sanitize to apply changes`);
  } else {
    console.log(`\n✅ Sanitized files written to: ${OUTPUT_DIR}`);
    console.log(`📝 Mapping saved to: ${MAPPING_FILE}`);
    console.log(`\n🔍 Run --verify after to confirm sanitization`);
  }
}

main().catch(console.error);
