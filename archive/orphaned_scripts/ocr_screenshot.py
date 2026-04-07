#!/usr/bin/env python3
"""OCR - Text from Screenshots using tesseract"""
import subprocess
import sys
import os

def extract_text(image_path):
    """Extract text from image"""
    if not os.path.exists(image_path):
        return f"❌ File not found: {image_path}"
    
    try:
        result = subprocess.run(
            ['tesseract', image_path, 'stdout'],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else "screenshot.png"
    print(f"=== 🔍 OCR: {img} ===")
    print(extract_text(img))
