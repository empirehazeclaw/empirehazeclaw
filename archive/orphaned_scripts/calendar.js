#!/usr/bin/env node
/**
 * Simple Calendar Tool
 * Uses Google Calendar API or basic iCal
 */

const fs = require('fs');
const path = require('path');

// Simple JSON calendar storage
const CALENDAR_FILE = '/home/clawbot/.openclaw/workspace/data/calendar.json';

// Ensure data directory exists
const dataDir = path.dirname(CALENDAR_FILE);
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
}

// Load calendar
function loadCalendar() {
    if (fs.existsSync(CALENDAR_FILE)) {
        return JSON.parse(fs.readFileSync(CALENDAR_FILE, 'utf8'));
    }
    return { events: [] };
}

// Save calendar
function saveCalendar(data) {
    fs.writeFileSync(CALENDAR_FILE, JSON.stringify(data, null, 2));
}

// Add event
function addEvent(title, date, time, description = '') {
    const calendar = loadCalendar();
    calendar.events.push({
        id: Date.now(),
        title,
        date,
        time,
        description,
        created: new Date().toISOString()
    });
    saveCalendar(calendar);
    return calendar.events[calendar.events.length - 1];
}

// List events
function listEvents(days = 7) {
    const calendar = loadCalendar();
    const now = new Date();
    const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
    
    return calendar.events.filter(e => {
        const eventDate = new Date(e.date);
        return eventDate >= now && eventDate <= future;
    });
}

// Delete event
function deleteEvent(id) {
    const calendar = loadCalendar();
    calendar.events = calendar.events.filter(e => e.id != id);
    saveCalendar(calendar);
    return calendar.events;
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (command === 'add') {
    const [title, date, time] = args.slice(1);
    if (!title || !date) {
        console.log('Usage: calendar add "Title" "2026-03-20" "14:00"');
        process.exit(1);
    }
    const event = addEvent(title, date, time, args[3] || '');
    console.log('✅ Event added:', event.title);
} else if (command === 'list') {
    const days = parseInt(args[1]) || 7;
    const events = listEvents(days);
    console.log(`📅 Events for next ${days} days:\n`);
    events.forEach(e => {
        console.log(`${e.date} ${e.time} - ${e.title}`);
    });
    if (events.length === 0) console.log('No events found.');
} else if (command === 'delete') {
    const id = parseInt(args[1]);
    deleteEvent(id);
    console.log('✅ Event deleted');
} else {
    console.log(`
📅 Calendar CLI

Commands:
  calendar add "Title" "YYYY-MM-DD" "HH:MM" [description]
  calendar list [days]
  calendar delete <id>

Examples:
  calendar add "Meeting" "2026-03-20" "14:00" "Team sync"
  calendar list 30
  calendar delete 123456789
`);
}
