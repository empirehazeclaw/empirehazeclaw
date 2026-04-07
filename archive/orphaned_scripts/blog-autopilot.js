#!/usr/bin/env node
/**
 * Blog Auto-Post System
 * Automatisiert Blog-Posts erstellen & veröffentlichen
 * 
 * Usage:
 *   node blog-autopilot.js generate "topic"     # Generate Blog Post
 *   node blog-autopilot.js publish              # Publish to .info
 *   node blog-autopilot.js schedule "topic"      # Schedule for later
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
    blogDir: '/var/www/empirehazeclaw-info',
    templateDir: '/home/clawbot/.openclaw/workspace/blogs',
    scheduleFile: '/home/clawbot/.openclaw/workspace/data/blog-schedule.json'
};

// Templates
const TEMPLATES = {
    de: {
        title: 'KI {topic} - Der komplette Guide',
        intro: 'In diesem Artikel erfährst du alles über {topic}.',
        structure: ['Was ist {topic}?', 'Vorteile', 'Anleitung', 'Fazit']
    },
    en: {
        title: 'AI {topic} - The Complete Guide',
        intro: 'In this article you will learn everything about {topic}.',
        structure: ['What is {topic}?', 'Benefits', 'How-to', 'Conclusion']
    }
};

// Generate blog post
function generate(topic, lang = 'de') {
    const template = TEMPLATES[lang] || TEMPLATES.de;
    const title = template.title.replace('{topic}', topic);
    const date = new Date().toISOString().split('T')[0];
    const slug = topic.toLowerCase().replace(/\s+/g, '-');
    
    const content = `<!DOCTYPE html>
<html lang="${lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <meta name="description" content="${template.intro.replace('{topic}', topic)}">
    <link rel="canonical" href="https://empirehazeclaw.info/posts/${slug}.html">
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #6366f1; }
        h2 { color: #333; margin-top: 2rem; }
        .meta { color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <article>
        <h1>${title}</h1>
        <p class="meta">Veröffentlicht am ${date}</p>
        
        <p>${template.intro.replace('{topic}', topic)}</p>
        
        ${template.structure.map(s => `<h2>${s.replace('{topic}', topic)}</h2><p>Content für "${s}"...</p>`).join('\n')}
        
        <h2>Fazit</h2>
        <p>${topic} ist ein wichtiges Thema für Unternehmen. Kontaktieren Sie uns für mehr Informationen.</p>
        
        <hr>
        <p><a href="/">← Zurück zur Startseite</a></p>
    </article>
</body>
</html>`;

    const filename = `${slug}.html`;
    const filepath = path.join(CONFIG.blogDir, 'posts', filename);
    
    // Ensure directory exists
    const postsDir = path.join(CONFIG.blogDir, 'posts');
    if (!fs.existsSync(postsDir)) {
        fs.mkdirSync(postsDir, { recursive: true });
    }
    
    fs.writeFileSync(filepath, content);
    console.log(`✅ Blog Post erstellt: ${filepath}`);
    
    return { title, slug, filepath };
}

// Publish to blog
function publish() {
    const postsDir = path.join(CONFIG.blogDir, 'posts');
    if (!fs.existsSync(postsDir)) {
        console.log('❌ Keine Posts gefunden');
        return;
    }
    
    const files = fs.readdirSync(postsDir).filter(f => f.endsWith('.html'));
    console.log(`📤 ${files.length} Posts verfügbar zum Publish`);
    
    files.forEach(f => {
        console.log(`  - ${f}`);
    });
}

// Schedule
function schedule(topic, date) {
    let schedule = [];
    
    try {
        schedule = JSON.parse(fs.readFileSync(CONFIG.scheduleFile, 'utf8'));
    } catch {}
    
    schedule.push({ topic, date, status: 'pending' });
    fs.writeFileSync(CONFIG.scheduleFile, JSON.stringify(schedule, null, 2));
    
    console.log(`✅ "${topic}" geplant für ${date}`);
}

// CLI
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'generate') {
    const topic = args.slice(1).join(' ');
    generate(topic);
} else if (cmd === 'publish') {
    publish();
} else if (cmd === 'schedule') {
    const topic = args[1];
    const date = args[2] || new Date().toISOString().split('T')[0];
    schedule(topic, date);
} else {
    console.log('Blog Auto-Pilot');
    console.log(`
Usage:
  node blog-autopilot.js generate "topic"     # Generate Blog Post
  node blog-autopilot.js publish              # Publish to .info
  node blog-autopilot.js schedule "topic"     # Schedule for later
    `);
}
