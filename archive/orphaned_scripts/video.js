#!/usr/bin/env node
/**
 * UNIFIED VIDEO TOOL
 * Combines: tiktok, thumbnails, ideas
 */

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'ideas') {
    const count = parseInt(args[1]) || 5;
    const topics = ['AI', 'Tech', 'Business'];
    console.log(`\n🎬 VIDEO IDEAS (${count}):\n`);
    for(let i=0; i<count; i++) {
        const topic = topics[i % topics.length];
        console.log(`${i+1}. ${topic} content idea ${i+1}`);
    }
}
else if (cmd === 'generate') {
    console.log('\n🖼️ Generate images with:\n  node skills/larry/scripts/fal-image.js "prompt"\n');
}
else if (cmd === 'thumbnail') {
    console.log('\n🖼️ Generate thumbnails with:\n  node scripts/thumbnail-gen.js\n');
}
else {
    console.log(`
🎬 UNIFIED VIDEO TOOL

Commands:
  node video.js ideas [count]     - Generate video ideas
  node video.js generate          - Generate AI images
  node video.js thumbnail         - Create thumbnails
  node video.js script            - Generate script
`);
}
