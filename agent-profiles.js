#!/usr/bin/env node
/**
 * Agent Profiles - Stärken & Spezialisierungen
 * Jeder Agent hat definierte Stärken
 */

const AGENTS = {
    research: {
        name: 'Research Agent',
        emoji: '🔍',
        stärken: [
            'Web Search & Recherche',
            'Competitor Analysis',
            'Marktforschung',
            'Trend-Identifikation',
            'Daten-Analyse'
        ],
        keywords: ['research', 'recherchiere', 'suche', 'analysiere', 'finde', 'vergleiche'],
        tools: ['web_search', 'web_fetch', 'tavily'],
        color: '🔍'
    },
    
    content: {
        name: 'Content Agent',
        emoji: '✍️',
        stärken: [
            'Blog Posts schreiben',
            'Social Media Content',
            'SEO-Optimierung',
            'Email Marketing',
            'Copywriting'
        ],
        keywords: ['blog', 'post', 'artikel', 'schreibe', 'content', 'beschreibe'],
        tools: ['write', 'memory'],
        color: '✍️'
    },
    
    dev: {
        name: 'Developer Agent',
        emoji: '💻',
        stärken: [
            'Code schreiben & debuggen',
            'API Integration',
            'Deployment',
            'Scripting',
            'Infrastructure'
        ],
        keywords: ['code', 'fix', 'bug', 'entwickle', 'programmiere', 'deploy', 'erstelle'],
        tools: ['exec', 'write', 'edit'],
        color: '💻'
    },
    
    social: {
        name: 'Social Media Agent',
        emoji: '📱',
        stärken: [
            'Twitter/X Posts',
            'TikTok Content',
            'Instagram',
            'Engagement Strategies',
            'Viral Content'
        ],
        keywords: ['twitter', 'social', 'tiktok', 'instagram', 'post', 'kampagne'],
        tools: ['xurl', 'browser', 'tts'],
        color: '📱'
    },
    
    trading: {
        name: 'Trading Agent',
        emoji: '📈',
        stärken: [
            'Trading Signale',
            'Market Analysis',
            'Crypto/Stock Trading',
            'Bot Entwicklung',
            'Risk Management'
        ],
        keywords: ['trading', 'crypto', 'trade', 'binance', 'invest', 'aktie'],
        tools: ['exec (Python)', 'api'],
        color: '📈'
    },
    
    revenue: {
        name: 'Revenue Agent',
        emoji: '💰',
        stärken: [
            'Lead Generation',
            'Outreach',
            'Sales',
            'Kunden-Akquise',
            'Pricing Strategien'
        ],
        keywords: ['sales', 'verkauf', 'outreach', 'lead', 'kunde', 'umsatz'],
        tools: ['gog', 'message'],
        color: '💰'
    },
    
    pod: {
        name: 'POD Agent',
        emoji: '🎨',
        stärken: [
            'Print on Demand Designs',
            'Etsy Listings',
            'Printify Integration',
            'Produkt-Designs',
            'SEO für POD'
        ],
        keywords: ['pod', 'etsy', 'design', 'druck', 't-shirt', 'merch'],
        tools: ['browser', 'memory'],
        color: '🎨'
    },
    
    debugger: {
        name: 'Debugger Agent',
        emoji: '🔧',
        stärken: [
            'Fehler-Analyse',
            'Log-Interpretation',
            'Debugging',
            'Performance Issues',
            'Security Audits'
        ],
        keywords: ['bug', 'error', 'fix', 'debug', 'fehler', 'problem'],
        tools: ['exec', 'read', 'logs'],
        color: '🔧'
    }
};

// CLI: Agent Details anzeigen
function showAgent(agentName) {
    const agent = AGENTS[agentName];
    
    if (!agent) {
        console.log('Unbekannter Agent. Verfügbar:', Object.keys(AGENTS).join(', '));
        return;
    }
    
    console.log(`\n${agent.emoji} ${agent.name.toUpperCase()}\n`);
    console.log('Stärken:');
    agent.stärken.forEach(s => console.log(`  • ${s}`));
    console.log('\nKeywords:', agent.keywords.join(', '));
    console.log('Tools:', agent.tools.join(', '));
}

// CLI: Alle Agents
function showAll() {
    console.log('\n🤖 AGENT POOL\n');
    Object.entries(AGENTS).forEach(([key, agent]) => {
        console.log(`${agent.emoji} ${key}: ${agent.name}`);
    });
}

// Main
const args = process.argv.slice(2);
const agent = args[0];

if (!agent) {
    showAll();
} else if (agent === '--all') {
    Object.entries(AGENTS).forEach(([key, a]) => showAgent(key));
} else {
    showAgent(agent);
}
