#!/bin/bash
# Printify Manual Upload Helper
# Since API upload is restricted, this helps you prepare

echo "📋 Printify Design Upload Checklist"
echo "================================"
echo ""
echo "Designs to upload (32 total):"
echo ""

ls -1 /home/clawbot/.openclaw/workspace/knowledge/pod_designs_upscaled/*.jpg | nl | while read n f; do
    name=$(basename "$f" .jpg)
    echo "$n. $name"
done

echo ""
echo "📝 NEXT STEPS:"
echo "-------------"
echo "1. Go to printify.com → Dashboard"
echo "2. Click 'Upload' button"
echo "3. Select designs from: knowledge/pod_designs_upscaled/"
echo "4. Create products"
echo "5. Connect to Etsy"
echo ""
echo "🎯 First 5 recommended designs:"
ls -1 /home/clawbot/.openclaw/workspace/knowledge/pod_designs_upscaled/*.jpg | head -5 | while read f; do
    echo "   - $(basename "$f")"
done

echo ""
echo "✅ Total designs ready: 32"
