#!/usr/bin/env python3
"""
🎬 Ken Burns Animation - Smooth Version
Uses OpenCV for smooth interpolation
"""
import cv2
import numpy as np
import argparse
import os

def smooth_zoom_in(image_path, output_path, duration=5, zoom_factor=1.3, fps=30):
    """
    Create smooth Ken Burns zoom effect using OpenCV
    """
    print(f"🎬 Creating smooth Ken Burns: {image_path}")
    print(f"   Duration: {duration}s, Zoom: {zoom_factor}x, FPS: {fps}")
    
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: Could not load image: {image_path}")
        return False
    
    height, width = img.shape[:2]
    total_frames = duration * fps
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"   Generating {total_frames} smooth frames...")
    
    for frame_num in range(total_frames):
        # Smooth progress (ease-in-out)
        progress = frame_num / total_frames
        # Cubic easing for extra smoothness
        eased = progress * progress * (3 - 2 * progress)
        
        # Calculate current zoom
        current_zoom = 1 + (zoom_factor - 1) * eased
        
        # Calculate new dimensions
        new_width = int(width / current_zoom)
        new_height = int(height / current_zoom)
        
        # Calculate crop position (center)
        x = (width - new_width) // 2
        y = (height - new_height) // 2
        
        # Crop
        cropped = img[y:y+new_height, x:x+new_width]
        
        # Resize back to original size (OpenCV INTER_CUBIC for smoothness)
        resized = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_CUBIC)
        
        # Write frame
        out.write(resized)
        
        if frame_num % 30 == 0:
            print(f"   Frame {frame_num}/{total_frames}")
    
    out.release()
    print(f"   ✅ Video created: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Smooth Ken Burns Animation")
    parser.add_argument("-i", "--input", required=True, help="Input image path")
    parser.add_argument("-o", "--output", default="output.mp4", help="Output video path")
    parser.add_argument("-d", "--duration", type=int, default=5, help="Duration in seconds")
    parser.add_argument("--zoom", type=float, default=1.3, help="Zoom factor")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        return
    
    smooth_zoom_in(
        args.input, 
        args.output, 
        args.duration, 
        args.zoom,
        args.fps
    )
    
    print(f"\n✅ Done! {args.output}")

if __name__ == "__main__":
    main()
