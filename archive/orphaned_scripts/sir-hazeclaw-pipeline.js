/**
 * SIR HAZECLAW Anime Episode Pipeline v2
 * 
 * Fixed:
 * - Working TTS audio
 * - Full duration videos
 * - Ken Burns effect on images
 */

const fs = require('fs');
const { execSync } = require('child_process');

const ASSETS = '/var/www/empirehazeclaw-de';
const OUTPUT_DIR = '/var/www/empirehazeclaw-de';

class SirHazeclawPipeline {
  constructor() {
    this.episodeNumber = this.getNextEpisodeNumber();
  }

  getNextEpisodeNumber() {
    const files = fs.readdirSync(OUTPUT_DIR).filter(f => f.match(/SIR_HAZECLAW_EP\d+/));
    if (files.length === 0) return 1;
    const nums = files.map(f => parseInt(f.match(/SIR_HAZECLAW_EP(\d+)/)?.[1] || '0'));
    return Math.max(...nums) + 1;
  }

  generateTTS(text, outputPath) {
    console.log('🎤 Generating TTS...');
    execSync(`node /home/clawbot/.openclaw/workspace/scripts/ttsnotify.js "${text}" --voice en-US-GuyNeural --output ${outputPath}`, {
      stdio: 'inherit'
    });
  }

  // Create clip with KEN BURNS effect
  createClip(text, asset, outputPath, duration) {
    console.log(`🎬 Creating clip with Ken Burns: ${text}`);
    
    const isVideo = asset.endsWith('.mp4');
    
    if (isVideo) {
      // For videos, add text overlay
      execSync(`ffmpeg -y -i ${ASSETS}/${asset} -vf "drawtext=text='${text}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-120:shadowcolor=black:shadowx=3:shadowy=3" -t ${duration} -c:v libx264 -pix_fmt yuv420p -crf 21 ${outputPath} 2>&1 | tail -1`, {
        stdio: 'inherit'
      });
    } else {
      // For images, use Ken Burns (zoom effect)
      // First create a slow zoom video from image, then add text
      const tempNoText = outputPath.replace('.mp4', '_notext.mp4');
      
      execSync(`ffmpeg -y -loop 1 -i ${ASSETS}/${asset} -vf "scale=800:-1,zoompan=z='1+0.005*min(t,${duration})':d=${duration*30}:s=720x1280:fps=30" -r 30 -c:v libx264 -pix_fmt yuv420p -crf 21 -t ${duration} ${tempNoText} 2>&1 | tail -1`, {
        stdio: 'inherit'
      });
      
      // Add text overlay
      execSync(`ffmpeg -y -i ${tempNoText} -vf "drawtext=text='${text}':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=h-120:shadowcolor=black:shadowx=3:shadowy=3" -c:a copy ${outputPath} 2>&1 | tail -1`, {
        stdio: 'inherit'
      });
      
      // Cleanup
      try { fs.unlinkSync(tempNoText); } catch(e) {}
    }
  }

  async createEpisode(storyText) {
    console.log(`\n🎬 Creating SIR HAZECLAW Episode ${this.episodeNumber}`);
    console.log(`📖 Story: ${storyText}\n`);
    
    const episodeId = `SIR_HAZECLAW_EP${this.episodeNumber}`;
    const clips = [];
    const timestamp = Date.now();
    const tmpDir = '/tmp';
    
    // Split story into parts for clips
    const storyParts = [
      'SIR HAZECLAW',
      storyText.split('.')[0] || 'was once a great knight',
      storyText.split('.')[1] || 'But in the digital age',
      storyText.split('.')[2] || 'his sword battery is empty',
      'TO BE CONTINUED'
    ];
    
    // Map to assets
    const clipAssets = [
      'SIR_HAZECLAW_hero.mp4',
      'SIR_HAZECLAW_human.jpg',
      'SIR_HAZECLAW_robot.jpg',
      'SIR_HAZECLAW_charging.jpg',
      'SIR_HAZECLAW_spin.mp4'
    ];
    
    const durations = [4, 4, 4, 4, 4]; // 4 seconds each = 20s total
    
    // Step 1: Generate TTS
    const ttsPath = `${tmpDir}/${episodeId}_${timestamp}.mp3`;
    this.generateTTS(storyText, ttsPath);
    
    // Step 2: Create each clip with Ken Burns
    for (let i = 0; i < storyParts.length; i++) {
      const clipPath = `${tmpDir}/${episodeId}_${i}_${timestamp}.mp4`;
      this.createClip(storyParts[i], clipAssets[i], clipPath, durations[i]);
      clips.push(clipPath);
    }
    
    // Step 3: Combine clips
    console.log('🎞️ Combining clips...');
    const listFile = `${tmpDir}/list_${timestamp}.txt`;
    fs.writeFileSync(listFile, clips.map(c => `file '${c}'`).join('\n'));
    
    const combinedPath = `${tmpDir}/${episodeId}_combined_${timestamp}.mp4`;
    execSync(`ffmpeg -y -f concat -safe 0 -i ${listFile} -c copy ${combinedPath} 2>&1 | tail -1`, {
      stdio: 'inherit'
    });
    
    // Step 4: Add TTS audio
    console.log('🔊 Adding TTS audio...');
    const outputPath = `${OUTPUT_DIR}/${episodeId}.mp4`;
    
    // Use -shortest to match video length
    execSync(`ffmpeg -y -i ${combinedPath} -i ${ttsPath} -c:v copy -c:a aac -b:a 192k -shortest ${outputPath} 2>&1 | tail -1`, {
      stdio: 'inherit'
    });
    
    // Cleanup
    clips.forEach(c => { try { fs.unlinkSync(c); } catch(e) {} });
    try { fs.unlinkSync(listFile); } catch(e) {}
    try { fs.unlinkSync(combinedPath); } catch(e) {}
    try { fs.unlinkSync(ttsPath); } catch(e) {}
    
    console.log(`\n✅ Episode created: ${outputPath}`);
    console.log(`🔗 URL: https://empirehazeclaw.de/${episodeId}.mp4`);
    
    return outputPath;
  }
}

// CLI
const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('Usage: node sir-hazeclaw-pipeline.js "Story text here"');
  process.exit(1);
}

const story = args.join(' ');
const pipeline = new SirHazeclawPipeline();
pipeline.createEpisode(story).catch(console.error);
