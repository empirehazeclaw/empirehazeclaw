---
name: video-renderer
description: Erstellt Promotions-Videos mit Remotion. Nutze diese Skill wenn du ein Werbevideo für EmpireHazeClaw brauchst. Erstellt 75-Sekunden Videos mit 6 Scenes: Hook, Email Demo, Features, Booking, Analytics, CTA.
---

# 🎬 Video Renderer Skill

Erstellt Promotions-Videos mit Remotion Framework.

## Struktur

```
video-renderer/
├── SKILL.md          # Diese Datei
├── index.js          # Hauptexport
├── scripts/
│   └── render.sh     # Rendering CLI
└── assets/
    └── storyboard.md # Video-Storyboard
```

## Nutzung

```bash
cd /home/clawbot/.openclaw/workspace/remotion-video
node index.js render
```

## Storyboard nutzen

Das Video-Storyboard liegt unter `video_storyboard.md` im Workspace Root.

## Workflow

1. Storyboard analysieren (im Workspace)
2. Remotion Projekt in `/workspace/remotion-video/`
3. React Components für jede Scene
4. Mit `npx remotion render` rendern

## Export

Output: `/tmp/video-ad.mp4`
