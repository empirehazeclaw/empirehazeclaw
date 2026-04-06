#!/usr/bin/env python3
"""
LinkedIn Outreach Agent
=======================
Manages LinkedIn outreach campaigns, tracks connections and messages.
"""

import argparse
import json
import logging
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import hashlib

AGENT_DIR = Path(__file__).parent
WORKSPACE = AGENT_DIR.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "linkedin_outreach.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("LinkedInOutreach")


class LinkedInProfile:
    """Represents a LinkedIn profile/connection."""
    
    def __init__(self, name: str, profile_url: str = "",
                 headline: str = "", company: str = "",
                 current_position: str = "", location: str = "",
                 email: str = "", phone: str = "",
                 connection_degree: str = "2nd",  # 1st, 2nd, 3rd
                 tags: List[str] = None):
        self.id = self._generate_id(profile_url or name)
        self.name = name
        self.profile_url = profile_url
        self.headline = headline
        self.company = company
        self.current_position = current_position
        self.location = location
        self.email = email
        self.phone = phone
        self.connection_degree = connection_degree
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def _generate_id(self, source: str) -> str:
        raw = f"{source}{datetime.now().isoformat()}"
        return "li_" + hashlib.md5(raw.encode()).hexdigest()[:10]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "profile_url": self.profile_url,
            "headline": self.headline,
            "company": self.company,
            "current_position": self.current_position,
            "location": self.location,
            "email": self.email,
            "phone": self.phone,
            "connection_degree": self.connection_degree,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LinkedInProfile':
        p = cls(
            name=data.get("name", ""),
            profile_url=data.get("profile_url", ""),
            headline=data.get("headline", ""),
            company=data.get("company", ""),
            current_position=data.get("current_position", ""),
            location=data.get("location", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            connection_degree=data.get("connection_degree", "2nd"),
            tags=data.get("tags", [])
        )
        for key in ["id", "created_at", "updated_at"]:
            if key in data:
                setattr(p, key, data[key])
        return p


class OutreachMessage:
    """Represents an outreach message."""
    
    TEMPLATES = ["connection", "follow_up_1", "follow_up_2", "value_add", "meeting_request"]
    
    def __init__(self, profile_id: str, template: str, content: str,
                 subject: str = "", sent_at: str = None,
                 opened: bool = False, responded: bool = False,
                 clicked: bool = False):
        self.id = self._generate_id()
        self.profile_id = profile_id
        self.template = template
        self.subject = subject
        self.content = content
        self.sent_at = sent_at or datetime.now().isoformat()
        self.opened = opened
        self.responded = responded
        self.clicked = clicked
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def _generate_id(self) -> str:
        raw = f"{datetime.now().isoformat()}"
        return "msg_" + hashlib.md5(raw.encode()).hexdigest()[:10]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "template": self.template,
            "subject": self.subject,
            "content": self.content,
            "sent_at": self.sent_at,
            "opened": self.opened,
            "responded": self.responded,
            "clicked": self.clicked,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OutreachMessage':
        m = cls(
            profile_id=data.get("profile_id", ""),
            template=data.get("template", ""),
            content=data.get("content", ""),
            subject=data.get("subject", ""),
            sent_at=data.get("sent_at")
        )
        for key in ["id", "opened", "responded", "clicked", "created_at", "updated_at"]:
            if key in data:
                setattr(m, key, data[key])
        return m
    
    def mark_opened(self):
        self.opened = True
        self.updated_at = datetime.now().isoformat()
    
    def mark_responded(self):
        self.responded = True
        self.updated_at = datetime.now().isoformat()
    
    def mark_clicked(self):
        self.clicked = True
        self.updated_at = datetime.now().isoformat()


class OutreachCampaign:
    """Represents an outreach campaign."""
    
    def __init__(self, name: str, description: str = "",
                 target_industry: str = "", target_titles: List[str] = None,
                 template: str = "connection"):
        self.id = self._generate_id()
        self.name = name
        self.description = description
        self.target_industry = target_industry
        self.target_titles = target_titles or []
        self.template = template
        self.status = "active"
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.sent_count = 0
        self.opened_count = 0
        self.responded_count = 0
    
    def _generate_id(self) -> str:
        raw = f"{self.name}{datetime.now().isoformat()}"
        return "camp_" + hashlib.md5(raw.encode()).hexdigest()[:10]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_industry": self.target_industry,
            "target_titles": self.target_titles,
            "template": self.template,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "sent_count": self.sent_count,
            "opened_count": self.opened_count,
            "responded_count": self.responded_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OutreachCampaign':
        c = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            target_industry=data.get("target_industry", ""),
            target_titles=data.get("target_titles", []),
            template=data.get("template", "connection")
        )
        for key in ["id", "status", "created_at", "updated_at", "sent_count", "opened_count", "responded_count"]:
            if key in data:
                setattr(c, key, data[key])
        return c
    
    def pause(self):
        self.status = "paused"
        self.updated_at = datetime.now().isoformat()
    
    def resume(self):
        self.status = "active"
        self.updated_at = datetime.now().isoformat()
    
    def complete(self):
        self.status = "completed"
        self.updated_at = datetime.now().isoformat()


