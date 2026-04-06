// Root level API entry - routes to individual handlers
module.exports = (req, res) => {
  const url = req.url;
  if (url.startsWith('/stripe-webhook')) {
    const handler = require('./stripe-webhook');
    return handler.default ? handler.default(req, res) : handler(req, res);
  }
  res.status(404).json({ error: 'Not found' });
};
