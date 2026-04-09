module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  console.log('Stripe webhook hit:', req.body?.type);
  res.json({ received: true });
};
