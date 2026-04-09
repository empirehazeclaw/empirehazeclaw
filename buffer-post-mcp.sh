#!/bin/bash
# Buffer MCP Posting Script

ORG="69bab5f4723eb2195f93ba4c"

case "$1" in
    channels)
        mcporter call buffer.list_channels organizationId="$ORG"
        ;;
    idea)
        shift
        TEXT="$*"
        mcporter call buffer.create_idea organizationId="$ORG" content="{\"text\":\"$TEXT\"}"
        ;;
    post)
        shift
        CHANNEL="$1"
        shift
        TEXT="$*"
        
        case "$CHANNEL" in
            tiktok) ID="69bbdd587be9f8b17170ef0b" ;;
            youtube) ID="69bbddad7be9f8b17170f03a" ;;
            instagram) ID="69bbe5e67be9f8b171711108" ;;
            *) echo "Unknown channel"; exit 1 ;;
        esac
        
        mcporter call buffer.create_post channelId="$ID" schedulingType="automatic" mode="shareNow" text="$TEXT"
        ;;
    *)
        echo "Usage: $0 channels|idea \"text\"|post tiktok|youtube|instagram \"text\""
        ;;
esac
