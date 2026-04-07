#!/usr/bin/env node
/**
 * Local Closer V3 - Premium Demo Site Generator
 * Next Level Quality - With Animations, Testimonials, Social Proof
 */

const fs = require('fs');
const path = require('path');

const BUSINESSES = JSON.parse(fs.readFileSync('./projects/archiv/local-closer/businesses.json', 'utf8'));

const CATEGORIES = {
    restaurant: { name: "Restaurant", priceBasic: 299, pricePro: 499, pricePremium: 799, headline: "Willkommen in Ihrem Restaurant", subheadline: "Verwöhnen Sie Ihre Gäste mit einer professionellen Online-Präsenz" },
    bakery: { name: "Bäckerei", priceBasic: 249, pricePro: 399, pricePremium: 599, headline: "Ihre Bäckerei online", subheadline: "Präsentieren Sie Ihre Backwaren und Öffnungszeiten" },
    handwerk: { name: "Handwerk", priceBasic: 349, pricePro: 549, pricePremium: 849, headline: "Ihr Handwerksbetrieb im Internet", subheadline: "Professionelle Darstellung Ihrer handwerklichen Leistungen" },
    salon: { name: "Friseur/Salon", priceBasic: 279, pricePro: 449, pricePremium: 699, headline: "Ihr Salon - Schönheit online", subheadline: "Zeigen Sie Ihre Styles und Preise" },
    health: { name: "Gesundheit", priceBasic: 399, pricePro: 649, pricePremium: 949, headline: "Ihre Praxis online", subheadline: "Moderne Patientenbetreuung durch digitale Services" },
    cafe: { name: "Café", priceBasic: 249, pricePro: 399, pricePremium: 599, headline: "Ihr Café im Netz", subheadline: "Lassen Sie Ihre Gäste vorab einen Blick werfen" },
    fitness: { name: "Fitness", priceBasic: 349, pricePro: 549, pricePremium: 849, headline: "Fitnesstudio digital", subheadline: "Mitglieder gewinnen und informieren" },
    default: { name: "Gewerbe", priceBasic: 299, pricePro: 499, pricePremium: 799, headline: "Ihr Unternehmen online", subheadline: "Professionelle Präsenz im Internet" }
};

const TEMPLATE = fs.readFileSync('./projects/local-closer/templates/demo-v3-premium.html', 'utf8');

function getSlug(business) {
    return business.name.toLowerCase().replace(/[^a-z0-9äöüß]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

function generateDemoSite(business) {
    const slug = getSlug(business);
    const cat = CATEGORIES[business.category] || CATEGORIES.default;
    
    let html = TEMPLATE
        .replace(/{{BUSINESS_NAME}}/g, business.name)
        .replace(/{{CATEGORY}}/g, cat.name.toLowerCase())
        .replace(/{{HEADLINE}}/g, cat.headline)
        .replace(/{{SUBHEADLINE}}/g, cat.subheadline)
        .replace(/{{PRICE_BASIC}}/g, cat.priceBasic)
        .replace(/{{PRICE_PRO}}/g, cat.pricePro)
        .replace(/{{PRICE_PREMIUM}}/g, cat.pricePremium)
        .replace(/{{ADDRESS}}/g, business.address || 'Ihre Adresse')
        .replace(/{{PHONE}}/g, business.phone || '+49 123 456789')
        .replace(/{{EMAIL}}/g, business.email || 'info@beispiel.de')
        .replace(/{{CITY}}/g, business.city || 'Deutschland');
    
    return { html, slug };
}

function createDemoForBusiness(business) {
    const { html, slug } = generateDemoSite(business);
    const filename = `demo-${slug}.html`;
    const filepath = path.join('./projects/local-closer/demos-v3', filename);
    
    if (!fs.existsSync('./projects/local-closer/demos-v3')) {
        fs.mkdirSync('./projects/local-closer/demos-v3', { recursive: true });
    }
    
    fs.writeFileSync(filepath, html);
    return { filepath, slug };
}

const args = process.argv.slice(2);
const command = args[0];

if (command === 'run') {
    const index = parseInt(args[1]) || 0;
    const business = BUSINESSES[index];
    if (business) {
        const { slug } = createDemoForBusiness(business);
        const demoUrl = `https://empirehazeclaw.info/local-closer/demo-${slug}.html`;
        console.log(`✅ Demo erstellt: ${demoUrl}`);
    }
} else if (command === 'all') {
    console.log("🔄 Generiere Premium Demo-Sites V3...\n");
    BUSINESSES.forEach((b, i) => {
        const { slug } = createDemoForBusiness(b);
        console.log(`✅ ${i+1}. ${b.name} → demo-${slug}.html`);
    });
    console.log("\n✅ Alle V3 Demos erstellt!");
} else if (command === 'deploy') {
    console.log("🔄 Kopiere nach /var/www...");
    const { execSync } = require('child_process');
    execSync('cp projects/local-closer/demos-v3/*.html /var/www/empirehazeclaw-info/local-closer/', { stdio: 'inherit' });
    console.log("✅ Deploy abgeschlossen!");
} else {
    console.log(`
╔══════════════════════════════════════════╗
║  LOCAL CLOSER V3 - Premium Generator   ║
╠══════════════════════════════════════════╣
║  node local_closer_v3.js all            ║
║  node local_closer_v3.js run [n]       ║
║  node local_closer_v3.js deploy        ║
╚══════════════════════════════════════════╝
    `);
}
