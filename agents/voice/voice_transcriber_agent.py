#!/usr/bin/env python3
"""
Voice Transcriber Agent
======================
Transcribe audio files to text using Whisper.

Usage:
    python3 voice_transcriber_agent.py --file <audio_file>
    python3 voice_transcriber_agent.py --batch --directory <dir>
    python3 voice_transcriber_agent.py --list
"""

import argparse
import json
import logging
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "voice_transcriber.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/agents/voice")
DATA_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPTS_FILE = DATA_DIR / "transcripts.json"
SETTINGS_FILE = DATA_DIR / "transcriber_settings.json"


def load_json(filepath: Path, default: dict = {}) -> dict:
    """Load JSON data from file."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON data to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_whisper():
    """Check if whisper is available."""
    try:
        import whisper
        return True
    except ImportError:
        return False


def convert_to_wav(input_file: str, output_file: str) -> bool:
    """Convert audio file to WAV format for Whisper."""
    try:
        cmd = [
            "ffmpeg", "-i", input_file,
            "-ar", "16000", "-ac", "1",
            "-acodec", "pcm_s16le",
            "-y", output_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error converting file: {e}")
        return False


def transcribe_audio(file_path: str, model_size: str = "base", language: Optional[str] = None) -> dict:
    """Transcribe an audio file using Whisper."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    try:
        import whisper
    except ImportError:
        raise RuntimeError("Whisper not installed. Run: pip install openai-whisper")
    
    logger.info(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)
    
    # Transcribe
    logger.info(f"Transcribing: {file_path}")
    options = {}
    if language:
        options["language"] = language
    
    result = model.transcribe(file_path, **options)
    
    transcript = {
        "id": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "source_file": file_path,
        "model": model_size,
        "language": result.get("language", language or "auto-detected"),
        "text": result["text"].strip(),
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            }
            for seg in result.get("segments", [])
        ],
        "duration_seconds": result.get("duration", 0),
        "created_at": datetime.now().isoformat()
    }
    
    return transcript


def save_transcript(transcript: dict) -> bool:
    """Save transcript to file."""
    transcripts = load_json(TRANSCRIPTS_FILE)
    
    if "transcripts" not in transcripts:
        transcripts["transcripts"] = []
    
    transcripts["transcripts"].append(transcript)
    transcripts["last_updated"] = datetime.now().isoformat()
    
    return save_json(TRANSCRIPTS_FILE, transcripts)


def get_transcripts(limit: Optional[int] = None) -> List[dict]:
    """Get all transcripts."""
    transcripts = load_json(TRANSCRIPTS_FILE)
    result = transcripts.get("transcripts", [])
    
    if limit:
        result = result[-limit:]
    
    return result


def get_transcript_by_id(transcript_id: str) -> Optional[dict]:
    """Get a specific transcript by ID."""
    transcripts = load_json(TRANSCRIPTS_FILE)
    
    for t in transcripts.get("transcripts", []):
        if t["id"] == transcript_id:
            return t
    
    return None


