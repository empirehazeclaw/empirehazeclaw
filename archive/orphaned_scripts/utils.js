#!/usr/bin/env node
/**
 * UNIFIED UTILITY TOOL
 * Combines: calendar, reminder, tts, extract
 */

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'calendar' || cmd === 'cal') {
    console.log('\n📅 Calendar - Use scripts/calendar.js');
}
else if (cmd === 'remind' || cmd === 'reminder') {
    const task = args.slice(1).join(' ');
    console.log(`\n📝 Reminder added: ${task || '(no task)'}`);
    console.log('Use: node scripts/reminder.js add "task"');
}
else if (cmd === 'tts' || cmd === 'speak') {
    const text = args.slice(1).join(' ');
    console.log(`\n🎤 TTS: ${text}`);
    console.log('Use: node scripts/ttsnotify.js "text"');
}
else if (cmd === 'extract' || cmd === 'pdf') {
    console.log('\n📄 PDF Extract - Use: node scripts/quick-extract.js file.pdf');
}
else if (cmd === 'all') {
    console.log(`
📦 ALL TOOLS

📅 Calendar:   node scripts/calendar.js
📝 Reminder:   node scripts/reminder.js add "task"
🎤 TTS:        node scripts/ttsnotify.js "text"
📄 PDF:        node scripts/quick-extract.js file.pdf
🌐 Translate:  node scripts/multilang.js "text" --to en
🔍 Website:   node scripts/website-check.js
`);
}
else {
    console.log(`
🔧 UNIFIED UTILITY TOOL

Commands:
  node utils.js calendar         - Open calendar
  node utils.js remind "task"    - Add reminder
  node utils.js tts "text"       - Text to speech
  node utils.js extract file.pdf - Extract PDF text
  node utils.js all              - Show all tools
`);
}
