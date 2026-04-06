/**
 * Stripe Webhook Handler
 */
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    event = req.body;
  } catch (err) {
    console.error('Webhook Error:', err.message);
    return res.status(400).json({ error: `Webhook Error: ${err.message}` });
  }

  // Handle the event
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object;
      console.log('💳 Payment received:', session.id);
      
      const logFile = path.join(process.cwd(), 'data', 'stripe_events.json');
      let events = [];
      if (fs.existsSync(logFile)) {
        events = JSON.parse(fs.readFileSync(logFile, 'utf8'));
      }
      events.push({
        type: 'checkout.session.completed',
        session_id: session.id,
        customer_email: session.customer_details?.email,
        amount: session.amount_total / 100,
        currency: session.currency,
        product: session.metadata?.product_name,
        timestamp: new Date().toISOString()
      });
      fs.writeFileSync(logFile, JSON.stringify(events, null, 2));
      console.log('✅ Order logged');
      break;
      
    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  res.json({ received: true });
};
