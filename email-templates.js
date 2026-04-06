/**
 * Email Templates for EmpireHazeClaw
 * Automatisierte Kundenkommunikation
 */

const EMAIL_TEMPLATES = {
    // ============================================
    // LANDING PAGE SERVICE
    // ============================================
    'landing-page-order': {
        subject: '🛠️ Ihre Landing Page Bestellung - Nächste Schritte',
        variables: ['customerName', 'orderId', 'productName', 'amount'],
        html: (data) => `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bestellung bestätigt</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #0f0f0f; color: #e5e5e5; padding: 2rem; }
        .container { max-width: 600px; margin: 0 auto; background: #1a1a1a; border-radius: 12px; overflow: hidden; }
        .header { background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 2rem; text-align: center; }
        .header h1 { margin: 0; color: white; font-size: 1.5rem; }
        .content { padding: 2rem; }
        .order-box { background: #262626; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
        .order-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #333; }
        .order-row:last-child { border-bottom: none; }
        .label { color: #888; }
        .value { color: #e5e5e5; font-weight: 500; }
        .steps { background: #262626; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
        .steps h3 { margin-top: 0; color: #6366f1; }
        .steps ol { padding-left: 1.25rem; line-height: 1.8; }
        .cta { display: inline-block; background: #6366f1; color: white; padding: 0.75rem 1.5rem; 
                border-radius: 8px; text-decoration: none; margin-top: 1rem; }
        .footer { text-align: center; padding: 1.5rem; color: #666; font-size: 0.875rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ Bestellung erfolgreich!</h1>
        </div>
        <div class="content">
            <p>Hallo <strong>${data.customerName}</strong>,</p>
            <p>vielen Dank für Ihre Bestellung! Wir freuen uns, Ihre Landing Page zu erstellen.</p>
            
            <div class="order-box">
                <div class="order-row">
                    <span class="label">Bestellnummer:</span>
                    <span class="value">${data.orderId}</span>
                </div>
                <div class="order-row">
                    <span class="label">Produkt:</span>
                    <span class="value">${data.productName}</span>
                </div>
                <div class="order-row">
                    <span class="label">Betrag:</span>
                    <span class="value">${data.amount}</span>
                </div>
            </div>
            
            <div class="steps">
                <h3>📋 Nächste Schritte</h3>
                <ol>
                    <li>Füllen Sie unser <strong>Briefing-Formular</strong> aus (Link in Kürze)</li>
                    <li>Teilen Sie uns Ihre <strong>Inhalte</strong> mit: Texte, Bilder, Logos</li>
                    <li>Erhalten Sie den <strong>ersten Entwurf</strong> innerhalb von 3-5 Werktagen</li>
                </ol>
            </div>
            
            <p>Haben Sie Fragen? Wir sind für Sie da!</p>
            <a href="mailto:support@empirehazeclaw.de" class="cta">📧 Support kontaktieren</a>
        </div>
        <div class="footer">
            🦞 EmpireHazeClaw | empirehazeclaw.de
        </div>
    </div>
</body>
</html>
        `,
        text: (data) => `
Bestellbestätigung - EmpireHazeClaw

Hallo ${data.customerName},

vielen Dank für Ihre Bestellung!

BESTELLDETAILS:
- Bestellnummer: ${data.orderId}
- Produkt: ${data.productName}
- Betrag: ${data.amount}

NÄCHSTE SCHRITTE:
1. Briefing-Formular ausfüllen
2. Inhalte bereitstellen (Texte, Bilder, Logos)
3. Ersten Entwurf in 3-5 Tagen erhalten

Fragen? support@empirehazeclaw.de

Ihr EmpireHazeClaw Team
        `
    },

    // ============================================
    // POD DESIGN SERVICE
    // ============================================
    'pod-design-order': {
        subject: '🎨 Ihre POD Design Bestellung - Next Steps',
        variables: ['customerName', 'orderId', 'productName', 'amount'],
        html: (data) => `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bestellung bestätigt</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #0f0f0f; color: #e5e5e5; padding: 2rem; }
        .container { max-width: 600px; margin: 0 auto; background: #1a1a1a; border-radius: 12px; overflow: hidden; }
        .header { background: linear-gradient(135deg, #ec4899, #f43f5e); padding: 2rem; text-align: center; }
        .header h1 { margin: 0; color: white; font-size: 1.5rem; }
        .content { padding: 2rem; }
        .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 1rem 0; }
        .product-item { background: #262626; padding: 1rem; border-radius: 8px; text-align: center; }
        .product-item span { font-size: 2rem; display: block; margin-bottom: 0.5rem; }
        .steps { background: #262626; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
        .steps h3 { margin-top: 0; color: #ec4899; }
        .steps ol { padding-left: 1.25rem; line-height: 1.8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Bestellung erfolgreich!</h1>
        </div>
        <div class="content">
            <p>Hallo <strong>${data.customerName}</strong>,</p>
            <p>wir haben Ihre POD Design Bestellung erhalten!</p>
            
            <div class="product-grid">
                <div class="product-item"><span>👕</span>T-Shirt</div>
                <div class="product-item"><span>🧥</span>Hoodie</div>
                <div class="product-item"><span>☕</span>Tasse</div>
                <div class="product-item"><span>🖼️</span>Poster</div>
            </div>
            
            <div class="steps">
                <h3>📋 So gehen wir vor</h3>
                <ol>
                    <li>Teilen Sie uns Ihr <strong>Design-Konzept</strong> mit (Stil, Farben, Motive)</li>
                    <li>Wählen Sie den <strong>Produkttyp</strong> (T-Shirt, Hoodie, etc.)</li>
                    <li>Erhalten Sie einen <strong>Design-Prototyp</strong> in 2-3 Werktagen</li>
                </ol>
            </div>
            
            <p>Design-Wünsche an: <strong>design@empirehazeclaw.de</strong></p>
        </div>
    </div>
</body>
</html>
        `
    },

    // ============================================
    // DISCORD BOT SERVICE
    // ============================================
    'discord-bot-order': {
        subject: '💬 Ihre Discord Bot Bestellung - Setup Anleitung',
        variables: ['customerName', 'orderId', 'productName', 'amount'],
        html: (data) => `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bestellung bestätigt</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #0f0f0f; color: #e5e5e5; padding: 2rem; }
        .container { max-width: 600px; margin: 0 auto; background: #1a1a1a; border-radius: 12px; overflow: hidden; }
        .header { background: linear-gradient(135deg, #5865F2, #7289DA); padding: 2rem; text-align: center; }
        .header h1 { margin: 0; color: white; font-size: 1.5rem; }
        .content { padding: 2rem; }
        .alert { background: #fef3c7; color: #92400e; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        .steps { background: #262626; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
        .steps ol { padding-left: 1.25rem; line-height: 1.8; }
        .steps li { margin-bottom: 0.5rem; }
        code { background: #333; padding: 0.25rem 0.5rem; border-radius: 4px; font-family: monospace; }
        .features { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1rem 0; }
        .feature { background: #5865F2; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.875rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 Discord Bot bestellt!</h1>
        </div>
        <div class="content">
            <p>Hallo <strong>${data.customerName}</strong>,</p>
            <p>wir richten Ihren Discord Bot ein!</p>
            
            <div class="features">
                <span class="feature">🛡️ Moderation</span>
                <span class="feature">🎵 Musik</span>
                <span class="feature">📊 Level System</span>
                <span class="feature">🤖 Custom Commands</span>
            </div>
            
            <div class="steps">
                <h3>🚀 Quick Setup</h3>
                <ol>
                    <li>Gehen Sie zu <a href="https://discord.com/developers/applications" style="color: #5865F2;">Discord Developer Portal</a></li>
                    <li>Erstellen Sie eine neue Application oder wählen Sie eine existierende</li>
                    <li>Gehen Sie zu "Bot" und erstellen Sie einen Bot</li>
                    <li>Kopieren Sie den <strong>Token</strong> und senden Sie ihn an uns</li>
                </ol>
            </div>
            
            <div class="alert">
                <strong>📧 Wichtig:</strong> Bitte antworten Sie auf diese E-Mail mit:
                <ul>
                    <li>Ihrem Discord Server-Link</li>
                    <li>Gewünschten Funktionen</li>
                    <li>Bot Token (falls schon erstellt)</li>
                </ul>
            </div>
            
            <p>Fragen? Discord: <strong>OpenClaw#0001</strong></p>
        </div>
    </div>
</body>
</html>
        `
    }
};

/**
 * Get email template by type
 */
function getTemplate(type, format = 'html') {
    const template = EMAIL_TEMPLATES[type];
    if (!template) return null;
    
    return {
        subject: template.subject,
        content: format === 'html' ? template.html : template.text
    };
}

/**
 * Render template with data
 */
function renderTemplate(type, data, format = 'html') {
    const template = EMAIL_TEMPLATES[type];
    if (!template) return null;
    
    return {
        subject: template.subject,
        content: template[format] ? template[format](data) : template.html(data)
    };
}

// Export for use in webhook handler
module.exports = { EMAIL_TEMPLATES, getTemplate, renderTemplate };
