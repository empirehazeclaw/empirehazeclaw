#!/usr/bin/env node
/**
 * Newsletter System - Full Integration
 * Blog Post → Newsletter via Brevo
 * 
 * Usage:
 *   node newsletter-send.js send-latest    # Send latest blog post
 *   node newsletter-send.js send-url "url" # Send specific URL
 *   node newsletter-send.js test            # Send test
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BLOG_URL = 'https://empirehazeclaw.info/posts';

// Get latest blog posts
function getLatestPosts(count = 3) {
    try {
        const postsDir = '/var/www/empirehazeclaw-info/posts';
        if (!fs.existsSync(postsDir)) return [];
        
        const files = fs.readdirSync(postsDir)
            .filter(f => f.endsWith('.html'))
            .sort()
            .reverse()
            .slice(0, count);
        
        return files.map(f => ({
            file: f,
            url: `${BLOG_URL}/${f}`,
            title: f.replace('.html', '').replace(/-/g, ' ')
        }));
    } catch {
        return [];
    }
}

// Generate newsletter HTML
function generateNewsletter(posts) {
    const postsHtml = posts.map(p => `
        <div style="margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0;">📝 ${p.title}</h3>
            <p style="margin: 0 0 10px 0;">Lesen Sie mehr...</p>
            <a href="${p.url}" style="display: inline-block; background: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Artikel lesen →</a>
        </div>
    `).join('');
    
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EmpireHazeClaw Newsletter</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    
    <div style="background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="margin: 0; font-size: 28px;">🦞 EmpireHazeClaw</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">KI & Automation Insights</p>
    </div>
    
    <div style="background: #f9f9f9; padding: 30px;">
        <h2 style="color: #6366f1; margin-top: 0;">Hallo! 👋</h2>
        <p>Will zu unserem wöchentlichen Update! Hier sind die neuesten Artikel:</p>
        
        ${postsHtml}
        
        <div style="margin: 30px 0; padding: 20px; background: white; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0;">🚀 KI & Automation Services</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li>KI Chatbots - ab €49/Monat</li>
                <li>Trading Bots - ab €79/Monat</li>
                <li>Discord Bots - ab €79</li>
                <li>Landing Pages - ab €199</li>
            </ul>
            <a href="https://empirehazeclaw.store" style="display: inline-block; margin-top: 15px; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Zum Shop →</a>
        </div>
        
        <p style="margin-top: 30px;">Beste Grüße,<br>Nico 🦞</p>
    </div>
    
    <div style="background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px;">
        <p>EmpireHazeClaw - KI & Automation Solutions</p>
        <p>
            <a href="https://empirehazeclaw.de" style="color: #6366f1;">Website</a> | 
            <a href="https://empirehazeclaw.store" style="color: #6366f1;">Shop</a> | 
            <a href="https://empirehazeclaw.info" style="color: #6366f1;">Blog</a>
        </p>
        <p style="opacity: 0.6; margin-top: 15px;">
            Sie erhalten diese Email, weil Sie sich für unseren Newsletter angemeldet haben.<br>
            <a href="https://empirehazeclaw.de/unsubscribe" style="color: #6366f1;">Abmelden</a>
        </p>
    </div>
</body>
</html>`;
}

// Send newsletter
async function sendNewsletter(posts) {
    const html = generateNewsletter(posts);
    
    console.log('\n📧 Sende Newsletter...\n');
    console.log(`Posts: ${posts.length}`);
    console.log(`Empfänger: Test (empirehazeclaw@gmail.com)\n`);
    
    const { execSync } = require('child_process');
    
    try {
        execSync(`node "${BREVO_SCRIPT}" send --to "empirehazeclaw@gmail.com" --subject "🦞 Neueste Artikel von EmpireHazeClaw - KW12" --body "${html.replace(/"/g, '\\"')}" --html`, {
            stdio: 'inherit'
        });
    } catch (e) {
        console.log('Brevo call failed, saving locally...');
        fs.writeFileSync('/tmp/newsletter_latest.html', html);
        console.log('Saved to /tmp/newsletter_latest.html');
    }
}

// CLI
async function main() {
    const args = process.argv.slice(2);
    const cmd = args[0];
    
    if (cmd === 'send-latest' || cmd === 'send') {
        const posts = getLatestPosts(3);
        console.log('📝 Neueste Posts:', posts.map(p => p.title));
        await sendNewsletter(posts);
        
    } else if (cmd === 'test') {
        const posts = [{ title: 'Test Artikel', url: 'https://empirehazeclaw.de' }];
        await sendNewsletter(posts);
        
    } else if (cmd === 'preview') {
        const posts = getLatestPosts(3);
        console.log(generateNewsletter(posts));
        
    } else {
        console.log(`
📧 Newsletter System

Usage:
  node newsletter-send.js send-latest    # Sende neueste Posts
  node newsletter-send.js preview        # Vorschau
  node newsletter-send.js test          # Test Email
        `);
    }
}

main();
