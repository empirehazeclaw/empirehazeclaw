module.exports = {
  name: 'email-outreach',
  description: 'Automatisierte B2B E-Mail Outreach Kampagnen',
  main: async () => {
    return { status: 'ok', message: 'Email outreach skill geladen. Nutze: python3 /home/clawbot/.openclaw/workspace/scripts/automated_outreach.py --help' };
  }
};
