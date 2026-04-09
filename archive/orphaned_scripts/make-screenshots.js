const { toPng } = require('html-to-image');
const fs = require('fs');
const path = require('path');

const files = [
  'notion-templates/screenshots/business-planner-preview.html',
  'notion-templates/screenshots/content-calendar-preview.html', 
  'notion-templates/screenshots/crm-preview.html',
  'notion-templates/screenshots/projektmanager-preview.html',
  'notion-templates/screenshots/goal-tracker-preview.html',
  'notion-templates/screenshots/bundle-preview.html'
];

// Create a simple function that just informs user
console.log('=== SCREENSHOT OPTION ===');
console.log('');
console.log('Since server cannot take screenshots, here is the workaround:');
console.log('');
console.log('1. Open these URLs in your browser:');
files.forEach(f => {
  const name = path.basename(f, '.html');
  console.log(`   https://empirehazeclaw.info/downloads/notion-previews/${name}.html`);
});
console.log('');
console.log('2. Press Cmd+Shift+4 (Mac) or Win+Shift+S (Windows)');
console.log('3. Save as PNG');
console.log('');
console.log('OR use a browser extension like "Full Page Screen Capture"');
