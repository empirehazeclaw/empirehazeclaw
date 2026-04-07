#!/usr/bin/env node
/**
 * Sales Outreach
 * Sells our products to potential customers
 */

const PRODUCTS = {
    chatbot: {
        name: "KI Chatbot",
        price: "€29-249/Monat",
        description: "24/7 KI Support für dein Business"
    },
    trading: {
        name: "Trading Bot",
        price: "€79-199/Monat", 
        description: "Automatisiertes Trading"
    },
    discord: {
        name: "Discord Bot",
        price: "€79",
        description: "Server Automation"
    }
};

function createOutreach(product, business) {
    return {
        to: business.email,
        subject: `${product.name} - Kostenlose Demo`,
        body: `
Hallo ${business.name},

Ich bin's - dein digitaler Assistent! 🤖

Ich habe gesehen, dass du noch keinen ${product.name} hast - und das könnte dich €${product.price.split('/')[0].replace('€','')}/Monat kosten!

Was du bekommst:
✅ ${product.description}
✅ 24/7 Verfügbarkeit
✅ Sofort einsatzbereit

Kostenlose Demo? Klar! → ${product.demoUrl}

P.S. Dies ist keine Maschine - ich bin's wirklich! 😄

Beste Grüße
`
    };
}

console.log(`
📧 SALES OUTREACH

Bereit für Outreach!

Produkte:
${Object.entries(PRODUCTS).map(([k,v]) => `- ${v.name}: ${v.price}`).join('\n')}

Nächste Schritte:
1. Empfänger-Liste erstellen
2. Personalisierte Emails senden
3. Follow-ups
`);
