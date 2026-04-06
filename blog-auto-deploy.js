#!/usr/bin/env node
/**
 * Blog Auto-Deploy Script
 * Converts MD files to HTML and deploys to Vercel
 * 
 * Usage: node blog-auto-deploy.js [--watch] [--deploy]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const BLOG_DIR = '/home/clawbot/.openclaw/workspace/projects/landing-pages/info';
const CONTENT_DIR = path.join(BLOG_DIR, 'content');
const POSTS_DIR = path.join(BLOG_DIR, 'posts');
const DE_POSTS_DIR = path.join(POSTS_DIR, 'de');
const EN_POSTS_DIR = path.join(POSTS_DIR, 'en');

// Load marked (from openclaw's node_modules)
const markedPath = '/home/clawbot/.npm-global/lib/node_modules/openclaw/node_modules/marked';
const { marked } = require(markedPath);

// Simple frontmatter parser
function parseFrontmatter(content) {
    const frontmatter = {};
    const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    
    if (match) {
        const lines = match[1].split('\n');
        lines.forEach(line => {
            const [key, ...valueParts] = line.split(':');
            if (key && valueParts.length > 0) {
                const value = valueParts.join(':').trim().replace(/^["']|["']$/g, '');
                frontmatter[key.trim()] = value;
            }
        });
        return {
            frontmatter,
            body: match[2]
        };
    }
    return { frontmatter: {}, body: content };
}

// Convert slug to filename
function slugToFilename(slug) {
    return slug.toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '') + '.html';
}

// Detect language from frontmatter or filename
function detectLanguage(frontmatter, filename) {
    if (frontmatter.lang === 'en') return 'en';
    if (filename.includes('-en.') || filename.includes('_en.')) return 'en';
    return 'de';
}

// Generate HTML from markdown with proper inline CSS
function markdownToHtml(markdown, frontmatter, lang) {
    const content = marked.parse(markdown);
    const title = frontmatter.title || 'Blog Post';
    const description = frontmatter.description || '';
    const date = frontmatter.date || new Date().toISOString().split('T')[0];
    const tags = frontmatter.tags ? frontmatter.tags.replace(/[\[\]]/g, '').split(',').map(t => t.trim()) : [];
    const category = tags[0] || (lang === 'de' ? 'KI & Business' : 'AI & Business');
    
    const ctaLink = lang === 'de' ? 'https://empirehazeclaw.de' : 'https://empirehazeclaw.com';
    const ctaText = lang === 'de' ? 'Mehr erfahren' : 'Learn more';
    const backText = lang === 'de' ? '← Zurück zum Blog' : '← Back to Blog';
    
    return `<!DOCTYPE html>
<html lang="${lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} | EmpireHazeClaw</title>
    <meta name="description" content="${description}">
    ${tags.map(t => `<meta name="keywords" content="${t}">`).join('\n    ')}
    <meta property="og:title" content="${title}">
    <meta property="og:description" content="${description}">
    <meta property="og:type" content="article">
    <style>
        *{box-sizing:border-box}
        body{font-family:system-ui;margin:0;padding:0;background:#0a0a0f;color:#e8e8e8;line-height:1.7}
        a{color:#c9a227;text-decoration:none}
        a:hover{text-decoration:underline}
        header{background:linear-gradient(135deg,#1a1a2e,#0a0a0f);padding:20px;text-align:center}
        .logo{font-size:1.5em;font-weight:bold;color:#c9a227;text-decoration:none}
        .back-link{display:inline-block;margin-top:10px;color:#888;font-size:0.9em}
        article{max-width:800px;margin:0 auto;padding:40px 20px}
        .post-header{text-align:center;margin-bottom:40px}
        .category{display:inline-block;background:#c9a227;color:#000;padding:4px 12px;border-radius:4px;font-size:0.85em;font-weight:600;margin-bottom:15px}
        h1{color:#fff;font-size:2.2em;margin:10px 0;line-height:1.3}
        .meta{color:#888;font-size:0.95em;margin-top:10px}
        .post-content{background:#151520;padding:40px;border-radius:16px}
        .lead{font-size:1.15em;color:#ddd;border-left:4px solid #c9a227;padding-left:20px;margin-bottom:30px}
        h2{color:#c9a227;font-size:1.5em;margin:40px 0 20px;border-bottom:1px solid #333;padding-bottom:10px}
        h3{color:#fff;font-size:1.2em;margin:30px 0 15px}
        p{color:#ccc;margin:15px 0}
        ul,ol{color:#ccc;margin:15px 0;padding-left:25px}
        li{margin:8px 0}
        strong{color:#fff}
        table{width:100%;border-collapse:collapse;margin:25px 0;background:#0a0a0f;border-radius:8px;overflow:hidden}
        th{background:#c9a227;color:#000;padding:12px 15px;text-align:left;font-weight:600}
        td{padding:12px 15px;border-bottom:1px solid #333;color:#ccc}
        tr:last-child td{border-bottom:none}
        .cta-box{background:linear-gradient(135deg,#1a1a2e,#0f0f1a);border:2px solid #c9a227;border-radius:12px;padding:30px;text-align:center;margin:40px 0}
        .cta-box h3{color:#c9a227;font-size:1.4em;margin:0 0 15px}
        .cta-box p{color:#ccc;margin:0 0 20px}
        .cta-button{display:inline-block;background:#c9a227;color:#000;padding:14px 28px;border-radius:8px;font-weight:bold;font-size:1.1em;transition:transform 0.2s}
        .cta-button:hover{transform:scale(1.05);text-decoration:none}
        footer{background:#050508;padding:40px;text-align:center;color:#666;margin-top:60px}
        footer a{color:#c9a227}
        .disclaimer{font-size:0.85em;color:#666;text-align:center;margin-top:40px;font-style:italic}
        img{max-width:100%;height:auto;border-radius:8px;margin:20px 0}
        blockquote{border-left:4px solid #c9a227;padding-left:20px;margin:20px 0;color:#ccc;font-style:italic}
        code{background:#0a0a0f;padding:2px 6px;border-radius:4px;font-size:0.95em}
        pre{background:#0a0a0f;padding:20px;border-radius:8px;overflow-x:auto;margin:20px 0}
        pre code{background:none;padding:0}
    </style>
</head>
<body>
    <header>
        <a href="https://empirehazeclaw.info/" class="logo">🏢 EmpireHazeClaw</a>
        <br>
        <a href="https://empirehazeclaw.info/blog.html" class="back-link">${backText}</a>
    </header>

    <article>
        <div class="post-header">
            <span class="category">📰 ${category}</span>
            <h1>${title}</h1>
            <p class="meta">📅 ${date}</p>
        </div>

        <div class="post-content">
            ${content}
            
            <div class="cta-box">
                <h3>🚀 ${lang === 'de' ? 'Managed AI Hosting – direkt starten' : 'Managed AI Hosting – start today'}</h3>
                <p>${lang === 'de' ? 'Deutsche Server, DSGVO-konform, ohne technisches Vorwissen.' : 'German servers, GDPR-compliant, no technical knowledge required.'}</p>
                <a href="${ctaLink}" class="cta-button">${ctaText} →</a>
            </div>
        </div>
    </article>

    <footer>
        <p><a href="https://empirehazeclaw.info/">EmpireHazeClaw</a> – ${lang === 'de' ? 'KI-Lösungen für deutsche Unternehmen' : 'AI solutions for European businesses'}</p>
    </footer>
</body>
</html>`;
}

// Extract slug from filename
function extractSlug(filename) {
    return filename
        .replace(/\.md$/, '')
        .replace(/^de[_-]/, '')
        .replace(/^en[_-]/, '');
}

// Process a single markdown file
function processMarkdownFile(filepath) {
    const filename = path.basename(filepath);
    console.log(`📄 Processing: ${filename}`);
    
    // Read and parse file
    const content = fs.readFileSync(filepath, 'utf-8');
    const { frontmatter, body } = parseFrontmatter(content);
    
    // Detect language
    const lang = detectLanguage(frontmatter, filename);
    const targetDir = lang === 'en' ? EN_POSTS_DIR : DE_POSTS_DIR;
    
    // Generate output filename
    const slug = frontmatter.slug || extractSlug(filename);
    const outputFilename = slugToFilename(slug);
    const outputPath = path.join(targetDir, outputFilename);
    
    // Convert to HTML
    const html = markdownToHtml(body, frontmatter, lang);
    
    // Write HTML file
    fs.writeFileSync(outputPath, html, 'utf-8');
    console.log(`✅ Created: ${outputPath}`);
    
    return { filepath, outputPath, lang };
}

// Deploy to Vercel
function deployToVercel() {
    console.log('🚀 Deploying to Vercel...');
    try {
        execSync('vercel --prod --yes', {
            cwd: BLOG_DIR,
            stdio: 'inherit'
        });
        console.log('✅ Deployment complete!');
        return true;
    } catch (error) {
        console.error('❌ Deployment failed:', error.message);
        return false;
    }
}

// Watch mode using fs.watch
function watchMode() {
    console.log('👀 Watching for changes in:', CONTENT_DIR);
    console.log('Press Ctrl+C to stop.\n');
    
    // Initial scan
    scanAndDeploy();
    
    // Watch for changes
    fs.watch(CONTENT_DIR, { persistent: true }, (eventType, filename) => {
        if (filename && filename.endsWith('.md')) {
            console.log(`\n📝 Change detected: ${filename} (${eventType})`);
            setTimeout(() => scanAndDeploy(), 500);
        }
    });
}

// Scan content dir and deploy
function scanAndDeploy() {
    try {
        const files = fs.readdirSync(CONTENT_DIR).filter(f => f.endsWith('.md'));
        
        if (files.length === 0) {
            console.log('No markdown files found.');
            return;
        }
        
        console.log(`Found ${files.length} markdown file(s):`);
        
        const processed = [];
        files.forEach(file => {
            const filepath = path.join(CONTENT_DIR, file);
            processed.push(processMarkdownFile(filepath));
        });
        
        console.log('\n' + '='.repeat(50));
        
        // Deploy
        deployToVercel();
        
        // Log processed files
        processed.forEach(p => {
            console.log(`🌐 ${p.lang === 'de' ? '🇩🇪' : '🇬🇧'} ${path.basename(p.outputPath)}`);
        });
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Main
function main() {
    const args = process.argv.slice(2);
    const watch = args.includes('--watch');
    const deployOnly = args.includes('--deploy-only');
    
    if (watch) {
        watchMode();
    } else if (deployOnly) {
        deployToVercel();
    } else {
        scanAndDeploy();
    }
}

main();
