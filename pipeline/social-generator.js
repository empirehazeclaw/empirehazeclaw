#!/usr/bin/env node
/**
 * Social Media Content Generator - WITH HUMANIZER
 * Creates humanized posts for Twitter, LinkedIn, Instagram
 */

// Humanizer function
function humanize(text) {
    const rules = [
        { from: /In conclusion/gi, to: 'Bottom line' },
        { from: /Furthermore/gi, to: 'Also' },
        { from: /Therefore/gi, to: 'So' },
        { from: /Additionally/gi, to: 'Plus' },
        { from: /It is important to note/gi, to: 'Here\'s the thing' },
        { from: /utilize/gi, to: 'use' },
        { from: /numerous/gi, to: 'many' },
    ];
    rules.forEach(rule => text = text.replace(rule.from, rule.to));
    return text;
}

// Templates
function generateContent(topic, platform, count = 3) {
    console.log(`\n📱 ${platform.toUpperCase()} CONTENT: ${topic}`);
    console.log('(✨ Humanized)\n');
    
    const templates = {
        twitter: [
            `🚀 ${topic}: Here's what you need to know 👇`,
            `💡 Unpopular opinion: ${topic} is overrated`,
            `5 ${topic} tips that actually work:`,
            `The future of ${topic} looks like this...`,
            `Stop doing ${topic} the hard way. Do this instead:`
        ],
        linkedin: [
            `How we increased our results by 300% using ${topic}`,
            `Why ${topic} is the biggest opportunity of 2026`,
            `Everything you know about ${topic} is wrong`,
            `The ${topic} guide you wish you had earlier`
        ],
        instagram: [
            `${topic} ✨`,
            `The secret about ${topic} no one talks about`,
            `Save this for later! 📌 ${topic}`
        ]
    };
    
    const posts = templates[platform].slice(0, count);
    posts.forEach((post, i) => {
        console.log(`${i+1}. ${humanize(post)}`);
        console.log('');
    });
}

const args = process.argv.slice(2);
const platform = args[0] || 'twitter';
const topic = args.slice(1).join(' ') || 'AI';

generateContent(topic, platform);
