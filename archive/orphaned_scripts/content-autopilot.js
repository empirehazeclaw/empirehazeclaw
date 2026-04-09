#!/usr/bin/env node
/**
 * Content Autopilot v2.1
 * Automatischer Content-Generator mit Plan
 * 
 * Features:
 * - Liest Content-Ideen aus data/content-ideas.md
 * - Zeigt today's content plan
 * - Markiert gepostete Items
 * - Generiert Weekly Report
 */

const fs = require('fs');
const path = require('path');

const CONTENT_FILE = path.join(__dirname, '..', 'data', 'content-ideas.md');
const POSTED_FILE = path.join(__dirname, '..', 'data', 'posted-content.json');

// Load posted content tracker
function loadPosted() {
    try {
        if (fs.existsSync(POSTED_FILE)) {
            return JSON.parse(fs.readFileSync(POSTED_FILE, 'utf8'));
        }
    } catch (e) {}
    return { twitter: [], blog: [], linkedin: [] };
}

function savePosted(posted) {
    fs.writeFileSync(POSTED_FILE, JSON.stringify(posted, null, 2));
}

// Parse content ideas from markdown - improved parser
function parseContentIdeas() {
    const content = fs.readFileSync(CONTENT_FILE, 'utf8');
    const ideas = {
        twitter: [],
        blog: [],
        linkedin: []
    };
    
    let currentSection = null;
    const lines = content.split('\n');
    
    for (const line of lines) {
        // Section detection
        if (line.match(/^## (Twitter|X|Twitter\/X)/i)) {
            currentSection = 'twitter';
        } else if (line.match(/^## Blog Post Ideas/i)) {
            currentSection = 'blog';
        } else if (line.match(/^## LinkedIn/i)) {
            currentSection = 'linkedin';
        } else if (line.match(/^## (Blog|Blog Posts)/i)) {
            currentSection = 'blog';
        } else if (line.match(/^## Twitter Threads/i)) {
            currentSection = 'twitter';
        }
        
        // Content extraction - handles "- [ ] " and plain "- "
        if (currentSection && line.match(/^(- \[ \] |- )/)) {
            let text = line.replace(/^(- \[ \] |- )/, '').trim();
            // Remove quotes if present
            if (text.startsWith('"') && text.endsWith('"')) {
                text = text.slice(1, -1);
            }
            if (text) {
                ideas[currentSection].push(text);
            }
        }
    }
    
    return ideas;
}

// Today's content plan
function showTodayPlan() {
    const ideas = parseContentIdeas();
    const posted = loadPosted();
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    const today = days[new Date().getDay()];
    
    const plans = {
        monday: { type: 'Blog', platform: 'Twitter', suggestion: ideas.twitter[0] || ideas.blog[0] },
        wednesday: { type: 'Social', platform: 'LinkedIn', suggestion: ideas.linkedin[0] },
        friday: { type: 'Newsletter', platform: 'Email' },
        sunday: { type: 'Blog', platform: 'Blog', suggestion: ideas.blog[0] }
    };
    
    console.log('\n=== 📅 CONTENT AUTOPILOT - TAGESPLAN ===\n');
    console.log(`📆 Heute ist: ${today.charAt(0).toUpperCase() + today.slice(1)}`);
    console.log('');
    
    if (plans[today]) {
        const plan = plans[today];
        console.log(`🎯 Heutige Aufgabe: ${plan.type} auf ${plan.platform}`);
        console.log('');
        
        // Available content
        const total = ideas.twitter.length + ideas.blog.length + ideas.linkedin.length;
        console.log(`📊 Content Pool: ${total} Ideen verfügbar`);
        console.log(`   🐦 Twitter: ${ideas.twitter.length}`);
        console.log(`   📝 Blog: ${ideas.blog.length}`);
        console.log(`   💼 LinkedIn: ${ideas.linkedin.length}`);
        console.log('');
        
        // Suggest next content
        if (plan.suggestion) {
            console.log(`🔥 Empfehlung: "${plan.suggestion}"`);
        }
    } else {
        console.log('📝 Kein geplanter Content heute - perfekt für Research & Planning!');
    }
    
    console.log('');
}

// Show stats
function showStats() {
    const posted = loadPosted();
    const ideas = parseContentIdeas();
    
    console.log('=== 📊 CONTENT STATS ===\n');
    console.log(`📝 Verfügbare Ideen: ${ideas.twitter.length + ideas.blog.length + ideas.linkedin.length}`);
    console.log(`   🐦 Twitter: ${ideas.twitter.length}`);
    console.log(`   📝 Blog: ${ideas.blog.length}`);
    console.log(`   💼 LinkedIn: ${ideas.linkedin.length}`);
    console.log('');
    console.log(`✅ Gepostet gesamt: ${posted.twitter.length + posted.blog.length + posted.linkedin.length}`);
    console.log('');
}

// Mark content as posted
function markPosted(platform, content) {
    const posted = loadPosted();
    if (!posted[platform]) {
        posted[platform] = [];
    }
    posted[platform].push({
        content: content,
        postedAt: new Date().toISOString()
    });
    savePosted(posted);
    console.log(`✅ Markiert als gepostet: ${platform} - "${content}"`);
}

// CLI
const args = process.argv.slice(2);
if (args.includes('--plan')) {
    showTodayPlan();
} else if (args.includes('--stats')) {
    showStats();
} else if (args[0] === '--post' && args[1] && args[2]) {
    const platform = args[1];
    const content = args.slice(2).join(' ');
    markPosted(platform, content);
} else {
    showTodayPlan();
    showStats();
}

console.log('');