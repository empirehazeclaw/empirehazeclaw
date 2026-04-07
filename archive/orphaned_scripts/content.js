#!/usr/bin/env node
/**
 * UNIFIED CONTENT PIPELINE
 * Combines: Social, Blog, Humanizer, Images
 */

function humanize(text) {
    const rules = [
        { from: /In conclusion/gi, to: 'Bottom line' },
        { from: /Furthermore/gi, to: 'Also' },
        { from: /Therefore/gi, to: 'So' },
        { from: /utilize/gi, to: 'use' },
        { from: /numerous/gi, to: 'many' },
    ];
    rules.forEach(r => text = text.replace(r.from, r.to));
    return text;
}

const args = process.argv.slice(2);
const cmd = args[0];
const platform = args[0];
const topic = args.slice(1).join(' ') || 'AI';

function generateTwitter(topic, count = 3) {
    const templates = [
        `🚀 ${topic}: Here's what you need to know 👇`,
        `💡 Unpopular opinion: ${topic} is overrated`,
        `5 ${topic} tips that actually work:`,
        `The future of ${topic} looks like this...`,
        `Stop doing ${topic} the hard way. Do this instead:`
    ];
    return templates.slice(0, count).map(t => humanize(t));
}

function generateLinkedIn(topic, count = 3) {
    const templates = [
        `How we increased our results by 300% using ${topic}`,
        `Why ${topic} is the biggest opportunity of 2026`,
        `Everything you know about ${topic} is wrong`,
        `The ${topic} guide you wish you had earlier`
    ];
    return templates.slice(0, count).map(t => humanize(t));
}

function generateBlog(topic) {
    const slug = topic.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    return {
        title: topic,
        slug: `/blog/${slug}`,
        content: `# ${topic}: The Complete Guide\n\n## Introduction\n\n## What is ${topic}?\n\n## Key Benefits\n\n## How to Get Started\n\n## Conclusion`
    };
}

if (cmd === 'twitter' || cmd === 'tweet') {
    console.log(`\n🐦 TWITTER: ${topic}\n✨ Humanized\n`);
    generateTwitter(topic).forEach((post, i) => console.log(`${i+1}. ${post}\n`));
}
else if (cmd === 'linkedin' || cmd === 'li') {
    console.log(`\n💼 LINKEDIN: ${topic}\n✨ Humanized\n`);
    generateLinkedIn(topic).forEach((post, i) => console.log(`${i+1}. ${post}\n`));
}
else if (cmd === 'blog') {
    console.log(`\n📝 BLOG: ${topic}\n`);
    console.log(generateBlog(topic).content);
}
else if (cmd === 'all') {
    console.log(`\n📱 ALL CONTENT: ${topic}\n✨ Humanized\n`);
    console.log('--- TWITTER ---');
    generateTwitter(topic).forEach((p, i) => console.log(`${i+1}. ${p}`));
    console.log('\n--- LINKEDIN ---');
    generateLinkedIn(topic).forEach((p, i) => console.log(`${i+1}. ${p}`));
    console.log('\n--- BLOG ---');
    console.log(generateBlog(topic).content);
}
else {
    console.log(`
📝 UNIFIED CONTENT PIPELINE

Usage:
  node content.js twitter "topic"     - Generate tweets
  node content.js linkedin "topic"    - Generate LinkedIn posts
  node content.js blog "topic"        - Generate blog outline
  node content.js all "topic"         - Generate all content
  node content.js "topic"             - Alias for twitter

✨ Auto-humanized!
`);
}
