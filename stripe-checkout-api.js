#!/usr/bin/env node
/**
 * Stripe Checkout Session API
 */

const http = require('http');
const https = require('https');

// Stripe API
const STRIPE_KEY = '${STRIPE_SECRET_KEY}';
const DOMAIN = 'https://empirehazeclaw.store';

const PRICE_IDS = {
    'price_1TD7KWFuuesWE4tmZdLPltuR': { name: 'KI Chatbot', price: 4900 },
    'price_1TD7KXFuuesWE4tmRgwMwLJY': { name: 'Trading Bot', price: 7900 },
    'price_1TD7K9FuuesWE4tm7aNzJyPs': { name: 'Discord Bot', price: 7900 },
    'price_1TD7KAFuuesWE4tmlfbx3Hch': { name: 'Landing Page', price: 29900 },
    'price_1TD7KBFuuesWE4tmfG4psrxq': { name: 'AI Consulting', price: 14900 },
    'price_1TD7KYFuuesWE4tm8CbNcxM5': { name: 'Discord Bot Pro', price: 14900 }
};

function createCheckoutSession(priceId) {
    return new Promise((resolve, reject) => {
        const product = PRICE_IDS[priceId];
        if (!product) {
            reject(new Error('Invalid price ID'));
            return;
        }

        const isSubscription = product.price % 100 === 0 && product.price < 10000;
        
        const postData = JSON.stringify({
            line_items: [{ price: priceId, quantity: 1 }],
            mode: isSubscription ? 'subscription' : 'payment',
            success_url: `${DOMAIN}/success.html`,
            cancel_url: `${DOMAIN}/`,
            customer_email: '',
            metadata: { product: product.name }
        });

        const options = {
            hostname: 'api.stripe.com',
            port: 443,
            path: '/v1/checkout/sessions',
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${STRIPE_KEY}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.error) reject(new Error(json.error.message));
                    else resolve(json);
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

const server = http.createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    if (req.url === '/api/create-checkout-session' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const { priceId } = JSON.parse(body);
                const session = await createCheckoutSession(priceId);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ id: session.id, url: session.url }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
    } else {
        res.writeHead(404);
        res.end();
    }
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
    console.log(`Stripe Checkout API running on port ${PORT}`);
});
