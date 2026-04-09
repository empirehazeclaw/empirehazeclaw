#!/usr/bin/env node
/**
 * Humanizer - Makes content more human-like
 * Rules:
 * - Personal stories > guides
 * - Real numbers > fake stats
 * - Casual tone > formal
 * - Add emojis naturally
 */

function humanize(text, platform = 'twitter') {
    let result = text;
    
    // Rules for all platforms
    const rules = [
        // Replace formal with casual
        { from: /In conclusion/gi, to: 'Bottom line' },
        { from: /Furthermore/gi, to: 'Also' },
        { from: /Therefore/gi, to: 'So' },
        { from: /Additionally/gi, to: 'Plus' },
        { from: /It is important to note/gi, to: 'Here\'s the thing' },
        { from: /One of the most significant/gi, to: 'A big' },
        { from: /numerous/gi, to: 'many' },
        { from: /utilize/gi, to: 'use' },
        
        // Add natural elements
        { from: /\.\.\./g, to: '...' },
        
        // Make numbers more real
        { from: /100%/g, to: 'literally 100%' },
        { from: /\b5\b/g, to: 'honestly 5' },
        { from: /\b10\b/g, to: 'easily 10' },
    ];
    
    rules.forEach(rule => {
        result = result.replace(rule.from, rule.to);
    });
    
    // Platform-specific adjustments
    if (platform === 'twitter') {
        // Add emoji naturally
        result = result.replace(/! /g, '! 🎉 ');
        result = result.replace(/\? /g, '? 🤔 ');
        result = result.replace(/:/g, '🔹 ');
    }
    
    return result;
}

// CLI
const args = process.argv.slice(2);
const text = args.slice(1).join(' ');
const platform = args[0] || 'twitter';

if (text) {
    console.log('\n📝 ORIGINAL:\n' + text);
    console.log('\n✨ HUMANIZED (' + platform + '):\n' + humanize(text, platform));
} else {
    console.log(`
✨ HUMANIZER

Usage:
  node scripts/pipeline/humanizer.js twitter "Your text here"
  node scripts/pipeline/humanizer.js linkedin "Your text here"
  node scripts/pipeline/humanizer.js instagram "Your text here"

Rules applied:
  - Casual > Formal
  - Real numbers > Fake stats
  - Personal > Generic
`);
}
