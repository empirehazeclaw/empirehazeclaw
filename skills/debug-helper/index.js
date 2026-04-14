#!/usr/bin/env node

/**
 * Debug Helper - Automated failure analysis
 * 
 * Usage:
 *   node index.js <error-file>
 *   node index.js --recent
 *   node index.js --tail <lines>
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const HOME = process.env.HOME || '/home/clawbot';
const LOG_DIR = path.join(HOME, '.openclaw/logs');
const MEMORY_LOG_DIR = path.join(HOME, '.openclaw/workspace/memory/logs');
const WORKSPACE = path.join(HOME, '.openclaw/workspace');

const LOG_FILES = [
  `${LOG_DIR}/openclaw.log`,
  `${LOG_DIR}/error.log`,
  `${LOG_DIR}/commands.log`,
  `${LOG_DIR}/cron_healer.log`,
  `${LOG_DIR}/evening_capture.log`,
  `${MEMORY_LOG_DIR}/learning_loop.log`
];

// Also check these common locations
const LOG_GLOBS = [
  `${LOG_DIR}/*.log`,
  `${WORKSPACE}/memory/logs/*.log`
];

const PATTERNS = [
  { pattern: /ECONNREFUSED/, cause: 'Connection refused - service not running', fix: 'systemctl restart <service>' },
  { pattern: /ENOENT/, cause: 'File or path not found', fix: 'Check paths, create missing directories' },
  { pattern: /EACCES/, cause: 'Permission denied', fix: 'chmod/chown or run with elevated permissions' },
  { pattern: /ETIMEDOUT|TIMEOUT/, cause: 'Operation timed out', fix: 'Increase timeout or check service health' },
  { pattern: /JSON\.parse/, cause: 'Malformed JSON in config', fix: 'Validate JSON syntax with jq or JSON.parse test' },
  { pattern: /Permission denied.*socket/, cause: 'Socket ownership issue', fix: 'chown clawbot:clawbot <socket-path>' },
  { pattern: /spawn.*ENOENT/, cause: 'Command not found in PATH', fix: 'Install missing binary or use full path' },
  { pattern: /Cannot find module/, cause: 'Node module not installed', fix: 'npm install <module> in project directory' },
  { pattern: /E11000 duplicate key/, cause: 'MongoDB duplicate key error', fix: 'Check unique indexes, handle conflicts' },
  { pattern: /CERT_HAS_EXPIRED/, cause: 'SSL certificate expired', fix: 'Renew certificate or update CA bundle' }
];

/**
 * Parse error file or stdin
 */
function parseError(input) {
  const lines = input.split('\n').filter(l => l.trim());
  const result = {
    timestamp: null,
    errorType: null,
    message: '',
    stack: [],
    context: []
  };

  for (const line of lines) {
    // Detect timestamp
    const tsMatch = line.match(/^\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})/);
    if (tsMatch && !result.timestamp) {
      result.timestamp = tsMatch[1];
    }

    // Detect error type
    const typeMatch = line.match(/(Error|Exception|Failed):\s*(.+)/i);
    if (typeMatch) {
      result.errorType = typeMatch[1];
      result.message = typeMatch[2];
    }

    // Collect stack trace lines
    if (line.match(/\s+at\s+/) || line.includes('Traceback')) {
      result.stack.push(line.trim());
    } else if (result.stack.length === 0 && line.match(/^[A-Z][a-z]+Error/)) {
      result.errorType = line.split(':')[0];
    } else if (!result.errorType && line.includes('Error:')) {
      result.message = line.replace('Error:', '').trim();
    }

    // Context lines (before error)
    if (result.stack.length === 0 && !line.match(/^\s*$/)) {
      result.context.push(line);
    }
  }

  return result;
}

/**
 * Match error against known patterns
 */
function matchPatterns(errorStr) {
  const matches = [];
  for (const { pattern, cause, fix } of PATTERNS) {
    if (pattern.test(errorStr)) {
      matches.push({ pattern: pattern.toString(), cause, fix });
    }
  }
  return matches;
}

/**
 * Get recent logs from various sources
 */
