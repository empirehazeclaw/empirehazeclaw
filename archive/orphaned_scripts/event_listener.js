#!/usr/bin/env node

/**
 * Event Listener - Triggers autonomous agents based on events
 * Watches /home/clawbot/.openclaw/workspace/data/events/ for new events
 */

const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');

const EVENTS_DIR = '/home/clawbot/.openclaw/workspace/data/events/';
const PROCESSED_DIR = EVENTS_DIR + 'processed/';

// Ensure directories exist
if (!fs.existsSync(PROCESSED_DIR)) {
  fs.mkdirSync(PROCESSED_DIR, { recursive: true });
}

// Event → Agent Mapping
const EVENT_TRIGGERS = {
  'deployment': {
    agent: 'architect',
    action: 'Neues Deployment erkannt - prüfe Architektur und dokumentiere'
  },
  'deployment_failed': {
    agent: 'debugger',
    action: 'Deployment fehlgeschlagen - analysiere Fehler und fixe'
  },
  'error': {
    agent: 'debugger',
    action: 'Neuer Fehler erkannt - analysiere und behebe'
  },
  'build_complete': {
    agent: 'verification',
    action: 'Build fertig - führe Tests und Qualitätscheck durch'
  },
  'push': {
    agent: 'verification',
    action: 'Code Push erkannt - prüfe Code Quality'
  },
  'code_change': {
    agent: 'verification',
    action: 'Code Änderung erkannt - validiere Änderungen'
  },
  'new_issue': {
    agent: 'dev',
    action: 'Neues Issue erstellt - prüfe und implementiere Fix'
  },
  'design_request': {
    agent: 'architect',
    action: 'Neue Design-Anfrage - erstelle Tech-Spec'
  },
  'service_down': {
    agent: 'debugger',
    action: 'Service ausgefallen - prüfe und starte neu'
  },
  'security_alert': {
    agent: 'verification',
    action: 'Security Alert - analysiere und ergreife Maßnahmen'
  }
};

// Get agent prompt based on agent type
function getAgentPrompt(agent, eventType, eventData) {
  const prompts = {
    architect: `🤖 EVENT TRIGGER: ${eventType}\n\nDu bist der autonome Architect Agent.\n\n${EVENT_TRIGGERS[eventType]?.action || 'Prüfe die Situation und mache Vorschläge.'}\n\nEvent Data: ${JSON.stringify(eventData || {}, null, 2)}\n\nAufgabe:\n1. Analysiere die Situation\n2. Erstelle eine Architecture-Empfehlung\n3. Dokumentiere in /home/clawbot/.openclaw/workspace/memory/agents/\n\nOutput: "Architect: [Analyse] + [Empfehlung]"`,
    
    debugger: `🤖 EVENT TRIGGER: ${eventType}\n\nDu bist der autonome Debugger Agent.\n\n${EVENT_TRIGGERS[eventType]?.action || 'Analysiere und behebe den Fehler.'}\n\nEvent Data: ${JSON.stringify(eventData || {}, null, 2)}\n\nAufgabe:\n1. Analysiere die Fehler\n2. Prüfe Logs (/tmp/openclaw/)\n3. Versuche automatisch zu fixen\n4. Dokumentiere größere Issues in TODO.md\n\nOutput: "Debugger: [X] analysiert, [Y] gefixt, [Z] 需要 Aufmerksamkeit"`,
    
    verification: `🤖 EVENT TRIGGER: ${eventType}\n\nDu bist der autonome Verification Agent.\n\n${EVENT_TRIGGERS[eventType]?.action || 'Prüfe die Code-Qualität.'}\n\nEvent Data: ${JSON.stringify(eventData || {}, null, 2)}\n\nAufgabe:\n1. Führe Quality-Checks durch\n2. Prüfe auf Security-Probleme\n3. Validiere Tests\n\nOutput: "Verification: [X] Files geprüft, [Y] Issues, [Z] Tests passed"`,
    
    dev: `🤖 EVENT TRIGGER: ${eventType}\n\nDu bist der autonome Coder Agent.\n\n${EVENT_TRIGGERS[eventType]?.action || 'Prüfe und implementiere.'}\n\nEvent Data: ${JSON.stringify(eventData || {}, null, 2)}\n\nAufgabe:\n1. Prüfe die Task/Issue\n2. Implementiere Fixes\n3. Teste die Änderungen\n\nOutput: "Coder: [X] Tasks geprüft, [Y] erledigt"`,
    
    coder: `🤖 EVENT TRIGGER: ${eventType}\n\nDu bist der autonome Coder Agent.\n\n${EVENT_TRIGGERS[eventType]?.action || 'Prüfe und implementiere.'}\n\nEvent Data: ${JSON.stringify(eventData || {}, null, 2)}\n\nAufgabe:\n1. Prüfe die Task/Issue\n2. Implementiere Fixes\n3. Teste die Änderungen\n\nOutput: "Coder: [X] Tasks geprüft, [Y] erledigt"`
  };
  
  return prompts[agent] || prompts.dev;
}

