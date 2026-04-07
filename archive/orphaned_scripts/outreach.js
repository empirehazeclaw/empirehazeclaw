#!/usr/bin/env node
/**
 * Outreach Automation System
 * Automatisiert cold outreach Kampagnen
 * 
 * Usage:
 *   node outreach.js add "company" "email@company.com"
 *   node outreach.js list
 *   node outreach.js send
 *   node outreach.js followup
 */

const fs = require('fs');
const path = require('path');

const DATA_FILE = '/home/clawbot/.openclaw/workspace/data/outreach.json';

// Templates
const TEMPLATES = {
    initial: {
        subject: 'Schnelle Frage zu {company}',
        body: `Hallo,

ich bin gerade auf {company} gestoßen und habe eine kurze Frage:

Was ist euer größtes Problem bei eurer Marketing/Website/Automation?

Ich helfe Unternehmen dabei, diese Probleme zu lösen - vielleicht kann ich auch euch helfen.

Hast du 5 Minuten für einen kurzen Call?

Beste Grüße,
Nico
EmpireHazeClaw`
    },
    followup: {
        subject: 'Folgefrage - {company}',
        body: `Hallo,

ich wollte nachhaken - hat meine letzte Email dich erreicht?

Falls du interesse hast, lass es mich wissen - ich helfe gerne.

Beste Grüße,
Nico`
    }
};

// Load data
function loadData() {
    try {
        return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    } catch {
        return { contacts: [], campaigns: [] };
    }
}

// Save data
function saveData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// Add contact
function add(company, email) {
    const data = loadData();
    
    data.contacts.push({
        id: Date.now(),
        company,
        email,
        status: 'new',
        added: new Date().toISOString(),
        emails: []
    });
    
    saveData(data);
    console.log(`✅ Contact hinzugefügt: ${company} <${email}>`);
}

// List contacts
function list() {
    const data = loadData();
    
    console.log('\n📋 Outreach Kontakte\n');
    console.log('='.repeat(50));
    
    data.contacts.forEach(c => {
        const status = c.status === 'replied' ? '✅' : c.status === 'sent' ? '📤' : '⬜';
        console.log(`\n${status} ${c.company}`);
        console.log(`   ${c.email}`);
        console.log(`   Status: ${c.status}`);
    });
    
    console.log('\n');
}

// Send email (placeholder - needs Gmail integration)
function send() {
    const data = loadData();
    const pending = data.contacts.filter(c => c.status === 'new');
    
    console.log(`📤 Bereit zum Senden: ${pending.length} Emails`);
    console.log('\nHinweis: Gmail Integration fehlt noch!');
    console.log('Email muss manuell gesendet werden oder via gog auth');
}

// Follow-up
function followup() {
    const data = loadData();
    const sent = data.contacts.filter(c => c.status === 'sent');
    
    console.log(`📬 Follow-up fällig: ${sent.length} Kontakte`);
}

// CLI
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'add') {
    add(args[1], args[2]);
} else if (cmd === 'list') {
    list();
} else if (cmd === 'send') {
    send();
} else if (cmd === 'followup') {
    followup();
} else {
    console.log('Outreach Automation');
    console.log(`
Usage:
  node outreach.js add "Company" "email@company.com"
  node outreach.js list
  node outreach.js send
  node outreach.js followup
    `);
}
