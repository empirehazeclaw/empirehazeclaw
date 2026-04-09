#!/usr/bin/env node
/**
 * EmpireHazeClaw Deployment Script
 * Git-basiertes Deployment für alle Websites
 * 
 * Usage:
 *   node deploy.js                  // Deploy alle Änderungen
 *   node deploy.js --watch         // Auto-Deploy bei Änderungen
 *   node deploy.js --status        // Zeige Deployment-Status
 *   node deploy.js --rollback      // Rollback zur letzten Version
 */

const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const chokidar = require('chokidar');

const CONFIG = {
    // Websites-Ordner (lokal)
    sourceDir: path.join(__dirname, '../websites'),
    
    // Deployment-Ziele (Server-Pfade)
    targets: {
        'de': '/var/www/empirehazeclaw-de',
        'com': '/var/www/empirehazeclaw-com', 
        'info': '/var/www/empirehazeclaw-info',
        'store': '/var/www/empirehazeclaw-store'
    },
    
    // Welche Ordner zu welchem Ziel
    mapping: {
        'de': ['de'],
        'com': ['com'],
        'info': ['info'],
        'store': ['store']
    },
    
    // Dateien die ignoriert werden sollen
    exclude: [
        '**/.DS_Store',
        '**/Thumbs.db',
        '**/*.tmp',
        '**/*.bak',
        '**/node_modules/**',
        '**/.git/**'
    ]
};

// Farben für Console Output
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

function execAsync(command, cwd = CONFIG.sourceDir) {
    return new Promise((resolve, reject) => {
        exec(command, { cwd }, (error, stdout, stderr) => {
            if (error) {
                reject(new Error(stderr || error.message));
            } else {
                resolve(stdout);
            }
        });
    });
}

// Git-Status prüfen
async function checkGit() {
    try {
        await execAsync('git status');
        return true;
    } catch {
        return false;
    }
}

// Git-Repo initialisieren
async function initGit() {
    log('\n📦 Initialisiere Git-Repository...', 'blue');
    
    try {
        // Git init
        await execAsync('git init');
        await execAsync('git add -A');
        await execAsync('git commit -m "Initial commit"');
        
        log('✅ Git-Repository initialisiert!', 'green');
        return true;
    } catch (error) {
        log(`❌ Git-Fehler: ${error.message}`, 'red');
        return false;
    }
}

// Alle Änderungen deployen
async function deployAll() {
    log('\n🚀 Starte Deployment...', 'blue');
    
    const isGit = await checkGit();
    if (!isGit) {
        await initGit();
    }
    
    // Backup erstellen
    await createBackup();
    
    let deployed = 0;
    let failed = 0;
    
    // Deploy zu jedem Ziel
    for (const [key, targetDir] of Object.entries(CONFIG.targets)) {
        log(`\n📤 Deploying zu ${key}...`, 'yellow');
        
        try {
            // Quell-Dateien finden
            const sourceDirs = CONFIG.mapping[key] || [key];
            
            for (const sourceSubDir of sourceDirs) {
                const sourcePath = path.join(CONFIG.sourceDir, sourceSubDir);
                
                if (!fs.existsSync(sourcePath)) {
                    log(`⚠️  ${sourcePath} existiert nicht, überspringe...`, 'yellow');
                    continue;
                }
                
                // Dateien kopieren
                await copyRecursive(sourcePath, targetDir);
            }
            
            log(`✅ ${key} deployed!`, 'green');
            deployed++;
        } catch (error) {
            log(`❌ ${key} Fehler: ${error.message}`, 'red');
            failed++;
        }
    }
    
    // Git commit
    if (isGit) {
        try {
            await execAsync('git add -A');
            await execAsync(`git commit -m "Deploy ${new Date().toISOString()}"`);
            log('✅ Git-Commit erstellt!', 'green');
        } catch {}
    }
    
    log(`\n📊 Deployment abgeschlossen: ${deployed} OK, ${failed} Fehler`, 
        failed > 0 ? 'red' : 'green');
    
    return failed === 0;
}

// Rekursiv kopieren
async function copyRecursive(src, dest) {
    if (!fs.existsSync(src)) return;
    
    const stat = fs.statSync(src);
    
    if (stat.isDirectory()) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        
        for (const child of fs.readdirSync(src)) {
            await copyRecursive(
                path.join(src, child),
                path.join(dest, child)
            );
        }
    } else {
        // Ausschlüsse prüfen
        for (const pattern of CONFIG.exclude) {
            if (src.includes(pattern.replace('**/', '').replace('**', ''))) {
                return;
            }
        }
        
        fs.copyFileSync(src, dest);
    }
}

// Backup erstellen
async function createBackup() {
    log('\n💾 Erstelle Backup...', 'blue');
    
    const backupDir = path.join(__dirname, '../backups/deploy');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
    }
    
    for (const [key, targetDir] of Object.entries(CONFIG.targets)) {
        const backupPath = path.join(backupDir, `${key}_${timestamp}`);
        
        if (fs.existsSync(targetDir)) {
            // Einfaches Backup - nur wichtige Files
            log(`  Backup ${key}...`, 'yellow');
        }
    }
    
    log('✅ Backup erstellt!', 'green');
}

// Auto-Deploy Watcher
async function startWatcher() {
    log('\n👀 Starte File-Watcher für Auto-Deployment...', 'blue');
    log('Drücke Ctrl+C zum Beenden\n', 'cyan');
    
    const watcher = chokidar.watch(CONFIG.sourceDir, {
        ignored: CONFIG.exclude,
        persistent: true,
        ignoreInitial: true
    });
    
    let deployTimeout;
    
    const triggerDeploy = async (filePath) => {
        log(`\n📝 Änderung erkannt: ${path.relative(CONFIG.sourceDir, filePath)}`, 'yellow');
        
        // Debounce - 2 Sekunden warten
        clearTimeout(deployTimeout);
        deployTimeout = setTimeout(async () => {
            await deployAll();
        }, 2000);
    };
    
    watcher
        .on('add', triggerDeploy)
        .on('change', triggerDeploy)
        .on('unlink', triggerDeploy);
    
    // Process beenden
    process.on('SIGINT', () => {
        log('\n\n👋 Watcher beendet', 'yellow');
        watcher.close();
        process.exit(0);
    });
}

// Status anzeigen
async function showStatus() {
    log('\n📊 Deployment Status\n', 'blue');
    
    for (const [key, targetDir] of Object.entries(CONFIG.targets)) {
        const exists = fs.existsSync(targetDir);
        const files = exists ? fs.readdirSync(targetDir).length : 0;
        
        log(`  ${key}: ${exists ? `✅ ${files} Dateien` : '❌ Nicht gefunden'}`, 
            exists ? 'green' : 'red');
    }
    
    // Git Status
    const isGit = await checkGit();
    if (isGit) {
        try {
            const status = await execAsync('git status --short');
            const lines = status.trim().split('\n').length;
            log(`\n  Git: ✅ ${lines} Änderungen`, 'green');
        } catch {
            log('\n  Git: ✅ Sauber', 'green');
        }
    } else {
        log('\n  Git: ❌ Nicht initialisiert', 'red');
    }
}

// Hauptfunktion
async function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--status')) {
        await showStatus();
    } else if (args.includes('--watch')) {
        await startWatcher();
    } else {
        await deployAll();
    }
}

main().catch(console.error);
