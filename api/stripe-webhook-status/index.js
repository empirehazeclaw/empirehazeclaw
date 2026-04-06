/**
 * Stripe Webhook Status
 */
const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  const eventsFile = path.join(process.cwd(), 'data', 'stripe_events.json');
  
  let events = [];
  if (fs.existsSync(eventsFile)) {
    events = JSON.parse(fs.readFileSync(eventsFile, 'utf8'));
  }
  
  res.json({
    webhook_active: true,
    events_received: events.length,
    recent_events: events.slice(-10).reverse()
  });
};
