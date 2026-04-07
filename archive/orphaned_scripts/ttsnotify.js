#!/usr/bin/env node

/**
 * ttsnotify.js - Text-to-Speech Notification Script
 * 
 * Usage: node ttsnotify.js "Your text here"
 *        node ttsnotify.js "Text" --voice de-DE-SeraphinaMultilingualNeural
 *        node ttsnotify.js "Text" --output /path/to/output.mp3
 * 
 * Features:
 * - Uses Microsoft Edge TTS (free, high quality)
 * - Supports German voices (Seraphina, etc.)
 * - CLI interface with arguments
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { promisify } = require('util');

const execAsync = promisify(exec);

// Configuration
const DEFAULT_VOICE = 'de-DE-SeraphinaMultilingualNeural';
const DEFAULT_OUTPUT_FILE = path.join(os.tmpdir(), 'ttsnotify_output.mp3');

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    text: '',
    voice: DEFAULT_VOICE,
    outputFile: DEFAULT_OUTPUT_FILE,
    play: true
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--voice' || arg === '-v') {
      options.voice = args[++i];
    } else if (arg === '--output' || arg === '-o') {
      options.outputFile = args[++i];
      options.play = false;
    } else if (arg === '--no-play') {
      options.play = false;
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if (!arg.startsWith('--')) {
      options.text = arg;
    }
  }
  
  return options;
}

function printHelp() {
  console.log(`
🎤 ttsnotify.js - Text-to-Speech Notification Script

USAGE:
  node ttsnotify.js "Your text here" [OPTIONS]

OPTIONS:
  -v, --voice <voice>    Set the voice (default: de-DE-SeraphinaMultilingualNeural)
  -o, --output <file>    Save to file instead of playing
  --no-play              Don't play audio (only generate file)
  -h, --help             Show this help message

EXAMPLES:
  node ttsnotify.js "Hallo Welt!"
  node ttsnotify.js "Agent finished task" --voice en-US-AriaNeural
  node ttsnotify.js "Wichtige Nachricht" --output /tmp/alert.mp3

AVAILABLE VOICES:
  German:   de-DE-SeraphinaMultilingualNeural, de-DE-KlausNeural, de-DE-KlaraNeural
  English:  en-US-AriaNeural, en-US-GuyNeural, en-GB-SoniaNeural
  More:     https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech
`);
}

// Play audio file
function playAudio(filePath) {
  return new Promise((resolve, reject) => {
    const players = [
      { cmd: 'ffplay', args: ['-nodisp', '-autoexit', '-loglevel', 'quiet', filePath] },
      { cmd: 'mpg123', args: [filePath] },
      { cmd: 'play', args: [filePath] }
    ];
    
    let playerIndex = 0;
    
    function tryNextPlayer() {
      if (playerIndex >= players.length) {
        console.log('⚠️ No audio player found. File saved to:', filePath);
        resolve();
        return;
      }
      
      const player = players[playerIndex++];
      const proc = spawn(player.cmd, player.args, { stdio: 'ignore' });
      
      proc.on('error', () => {
        tryNextPlayer();
      });
      
      proc.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          tryNextPlayer();
        }
      });
    }
    
    tryNextPlayer();
  });
}

// Main TTS function using edge-tts CLI
async function speak(text, options = {}) {
  const voice = options.voice || DEFAULT_VOICE;
  const outputFile = options.outputFile || DEFAULT_OUTPUT_FILE;
  const shouldPlay = options.play !== false;
  
  if (!text) {
    console.error('❌ Error: No text provided');
    printHelp();
    process.exit(1);
  }
  
  // Sanitize text for CLI
  const escapedText = text.replace(/"/g, '\\"');
  
  console.log(`🎤 Generating speech...`);
  console.log(`   Text: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);
  console.log(`   Voice: ${voice}`);
  console.log(`   Output: ${outputFile}`);
  
  try {
    // Use edge-tts CLI
    const cmd = `edge-tts --voice "${voice}" --text "${escapedText}" --write-media "${outputFile}"`;
    await execAsync(cmd);
    
    console.log('✅ Audio file generated');
    
    // Play if requested
    if (shouldPlay) {
      console.log('🔊 Playing audio...');
      await playAudio(outputFile);
      console.log('✅ Playback finished');
    }
    
    return outputFile;
    
  } catch (error) {
    console.error('❌ Error generating speech:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  const options = parseArgs();
  speak(options.text, options);
}

module.exports = { speak, DEFAULT_VOICE };
