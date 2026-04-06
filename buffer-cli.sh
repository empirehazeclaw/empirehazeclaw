#!/bin/bash
# Buffer CLI - Einfache Commands für Buffer

ORG="69bab5f4723eb2195f93ba4c"
TIKTOK="69bbdd587be9f8b17170ef0b"
YOUTUBE="69bbddad7be9f8b17170f03a"
INSTAGRAM="69bbe5e67be9f8b171711108"

case "$1" in
    channels)
        mcporter call buffer.list_channels organizationId="$ORG"
        ;;
    post)
        CHANNEL="$2"
        shift 2
        TEXT="$*"
        
        case "$CHANNEL" in
            tiktok) ID="$TIKTOK" ;;
            youtube) ID="$YOUTUBE" ;;
            instagram) ID="$INSTAGRAM" ;;
            *) echo "Error: Use tiktok, youtube, or instagram"; exit 1 ;;
        esac
        
        mcporter call buffer.create_post channelId="$ID" schedulingType="automatic" mode="shareNow" text="$TEXT"
        ;;
    draft)
        CHANNEL="$2"
        shift 2
        TEXT="$*"
        
        case "$CHANNEL" in
            tiktok) ID="$TIKTOK" ;;
            *) echo "Error: Only tiktok supports drafts"; exit 1 ;;
        esac
        
        mcporter call buffer.create_post channelId="$ID" schedulingType="automatic" mode="addToQueue" text="$TEXT" saveToDraft="true"
        ;;
    idea)
        shift
        TEXT="$*"
        mcporter call buffer.create_idea organizationId="$ORG" content="{\"text\":\"$TEXT\"}"
        ;;
    video)
        # ⚠️ Video Upload über MCP NICHT möglich!
        echo "Error: Video uploads not supported via MCP"
        echo ""
        echo "Workaround:"
        echo "1. Video zu Cloudinary/Vercel hosten"
        echo "2. Als Link posten"
        echo "3. Oder manuell über buffer.com"
        exit 1
        ;;
    *)
        echo "Buffer CLI"
        echo ""
        echo "Usage:"
        echo "  buffer-cli channels              - List all channels"
        echo "  buffer-cli post tiktok \"Text\"    - Post to TikTok"
        echo "  buffer-cli post youtube \"Text\"   - Post to YouTube"
        echo "  buffer-cli post instagram \"Text\" - Post to Instagram"
        echo "  buffer-cli idea \"Text\"           - Create an idea"
        echo "  buffer-cli video                  - Show video upload info"
        echo ""
        echo "⚠️ Video Upload via MCP NOT SUPPORTED"
        ;;
esac
