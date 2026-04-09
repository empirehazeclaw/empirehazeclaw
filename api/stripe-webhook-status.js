module.exports = (req, res) => {
  res.json({ 
    webhook_active: true,
    url: '/stripe-webhook',
    status: 'ready'
  });
};
