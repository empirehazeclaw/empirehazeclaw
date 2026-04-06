module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  console.log('Webhook received:', req.body?.type || 'unknown');
  
  // Handle Stripe events
  if (req.body?.type === 'checkout.session.completed') {
    const session = req.body.data.object;
    console.log('💳 Payment from:', session.customer_details?.email);
    // Log payment - in production you'd save to DB
  }
  
  res.json({ received: true });
};
