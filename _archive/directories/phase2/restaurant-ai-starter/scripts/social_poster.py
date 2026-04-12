#!/usr/bin/env python3
"""
📱 RESTAURANT SOCIAL MEDIA POSTER
===================================
Generate and schedule social media posts for restaurants.
Supports: Instagram, Facebook, Twitter/X, LinkedIn

Usage:
    python3 social_poster.py --platform instagram --type menu --dish "Risotto"
    python3 social_poster.py --platform all --type promotion --code "BIRTHDAY20"
    python3 social_poster.py --generate-week

Author: EmpireHazeClaw
Version: 1.0
"""

import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
import random

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
POSTS_FILE = DATA_DIR / "social_posts.json"
TEMPLATES_FILE = DATA_DIR / "social_templates.json"

class SocialMediaPoster:
    
    # Post Templates
    PLATFORMS = {
        "instagram": {
            "max_length": 2200,
            "hashtag_limit": 30,
            "caption_template": "{hook}\n\n{content}\n\n{call_to_action}\n\n{hashtags}"
        },
        "facebook": {
            "max_length": 500,
            "hashtag_limit": 3,
            "caption_template": "{hook}\n\n{content}\n\n{call_to_action}"
        },
        "twitter": {
            "max_length": 280,
            "hashtag_limit": 3,
            "caption_template": "{hook} {content} {call_to_action}"
        },
        "linkedin": {
            "max_length": 3000,
            "hashtag_limit": 5,
            "caption_template": "{hook}\n\n{content}\n\n{call_to_action}"
        }
    }
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.posts = self._load_posts()
        self.templates = self._load_templates()
    
    def _load_posts(self):
        if POSTS_FILE.exists():
            with open(POSTS_FILE, 'r') as f:
                return json.load(f)
        return {"posts": [], "scheduled": []}
    
    def _load_templates(self):
        if TEMPLATES_FILE.exists():
            with open(TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        return self._default_templates()
    
    def _save_posts(self):
        with open(POSTS_FILE, 'w') as f:
            json.dump(self.posts, f, indent=2)
    
    def _default_templates(self):
        return {
            "menu": {
                "hooks": [
                    "Unser neues Gericht macht süchtig! 🤤",
                    "Handwerk trifft Leidenschaft auf einem Teller.",
                    "So schmeckt der Frühling! 🌿",
                    "Darf ich vorstellen: Unser neuestes Meisterwerk!",
                    "Frisch auf den Tisch – buchstäblich!"
                ],
                "content": [
                    "Unser Küchenteam hat sich selbst übertroffen.",
                    "Jede Zutat mit Bedacht gewählt, jeder Bissen ein Erlebnis.",
                    "Saisonal, lokal, und zubereitet mit Liebe."
                ],
                "cta": [
                    "Reserviert jetzt euren Tisch! 📞",
                    "Schaut vorbei und probiert selbst!",
                    "Ihr findet uns unter [Adresse]",
                    "Jetzt Tisch reservieren: [Link]"
                ],
                "hashtags": [
                    "#foodporn #instafood #foodie #lecker #yummy",
                    "#frischekoche #hausmannskost #restaurant #genuss",
                    "#foodstagram #eeeeeats #foodlover #gastro"
                ]
            },
            "promotion": {
                "hooks": [
                    "Nur noch bis Sonntag! ⏰",
                    "Das könnt ihr euch nicht entgehen lassen!",
                    "Spoiler: Es gibt etwas zu gewinnen! 🎁",
                    "Brief an alle Food-Lovers 📣",
                    "Setzt ein Lesezeichen – das wird euch gefallen!"
                ],
                "content": [
                    "[Promotion details hier einfügen]",
                    "Bedingungen: [hier einfügen]",
                    "Gilt für: [Datum/Wochenende/Zeitraum]"
                ],
                "cta": [
                    "Jetzt zugreifen!",
                    "Schreibt uns oder ruft an!",
                    "Reserviert jetzt und spart!",
                    "Teilt und likelihoodt!"
                ],
                "hashtags": [
                    "#angebot #sparen #deal #restaurant",
                    "#aktion #限定 #nurjetzt #nichtverpassen"
                ]
            },
            "behind_scenes": {
                "hooks": [
                    "Ihr wollt mal sehen, wie Magie entsteht? 👨‍🍳",
                    "Meet the Team: Heute stellen wir euch [Name] vor!",
                    "So sieht ein typischer Morgen in unserer Küche aus ☀️",
                    "Wusstet ihr schon...? 🤔",
                    "Das passiert, bevor die Küche öffnet! 🌅"
                ],
                "content": [
                    "Unsere Köche starten jeden Tag um 6 Uhr früh.",
                    "[Name] ist schon seit [X] Jahren Teil unserer Familie.",
                    "Hinter jedem Gericht steckt viel Vorbereitung."
                ],
                "cta": [
                    "Folgt uns für mehr Einblicke!",
                    "Schreibt uns eure Fragen in die Comments!",
                    "Lernt unser Team kennen!"
                ],
                "hashtags": [
                    "#behindthescenes #kitchenlife #teamwork #kochleben",
                    "#restaurantlife #food preparation #gastronomie"
                ]
            },
            "seasonal": {
                "hooks": [
                    "Der Herbst ist da – und mit ihm unser Seasonal Menu! 🍂",
                    "Winterzauber auf dem Teller! ❄️",
                    "Frühling auf jedem Bissen! 🌸",
                    "Sommer, Sonne, neue Gerichte! ☀️",
                    "Diese Woche im Zeichen des [Event/Feiertag]!"
                ],
                "content": [
                    "Wir haben unsere Karte frisch aufgefüllt.",
                    "Saisonal bedeutet: Am besten, wenn die Zutaten frisch sind.",
                    "Von Feld direkt auf euren Teller."
                ],
                "cta": [
                    "Probiert unsere Seasonal Specials!",
                    "Schaut vorbei und lasst euch überraschen!",
                    "Die Karte wartet auf euch!"
                ],
                "hashtags": [
                    "#seasonal #saison #frisch #regional",
                    "#seasonalfood #herbstküche #winterfood"
                ]
            }
        }
    
    def generate_post(self, post_type, platform="instagram", custom_data=None):
        """Generate a social media post"""
        
        template = self.templates.get(post_type, self.templates["menu"])
        platform_config = self.PLATFORMS.get(platform, self.PLATFORMS["instagram"])
        
        # Randomly select template parts
        hook = random.choice(template["hooks"])
        content = random.choice(template["content"])
        cta = random.choice(template["cta"])
        hashtags = random.choice(template["hashtags"])
        
        # Override with custom data if provided
        if custom_data:
            for key in ["hook", "content", "cta", "hashtags"]:
                if key in custom_data:
                    locals()[key] = custom_data[key]
        
        # Build post
        post = platform_config["caption_template"].format(
            hook=hook,
            content=content,
            call_to_action=cta,
            hashtags=hashtags if platform != "twitter" else ""
        )
        
        # Truncate if necessary
        max_len = platform_config["max_length"]
        if len(post) > max_len:
            post = post[:max_len-3] + "..."
        
        return {
            "post": post,
            "platform": platform,
            "type": post_type,
            "generated_at": datetime.now().isoformat(),
            "char_count": len(post),
            "hashtag_count": post.count('#')
        }
    
    def generate_weekly_content(self, restaurant_name="Unser Restaurant"):
        """Generate a week worth of content"""
        
        week_content = []
        
        # Monday - Menu Monday
        week_content.append({
            "day": "Montag",
            "theme": "menu",
            "suggestion": "Neues Gericht vorstellen oder Bestseller betonen",
            "post": self.generate_post("menu", "instagram")
        })
        
        # Tuesday - Behind the scenes
        week_content.append({
            "day": "Dienstag",
            "theme": "behind_scenes", 
            "suggestion": "Team-Mitglied vorstellen oder Küchen-Einblick",
            "post": self.generate_post("behind_scenes", "facebook")
        })
        
        # Wednesday - Promotion/Mid-week special
        week_content.append({
            "day": "Mittwoch",
            "theme": "promotion",
            "suggestion": "Mittwochs-Special oder Tagesangebot",
            "post": self.generate_post("promotion", "twitter")
        })
        
        # Thursday - Seasonal/Special
        week_content.append({
            "day": "Donnerstag",
            "theme": "seasonal",
            "suggestion": "Saisonales Gericht oder Event bewerben",
            "post": self.generate_post("seasonal", "instagram")
        })
        
        # Friday - Weekend promo
        week_content.append({
            "day": "Freitag",
            "theme": "promotion",
            "suggestion": "Wochenende-Tipps, Reservierungen, Atmosphäre",
            "post": self.generate_post("promotion", "instagram")
        })
        
        # Saturday - UGC/Social proof
        week_content.append({
            "day": "Samstag",
            "theme": "behind_scenes",
            "suggestion": "Gästebilder teilen oder Erfahrungsbericht",
            "post": self.generate_post("behind_scenes", "facebook")
        })
        
        # Sunday - Relaxed, community
        week_content.append({
            "day": "Sonntag",
            "theme": "seasonal",
            "suggestion": "Ausblick auf die neue Woche, Ruhetags-Vorbereitung",
            "post": self.generate_post("seasonal", "linkedin")
        })
        
        return week_content
    
    def schedule_post(self, post_content, platform, scheduled_time):
        """Schedule a post for later"""
        
        scheduled_post = {
            "id": f"SP-{len(self.posts['scheduled']) + 1:04d}",
            "content": post_content,
            "platform": platform,
            "scheduled_for": scheduled_time.isoformat() if isinstance(scheduled_time, datetime) else scheduled_time,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
        self.posts["scheduled"].append(scheduled_post)
        self._save_posts()
        
        return scheduled_post
    
    def save_post_history(self, post_data, platform):
        """Save a post to history"""
        
        history_entry = {
            "id": f"PH-{len(self.posts['posts']) + 1:04d}",
            "content": post_data.get("post", post_data.get("content", "")),
            "platform": platform,
            "posted_at": datetime.now().isoformat(),
            "type": post_data.get("type", "unknown")
        }
        
        self.posts["posts"].append(history_entry)
        self._save_posts()
        
        return history_entry
    
    def get_analytics_summary(self):
        """Get analytics summary"""
        
        posts = self.posts.get("posts", [])
        
        summary = {
            "total_posts": len(posts),
            "by_platform": {},
            "this_week": 0,
            "this_month": 0
        }
        
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        for post in posts:
            platform = post.get("platform", "unknown")
            summary["by_platform"][platform] = summary["by_platform"].get(platform, 0) + 1
            
            posted_at = post.get("posted_at", "")
            if posted_at > week_ago:
                summary["this_week"] += 1
            if posted_at > month_ago:
                summary["this_month"] += 1
        
        return summary
    
    def print_weekly_plan(self, content_plan):
        """Print weekly content plan"""
        
        print("\n📅 WOCHEN-PLAN (Content)")
        print("="*60)
        
        for day_content in content_plan:
            print(f"\n📌 {day_content['day']} - {day_content['theme'].upper()}")
            print(f"   Vorschlag: {day_content['suggestion']}")
            print(f"   Plattform: {day_content['post']['platform']}")
            print(f"   ---")
            print(f"   {day_content['post']['post'][:150]}...")
        
        print("\n" + "="*60)
        print(f"📊 Gesamt: {len(content_plan)} Posts geplant")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Restaurant Social Media Poster")
    parser.add_argument('--platform', 
                        choices=['instagram', 'facebook', 'twitter', 'linkedin', 'all'],
                        default='instagram',
                        help='Platform to generate for')
    parser.add_argument('--type',
                        choices=['menu', 'promotion', 'behind_scenes', 'seasonal', 'all'],
                        default='all',
                        help='Type of content')
    parser.add_argument('--generate-week', action='store_true',
                        help='Generate full week of content')
    parser.add_argument('--dish', default='', help='Dish name for menu post')
    parser.add_argument('--code', default='', help='Promo code')
    parser.add_argument('--save', action='store_true', help='Save to file')
    
    args = parser.parse_args()
    
    poster = SocialMediaPoster()
    
    if args.generate_week:
        week_plan = poster.generate_weekly_content()
        poster.print_weekly_plan(week_plan)
        
        if args.save:
            output_file = DATA_DIR / "weekly_content_plan.json"
            with open(output_file, 'w') as f:
                json.dump(week_plan, f, indent=2)
            print(f"\n✅ Week plan saved to {output_file}")
    
    else:
        # Generate single post
        custom_data = {}
        if args.dish:
            custom_data["content"] = f"Heute servieren wir: {args.dish}!"
        if args.code:
            custom_data["cta"] = f"Code: {args.code}"
        
        post = poster.generate_post(args.type, args.platform, custom_data if custom_data else None)
        
        print(f"\n📱 {args.platform.upper()} POST:")
        print("-"*60)
        print(post["post"])
        print("-"*60)
        print(f"\n📊 Stats: {post['char_count']} Zeichen, {post['hashtag_count']} Hashtags")

if __name__ == "__main__":
    main()
