#!/usr/bin/env python3
"""
Whisper Daemon - Läuft im Hintergrund, Model bleibt geladen.
Kommunikation via Unix Socket.
Start: python3 whisper_daemon.py &
Senden: echo "audio.ogg" | nc -U /tmp/whisper.sock
"""
from faster_whisper import WhisperModel
import socket
import os
import sys
import threading

SOCKET_PATH = "/tmp/whisper.sock"
LOCK_FILE = "/tmp/whisper.lock"

def load_model():
    """Model laden - läuft einmal beim Start"""
    print("[Whisper Daemon] Loading model...", flush=True)
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("[Whisper Daemon] Model ready!", flush=True)
    return model

def handle_client(model, conn):
    """Ein Client Request"""
    try:
        data = conn.recv(4096).decode().strip()
        if not data:
            conn.close()
            return
        
        audio_path = data
        
        if not os.path.exists(audio_path):
            conn.sendall(b"ERROR: File not found")
            conn.close()
            return
        
        segments, _ = model.transcribe(audio_path, language="de")
        text = "".join([seg.text for seg in segments])
        conn.sendall(text.encode())
        
    except Exception as e:
        conn.sendall(f"ERROR: {e}".encode())
    finally:
        conn.close()

def main():
    # Model laden
    model = load_model()
    
    # Alten Socket entfernen
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    
    # Socket erstellen
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    
    print(f"[Whisper Daemon] Listening on {SOCKET_PATH}", flush=True)
    
    while True:
        try:
            conn, _ = server.accept()
            threading.Thread(target=handle_client, args=(model, conn), daemon=True).start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()
