#!/usr/bin/env node

/**
 * File Watcher - Reagiert auf neue Dateien in einem Verzeichnis
 * 
 * Usage:
 *   node filewatcher.js --dir /path --command "echo neu"
 *   node filewatcher.js --dir /var/www --command "nginx -s reload" --extensions html,css,js
 *   node filewatcher.js --dir /path --command "npm run build" --verbose
 */

const chokidar = require('chokidar');
const { exec, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// CLI Argumente parsen
const args = process.argv.slice(2);
let options = {
  dir: null,
  command: null,
  extensions: [],
  verbose: false,
  debounce: 500,
  once: false
};

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--dir' && args[i + 1]) {
    options.dir = args[i + 1];
    i++;
  } else if (args[i] === '--command' && args[i + 1]) {
    options.command = args[i + 1];
    i++;
  } else if (args[i] === '--extensions' && args[i + 1]) {
    options.extensions = args[i + 1].split(',').map(e => e.trim().replace(/^\./, ''));
    i++;
  } else if (args[i] === '--verbose') {
    options.verbose = true;
  } else if (args[i] === '--debounce' && args[i + 1]) {
    options.debounce = parseInt(args[i + 1], 10);
    i++;
  } else if (args[i] === '--once') {
    options.once = true;
  } else if (args[i] === '--help') {
    printHelp();
    process.exit(0);
  }
}

// Validierung
if (!options.dir) {
  console.error('❌ Error: --dir ist erforderlich');
  console.error('Usage: node filewatcher.js --dir /path --command "echo neu"');
  process.exit(1);
}

if (!options.command) {
  console.error('❌ Error: --command ist erforderlich');
  console.error('Usage: node filewatcher.js --dir /path --command "echo neu"');
  process.exit(1);
}

// Verzeichnis existiert?
if (!fs.existsSync(options.dir)) {
  console.error(`❌ Error: Verzeichnis existiert nicht: ${options.dir}`);
  process.exit(1);
}

// Hilfefunktion
function printHelp() {
  console.log(`
📁 File Watcher - Automatisch bei neuen Dateien reagieren

Usage:
  node filewatcher.js --dir <verzeichnis> --command "<befehl>" [optionen]

Optionen:
  --dir <path>        Zu überwachendes Verzeichnis (erforderlich)
  --command <cmd>    Befehl der ausgeführt werden soll (erforderlich)
  --extensions <ext> Nur auf bestimmte Dateien reagieren (kommagetrennt)
                     Beispiel: --extensions html,css,js
  --debounce <ms>    Wartezeit zwischen Events (Standard: 500ms)
  --once             Nur einmal ausführen und dann beenden
  --verbose          Ausführliche Ausgabe
  --help             Diese Hilfe anzeigen

Beispiele:
  # Bei neuen HTML-Dateien deployen
  node filewatcher.js --dir /var/www --command "echo 'New file detected!'"
  
  # Nur HTML/CSS/JS überwachen
  node filewatcher.js --dir /var/www --command "nginx -s reload" --extensions html,css,js
  
  # Build bei Änderungen
  node filewatcher.js --dir ./src --command "npm run build" --extensions js,ts

Environment Variables:
  FILEWATCHER_COMMAND  Alternativ: Befehl via Env setzen
`);
}

// Befehl ausführen
let lastRun = 0;
let timeout = null;

function runCommand(filePath, eventType) {
  const now = Date.now();
  
  // Debounce: nur ausführen wenn genug Zeit vergangen
  if (now - lastRun < options.debounce) {
    if (options.verbose) {
      console.log(`⏳ Debounce: Warte auf weitere Events...`);
    }
    clearTimeout(timeout);
    timeout = setTimeout(() => runCommand(filePath, eventType), options.debounce);
    return;
  }
  
  lastRun = now;
  
  const fileName = path.basename(filePath);
  const ext = path.extname(filePath).slice(1);
  
  if (options.verbose) {
    console.log(`\n📄 Event: ${eventType} - ${fileName}`);
  }
  
  // Extensions filtern wenn angegeben
  if (options.extensions.length > 0 && !options.extensions.includes(ext)) {
    if (options.verbose) {
      console.log(`⏭️  Übersprungen (Extension ${ext} nicht in ${options.extensions.join(', ')})`);
    }
    return;
  }
  
  console.log(`\n⚡ Führe aus: ${options.command}`);
  if (options.verbose) {
    console.log(`   File: ${filePath}`);
  }
  
  // Befehl ausführen
  const cmd = options.command;
  
  exec(cmd, { shell: '/bin/bash' }, (error, stdout, stderr) => {
    if (error) {
      console.error(`❌ Error: ${error.message}`);
      return;
    }
    
    if (stdout && options.verbose) {
      console.log(`📝 Output: ${stdout}`);
    }
    
    if (stderr && options.verbose) {
      console.warn(`⚠️  Stderr: ${stderr}`);
    }
    
    console.log(`✅ Befehl erfolgreich ausgeführt`);
    
    // Wenn --once gesetzt, dann beenden
    if (options.once) {
      console.log('🔚 Beende (--once gesetzt)');
      watcher.close();
      process.exit(0);
    }
  });
}

// File Watcher starten
console.log(`
╔═══════════════════════════════════════════╗
║         📁 File Watcher gestartet          ║
╠═══════════════════════════════════════════╣
║ Verzeichnis: ${options.dir.padEnd(31)}║
║ Befehl:      ${options.command.substring(0, 31).padEnd(31)}║
${options.extensions.length > 0 ? `║ Extensions:  ${options.extensions.join(', ').padEnd(31)}║` : `║ Extensions:  alle${' '.repeat(24)}║`}
║ Debounce:    ${options.debounce}ms${' '.repeat(23)}║
╚═══════════════════════════════════════════╝
`);

const watchPath = path.join(options.dir, '**/*');

const watcher = chokidar.watch(watchPath, {
  persistent: true,
  ignoreInitial: true,
  awaitWriteFinish: {
    stabilityThreshold: 300,
    pollInterval: 100
  },
  depth: 10
});

// Events
watcher
  .on('add', (filePath) => runCommand(filePath, 'add'))
  .on('change', (filePath) => runCommand(filePath, 'change'))
  .on('error', (error) => {
    console.error(`❌ Watcher Error: ${error}`);
  });

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Stoppe File Watcher...');
  watcher.close();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Stoppe File Watcher...');
  watcher.close();
  process.exit(0);
});
