#!/usr/bin/env node

/**
 * 🎛️ Hyperparameter Tuner for Learning Loop v3
 * 
 * Analyzes current hyperparameters and suggests optimizations
 * to improve Learning Loop score from 0.76 to 0.85+
 * 
 * Usage:
 *   node index.js              # Analyze and suggest
 *   node index.js --apply      # Apply suggested changes
 *   node index.js --status     # Show current hyperparams
 *   node index.js --history    # Show tuning history
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const WORKSPACE = path.join(process.env.HOME || '/home/clawbot', '.openclaw/workspace');
const DATA_DIR = path.join(WORKSPACE, 'data');
const SCRIPTS_DIR = path.join(WORKSPACE, 'SCRIPTS', 'automation');
const LOOP_STATE_FILE = path.join(DATA_DIR, 'learning_loop_state.json');
const THOMPSON_FILE = path.join(DATA_DIR, 'thompson_rewards.json');
const VALIDATION_LOG = path.join(DATA_DIR, 'learning_loop', 'validation_log.json');
const LOOP_SCRIPT = path.join(SCRIPTS_DIR, 'learning_loop_v3.py');
const TUNING_HISTORY = path.join(DATA_DIR, 'tuning_history.json');

// Default hyperparameters from learning_loop_v3.py
const DEFAULTS = {
  epsilon_start: { current: 0.3, min: 0.2, max: 0.4, description: 'Initial exploration rate' },
  epsilon_decay: { current: 0.01, min: 0.005, max: 0.02, description: 'Epsilon decay per iteration' },
  epsilon_min: { current: 0.05, min: 0.02, max: 0.1, description: 'Minimum epsilon floor' },
  error_delta_threshold: { current: 0.1, min: 0.05, max: 0.2, description: 'Acceptable error increase' },
  pattern_decay_rate: { current: 0.05, min: 0.03, max: 0.1, description: 'Daily pattern confidence decay' },
  thompson_prior_alpha: { current: 2, min: 1, max: 5, description: 'Thompson sampling success prior' },
  thompson_prior_beta: { current: 1, min: 0.5, max: 3, description: 'Thompson sampling failure prior' }
};

/**
 * Load current state
 */
function loadState() {
  try {
    if (fs.existsSync(LOOP_STATE_FILE)) {
      return JSON.parse(fs.readFileSync(LOOP_STATE_FILE, 'utf8'));
    }
  } catch (e) {}
  return null;
}

/**
 * Load Thompson rewards
 */
function loadThompsonRewards() {
  try {
    if (fs.existsSync(THOMPSON_FILE)) {
      return JSON.parse(fs.readFileSync(THOMPSON_FILE, 'utf8'));
    }
  } catch (e) {}
  return {};
}

/**
 * Load tuning history
 */
function loadTuningHistory() {
  try {
    if (fs.existsSync(TUNING_HISTORY)) {
      return JSON.parse(fs.readFileSync(TUNING_HISTORY, 'utf8'));
    }
  } catch (e) {}
  return { iterations: [], suggestions: [] };
}

/**
 * Save tuning history
 */
function saveTuningHistory(history) {
  fs.mkdirSync(path.dirname(TUNING_HISTORY), { recursive: true });
  fs.writeFileSync(TUNING_HISTORY, JSON.stringify(history, null, 2));
}

/**
 * Extract current hyperparameters from learning_loop_v3.py
 */
