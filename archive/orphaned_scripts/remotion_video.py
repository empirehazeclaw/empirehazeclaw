#!/usr/bin/env python3
"""Remotion Video Creation"""
import subprocess
import sys
import os

def render_video(project, out_name="video.mp4"):
    """Render video with Remotion"""
    if not os.path.exists(project):
        return f"❌ Project not found: {project}"
    
    cmd = ["npx", "remotion", "render", project, out_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"✅ Rendered: {out_name}" if result.returncode == 0 else f"❌ {result.stderr[:200]}"

def list_projects():
    """List Remotion projects"""
    projects = [p for p in os.listdir(".") if "remotion" in p.lower() or "video" in p.lower()]
    return projects

if __name__ == "__main__":
    print("=== 🎬 REMOTION VIDEO ===")
    print("Usage: python3 remotion_video.py <project>")
    print(f"Projects: {list_projects()}")