def batch_transcribe(directory: str, model_size: str = "base", 
                     output_format: str = "json") -> List[dict]:
    """Transcribe all audio files in a directory."""
    supported_extensions = [".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac"]
    results = []
    
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    audio_files = [
        f for f in dir_path.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    if not audio_files:
        print(f"No audio files found in {directory}")
        return results
    
    print(f"Found {len(audio_files)} audio files to transcribe...")
    
    for audio_file in audio_files:
        try:
            print(f"\nTranscribing: {audio_file.name}")
            transcript = transcribe_audio(str(audio_file), model_size)
            save_transcript(transcript)
            results.append(transcript)
            print(f"✓ Completed: {transcript['id']} ({transcript['duration_seconds']:.1f}s)")
        except Exception as e:
            logger.error(f"Error transcribing {audio_file}: {e}")
            print(f"✗ Failed: {audio_file.name} - {e}")
    
    return results


def display_transcript(transcript: dict, show_segments: bool = False):
    """Display transcript details."""
    print("\n" + "=" * 60)
    print(f"📝 TRANSCRIPT: {transcript['id']}")
    print("=" * 60)
    print(f"  Source:    {transcript['source_file']}")
    print(f"  Duration:  {transcript['duration_seconds']:.1f} seconds")
    print(f"  Language:  {transcript['language']}")
    print(f"  Model:     {transcript['model']}")
    print(f"  Created:   {transcript['created_at'][:19].replace('T', ' ')}")
    print()
    print("-" * 60)
    print("TRANSCRIPT TEXT:")
    print("-" * 60)
    print(transcript["text"])
    
    if show_segments and transcript.get("segments"):
        print()
        print("-" * 60)
        print("SEGMENTS:")
        print("-" * 60)
        for seg in transcript["segments"]:
            start = f"[{seg['start']:.1f}s -> {seg['end']:.1f}s]"
            print(f"{start} {seg['text']}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Voice Transcriber Agent - Transcribe audio files to text using Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file audio.mp3
  %(prog)s --file audio.ogg --model small --language de
  %(prog)s --batch --directory ./recordings
  %(prog)s --list
  %(prog)s --list --latest 10
  %(prog)s --view TXN-20240115103045
        """
    )
    
    parser.add_argument("--file", type=str, help="Audio file to transcribe")
    parser.add_argument("--model", type=str, default="base", 
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--language", type=str, help="Source language (e.g., en, de, es)")
    parser.add_argument("--batch", action="store_true", help="Batch mode - transcribe all files in directory")
    parser.add_argument("--directory", type=str, help="Directory for batch mode")
    parser.add_argument("--list", action="store_true", help="List all transcripts")
    parser.add_argument("--latest", type=int, help="Show latest N transcripts")
    parser.add_argument("--view", type=str, help="View a specific transcript by ID")
    parser.add_argument("--segments", action="store_true", help="Show segments when viewing transcript")
    parser.add_argument("--check", action="store_true", help="Check system requirements")
    
    args = parser.parse_args()
    
    try:
        if args.check:
            print("\n🔧 System Requirements Check:")
            print("-" * 40)
            
            ffmpeg_ok = check_ffmpeg()
            print(f"  ffmpeg: {'✅ Available' if ffmpeg_ok else '❌ Not found'}")
            
            whisper_ok = check_whisper()
            print(f"  whisper: {'✅ Available' if whisper_ok else '❌ Not installed'}")
            
            if not whisper_ok:
                print("\n  Install whisper with:")
                print("  pip install openai-whisper")
            
            if not ffmpeg_ok:
                print("\n  Install ffmpeg with:")
                print("  sudo apt install ffmpeg  # Ubuntu/Debian")
                print("  brew install ffmpeg      # macOS")
            
            return
        
        if args.batch:
            if not args.directory:
                parser.error("--batch requires --directory")
            
            results = batch_transcribe(args.directory, args.model)
            print(f"\n\n✅ Batch complete: {len(results)}/{len(results)} files transcribed")
            return
        
        if args.file:
            # Convert to WAV if needed
            input_file = args.file
            needs_conversion = Path(input_file).suffix.lower() != ".wav"
            work_file = input_file
            
            if needs_conversion:
                if not check_ffmpeg():
                    print("❌ ffmpeg not found. Please install ffmpeg first.")
                    sys.exit(1)
                
                wav_file = Path(input_file).with_suffix(".wav")
                print(f"Converting {input_file} to WAV format...")
                if not convert_to_wav(input_file, str(wav_file)):
                    print(f"❌ Failed to convert audio file")
                    sys.exit(1)
                work_file = str(wav_file)
            
            transcript = transcribe_audio(work_file, args.model, args.language)
            save_transcript(transcript)
            
            print(f"\n✅ Transcription complete!")
            display_transcript(transcript, show_segments=True)
            return
        
        if args.list:
            transcripts = get_transcripts(limit=args.latest)
            if not transcripts:
                print("\nNo transcripts found.")
                return
            
            print(f"\n📝 TRANSCRIPTS (showing {len(transcripts)}):")
            print("-" * 70)
            for t in transcripts:
                text_preview = t["text"][:50] + "..." if len(t["text"]) > 50 else t["text"]
                print(f"  {t['id']} | {t['source_file'][:30]} | {t['duration_seconds']:.0f}s | {text_preview}")
            print("-" * 70)
            return
        
        if args.view:
            transcript = get_transcript_by_id(args.view)
            if transcript:
                display_transcript(transcript, show_segments=args.segments)
            else:
                print(f"\n❌ Transcript not found: {args.view}")
                sys.exit(1)
            return
        
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