// Process a single event file
async function processEvent(eventFile) {
  const eventPath = path.join(EVENTS_DIR, eventFile);
  
  try {
    // Wait a moment for file to be fully written
    await new Promise(r => setTimeout(r, 500));
    
    const content = fs.readFileSync(eventPath, 'utf8');
    const eventData = JSON.parse(content);
    
    const eventType = eventData.type || eventFile.replace('.json', '');
    const trigger = EVENT_TRIGGERS[eventType];
    
    if (!trigger) {
      console.log(`[EventListener] No trigger for event: ${eventType}`);
      // Move to processed anyway
      const processedPath = path.join(PROCESSED_DIR, eventFile);
      fs.renameSync(eventPath, processedPath);
      return;
    }
    
    console.log(`[EventListener] Processing event: ${eventType} → ${trigger.agent}`);
    
    // Get the agent prompt
    const prompt = getAgentPrompt(trigger.agent, eventType, eventData.data);
    
    // Trigger agent via sessions_spawn
    const taskEncoded = encodeURIComponent(prompt);
    const cmd = `curl -s -X POST http://127.0.0.1:18789/sessions/sessions_spawn -H "Content-Type: application/json" -d '{"runtime":"subagent","agentId":"${trigger.agent}","task":"${taskEncoded.replace(/'/g, "''")}","label":"event-${eventType}","mode":"run"}'`;
    
    try {
      execSync(cmd, { cwd: '/home/clawbot/.openclaw/workspace', stdio: 'pipe' });
      console.log(`[EventListener] Agent ${trigger.agent} triggered successfully`);
    } catch (e) {
      console.log(`[EventListener] Trigger failed: ${e.message}`);
    }
    
    // Move to processed
    const processedPath = path.join(PROCESSED_DIR, eventFile);
    fs.renameSync(eventPath, processedPath);
    
  } catch (error) {
    console.error(`[EventListener] Error processing ${eventFile}:`, error.message);
  }
}

// Main loop - watch for new events
async function main() {
  console.log('[EventListener] Starting event listener...');
  console.log(`[EventListener] Watching: ${EVENTS_DIR}`);
  console.log(`[EventListener] Triggers:`, Object.keys(EVENT_TRIGGERS).join(', '));
  
  // Process any existing events first
  const existingEvents = fs.readdirSync(EVENTS_DIR).filter(f => f.endsWith('.json'));
  for (const event of existingEvents) {
    await processEvent(event);
  }
  
  // Watch for new events using fs.watch
  fs.watch(EVENTS_DIR, (eventType, filename) => {
    if (eventType === 'rename' && filename && filename.endsWith('.json')) {
      console.log(`[EventListener] New event detected: ${filename}`);
      processEvent(filename);
    }
  });
  
  console.log('[EventListener] Watching for events...');
}

main().catch(console.error);
