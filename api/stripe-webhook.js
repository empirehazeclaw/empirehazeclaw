module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  console.log('Webhook hit:', req.body?.type || 'unknown');
  res.json({ received: true });
};
