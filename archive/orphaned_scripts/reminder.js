#!/usr/bin/env node
/**
 * Auto Reminder System
 * Manages reminders and notifications
 */

const fs = require('fs');
const REMINDER_FILE = '/home/clawbot/.openclaw/workspace/data/reminders.json';

function loadReminders() {
    if (fs.existsSync(REMINDER_FILE)) {
        return JSON.parse(fs.readFileSync(REMINDER_FILE, 'utf8'));
    }
    return [];
}

function addReminder(text, time) {
    const reminders = loadReminders();
    reminders.push({ id: Date.now(), text, time, done: false });
    fs.writeFileSync(REMINDER_FILE, JSON.stringify(reminders, null, 2));
    return reminders;
}

function listReminders() {
    return loadReminders().filter(r => !r.done);
}

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'add') {
    const text = args.slice(1).join(' ');
    addReminder(text, 'now');
    console.log('✅ Reminder added:', text);
} else if (cmd === 'list') {
    console.log('📝 REMINDERS:\n');
    listReminders().forEach(r => console.log(`• ${r.text}`));
} else {
    console.log('Usage: node reminder.js add "Task"');
    console.log('       node reminder.js list');
}
