#!/usr/bin/env node
/**
 * Hashtag Generator
 * Generates relevant hashtags
 */

const topic = process.argv.slice(2).join(' ') || 'AI';

const hashtagSets = {
    ai: ['#AI', '#ArtificialIntelligence', '#MachineLearning', '#Tech', '#Innovation', '#Future'],
    business: ['#Business', '#Entrepreneur', '#Startup', '#Success', '#Motivation'],
    trading: ['#Trading', '#Crypto', '#Invest', '#Finance', '#Money'],
    default: ['#Content', '#Tips', '#Learn', '#Growth']
};

const tags = hashtagSets[topic.toLowerCase()] || hashtagSets.default;

console.log(`\n#️⃣ HASHTAGS FOR: ${topic}\n`);
console.log(tags.join(' '));
console.log('\n' + tags.slice(0, 3).join(' '));
