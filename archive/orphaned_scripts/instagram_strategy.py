#!/usr/bin/env python3
"""
Instagram Content Generator - Basierend auf Torben Platzer Strategie
"""

# Instagram Growth Framework (Torben Platzer)
INSTAGRAM_GROWTH_FRAMEWORK = {
    "phase_1_positionierung": {
        "name": "Positionierung & Nische",
        "duration": "Woche 1-2",
        "actions": [
            "Klare Bio: Wer bin ich, für wen?",
            "Profilbild & Highlights gestalten",
            "Nische definieren (3-5 Themen)"
        ]
    },
    "phase_2_content": {
        "name": "Content Aufbau",
        "duration": "Woche 3-6",
        "actions": [
            "Reels erstellen (3x/Woche)",
            "Carousels für Value",
            "Stories für Community"
        ]
    },
    "phase_3_growth": {
        "name": "Organisches Wachstum",
        "duration": "Woche 7-10",
        "actions": [
            "Konsistenz: täglich posten",
            "Community Engagement",
            "Hashtag Strategie",
            "Cross-Promotion"
        ]
    }
}

# Instagram Best Practices 2026
INSTAGRAM_BEST_PRACTICES_2026 = {
    "content_formats": {
        "reels": {
            "priority": 1,
            "length": "15-60 seconds",
            "music": "trending sounds",
            "hook": "first 3 seconds critical"
        },
        "carousels": {
            "priority": 2,
            "slides": "5-10",
            "value": "educational/tips"
        },
        "stories": {
            "priority": 3,
            "frequency": "daily",
            "interactive": True
        }
    },
    "posting_times": {
        "weekday": ["11:00-13:00", "19:00-21:00"],
        "weekend": ["10:00-12:00", "16:00-18:00"]
    },
    "hashtag_strategy": {
        "tier1_niche": ["#DeinNischenBegriff"],
        "tier2_industry": ["#IndustryKeyword"],
        "tier3_broad": ["#SocialMedia", "#Marketing"],
        "max_count": 30,
        "min_count": 5
    },
    "engagement": {
        "comment_response": "< 1 hour",
        "dm_response": "< 2 hours",
        "stories_reply": "always"
    }
}

# Content Ideen Generator
CONTENT_IDEAS = {
    "education": [
        "How-To Tutorials",
        "Tipps & Tricks",
        "Behind the Scenes",
        "Process Shows"
    ],
    "entertainment": [
        "Reels mit Trends",
        "Kommentare",
        "Q&A Sessions"
    ],
    "inspiration": [
        "Success Stories",
        "Client Results",
        "Motivation"
    ],
    "community": [
        "User Generated Content",
        "Duette/Stitches",
        "Polls & Questions"
    ]
}

# Template Generator
import random

def generate_post_content(content_type, topic, tone="professional"):
    """Generate Instagram-ready content"""
    
    templates = {
        "reel_hook": [
            "Das wusste ich mit 20 nicht... 🤔",
            f"3 Tipps für {topic} die jeder kennen sollte 👇",
            f"Warum {topic} so wichtig ist... 📊"
        ],
        "carousel_intro": [
            f"Komplette Anleitung zu {topic} 📱",
            f"Alles was du über {topic} wissen musst 🧵",
            f"{topic} - Schritt für Schritt 👇"
        ],
        "story_poll": [
            "Was soll ich als nächstes zeigen?",
            "Wolltest du schon immer wissen...",
            "Rate mal, was passiert ist!"
        ]
    }
    
    options = templates.get(content_type, templates["reel_hook"])
    return random.choice(options)


def get_hashtags(niche, industry):
    """Generate hashtag set"""
    return [
        f"#{niche.replace(' ', '')}",
        f"#{industry.replace(' ', '')}",
        "#growthhacking",
        "#digitalmarketing",
        "#2026"
    ]


# Export for use
if __name__ == "__main__":
    print("=== INSTAGRAM GROWTH STRATEGY 2026 ===")
    print(f"Framework Phases: {len(INSTAGRAM_GROWTH_FRAMEWORK)}")
    print(f"Best Practices: {len(INSTAGRAM_BEST_PRACTICES_2026)}")
    print(f"Content Ideas: {len(CONTENT_IDEAS)}")
