#!/usr/bin/env python3
"""
🎬 Ken Burns Animation Generator
Creates smooth zoom/pan effects from images
"""
import os
import sys
import argparse
from PIL import Image, ImageEnhance

# Try to import moviepy or use fallback
try:
    from moviepy.editor import ImageClip, vfx
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

def create_ken_burns_pil(input_path, output_path, duration=5, zoom=1.15, direction="in"):
    """
    Create Ken Burns effect using PIL and raw video generation
    """
    print(f"🎬 Creating Ken Burns: {input_path} → {output_path}")
    print(f"   Duration: {duration}s, Zoom: {zoom}x, Direction: {direction}")
    
    # Load image
    img = Image.open(input_path)
    width, height = img.size
    
    # Calculate frames (30 fps)
    fps = 30
    total_frames = duration * fps
    
    # Output directory
    output_dir = os.path.dirname(output_path) or "/tmp/ken_burns"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate frames
    print(f"   Generating {total_frames} frames...")
    
    for frame_num in range(total_frames):
        progress = frame_num / total_frames
        
        # Calculate zoom
        if direction == "in":
            current_zoom = 1 + (zoom - 1) * progress
        else:
            current_zoom = zoom - (zoom - 1) * progress
        
        # Calculate crop area
        crop_width = int(width / current_zoom)
        crop_height = int(height / current_zoom)
        
        # Center crop
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height
        
        # Crop and resize
        cropped = img.crop((left, top, right, bottom))
        resized = cropped.resize((width, height), Image.LANCZOS)
        
        # Save frame
        frame_path = f"{output_dir}/frame_{frame_num:05d}.jpg"
        resized.save(frame_path, quality=95)
        
        if frame_num % 30 == 0:
            print(f"   Frame {frame_num}/{total_frames}")
    
    print(f"   Frames saved to {output_dir}")
    return output_dir

def create_video_ffmpeg(frames_dir, output_path, fps=30):
    """Create video from frames using ffmpeg"""
    print(f"   Encoding video with ffmpeg...")
    
    # Check if ffmpeg is available
    result = os.system("which ffmpeg > /dev/null 2>&1")
    
    if result != 0:
        # Try using avconv or create animated gif instead
        print("   ⚠️ ffmpeg not available, creating GIF instead")
        output_path = output_path.replace('.mp4', '.gif')
        
        # Create GIF from first and last frame
        import glob
        frames = sorted(glob.glob(f"{frames_dir}/*.jpg"))
        
        if len(frames) >= 2:
            img1 = Image.open(frames[0])
            img2 = Image.open(frames[-1])
            
            # Simple GIF with 2 frames
            img1.save(output_path, 
                     save_all=True, 
                     append_images=[img2], 
                     duration=2000, 
                     loop=0)
        
        print(f"   ✅ GIF created: {output_path}")
        return output_path
    
    # Use ffmpeg
    cmd = f'ffmpeg -y -framerate {fps} -i "{frames_dir}/frame_%05d.jpg" -c:v libx264 -pix_fmt yuv420p -crf 23 "{output_path}" 2>/dev/null'
    os.system(cmd)
    
    print(f"   ✅ Video created: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Ken Burns Animation Generator")
    parser.add_argument("-i", "--input", required=True, help="Input image path")
    parser.add_argument("-o", "--output", default="output.mp4", help="Output video path")
    parser.add_argument("-d", "--duration", type=int, default=5, help="Duration in seconds")
    parser.add_argument("--zoom", type=float, default=1.15, help="Zoom factor")
    parser.add_argument("--direction", choices=["in", "out"], default="in", help="Zoom direction")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Create animation
    frames_dir = create_ken_burns_pil(
        args.input, 
        args.output, 
        args.duration, 
        args.zoom, 
        args.direction
    )
    
    # Create video
    output = create_video_ffmpeg(frames_dir, args.output)
    
    print(f"\n✅ Done! Output: {output}")

if __name__ == "__main__":
    main()
