#!/usr/bin/env python3
"""Ken Burns Animation - Create video from image"""
import subprocess
import sys
import os

def create_video(image, output="video.mp4", duration=10):
    """Create Ken Burns video"""
    script = "scripts/ai/ken_burns_pro.py"
    
    if not os.path.exists(image):
        return f"❌ Image not found: {image}"
    
    cmd = ["python3", script, "-i", image, "-o", output, "-d", str(duration)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return f"✅ Video: {output}" if result.returncode == 0 else f"❌ {result.stderr[:200]}"

if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else "image.jpg"
    out = sys.argv[2] if len(sys.argv) > 2 else "video.mp4"
    print(f"🎬 Creating Ken Burns video...")
    print(create_video(img, out))
