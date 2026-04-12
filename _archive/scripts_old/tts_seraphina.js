#!/usr/bin/env node
/**
 * 🗣️ Seraphina TTS - Edge TTS mit Seraphina Stimme
 */
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const VOICE = 'de-DE-SeraphinaMultilingualNeural';

function speak(text, options = {}) {
    const rate = options.rate || '+0%';
    const volume = options.volume || '+0%';
    const pitch = options.pitch || '+0Hz';
    const output = options.output || '/tmp/speech.mp3';
    
    try {
        execSync(`edge-tts -v "${VOICE}" -t "${text.replace(/"/g, '\\"')}" --rate ${rate} --volume ${volume} --pitch ${pitch} --write-media ${output}`, { stdio: 'inherit' });
        return output;
    } catch (e) {
        console.error('TTS Error:', e.message);
        return null;
    }
}

function speakToFile(text, outputFile) {
    return speak(text, { output: outputFile });
}

module.exports = { speak, speakToFile };

// CLI
if (require.main === module) {
    const text = process.argv.slice(2).join(' ') || 'Hallo! Ich bin Seraphina.';
    const output = '/tmp/speech.mp3';
    
    console.log('🗣️ Speaking with Seraphina...');
    const result = speak(text, { output });
    
    if (result) {
        console.log('✅ Saved to:', result);
    }
}
