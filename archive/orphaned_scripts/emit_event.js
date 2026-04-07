#!/usr/bin/env node

/**
 * Event Emitter - Send events to trigger autonomous agents
 * Usage: node emit_event.js <event_type> [data_json]
 */

const fs = require('fs');
const path = require('path');

const EVENTS_DIR = '/home/clawbot/.openclaw/workspace/data/events/';

// Ensure events directory exists
if (!fs.existsSync(EVENTS_DIR)) {
  fs.mkdirSync(EVENTS_DIR, { recursive: true });
}

const args = process.argv.slice(2);
const eventType = args[0];
const eventData = args[1] ? JSON.parse(args[1]) : {};

if (!eventType) {
  console.log('Usage: node emit_event.js <event_type> [data_json]');
  console.log('\nAvailable events:');
  console.log('  deployment          → triggers architect');
  console.log('  deployment_failed   → triggers debugger');
  console.log('  error               → triggers debugger');
  console.log('  build_complete     → triggers verification');
  console.log('  push                → triggers verification');
  console.log('  code_change         → triggers verification');
  console.log('  new_issue           → triggers coder');
  console.log('  design_request     → triggers architect');
  console.log('  service_down        → triggers debugger');
  console.log('  security_alert      → triggers verification');
  console.log('\nExample:');
  console.log('  node emit_event.js deployment_failed \'{"service":"api","error":"timeout"}\'');
  process.exit(1);
}

// Create event file
const timestamp = Date.now();
const eventFile = `${eventType}_${timestamp}.json`;
const eventPath = path.join(EVENTS_DIR, eventFile);

const event = {
  type: eventType,
  timestamp: new Date().toISOString(),
  data: eventData
};

fs.writeFileSync(eventPath, JSON.stringify(event, null, 2));

console.log(`✅ Event emitted: ${eventType}`);
console.log(`   File: ${eventFile}`);
console.log(`   Data: ${JSON.stringify(eventData)}`);
