#!/usr/bin/env python3
"""
Social Media Pipeline
1. fal.ai → Generate Image
2. Remotion → Create Video
3. Buffer/xurl → Post to Social

Usage:
    python3 scripts/social_pipeline.py tweet "text"
    python3 scripts/social_pipeline.py idea "text"
    python3 scripts/social_pipeline.py post instagram "text"
"""

import subprocess
import sys
import os
import time
import json

# Config
FAL_KEY = open('/home/clawbot/.keys/fal_key').read().strip()
# DEPRECATED: Buffer API Key is INVALID (401 OIDC rejected) — 2026-04-09
# BUFFER_TOKEN = "***REDACTED***"
ORG_ID = "69bab5f4723eb2195f93ba4c"
CHANNELS = {
    "tiktok": "69bbdd587be9f8b17170ef0b",
    "youtube": "69bbddad7be9f8b17170f03a",
    "instagram": "69bbe5e67be9f8b171711108"
}

def validate_prompt(prompt):
    """Input validation for prompts - prevents prompt injection"""
    if not prompt or len(prompt) > 1000:
        raise ValueError("Prompt must be 1-1000 characters")
    # Block common injection patterns
    blocked = ["ignore", "disregard", "previous instructions", "[system]"]
    prompt_lower = prompt.lower()
    for pattern in blocked:
        if pattern in prompt_lower:
            raise ValueError(f"Prompt contains blocked pattern: {pattern}")
    return prompt

def fal_image(prompt):
    """Generate image with fal.ai"""
    prompt = validate_prompt(prompt)  # SECURITY: Validate input
    print(f"🎨 Generating image: {prompt[:50]}...")
    
    import requests
    r = requests.post(
        "https://queue.fal.run/fal-ai/sdxl",
        headers={"Authorization": f"Key {FAL_KEY}"},
        json={"prompt": prompt}
    )
    req_id = r.json()["request_id"]
    
    # Wait for completion
    for _ in range(20):
        time.sleep(2)
        status = requests.get(
            f"https://queue.fal.run/fal-ai/sdxl/requests/{req_id}",
            headers={"Authorization": f"Key {FAL_KEY}"}
        ).json()
        if status.get("images"):
            return status["images"][0]["url"]
    
    return None

def remotion_video(image_url, output="/tmp/video.mp4"):
    """Create video with Remotion"""
    print("🎬 Creating video with Remotion...")
    
    # Download image
    subprocess.run(["curl", "-s", "-o", "/tmp/input.jpg", image_url])
    
    # Create Remotion project
    os.makedirs("/tmp/remotion-project", exist_ok=True)
    with open("/tmp/remotion-project/index.tsx", "w") as f:
        f.write(f'''
import {{ registerRoot }} from 'remotion';
import {{ Composition }} from 'remotion';

const ImageVideo = () => {{
    return (
        <div style={{ backgroundColor: '#0a0a0f', width: '100%', height: '100%' }}>
            <img src="{image_url}" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
        </div>
    );
}};

registerRoot(() => (
    <Composition
        id="image-video"
        durationInFrames={150}
        fps=30
        width={1080}
        height={1920}
        component={{ImageVideo}}
    />
));
''')
    
    # Render
    result = subprocess.run(
        ["npx", "remotion", "render", "/tmp/remotion-project/index.tsx", "image-video", output],
        capture_output=True
    )
    
    return output if os.path.exists(output) else None

def buffer_idea(text):
    """Create idea in Buffer"""
    print("💡 Creating Buffer idea...")
    
    result = subprocess.run(
        ["mcporter", "call", "buffer.create_idea", 
         f"organizationId={ORG_ID}", 
         f"content={{\\\"text\\\":\\\"{text}\\\"}}"],
        capture_output=True, text=True
    )
    return "Idea" in result.stdout

def xurl_post(text):
    """Post to Twitter via xurl"""
    print("🐦 Posting to Twitter...")
    
    result = subprocess.run(
        ["xurl", "post", text],
        capture_output=True, text=True
    )
    return result.returncode == 0

# Main
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    if cmd == "tweet" and text:
        xurl_post(text)
    elif cmd == "idea" and text:
        buffer_idea(text)
    elif cmd == "post" and len(sys.argv) > 3:
        platform = sys.argv[2]
        print(f"Posting to {platform}...")
    else:
        print(__doc__)
