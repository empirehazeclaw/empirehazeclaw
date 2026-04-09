#!/usr/bin/env node

/**
 * Memory Auto-Sync Script v2
 * Verbessertes Memory-System mit自动 Struktur
 * 
 * Usage:
 *   node autosync.js "Nachricht"                    # Decision (Standard)
 *   node autosync.js --type decision "Entscheidung"
 *   node autosync.js --type todo "Neue Aufgabe"
 *   node autosync.js --type learning "Gelerntes"
 *   node autosync.js --type project "Projektname" --status "Fortschritt"
 *   node autosync.js --type daily "Tages-Notiz"
 *   node autosync.js --sync                        # Daily Summary
 *   node autosync.js --index                       # Rebuild Index
 *   node autosync.js --cleanup                     # Archive old files
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, '..', 'memory');
const STRUCTURE = {
    daily: path.join(MEMORY_DIR, 'daily'),
    agents: path.join(MEMORY_DIR, 'agents'),
    projects: path.join(MEMORY_DIR, 'projects'),
    decisions: path.join(MEMORY_DIR, 'decisions'),
    learnings: path.join(MEMORY_DIR, 'learnings'),
    archive: path.join(MEMORY_DIR, 'archive')
};

// Farben
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    red: '\x1b[31m',
    cyan: '\x1b[36m'
};

function log(msg, color = 'reset') {
    console.log(`${colors[color]}${msg}${colors.reset}`);
}

// Ensure directories exist
function ensureDirs() {
    Object.values(STRUCTURE).forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
}

// Get timestamp
function getTimestamp() {
    return new Date().toISOString().replace('T', ' ').substring(0, 16);
}

// Get date string
function getDateStr() {
    return new Date().toISOString().substring(0, 10);
}

// Save entry to daily log
function saveToDaily(type, message) {
    const dateStr = getDateStr();
    const file = path.join(STRUCTURE.daily, `${dateStr}.md`);
    
    let content = '';
    if (fs.existsSync(file)) {
        content = fs.readFileSync(file, 'utf8');
    } else {
        content = `# Daily Log - ${dateStr}\n\n`;
    }
    
    content += `## ${getTimestamp()} [${type.toUpperCase()}]\n\n${message}\n\n---\n\n`;
    
    fs.writeFileSync(file, content);
    return file;
}

// Save decision
function saveDecision(decision) {
    const dateStr = getDateStr();
    const file = path.join(STRUCTURE.decisions, `${dateStr}.md`);
    
    let content = '';
    if (fs.existsSync(file)) {
        content = fs.readFileSync(file, 'utf8');
    } else {
        content = `# Decisions - ${dateStr}\n\n`;
    }
    
    content += `## ${getTimestamp()}\n\n${decision}\n\n---\n\n`;
    
    fs.writeFileSync(file, content);
    return file;
}

// Save learning
function saveLearning(learning) {
    const dateStr = getDateStr();
    const file = path.join(STRUCTURE.learnings, `${dateStr}.md`);
    
    let content = '';
    if (fs.existsSync(file)) {
        content = fs.readFileSync(file, 'utf8');
    } else {
        content = `# Learnings - ${dateStr}\n\n`;
    }
    
    content += `## ${getTimestamp()}\n\n${learning}\n\n---\n\n`;
    
    fs.writeFileSync(file, content);
    return file;
}

// Save project update
function saveProject(project, status) {
    const file = path.join(STRUCTURE.projects, `${project}.md`);
    
    let content = '';
    if (fs.existsSync(file)) {
        content = fs.readFileSync(file, 'utf8');
    } else {
        content = `# Project: ${project}\n\n`;
    }
    
    content += `## ${getTimestamp()}\n\n**Status:** ${status}\n\n---\n\n`;
    
    fs.writeFileSync(file, content);
    return file;
}

// Rebuild INDEX.md
function rebuildIndex() {
    const indexPath = path.join(MEMORY_DIR, 'INDEX.md');
    
    let content = `# Memory Index\n\n*Automatisch generiert: ${getTimestamp()}*\n\n`;
    
    // Daily
    content += `## 📅 Daily Logs\n\n`;
    const daily = fs.readdirSync(STRUCTURE.daily).sort().reverse().slice(0, 7);
    daily.forEach(f => content += `- [${f}](./daily/${f})\n`);
    
    // Decisions
    content += `\n## 📋 Decisions\n\n`;
    const decisions = fs.readdirSync(STRUCTURE.decisions).sort().reverse().slice(0, 5);
    decisions.forEach(f => content += `- [${f}](./decisions/${f})\n`);
    
    // Learnings
    content += `\n## 🧠 Learnings\n\n`;
    const learnings = fs.readdirSync(STRUCTURE.learnings).sort().reverse().slice(0, 5);
    learnings.forEach(f => content += `- [${f}](./learnings/${f})\n`);
    
    // Projects
    content += `\n## 🚀 Projects\n\n`;
    const projects = fs.readdirSync(STRUCTURE.projects);
    projects.forEach(f => content += `- [${f.replace('.md', '')}](./projects/${f})\n`);
    
    fs.writeFileSync(indexPath, content);
    log('✅ Index rebuilt!', 'green');
}

// Main
function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--index')) {
        ensureDirs();
        rebuildIndex();
        return;
    }
    
    if (args.includes('--sync')) {
        log('📝 Running daily sync...', 'blue');
        ensureDirs();
        
        // Count entries
        const daily = fs.readdirSync(STRUCTURE.daily).length;
        const decisions = fs.readdirSync(STRUCTURE.decisions).length;
        const projects = fs.readdirSync(STRUCTURE.projects).length;
        
        log(`📊 Daily: ${daily}, Decisions: ${decisions}, Projects: ${projects}`, 'cyan');
        rebuildIndex();
        return;
    }
    
    if (args.includes('--cleanup')) {
        log('🧹 Running cleanup...', 'yellow');
        // Archive old files (older than 90 days)
        const cutoff = Date.now() - (90 * 24 * 60 * 60 * 1000);
        
        Object.entries(STRUCTURE).forEach(([name, dir]) => {
            if (name === 'archive' || name === 'projects') return;
            
            try {
                fs.readdirSync(dir).forEach(file => {
                    const filePath = path.join(dir, file);
                    const stats = fs.statSync(filePath);
                    
                    if (stats.mtimeMs < cutoff) {
                        const archivePath = path.join(STRUCTURE.archive, file);
                        fs.renameSync(filePath, archivePath);
                        log(`  📦 Archived: ${file}`, 'yellow');
                    }
                });
            } catch (e) {}
        });
        
        log('✅ Cleanup complete!', 'green');
        return;
    }
    
    // Parse arguments
    let type = 'decision';
    let message = '';
    let project = '';
    let status = '';
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--type' && args[i + 1]) {
            type = args[i + 1];
            i++;
        } else if (args[i] === '--project' && args[i + 1]) {
            project = args[i + 1];
            i++;
        } else if (args[i] === '--status' && args[i + 1]) {
            status = args[i + 1];
            i++;
        } else if (!args[i].startsWith('--')) {
            message = args[i];
        }
    }
    
    if (!message && !status) {
        log('Usage:', 'yellow');
        console.log('  node autosync.js "Nachricht"');
        console.log('  node autosync.js --type decision "Entscheidung"');
        console.log('  node autosync.js --type todo "Aufgabe"');
        console.log('  node autosync.js --type learning "Gelerntes"');
        console.log('  node autosync.js --project "name" --status "Fortschritt"');
        console.log('  node autosync.js --sync');
        console.log('  node autosync.js --index');
        console.log('  node autosync.js --cleanup');
        return;
    }
    
    ensureDirs();
    
    // Save based on type
    let savedTo = '';
    
    if (project && status) {
        savedTo = saveProject(project, status);
        log(`✅ Project update saved: ${project}`, 'green');
    } else if (type === 'decision') {
        savedTo = saveDecision(message);
        log(`✅ Decision saved`, 'green');
    } else if (type === 'learning') {
        savedTo = saveLearning(message);
        log(`✅ Learning saved`, 'green');
    } else {
        savedTo = saveToDaily(type, message);
        log(`✅ Saved to daily log`, 'green');
    }
    
    log(`📁 ${savedTo}`, 'cyan');
}

main();
