#!/usr/bin/env node
/**
 * SEO Tags Generator
 * Generates SEO meta tags for all pages
 */

const PAGES = {
    'index': {
        title: 'EmpireHazeClaw - AI Solutions & Automation',
        description: 'AI Chatbots, Trading Bots, Discord Bots und Automation Lösungen für Ihr Business. Professionelle KI-Entwicklung aus Deutschland.',
        keywords: 'KI, AI, Chatbot, Trading Bot, Discord Bot, Automation, Deutschland',
        ogTitle: 'EmpireHazeClaw - AI Solutions',
        ogDesc: 'AI Chatbots, Trading Bots & mehr'
    },
    'chatbot': {
        title: 'KI Chatbot - Professionelle AI Assistants',
        description: 'Maßgeschneiderte KI Chatbots für Unternehmen. 24/7 Support, Lead Generation, Customer Service.',
        keywords: 'KI Chatbot, AI Chatbot, Kundenservice, Support Bot',
        ogTitle: 'KI Chatbot Lösungen',
        ogDesc: '24/7 KI Support für Ihr Business'
    },
    'trading-bot': {
        title: 'Trading Bot - Automatisierter Handel',
        description: 'Professionelle Trading Bots für automatisierten Handel. Backtesting, Strategien, Paper Trading.',
        keywords: 'Trading Bot, Auto Trading, Algorithmic Trading, Bitcoin',
        ogTitle: 'Trading Bot Automation',
        ogDesc: 'Automatisierten Handel mit KI'
    },
    'discord-bot': {
        title: 'Discord Bot - Server Automation',
        description: 'Individuelle Discord Bots für Server Management, Moderation, und Automation.',
        keywords: 'Discord Bot, Server Bot, Moderation, Discord Automation',
        ogTitle: 'Discord Bot Entwicklung',
        ogDesc: 'Maßgeschneiderte Discord Bots'
    },
    'services': {
        title: 'Services - AI & Development',
        description: 'Unsere Services: KI Entwicklung, Webentwicklung, Discord Bots, Trading Bots, Consulting.',
        keywords: 'KI Entwicklung, Webentwicklung, Discord Bot, Trading Bot, Consulting',
        ogTitle: 'Unsere Services',
        ogDesc: 'Professionelle AI Entwicklung'
    },
    'pricing': {
        title: 'Preise - KI Solutions',
        description: 'Transparente Preise für alle KI Lösungen. Starter ab €29/Monat, Enterprise auf Anfrage.',
        keywords: 'Preise, Kosten, KI Chatbot, Trading Bot, Enterprise',
        ogTitle: 'Preise - EmpireHazeClaw',
        ogDesc: 'Transparente Preise für KI Lösungen'
    },
    'about': {
        title: 'Über uns - EmpireHazeClaw',
        description: 'Wir entwickeln innovative KI Lösungen für Unternehmen. Deutschland, Berlin.',
        keywords: 'Über uns, KI Unternehmen, Berlin, Development',
        ogTitle: 'Über EmpireHazeClaw',
        ogDesc: 'KI Innovation aus Deutschland'
    },
    'blog': {
        title: 'Blog - KI & Tech Insights',
        description: 'Aktuelle Artikel über KI, Trading, Automation und Tech. Tutorials, Guides, News.',
        keywords: 'Blog, KI, Tech, Trading, Automation, Tutorial',
        ogTitle: 'Blog - EmpireHazeClaw',
        ogDesc: 'KI & Tech Insights'
    },
    'newsletter': {
        title: 'Newsletter - AI Updates',
        description: 'Newsletter für KI Updates, Tech News und exklusive Angebote. Kostenlos abonnieren!',
        keywords: 'Newsletter, KI Newsletter, Tech Newsletter, Free',
        ogTitle: 'Newsletter - Kostenlos',
        ogDesc: 'KI Updates gratis erhalten'
    }
};

function generateTags(page) {
    const p = PAGES[page] || PAGES['index'];
    
    return `
    <!-- SEO Meta Tags -->
    <meta name="description" content="${p.description}">
    <meta name="keywords" content="${p.keywords}">
    <meta name="author" content="EmpireHazeClaw">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://empirehazeclaw.de/${page === 'index' ? '' : page}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="${p.ogTitle}">
    <meta property="og:description" content="${p.ogDesc}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://empirehazeclaw.de/${page === 'index' ? '' : page}">
    <meta property="og:site_name" content="EmpireHazeClaw">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${p.ogTitle}">
    <meta name="twitter:description" content="${p.ogDesc}">
    
    <!-- Schema.org -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "EmpireHazeClaw",
      "url": "https://empirehazeclaw.de",
      "description": "${p.description}"
    }
    </script>`;
}

const args = process.argv.slice(2);
const page = args[0] || 'index';

console.log(generateTags(page));
