#!/bin/bash
# Cache Cleanup — removes old QMD/whisper caches

find /home/clawbot/.cache/qmd -type f -mtime +7 -delete 2>/dev/null
find /home/clawbot/.cache/whisper -type f -mtime +7 -delete 2>/dev/null
npm cache clean --force 2>/dev/null
echo "Cache cleanup done"