function getRecentLogs(lines = 50) {
  const results = [];
  const seen = new Set();

  // First try explicit LOG_FILES
  for (const logFile of LOG_FILES) {
    if (seen.has(logFile)) continue;
    try {
      if (fs.existsSync(logFile)) {
        const stat = fs.statSync(logFile);
        if (stat.isFile() && stat.size > 0) {
          const content = execSync(`tail -${lines} "${logFile}" 2>/dev/null`, { encoding: 'utf8' });
          if (content.trim()) {
            results.push({ source: logFile, content });
            seen.add(logFile);
          }
        }
      }
    } catch (e) {
      // File doesn't exist or can't be read
    }
  }

  // Then try glob patterns
  for (const glob of LOG_GLOBS) {
    try {
      const dir = path.dirname(glob);
      const pattern = path.basename(glob).replace('*', '');
      if (fs.existsSync(dir)) {
        const files = fs.readdirSync(dir)
          .filter(f => f.endsWith('.log'))
          .filter(f => !seen.has(path.join(dir, f)))
          .map(f => ({ file: f, mtime: fs.statSync(path.join(dir, f)).mtime }))
          .sort((a, b) => b.mtime - a.mtime)
          .slice(0, 5);

        for (const { file } of files) {
          const fullPath = path.join(dir, file);
          if (seen.has(fullPath)) continue;
          const content = execSync(`tail -${lines} "${fullPath}" 2>/dev/null`, { encoding: 'utf8' });
          if (content.trim()) {
            results.push({ source: fullPath, content });
            seen.add(fullPath);
          }
        }
      }
    } catch (e) {
      // Ignore glob errors
    }
  }

  return results;
}

/**
 * Generate debug report
 */
function generateReport(error, patterns, logs) {
  let report = `## 🐛 Debug Report\n\n`;

  if (error.timestamp) {
    report += `**Timestamp:** ${error.timestamp}\n`;
  }
  if (error.errorType) {
    report += `**Error Type:** ${error.errorType}\n`;
  }
  report += `\n### Error Message\n${error.message || '(see raw output)'}\n`;

  if (error.stack.length > 0) {
    report += `\n### Stack Trace\n\`\`\`\n${error.stack.join('\n')}\n\`\`\`\n`;
  }

  if (patterns.length > 0) {
    report += `\n### Known Patterns Matched\n`;
    for (const p of patterns) {
      report += `- **${p.cause}** → ${p.fix}\n`;
    }
  }

  if (logs.length > 0) {
    report += `\n### Recent Context\n`;
    for (const log of logs) {
      report += `\n**${log.source}:**\n\`\`\`\n${log.content.slice(-500)}\n\`\`\`\n`;
    }
  }

  report += `\n### Recommended Next Steps\n`;
  if (patterns.length > 0) {
    report += `1. Apply fix for matched pattern(s)\n`;
  }
  report += `2. Verify with: \`tail -20 ~/.openclaw/logs/openclaw.log\`\n`;
  report += `3. If unresolved, run diagnostic manually\n`;

  return report;
}

// CLI
async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
🐛 Debug Helper - Automated failure analysis

Usage:
  node index.js <error-file>     Analyze error file
  node index.js --recent [lines]  Get recent logs (default: 50)
  node index.js --tail <lines>    Get last N lines from logs
  node index.js --check           Quick health check

Examples:
  node index.js /tmp/error.log
  node index.js --recent 100
  node index.js --tail 30
`);
    process.exit(0);
  }

  let input = '';

  if (args.includes('--recent')) {
    const lines = parseInt(args[args.indexOf('--recent') + 1] || '50');
    const logs = getRecentLogs(lines);
    if (logs.length === 0) {
      console.log('No logs found.');
      process.exit(1);
    }
    input = logs.map(l => l.content).join('\n');
  } else if (args.includes('--tail')) {
    const idx = args.indexOf('--tail');
    const lines = args[idx + 1] || '50';
    const logs = getRecentLogs(parseInt(lines));
    input = logs.map(l => l.content).join('\n');
  } else if (args.includes('--check')) {
    // Quick health check
    console.log('🔍 Running quick health check...\n');
    try {
      const health = execSync('openclaw status 2>/dev/null || echo "openclaw not accessible"', { encoding: 'utf8' });
      console.log(health);
    } catch (e) {
      console.log('Could not get openclaw status');
    }
    process.exit(0);
  } else if (args.length > 0) {
    // Read from file
    const filePath = args[0];
    if (!fs.existsSync(filePath)) {
      console.error(`File not found: ${filePath}`);
      process.exit(1);
    }
    input = fs.readFileSync(filePath, 'utf8');
  } else {
    // Read from stdin
    input = fs.readFileSync(0, 'utf8');
  }

  // Analyze
  const error = parseError(input);
  const patterns = matchPatterns(input);
  const logs = getRecentLogs(20);

  // Generate and print report
  const report = generateReport(error, patterns, logs);
  console.log(report);
}

main().catch(console.error);
