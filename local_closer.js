#!/usr/bin/env node
/**
 * Local Closer - Automated Business Outreach System
 * Integrated into autonomous workflow system
 */

const fs = require('fs');
const path = require('path');

// Business Database
const BUSINESSES = JSON.parse(fs.readFileSync('./projects/archiv/local-closer/businesses.json', 'utf8'));

// Categories with templates
const CATEGORIES = {
    restaurant: { name: "Restaurant", price: 199, features: ["Online-Speisekarte", "Reservierungsformular", "Galerie"] },
    bakery: { name: "Bäckerei", price: 169, features: ["Sortiment-Übersicht", "Öffnungszeiten", "Kontakt"] },
    handwerk: { name: "Handwerk", price: 179, features: ["Leistungsübersicht", "Kontaktformular", "Referenzen"] },
    salon: { name: "Friseur/Salon", price: 169, features: ["Preisliste", "Öffnungszeiten", "Galerie"] },
    health: { name: "Gesundheit", price: 229, features: ["Terminbuchung", "Team-Vorstellung", "Leistungen"] },
    fitness: { name: "Fitness", price: 199, features: ["Kurse", "Preise", "Kontakt"] },
    cafe: { name: "Café", price: 179, features: ["Speisekarte", "Öffnungszeiten", "Galerie"] },
    default: { name: "Gewerbe", price: 199, features: ["Leistungen", "Kontakt", "Über uns"] }
};

function getSlug(business) {
    return business.name.toLowerCase().replace(/[^a-z0-9äöüß]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

function generateDemoSite(business) {
    const slug = getSlug(business);
    const cat = CATEGORIES[business.category] || CATEGORIES.default;
    const html = `<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${business.name} - Ihre Website</title>
    <meta name="description" content="Moderne Website für ${business.name}">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #fff; color: #333; }
        header { background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; padding: 3rem 2rem; text-align: center; }
        h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .tagline { opacity: 0.8; font-size: 1.1rem; }
        .container { max-width: 900px; margin: 0 auto; padding: 2rem; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin: 2rem 0; }
        .feature { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; }
        .feature h3 { color: #1a1a2e; margin-bottom: 0.5rem; }
        .cta { background: #e94560; color: white; padding: 1rem 2rem; border-radius: 8px; text-align: center; margin: 2rem 0; }
        .price { font-size: 2rem; font-weight: bold; }
        footer { background: #1a1a2e; color: white; text-align: center; padding: 2rem; margin-top: 2rem; }
    </style>
</head>
<body>
    <header>
        <h1>${business.name}</h1>
        <p class="tagline">Professionelle Präsenz im Internet</p>
    </header>
    <div class="container">
        <h2>Was ich für Sie tun kann</h2>
        <div class="features">
            ${cat.features.map(f => `<div class="feature"><h3>✓ ${f}</h3></div>`).join('')}
        </div>
        <div class="cta">
            <p>Ihre persönliche Website ab nur</p>
            <div class="price">€${cat.price},-</div>
            <p>inklusive: Design, Hosting, Wartung</p>
        </div>
    </div>
    <footer>
        <p>© 2026 ${business.name}</p>
    </footer>
</body>
</html>`;
    
    return { html, slug };
}

function createDemoForBusiness(business) {
    const { html, slug } = generateDemoSite(business);
    const filename = `demo-${slug}.html`;
    const filepath = path.join('./projects/local-closer/demos', filename);
    fs.writeFileSync(filepath, html);
    return { filepath, slug };
}

function runOutreach(business) {
    const { slug } = createDemoForBusiness(business);
    const cat = CATEGORIES[business.category] || CATEGORIES.default;
    const demoUrl = `https://empirehazeclaw.info/local-closer/demo-${slug}.html`;
    
    console.log(`
╔══════════════════════════════════════╗
║  📧 OUTREACH: ${business.name}
╠══════════════════════════════════════╣
║  📂 Category: ${cat.name}
║  📧 Email: ${business.email}
║  📍 City: ${business.city || 'N/A'}
║  🔗 Demo: ${demoUrl}
║  💰 Price: €${cat.price}
╚══════════════════════════════════════╝
    `);
    
    return { business, demoUrl, price: cat.price, category: cat.name };
}

// Main execution
const args = process.argv.slice(2);
const command = args[0];

if (command === 'run' || command === 'outreach') {
    const index = parseInt(args[1]) || 0;
    const business = BUSINESSES[index];
    if (business) {
        runOutreach(business);
    } else {
        console.log("❌ Business nicht gefunden");
    }
} else if (command === 'all') {
    console.log("🔄 Generiere alle Demo-Sites...\n");
    BUSINESSES.forEach((b, i) => {
        const { slug } = createDemoForBusiness(b);
        console.log(`✅ ${i+1}. ${b.name} → demo-${slug}.html`);
    });
} else if (command === 'list') {
    console.log("\n📋 Verfügbare Businesses:\n");
    BUSINESSES.forEach((b, i) => {
        const cat = CATEGORIES[b.category] || CATEGORIES.default;
        console.log(`${i}. ${b.name} (${cat.name}) - €${cat.price}`);
    });
} else {
    console.log(`
╔══════════════════════════════════════╗
║  LOCAL CLOSER - Automated Workflow  ║
╠══════════════════════════════════════╣
║  Usage:                             ║
║    node local_closer.js list        ║
║    node local_closer.js all         ║
║    node local_closer.js run [n]     ║
╚══════════════════════════════════════╝
    `);
}
