#!/usr/bin/env node
/**
 * Newsletter Automation System
 * Erstellt & versendet Newsletter Templates
 * 
 * Usage:
 *   node newsletter.js template "topic"    # Generate Template
 *   node newsletter.js preview             # Preview HTML
 */

const fs = require('fs');
const path = require('path');

const TEMPLATE = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .content h2 {{ color: #6366f1; }}
        .content ul {{ padding-left: 20px; }}
        .content li {{ margin: 10px 0; }}
        .cta {{ display: inline-block; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
        .footer a {{ color: #6366f1; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦞 EmpireHazeClaw</h1>
        <p>KI & Automation Insights</p>
    </div>
    
    <div class="content">
        <h2>Hallo {name}! 👋</h2>
        
        {content}
        
        <p style="margin-top: 30px;">Beste Grüße,<br>Nico 🦞</p>
    </div>
    
    <div class="footer">
        <p>EmpireHazeClaw - KI & Automation Solutions</p>
        <p>
            <a href="https://empirehazeclaw.de">Website</a> | 
            <a href="https://empirehazeclaw.store">Shop</a> | 
            <a href="https://empirehazeclaw.info">Blog</a>
        </p>
        <p style="margin-top: 20px; opacity: 0.6;">
            Du erhältst diese Email, weil du dich für unseren Newsletter angemeldet hast.<br>
            <a href="{unsubscribe}">Abmelden</a>
        </p>
    </div>
</body>
</html>`;

// Content Sections
const SECTIONS = {
    update: `
        <h2>📣 Updates von EmpireHazeClaw</h2>
        <ul>
            <li><strong>Neue Features:</strong> {features}</li>
            <li><strong>Blog Posts:</strong> {blog_posts}</li>
        </ul>
    `,
    
    tip: `
        <h2>💡 Quick Tip</h2>
        <p>{tip_content}</p>
    `,
    
    offer: `
        <h2>🔥 Special Angebot</h2>
        <p>{offer_content}</p>
        <a href="{offer_link}" class="cta">Jetzt zugreifen →</a>
    `
};

// Generate newsletter
function generate(data) {
    let content = TEMPLATE;
    
    // Replace placeholders
    content = content.replace('{subject}', data.subject || 'Dein wöchentlicher KI-Update');
    content = content.replace('{name}', data.name || 'Leser');
    content = content.replace('{unsubscribe}', data.unsubscribe || 'https://empirehazeclaw.de/unsubscribe');
    
    // Build content section
    let contentHtml = '';
    
    if (data.sections) {
        for (const section of data.sections) {
            if (SECTIONS[section.type]) {
                let sectionHtml = SECTIONS[section.type];
                for (const [key, value] of Object.entries(section.data || {})) {
                    sectionHtml = sectionHtml.replace(`{${key}}`, value);
                }
                contentHtml += sectionHtml;
            }
        }
    }
    
    content = content.replace('{content}', contentHtml || '<p>Keine neuen Updates diese Woche.</p>');
    
    return content;
}

// Preview
function preview() {
    const sample = {
        subject: 'Dein wöchentlicher KI-Update - KW12',
        name: 'Nico',
        sections: [
            { type: 'update', data: { features: 'Trading Bot jetzt live!', blog_posts: '3 neue Artikel' }},
            { type: 'tip', data: { tip_content: 'Automatisier deinen Newsletter mit KI - spar 80% Zeit!' }},
            { type: 'offer', data: { offer_content: '20% Rabatt auf alle Services diese Woche!', offer_link: 'https://empirehazeclaw.store' }}
        ],
        unsubscribe: 'https://empirehazeclaw.de/unsubscribe'
    };
    
    console.log(generate(sample));
}

// Send (placeholder)
function send() {
    console.log('📤 Newsletter senden...');
    console.log('Alternativ: Export als HTML und manuell versenden');
}

// CLI
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'preview') {
    preview();
} else if (cmd === 'send') {
    send();
} else if (cmd === 'template') {
    const topic = args.slice(1).join(' ');
    console.log('Generiere Template für:', topic);
    
    const template = {
        subject: `Update zu: ${topic}`,
        sections: [
            { type: 'update', data: { features: '...', blog_posts: '...' }},
            { type: 'tip', data: { tip_content: '...' }}
        ]
    };
    
    console.log('\n=== Template ===\n');
    console.log(generate(template));
} else {
    console.log('Newsletter Automation');
    console.log(`
Usage:
  node newsletter.js template "topic"    # Generate Template
  node newsletter.js preview             # Preview HTML
    `);
}
