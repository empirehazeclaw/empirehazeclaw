#!/usr/bin/env node
/**
 * Social Media Analytics Tracker
 * Usage:
 *   node analytics-tracker.js view                    # Show all
 *   node analytics-tracker.js update youtube --subs 100 --views 5000
 *   node analytics-tracker.js update tiktok --followers 500
 */

const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', 'data', 'analytics.json');

// Load data
function loadData() {
    try {
        return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    } catch {
        return {};
    }
}

// Save data
function saveData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// View all
function view() {
    const data = loadData();
    console.log('\n📊 Social Media Analytics\n');
    console.log('='.repeat(40));
    
    if (data.social_media) {
        console.log('\n🌐 Social Media:');
        for (const [platform, stats] of Object.entries(data.social_media)) {
            console.log(`\n${platform}:`);
            for (const [key, value] of Object.entries(stats)) {
                if (key !== 'last_updated') {
                    console.log(`  ${key}: ${value.toLocaleString()}`);
                }
            }
        }
    }
    
    if (data.website) {
        console.log('\n\n🌍 Websites:');
        for (const [site, stats] of Object.entries(data.website)) {
            console.log(`\n${site}:`);
            for (const [key, value] of Object.entries(stats)) {
                if (key !== 'last_updated') {
                    console.log(`  ${key}: ${value.toLocaleString()}`);
                }
            }
        }
    }
    
    console.log('\n');
}

// Update platform
function update(platform, args) {
    const data = loadData();
    const today = new Date().toISOString().split('T')[0];
    
    // Find the right category
    let category = null;
    let target = null;
    
    if (data.social_media && data.social_media[platform]) {
        category = 'social_media';
        target = data.social_media[platform];
    } else if (data.website && data.website[platform]) {
        category = 'website';
        target = data.website[platform];
    } else if (data.pod && data.pod[platform]) {
        category = 'pod';
        target = data.pod[platform];
    }
    
    if (!target) {
        console.log(`❌ Platform not found: ${platform}`);
        console.log('Available:', Object.keys(data.social_media || {}), Object.keys(data.website || {}));
        return;
    }
    
    // Update fields
    for (const [key, value] of Object.entries(args)) {
        if (key !== 'platform' && value !== undefined) {
            target[key] = parseInt(value) || value;
        }
    }
    target.last_updated = today;
    
    saveData(data);
    console.log(`✅ ${platform} updated!`);
}

// Main
const args = process.argv.slice(2);
const command = args[0];

if (command === 'view' || !command) {
    view();
} else if (command === 'update') {
    const platform = args[1];
    const updates = {};
    
    for (let i = 2; i < args.length; i += 2) {
        if (args[i].startsWith('--')) {
            const key = args[i].replace('--', '');
            const value = args[i + 1];
            updates[key] = value;
        }
    }
    
    update(platform, updates);
} else if (command === 'init') {
    console.log('Analytics file exists at:', DATA_FILE);
} else {
    console.log('Usage:');
    console.log('  node analytics-tracker.js view');
    console.log('  node analytics-tracker.js update youtube --subs 100 --views 5000');
}