function extractCurrentHyperparams() {
  try {
    const content = fs.readFileSync(LOOP_SCRIPT, 'utf8');
    const hyperparams = {};
    
    // Epsilon annealing
    const epsilonMatch = content.match(/epsilon\s*=\s*max\(([\d.]+),\s*([\d.]+)\s*-\s*\(iteration\s*\*\s*([\d.]+)\)/);
    if (epsilonMatch) {
      hyperparams.epsilon_min = parseFloat(epsilonMatch[1]);
      hyperparams.epsilon_start = parseFloat(epsilonMatch[2]);
      hyperparams.epsilon_decay = parseFloat(epsilonMatch[3]);
    }
    
    // Error delta threshold
    const errorMatch = content.match(/ERROR_DELTA_THRESHOLD\s*=\s*([\d.]+)/);
    if (errorMatch) {
      hyperparams.error_delta_threshold = parseFloat(errorMatch[1]);
    }
    
    // Pattern decay rate
    const decayMatch = content.match(/decay_rate\s*=\s*([\d.]+)\s*#/);
    if (decayMatch) {
      hyperparams.pattern_decay_rate = parseFloat(decayMatch[1]);
    }
    
    return hyperparams;
  } catch (e) {
    return {};
  }
}

/**
 * Analyze score trajectory
 */
function analyzeScoreTrajectory(state) {
  const history = state?.score_history || [];
  if (history.length < 5) {
    return { status: 'insufficient_data', trend: 'unknown' };
  }
  
  const recent = history.slice(-10);
  const first = recent[0];
  const last = recent[recent.length - 1];
  const delta = last - first;
  
  // Check for plateau (less than 0.01 change over 10 iterations)
  const plateau = Math.abs(delta) < 0.01;
  
  // Check if improving
  const improving = delta > 0.01;
  const degrading = delta < -0.01;
  
  // Calculate variance
  const mean = recent.reduce((a, b) => a + b, 0) / recent.length;
  const variance = recent.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / recent.length;
  
  return {
    status: plateau ? 'plateau' : improving ? 'improving' : degrading ? 'degrading' : 'stable',
    trend: delta > 0.02 ? '📈' : delta < -0.02 ? '📉' : '➡️',
    delta: delta.toFixed(4),
    recent_avg: mean.toFixed(4),
    recent_range: `${Math.min(...recent).toFixed(3)} - ${Math.max(...recent).toFixed(3)}`
  };
}

/**
 * Analyze Thompson rewards for category performance
 */
function analyzeThompsonRewards(rewards) {
  const categories = Object.entries(rewards);
  if (categories.length === 0) {
    return { best: null, worst: null, analysis: 'No reward data yet' };
  }
  
  const analyzed = categories.map(([cat, data]) => {
    const total = (data.successes || 0) + (data.failures || 0);
    const success_rate = total > 0 ? (data.successes || 0) / total : 0;
    return { category: cat, ...data, total, success_rate };
  }).sort((a, b) => b.success_rate - a.success_rate);
  
  return {
    best: analyzed[0],
    worst: analyzed[analyzed.length - 1],
    all: analyzed.slice(0, 5),
    analysis: analyzed.length > 0 ? 'OK' : 'Insufficient data'
  };
}

/**
 * Generate hyperparameter suggestions based on analysis
 */
function generateSuggestions(state, thompson, trajectory, currentHP) {
  const suggestions = [];
  const score = state?.score || 0.5;
  const iteration = state?.iteration || 0;
  
  // Get effective epsilon at current iteration
  const effectiveEpsilon = Math.max(
    currentHP.epsilon_min || 0.05,
    currentHP.epsilon_start - (iteration * (currentHP.epsilon_decay || 0.01))
  );
  
  // Plateau detection → boost exploration
  if (trajectory.status === 'plateau') {
    suggestions.push({
      param: 'epsilon_start',
      current: currentHP.epsilon_start || DEFAULTS.epsilon_start.current,
      suggested: Math.min(0.4, (currentHP.epsilon_start || 0.3) + 0.05),
      reason: 'Plateau detected - need more exploration',
      expected_impact: '+0.02-0.05 score'
    });
    suggestions.push({
      param: 'epsilon_decay',
      current: currentHP.epsilon_decay || DEFAULTS.epsilon_decay.current,
      suggested: Math.min(0.015, (currentHP.epsilon_decay || 0.01) + 0.003),
      reason: 'Slower decay = more exploration longer',
      expected_impact: '+0.01-0.03 score'
    });
  }
  
  // Epsilon too low → not enough exploration
  if (effectiveEpsilon < 0.05 && trajectory.status !== 'improving') {
    suggestions.push({
      param: 'epsilon_min',
      current: currentHP.epsilon_min || DEFAULTS.epsilon_min.current,
      suggested: 0.08,
      reason: 'Epsilon hit floor too early - not exploring enough',
      expected_impact: '+0.02-0.04 score'
    });
  }
  
  // Error delta analysis
  const errorDelta = currentHP.error_delta_threshold || DEFAULTS.error_delta_threshold.current;
  if (trajectory.status === 'degrading' && errorDelta < 0.15) {
    suggestions.push({
      param: 'error_delta_threshold',
      current: errorDelta,
      suggested: 0.15,
      reason: 'Validation too strict - rejecting good changes',
      expected_impact: '+0.03-0.05 score'
    });
  }
  
  // Check Thompson performance
  if (thompson.best && thompson.worst) {
    if (thompson.worst.success_rate < 0.3) {
      suggestions.push({
        param: 'thompson_prior_beta',
        current: DEFAULTS.thompson_prior_beta.current,
        suggested: 2,
        reason: `Category "${thompson.worst.category}" has low success rate - increase beta to be less punitive`,
        expected_impact: '+0.01-0.02 score'
      });
    }
  }
  
  // Pattern decay suggestions
  const decayRate = currentHP.pattern_decay_rate || DEFAULTS.pattern_decay_rate.current;
  if (trajectory.status === 'plateau' && decayRate < 0.07) {
    suggestions.push({
      param: 'pattern_decay_rate',
      current: decayRate,
      suggested: 0.07,
      reason: 'Patterns decaying too slowly - need fresh patterns',
      expected_impact: '+0.01-0.03 score'
    });
  }
  
  return suggestions;
}

/**
 * Apply a hyperparameter change
 */
function applyChange(param, value) {
  try {
    let content = fs.readFileSync(LOOP_SCRIPT, 'utf8');
    let backupContent = content;
    
    // Backup first
    const backupFile = `${LOOP_SCRIPT}.tuning_backup_${Date.now()}`;
    fs.writeFileSync(backupFile, content);
    console.log(`📦 Backed up to: ${backupFile}`);
    
    // Apply change based on parameter
    switch (param) {
      case 'epsilon_start':
      case 'epsilon_min':
      case 'epsilon_decay':
        // Match: epsilon = max(0.05, 0.3 - (iteration * 0.01))
        content = content.replace(
          /epsilon\s*=\s*max\(([\d.]+),\s*([\d.]+)\s*-\s*\(iteration\s*\*\s*([\d.]+)\)/,
          (match, min, start, decay) => {
            if (param === 'epsilon_min') return `epsilon = max(${value}, ${start} - (iteration * ${decay}))`;
            if (param === 'epsilon_start') return `epsilon = max(${min}, ${value} - (iteration * ${decay}))`;
            if (param === 'epsilon_decay') return `epsilon = max(${min}, ${start} - (iteration * ${value}))`;
            return match;
          }
        );
        break;
        
      case 'error_delta_threshold':
        content = content.replace(
          /ERROR_DELTA_THRESHOLD\s*=\s*[\d.]+/,
          `ERROR_DELTA_THRESHOLD = ${value}`
        );
        break;
        
      case 'pattern_decay_rate':
        content = content.replace(
          /decay_rate\s*=\s*[\d.]+\s*#/,
          `decay_rate = ${value}  #`
        );
        break;
        
      default:
        console.log(`❌ Unknown parameter: ${param}`);
        return false;
    }
    
    fs.writeFileSync(LOOP_SCRIPT, content);
    console.log(`✅ Applied ${param} = ${value}`);
    return true;
  } catch (e) {
    console.error(`❌ Failed to apply change: ${e.message}`);
    return false;
  }
}

/**
 * Generate status report
 */
function generateStatusReport(state, thompson, trajectory, currentHP) {
  const score = state?.score || 0;
  const iteration = state?.iteration || 0;
  const effectiveEpsilon = Math.max(
    currentHP.epsilon_min || 0.05,
    (currentHP.epsilon_start || 0.3) - (iteration * (currentHP.epsilon_decay || 0.01))
  );
  
  let report = `## 🎛️ Hyperparameter Status\n\n`;
  report += `### Learning Loop State\n`;
  report += `| Metric | Value |\n|--------|-------|\n`;
  report += `| Score | ${score.toFixed(4)} |\n`;
  report += `| Iteration | ${iteration} |\n`;
  report += `| Status | ${trajectory.status} ${trajectory.trend} |\n`;
  report += `| Trajectory | ${trajectory.delta} (last 10) |\n`;
  report += `| Recent Avg | ${trajectory.recent_avg} |\n`;
  
  report += `\n### Effective Hyperparameters\n`;
  report += `| Parameter | Value | Description |\n|-----------|-------|-------------|\n`;
  report += `| epsilon (effective) | ${effectiveEpsilon.toFixed(4)} | At iteration ${iteration} |\n`;
  report += `| epsilon_start | ${currentHP.epsilon_start || '?'} | Initial exploration |\n`;
  report += `| epsilon_decay | ${currentHP.epsilon_decay || '?'} | Per iteration |\n`;
  report += `| epsilon_min | ${currentHP.epsilon_min || '?'} | Floor |\n`;
  report += `| error_delta | ${currentHP.error_delta_threshold || '?'} | Threshold |\n`;
  report += `| decay_rate | ${currentHP.pattern_decay_rate || '?'} | Per day |\n`;
  
  if (thompson.best) {
    report += `\n### Thompson Rewards\n`;
    report += `| Category | Success Rate | Trials |\n|---------|--------------|--------|\n`;
    for (const cat of thompson.all || []) {
      report += `| ${cat.category} | ${(cat.success_rate * 100).toFixed(1)}% | ${cat.total} |\n`;
    }
  }
  
  return report;
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
🎛️ Hyperparameter Tuner for Learning Loop v3

Usage:
  node index.js              # Analyze and suggest
  node index.js --status     # Show current hyperparameters
  node index.js --history     # Show tuning history
  node index.js --apply <param> <value>  # Apply a change

Examples:
  node index.js
  node index.js --status
  node index.js --apply epsilon_start 0.35
  node index.js --apply error_delta_threshold 0.15
`);
    process.exit(0);
  }
  
  // Load current state
  const state = loadState();
  const thompson = analyzeThompsonRewards(loadThompsonRewards());
  const currentHP = extractCurrentHyperparams();
  const trajectory = analyzeScoreTrajectory(state);
  
  if (args.includes('--status')) {
    console.log(generateStatusReport(state, thompson, trajectory, currentHP));
    process.exit(0);
  }
  
  if (args.includes('--history')) {
    const history = loadTuningHistory();
    console.log(`## 📜 Tuning History\n`);
    if (history.iterations.length === 0) {
      console.log('No tuning history yet.');
    } else {
      for (const iter of history.iterations.slice(-10)) {
        console.log(`- ${iter.date}: ${iter.param} ${iter.old} → ${iter.new} (score: ${iter.score})`);
      }
    }
    process.exit(0);
  }
  
  // Generate suggestions
  const suggestions = generateSuggestions(state, thompson, trajectory, currentHP);
  
  // If --apply specified
  const applyIdx = args.indexOf('--apply');
  if (applyIdx !== -1 && args[applyIdx + 1] && args[applyIdx + 2]) {
    const param = args[applyIdx + 1];
    const value = parseFloat(args[applyIdx + 2]);
    const success = applyChange(param, value);
    
    if (success) {
      // Record in history
      const history = loadTuningHistory();
      history.iterations.push({
        date: new Date().toISOString(),
        param,
        old: currentHP[param] || DEFAULTS[param]?.current,
        new: value,
        score: state?.score || 0
      });
      saveTuningHistory(history);
    }
    process.exit(success ? 0 : 1);
  }
  
  // Default: show analysis and suggestions
  let report = generateStatusReport(state, thompson, trajectory, currentHP);
  
  report += `\n## 💡 Suggestions\n\n`;
  
  if (suggestions.length === 0) {
    report += `✅ No changes recommended. Current hyperparameters are well-tuned.\n`;
    report += `\n**Tips:**\n`;
    report += `- If score is plateauing, try increasing epsilon_start\n`;
    report += `- If validation is too strict, try increasing error_delta_threshold\n`;
    report += `- If patterns are too persistent, try increasing pattern_decay_rate\n`;
  } else {
    report += `| Parameter | Current | Suggested | Reason | Expected Impact |\n`;
    report += `|-----------|---------|-----------|--------|----------------|\n`;
    for (const s of suggestions) {
      report += `| ${s.param} | ${s.current} | ${s.suggested} | ${s.reason} | ${s.expected_impact} |\n`;
    }
    
    report += `\n### To Apply Changes\n`;
    for (const s of suggestions) {
      report += `\`\`\`bash\nnode index.js --apply ${s.param} ${s.suggested}\n\`\`\`\n`;
    }
  }
  
  console.log(report);
}

main().catch(console.error);
