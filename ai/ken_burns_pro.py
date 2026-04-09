#!/usr/bin/env python3
"""
🎬 Ken Burns PRO - Ultra Smooth
Pan + Zoom combined with smooth easing
"""
import cv2
import numpy as np
import argparse
import os

def ease_out_cubic(t):
    """Smooth easing function"""
    return 1 - pow(1 - t, 3)

def ease_in_out_sine(t):
    """Even smoother sine easing"""
    return -(np.cos(np.pi * t) - 1) / 2

def create_pro_ken_burns(image_path, output_path, duration=8, zoom_range=(1.0, 1.5), 
                         pan_range=(-0.1, 0.1), fps=60):
    """
    Ultra smooth Ken Burns with pan + zoom + smooth easing
    """
    print(f"🎬 Ken Burns PRO: {image_path}")
    print(f"   Duration: {duration}s, Zoom: {zoom_range[0]}-{zoom_range[1]}x, FPS: {fps}")
    
    # Read image at high resolution
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error loading image")
        return False
    
    orig_height, orig_width = img.shape[:2]
    
    # Scale up for better quality
    scale = 2
    width = orig_width * scale
    height = orig_height * scale
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LANCZOS4)
    
    total_frames = duration * fps
    
    # Video writer - use H264 for better quality
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (orig_width, orig_height))
    
    print(f"   Generating {total_frames} frames at {orig_width}x{orig_height}...")
    
    for frame_num in range(total_frames):
        # Normalized progress
        t = frame_num / total_frames
        
        # Smooth easing (sine is smoothest)
        eased = ease_in_out_sine(t)
        
        # Calculate zoom
        zoom = zoom_range[0] + (zoom_range[1] - zoom_range[0]) * eased
        
        # Calculate pan (subtle movement)
        pan_x = pan_range[0] + (pan_range[1] - pan_range[0]) * np.sin(t * np.pi * 2)
        pan_y = pan_range[0] + (pan_range[1] - pan_range[0]) * np.cos(t * np.pi * 2)
        
        # Calculate dimensions
        new_width = int(width / zoom)
        new_height = int(height / zoom)
        
        # Calculate position with pan
        x = int((width - new_width) / 2 + pan_x * width)
        y = int((height - new_height) / 2 + pan_y * height)
        
        # Clamp
        x = max(0, min(x, width - new_width))
        y = max(0, min(y, height - new_height))
        
        # Crop
        cropped = img[y:y+new_height, x:x+new_width]
        
        # Resize back with LANCZOS4 (best quality)
        resized = cv2.resize(cropped, (orig_width, orig_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Write
        out.write(resized)
        
        if frame_num % 60 == 0:
            print(f"   Frame {frame_num}/{total_frames}")
    
    out.release()
    print(f"   ✅ Created: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Ken Burns PRO")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="output.mp4")
    parser.add_argument("-d", "--duration", type=int, default=8)
    parser.add_argument("--zoom-min", type=float, default=1.0)
    parser.add_argument("--zoom-max", type=float, default=1.5)
    parser.add_argument("--fps", type=int, default=60)
    
    args = parser.parse_args()
    
    create_pro_ken_burns(
        args.input, 
        args.output, 
        args.duration,
        (args.zoom_min, args.zoom_max),
        fps=args.fps
    )

if __name__ == "__main__":
    main()
