#!/usr/bin/env node
/**
 * Outreach Email Generator
 * Sells demo sites to local businesses
 */

const CATEGORIES = {
    restaurant: {
        subject: "Ihre kostenlose Website - Restaurant {name}",
        template: `
Sehr geehrte/r {name},

ich bins - Ihr digitaler Assistent! 🤖

Ich habe gerade eine **kostenlose Demo-Webseite** für {business_name} erstellt!

Was Sie sehen:
✅ Moderne Webseite mit Menü
✅ Für Mobile optimiert  
✅ Kontaktformular inklusive

🔗 Ihre Demo: {preview_link}

Keine Verpflichtung - schauen Sie einfach mal rein!

P.S. Diese Webseite ist 100% kostenlos für Sie - ich zeige Ihnen nur, was möglich ist.

Beste Grüße
`
    },
    plumber: {
        subject: "Kostenlose Webseite für {name}",
        template: `
Guten Tag,

Ich bins - 🤖

Ich habe eine **kostenlose Demo-Webseite** für {business_name} erstellt!

Highlights:
✅ 24/7 Online präsent
✅ Kunden können Sie sofort kontaktieren
✅ Modern & professionell

📸 Schauen Sie rein: {preview_link}

Kein Risiko - nur eine Demo!

Beste Grüße
`
    },
    default: {
        subject: "Ihre kostenlose Website - {name}",
        template: `
Hallo {contact_name},

ich bins - 🤖 Ihr digitaler Assistent!

Ich habe eine **kostenlose Demo-Webseite** für {business_name} erstellt!

Was Sie bekommen:
✅ Moderne, professionelle Webseite
✅ Auf Google gefunden werden
✅ Kunden können Sie einfach kontaktieren

👀 Hier rein schauen: {preview_link}

Kostenlos & unverbindlich!

Beste Grüße
`
    }
};

function generateEmail(business, demoLink) {
    const template = CATEGORIES[business.category] || CATEGORIES.default;
    
    const email = {
        to: business.email || "business@example.com",
        subject: template.subject.replace(/{name}|{business_name}/g, business.name),
        body: template.template
            .replace(/{name}|{contact_name}/g, business.contact || "Inhaber")
            .replace(/{business_name}/g, business.name)
            .replace(/{preview_link}/g, demoLink),
        stage: 1
    };
    
    return email;
}

function generateSequence() {
    return [
        { day: 0, type: "initial", subject: "Ihre kostenlose Demo" },
        { day: 2, type: "followup", subject: "Fragen zur Demo?" },
        { day: 5, type: "urgency", subject: "Demo läuft ab" }
    ];
}

// CLI
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'email') {
    const business = {
        name: args[1] || "Mario's Pizza",
        category: args[2] || "restaurant",
        email: args[3] || "mario@example.com",
        contact: "Mario"
    };
    const demoLink = args[4] || "https://demo.empirehazeclaw.de/mario";
    
    const email = generateEmail(business, demoLink);
    
    console.log('\n📧 OUTREACH EMAIL\n');
    console.log(`To: ${email.to}`);
    console.log(`Subject: ${email.subject}\n`);
    console.log(email.body);
}
else if (cmd === 'sequence') {
    console.log('\n📋 EMAIL SEQUENCE\n');
    generateSequence().forEach(s => {
        console.log(`Day ${s.day}: ${s.type} - ${s.subject}`);
    });
}
else {
    console.log(`
📧 OUTREACH SYSTEM

Usage:
  node outreach.js email "Business Name" "category" "email@..." "demo-link"
  node outreach.js sequence
`);
}