class LinkedInStore:
    """Manages LinkedIn outreach data persistence."""
    
    def __init__(self, profiles_file: Optional[Path] = None,
                 messages_file: Optional[Path] = None,
                 campaigns_file: Optional[Path] = None):
        self.profiles_file = profiles_file or (DATA_DIR / "linkedin_profiles.json")
        self.messages_file = messages_file or (DATA_DIR / "linkedin_messages.json")
        self.campaigns_file = campaigns_file or (DATA_DIR / "linkedin_campaigns.json")
        
        self.profiles = []
        self.messages = []
        self.campaigns = []
        
        self._load()
    
    def _load(self):
        # Load profiles
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    self.profiles = [LinkedInProfile.from_dict(p) for p in data.get("profiles", [])]
                logger.info(f"Loaded {len(self.profiles)} LinkedIn profiles")
            except Exception as e:
                logger.error(f"Failed to load profiles: {e}")
                self.profiles = []
        
        # Load messages
        if self.messages_file.exists():
            try:
                with open(self.messages_file, 'r') as f:
                    data = json.load(f)
                    self.messages = [OutreachMessage.from_dict(m) for m in data.get("messages", [])]
                logger.info(f"Loaded {len(self.messages)} outreach messages")
            except Exception as e:
                logger.error(f"Failed to load messages: {e}")
                self.messages = []
        
        # Load campaigns
        if self.campaigns_file.exists():
            try:
                with open(self.campaigns_file, 'r') as f:
                    data = json.load(f)
                    self.campaigns = [OutreachCampaign.from_dict(c) for c in data.get("campaigns", [])]
                logger.info(f"Loaded {len(self.campaigns)} campaigns")
            except Exception as e:
                logger.error(f"Failed to load campaigns: {e}")
                self.campaigns = []
    
    def _save_profiles(self):
        data = {"profiles": [p.to_dict() for p in self.profiles], "updated_at": datetime.now().isoformat()}
        with open(self.profiles_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_messages(self):
        data = {"messages": [m.to_dict() for m in self.messages], "updated_at": datetime.now().isoformat()}
        with open(self.messages_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_campaigns(self):
        data = {"campaigns": [c.to_dict() for c in self.campaigns], "updated_at": datetime.now().isoformat()}
        with open(self.campaigns_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save(self):
        self._save_profiles()
        self._save_messages()
        self._save_campaigns()
    
    def add_profile(self, profile: LinkedInProfile) -> bool:
        for existing in self.profiles:
            if existing.profile_url and profile.profile_url:
                if existing.profile_url == profile.profile_url:
                    logger.warning(f"Profile already exists: {profile.profile_url}")
                    return False
        self.profiles.append(profile)
        self._save_profiles()
        return True
    
    def get_profile(self, profile_id: str) -> Optional[LinkedInProfile]:
        for p in self.profiles:
            if p.id == profile_id:
                return p
        return None
    
    def list_profiles(self, campaign_id: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> List[LinkedInProfile]:
        profiles = self.profiles
        if tags:
            profiles = [p for p in profiles if any(t in p.tags for t in tags)]
        return sorted(profiles, key=lambda x: x.created_at, reverse=True)
    
    def add_message(self, message: OutreachMessage) -> bool:
        self.messages.append(message)
        self._save_messages()
        
        # Update campaign stats
        for c in self.campaigns:
            if c.id == message.profile_id:  # Simplified - campaign tracks by profile_id
                c.sent_count += 1
        self._save_campaigns()
        
        return True
    
    def get_messages_for(self, profile_id: str) -> List[OutreachMessage]:
        return [m for m in self.messages if m.profile_id == profile_id]
    
    def add_campaign(self, campaign: OutreachCampaign) -> bool:
        self.campaigns.append(campaign)
        self._save_campaigns()
        return True
    
    def get_campaign(self, campaign_id: str) -> Optional[OutreachCampaign]:
        for c in self.campaigns:
            if c.id == campaign_id:
                return c
        return None
    
    def list_campaigns(self, status: Optional[str] = None) -> List[OutreachCampaign]:
        campaigns = self.campaigns
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        return sorted(campaigns, key=lambda x: x.created_at, reverse=True)
    
    def get_stats(self) -> dict:
        total_profiles = len(self.profiles)
        total_messages = len(self.messages)
        sent_messages = len([m for m in self.messages if m.sent_at])
        opened_messages = len([m for m in self.messages if m.opened])
        responded_messages = len([m for m in self.messages if m.responded])
        
        open_rate = round(opened_messages / sent_messages * 100, 1) if sent_messages else 0
        response_rate = round(responded_messages / sent_messages * 100, 1) if sent_messages else 0
        
        by_degree = {}
        for p in self.profiles:
            by_degree[p.connection_degree] = by_degree.get(p.connection_degree, 0) + 1
        
        by_campaign_status = {}
        for c in self.campaigns:
            by_campaign_status[c.status] = by_campaign_status.get(c.status, 0) + 1
        
        return {
            "total_profiles": total_profiles,
            "total_messages": total_messages,
            "sent_messages": sent_messages,
            "opened_messages": opened_messages,
            "responded_messages": responded_messages,
            "open_rate": open_rate,
            "response_rate": response_rate,
            "by_connection_degree": by_degree,
            "by_campaign_status": by_campaign_status
        }


class LinkedInOutreach:
    """Main LinkedIn outreach agent."""
    
    MESSAGE_TEMPLATES = {
        "connection": """Hi {name},

I came across your profile and was impressed by your work at {company}. 

I help B2B companies automate their sales processes and generate qualified leads. Would love to connect and share some insights that could help with your team's outreach efforts.

Best,
{sender_name}""",
        
        "follow_up_1": """Hi {name},

Just following up on my previous message. I'd love to show you how we helped similar companies in {industry} achieve 3x more qualified leads with less manual effort.

Would you be open to a quick 15-minute call this week?

Best,
{sender_name}""",
        
        "follow_up_2": """Hi {name},

I know you're busy, so I'll keep this short. We're running a limited-time offer for companies in {industry} - free automation audit of your current outreach process.

Interested? Just reply "audit" and I'll send you the details.

Best,
{sender_name}""",
        
        "value_add": """Hi {name},

I noticed you mentioned challenges with lead generation in your recent posts. We just published a case study on how Company X increased their qualified leads by 280% using our approach.

Happy to share the relevant parts if it's helpful for your situation.

Best,
{sender_name}""",
        
        "meeting_request": """Hi {name},

Thanks for connecting! I enjoyed learning more about what you're working on at {company}.

I'd love to show you how we've helped similar companies streamline their sales pipeline. Are you available for a quick 20-minute call this week?

Best,
{sender_name}"""
    }
    
    def __init__(self, sender_name: str = "OpenClaw", sender_company: str = "EmpireHazeClaw"):
        self.store = LinkedInStore()
        self.sender_name = sender_name
        self.sender_company = sender_company
        logger.info("LinkedInOutreach initialized")
    
    def add_profile(self, data: dict) -> Optional[LinkedInProfile]:
        """Add new LinkedIn profile."""
        try:
            profile = LinkedInProfile(
                name=data.get("name", ""),
                profile_url=data.get("profile_url", ""),
                headline=data.get("headline", ""),
                company=data.get("company", ""),
                current_position=data.get("current_position", ""),
                location=data.get("location", ""),
                email=data.get("email", ""),
                phone=data.get("phone", ""),
                connection_degree=data.get("connection_degree", "2nd"),
                tags=data.get("tags", [])
            )
            self.store.add_profile(profile)
            logger.info(f"Added profile: {profile.name}")
            return profile
        except Exception as e:
            logger.error(f"Failed to add profile: {e}")
            return None
    
    def add_campaign(self, data: dict) -> Optional[OutreachCampaign]:
        """Add new outreach campaign."""
        try:
            campaign = OutreachCampaign(
                name=data.get("name", ""),
                description=data.get("description", ""),
                target_industry=data.get("target_industry", ""),
                target_titles=data.get("target_titles", []),
                template=data.get("template", "connection")
            )
            self.store.add_campaign(campaign)
            logger.info(f"Added campaign: {campaign.name}")
            return campaign
        except Exception as e:
            logger.error(f"Failed to add campaign: {e}")
            return None
    
    def generate_message(self, profile_id: str, template: str = "connection") -> Optional[dict]:
        """Generate outreach message from template."""
        profile = self.store.get_profile(profile_id)
        if not profile:
            logger.error(f"Profile not found: {profile_id}")
            return None
        
        if template not in self.MESSAGE_TEMPLATES:
            logger.error(f"Unknown template: {template}")
            return None
        
        template_str = self.MESSAGE_TEMPLATES[template]
        
        # Replace placeholders
        content = template_str.format(
            name=profile.name.split()[0] if profile.name else "",
            full_name=profile.name,
            company=profile.company or "{company}",
            industry=profile.current_position or "{industry}",
            sender_name=self.sender_name,
            sender_company=self.sender_company
        )
        
        return {
            "profile_id": profile_id,
            "profile_name": profile.name,
            "template": template,
            "content": content,
            "preview": content[:100] + "..." if len(content) > 100 else content
        }
    
    def send_message(self, profile_id: str, template: str = "connection",
                     custom_content: str = None) -> Optional[OutreachMessage]:
        """Send outreach message to profile."""
        profile = self.store.get_profile(profile_id)
        if not profile:
            logger.error(f"Profile not found: {profile_id}")
            return None
        
        if custom_content:
            content = custom_content
        else:
            generated = self.generate_message(profile_id, template)
            if not generated:
                return None
            content = generated["content"]
        
        message = OutreachMessage(
            profile_id=profile_id,
            template=template,
            content=content
        )
        
        self.store.add_message(message)
        logger.info(f"Sent message to {profile.name} using template {template}")
        return message
    
    def mark_message_opened(self, message_id: str) -> bool:
        for m in self.store.messages:
            if m.id == message_id:
                m.mark_opened()
                self.store._save_messages()
                return True
        return False
    
    def mark_message_responded(self, message_id: str) -> bool:
        for m in self.store.messages:
            if m.id == message_id:
                m.mark_responded()
                self.store._save_messages()
                return True
        return False
    
    def get_templates(self) -> dict:
        """List available message templates."""
        return {name: template[:200] + "..." for name, template in self.MESSAGE_TEMPLATES.items()}


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Outreach Agent - Manage LinkedIn outreach campaigns and messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --add-profile '{"name": "John Doe", "profile_url": "https://linkedin.com/in/johndoe", "company": "Acme Inc", "headline": "VP of Sales", "tags": ["enterprise", "saas"]}'
  %(prog)s --list-profiles
  %(prog)s --get-profile li_abc123
  %(prog)s --add-campaign '{"name": "SaaS Outreach Q2", "target_industry": "saas", "target_titles": ["VP Sales", "CEO"], "template": "connection"}'
  %(prog)s --list-campaigns
  %(prog)s --generate-message li_abc123 --template connection
  %(prog)s --send li_abc123 --template follow_up_1
  %(prog)s --send li_abc123 --custom "Hi John, I noticed your company..."'
  %(prog)s --mark-opened msg_xyz789
  %(prog)s --mark-responded msg_xyz789
  %(prog)s --get-messages li_abc123
  %(prog)s --templates
  %(prog)s --stats
        """
    )
    
    parser.add_argument("--add-profile", type=str, help="Add LinkedIn profile from JSON")
    parser.add_argument("--list-profiles", action="store_true", help="List all profiles")
    parser.add_argument("--get-profile", type=str, help="Get profile by ID")
    parser.add_argument("--add-campaign", type=str, help="Add campaign from JSON")
    parser.add_argument("--list-campaigns", action="store_true", help="List all campaigns")
    parser.add_argument("--get-campaign", type=str, help="Get campaign by ID")
    parser.add_argument("--generate-message", type=str, help="Generate message for profile")
    parser.add_argument("--template", type=str, default="connection", help="Message template to use")
    parser.add_argument("--send", type=str, help="Send message to profile ID")
    parser.add_argument("--custom", type=str, help="Custom message content")
    parser.add_argument("--mark-opened", type=str, help="Mark message as opened")
    parser.add_argument("--mark-responded", type=str, help="Mark message as responded")
    parser.add_argument("--get-messages", type=str, help="Get messages for profile")
    parser.add_argument("--templates", action="store_true", help="List available templates")
    parser.add_argument("--stats", action="store_true", help="Show outreach statistics")
    
    args = parser.parse_args()
    outreach = LinkedInOutreach()
    
    try:
        if args.add_profile:
            data = json.loads(args.add_profile)
            profile = outreach.add_profile(data)
            if profile:
                print(json.dumps({"success": True, "profile": profile.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to add profile"}))
        
        elif args.list_profiles:
            profiles = outreach.store.list_profiles()
            output = [p.to_dict() for p in profiles]
            print(json.dumps({"count": len(output), "profiles": output}, indent=2))
        
        elif args.get_profile:
            profile = outreach.store.get_profile(args.get_profile)
            if profile:
                print(json.dumps(profile.to_dict(), indent=2))
            else:
                print(json.dumps({"success": False, "message": "Profile not found"}))
        
        elif args.add_campaign:
            data = json.loads(args.add_campaign)
            campaign = outreach.add_campaign(data)
            if campaign:
                print(json.dumps({"success": True, "campaign": campaign.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to add campaign"}))
        
        elif args.list_campaigns:
            campaigns = outreach.store.list_campaigns()
            output = [c.to_dict() for c in campaigns]
            print(json.dumps({"count": len(output), "campaigns": output}, indent=2))
        
        elif args.get_campaign:
            campaign = outreach.store.get_campaign(args.get_campaign)
            if campaign:
                print(json.dumps(campaign.to_dict(), indent=2))
            else:
                print(json.dumps({"success": False, "message": "Campaign not found"}))
        
        elif args.generate_message:
            message = outreach.generate_message(args.generate_message, args.template)
            if message:
                print(json.dumps(message, indent=2))
            else:
                print(json.dumps({"success": False, "message": "Failed to generate message"}))
        
        elif args.send:
            message = outreach.send_message(args.send, args.template, args.custom)
            if message:
                print(json.dumps({"success": True, "message": message.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to send message"}))
        
        elif args.mark_opened:
            if outreach.mark_message_opened(args.mark_opened):
                print(json.dumps({"success": True, "message": "Message marked as opened"}))
            else:
                print(json.dumps({"success": False, "message": "Message not found"}))
        
        elif args.mark_responded:
            if outreach.mark_message_responded(args.mark_responded):
                print(json.dumps({"success": True, "message": "Message marked as responded"}))
            else:
                print(json.dumps({"success": False, "message": "Message not found"}))
        
        elif args.get_messages:
            messages = outreach.store.get_messages_for(args.get_messages)
            output = [m.to_dict() for m in messages]
            print(json.dumps({"count": len(output), "messages": output}, indent=2))
        
        elif args.templates:
            templates = outreach.get_templates()
            print(json.dumps(templates, indent=2))
        
        elif args.stats:
            stats = outreach.store.get_stats()
            print(json.dumps(stats, indent=2))
        
        else:
            parser.print_help()
    
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(json.dumps({"success": False, "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
