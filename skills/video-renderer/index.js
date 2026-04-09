module.exports = {
  name: 'video-renderer',
  description: 'Erstellt Promotions-Videos mit Remotion',
  main: async () => {
    return { status: 'ok', message: 'Video renderer skill geladen. Nutze: cd /home/clawbot/.openclaw/workspace/remotion-video && npx remotion render src/Root.tsx VideoAd /tmp/video-ad.mp4' };
  }
};
