#!/usr/bin/env node
/**
 * Stripe Webhook Handler for automated delivery
 */
const http = require('http');

const PORT = process.env.PORT || 3000;

const handleWebhook = (req, res) => {
    console.log(`📥 Request: ${req.method} ${req.url}`);
    
    // Handle health check
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok' }));
        return;
    }
    
    let body = '';
    
    req.on('data', chunk => { body += chunk; });
    
    req.on('end', () => {
        try {
            if (!body) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ received: true, note: 'empty' }));
                return;
            }
            
            const event = JSON.parse(body);
            
            console.log(`📦 Event: ${event.type}`);
            
            if (event.type === 'checkout.session.completed') {
                const session = event.data.object;
                const email = session.customer_email || session.customer_details?.email;
                const product = session.display_name || session.metadata?.product || 'Unknown';
                
                console.log(`✅ Payment received!`);
                console.log(`   Email: ${email}`);
                console.log(`   Product: ${product}`);
                
                // TODO: Trigger delivery workflow
            }
            
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ received: true }));
        } catch (e) {
            console.error(`❌ Error: ${e.message}`);
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
    });
};

const server = http.createServer(handleWebhook);
server.listen(PORT, () => {
    console.log(`🔔 Stripe Webhook Listener running on port ${PORT}`);
    console.log(`🌐 Webhook URL: http://2a02:4780:79:e396::1:${PORT}/webhook`);
});

module.exports = { handleWebhook };
