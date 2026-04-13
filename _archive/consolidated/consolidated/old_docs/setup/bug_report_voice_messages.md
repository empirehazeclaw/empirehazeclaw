# 🐛 Bug Report: Voice Messages Received as Tiny Files (10-17KB)

## Environment
- **OpenClaw Version**: Latest (2026-03)
- **Platform**: Ubuntu/Linux
- **Channel**: Telegram
- **Node.js**: v22.22.0
- **Server**: srv1432586

## Issue Description
Voice messages sent via Telegram are received as extremely small files (10-17KB) instead of actual audio data (expected 250KB-500KB for 1 minute of voice).

**Both .ogg (opus) and other audio formats are affected.**

## Steps to Reproduce
1. Send a voice message via Telegram (1 minute duration)
2. Message appears in OpenClaw as audio file
3. File size is only 10-17KB (should be ~250-500KB for 1 minute)
4. File cannot be played or transcribed

## Expected vs Actual Behavior
- **Expected**: Voice message stored as valid audio file (~250KB-500KB for 1 min)
- **Actual**: Voice message stored as tiny corrupted file (10-17KB)

## Investigation
- File header analysis shows files are NOT valid audio files
- Earlier tests showed PNG header appearing instead of OGG header in some cases
- This affects ALL voice messages regardless of duration

## Files Attached
- Sample corrupted audio files (see logs below)
- Screenshot showing Telegram recording at 1:00 but receiving as tiny file

## System Information
```
Server: srv1432586
OS: Linux 6.8.0-106-generic
Node: v22.22.0
OpenClaw: Latest
```

## Tags
`voice-message` `telegram` `audio` `corrupted` `inbound`
