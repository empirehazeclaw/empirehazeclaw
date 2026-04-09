#!/bin/bash
# Complete Social Media Automation Bundle
# Runs all social media automation tasks

echo "📱 Complete Social Media Bundle - $(date)"

# 1. Trend Research (nightly)
echo "🔍 Running trend research..."
python3 /home/clawbot/.openclaw/workspace/scripts/trend_research.py

# 2. Trend Catcher (every 4 hours)
echo "📈 Scanning for trending topics..."
python3 /home/clawbot/.openclaw/workspace/scripts/social_trend_catcher.py

# 3. Generate Posts from Trends
echo "✍️ Generating posts..."
python3 /home/clawbot/.openclaw/workspace/scripts/social_post_generator.py

# 4. Analytics Update
echo "📊 Updating analytics..."
python3 /home/clawbot/.openclaw/workspace/scripts/social_analytics.py

# 5. Posting Times Optimization
echo "🕐 Optimizing posting times..."
python3 /home/clawbot/.openclaw/workspace/scripts/social_posting_optimizer.py

# 6. Content Calendar Update
echo "📅 Updating content calendar..."
python3 /home/clawbot/.openclaw/workspace/scripts/social_content_calendar.py

# 7. Auto-Engagement (if enabled)
echo "🤝 Running engagement cycle..."
python3 /home/clawbot/.openclaw/workspace/scripts/social_auto_engagement.py

# 8. Check for reposts
echo "🔄 Checking for content to repost..."
python3 /home/clawbot/.openclaw/workspace/scripts/social_content_reposter.py

echo "✅ Bundle complete - $(date)"
