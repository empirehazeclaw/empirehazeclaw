#!/usr/bin/env node
/**
 * Local Closer V2 - Professional Demo Site Generator
 * Improved Quality - Professional Templates
 */

const fs = require('fs');
const path = require('path');

// Business Database
const BUSINESSES = JSON.parse(fs.readFileSync('./projects/archiv/local-closer/businesses.json', 'utf8'));

// Category configurations
const CATEGORIES = {
    restaurant: { 
        name: "Restaurant", 
        priceBasic: 299, 
        pricePro: 499, 
        pricePremium: 799,
        headline: "Willkommen in Ihrem Restaurant",
        subheadline: "Verwöhnen Sie Ihre Gäste mit einer professionellen Online-Präsenz",
        features: ["Online-Speisekarte", "Reservierungssystem", "Galerie", "Bewertungen"]
    },
    bakery: { 
        name: "Bäckerei", 
        priceBasic: 249, 
        pricePro: 399, 
        pricePremium: 599,
        headline: "Ihre Bäckerei online",
        subheadline: "Präsentieren Sie Ihre Backwaren und Öffnungszeiten",
        features: ["Sortiment-Übersicht", "Bestellsystem", "Öffnungszeiten", "Filialfinder"]
    },
    handwerk: { 
        name: "Handwerk", 
        priceBasic: 349, 
        pricePro: 549, 
        pricePremium: 849,
        headline: "Ihr Handwerksbetrieb im Internet",
        subheadline: "Professionelle Darstellung Ihrer handwerklichen Leistungen",
        features: ["Leistungsübersicht", "Projekt-Galerie", "Referenzen", "Angebotsanfrage"]
    },
    salon: { 
        name: "Friseur/Salon", 
        priceBasic: 279, 
        pricePro: 449, 
        pricePremium: 699,
        headline: "Ihr Salon - Schönheit online",
        subheadline: "Zeigen Sie Ihre Styles und Preise",
        features: ["Preisliste", "Online-Buchung", "Galerie", "Gutschein-System"]
    },
    health: { 
        name: "Gesundheit", 
        priceBasic: 399, 
        pricePro: 649, 
        pricePremium: 949,
        headline: "Ihre Praxis online",
        subheadline: "Moderne Patientenbetreuung durch digitale Services",
        features: ["Terminbuchung", "Team-Vorstellung", "Leistungen", "Kontaktformular"]
    },
    cafe: { 
        name: "Café", 
        priceBasic: 249, 
        pricePro: 399, 
        pricePremium: 599,
        headline: "Ihr Café im Netz",
        subheadline: "Lassen Sie Ihre Gäste vorab einen Blick werfen",
        features: ["Speisekarte", "Event-Kalender", "Galerie", "Bewertungen"]
    },
    fitness: { 
        name: "Fitness", 
        priceBasic: 349, 
        pricePro: 549, 
        pricePremium: 849,
        headline: "Fitnesstudio digital",
        subheadline: "Mitglieder gewinnen und informieren",
        features: ["Kurse-Übersicht", "Mitgliedschaft", "Trainer-Vorstellung", "Testimonial"]
    },
    default: { 
        name: "Gewerbe", 
        priceBasic: 299, 
        pricePro: 499, 
        pricePremium: 799,
        headline: "Ihr Unternehmen online",
        subheadline: "Professionelle Präsenz im Internet",
        features: ["Leistungen", "Über uns", "Kontaktformular", "Referenzen"]
    }
};

const TEMPLATE = fs.readFileSync('./projects/local-closer/templates/demo-v2-professional.html', 'utf8');

function getSlug(business) {
    return business.name.toLowerCase().replace(/[^a-z0-9äöüß]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

function generateDemoSite(business) {
    const slug = getSlug(business);
    const cat = CATEGORIES[business.category] || CATEGORIES.default;
    
    // Replace placeholders
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
        .replace(/{{EMAIL}}/g, business.email || 'info@beispiel.de');
    
    return { html, slug };
}

function createDemoForBusiness(business) {
    const { html, slug } = generateDemoSite(business);
    const filename = `demo-${slug}.html`;
    const filepath = path.join('./projects/local-closer/demos-v2', filename);
    
    // Create directory
    if (!fs.existsSync('./projects/local-closer/demos-v2')) {
        fs.mkdirSync('./projects/local-closer/demos-v2', { recursive: true });
    }
    
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
║  💰 Price: €${cat.pricePro}
╚══════════════════════════════════════╝
    `);
    
    return { business, demoUrl, price: cat.pricePro, category: cat.name };
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
    console.log("🔄 Generiere professionelle Demo-Sites V2...\n");
    BUSINESSES.forEach((b, i) => {
        const { slug } = createDemoForBusiness(b);
        console.log(`✅ ${i+1}. ${b.name} → demo-${slug}.html`);
    });
} else if (command === 'list') {
    console.log("\n📋 Verfügbare Businesses:\n");
    BUSINESSES.forEach((b, i) => {
        const cat = CATEGORIES[b.category] || CATEGORIES.default;
        console.log(`${i}. ${b.name} (${cat.name}) - ab €${cat.priceBasic}`);
    });
} else {
    console.log(`
╔══════════════════════════════════════╗
║  LOCAL CLOSER V2 - Professional    ║
╠══════════════════════════════════════╣
║  Usage:                             ║
║    node local_closer_v2.js list    ║
║    node local_closer_v2.js all    ║
║    node local_closer_v2.js run [n] ║
╚══════════════════════════════════════╝
    `);
}
