#!/usr/bin/env python3
"""
Twitter Profile Optimizer
Automatically optimize profile for follower growth
"""

import json
import os
from datetime import datetime

CONFIG_FILE = "/home/clawbot/.openclaw/workspace/memory/social_config.json"
PROFILE_FILE = "/home/clawbot/.openclaw/logs/profile_optimizer.json"

class ProfileOptimizer:
    def __init__(self):
        self.load_config()
        self.load_profile()
        
    def load_config(self):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            self.twitter = config.get("twitter", {})
            
    def load_profile(self):
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, 'r') as f:
                self.profile = json.load(f)
        else:
            self.profile = {
                "current": {
                    "name": "EmpireHazeClaw",
                    "bio": "",
                    "location": "",
                    "website": "",
                    "profile_image": ""
                },
                "optimizations": [],
                "history": []
            }
            self.save_profile()
            
    def save_profile(self):
        with open(PROFILE_FILE, 'w') as f:
            json.dump(self.profile, f, indent=2)
            
    def get_api(self):
        """Get Twitter API connection"""
        from requests_oauthlib import OAuth1
        
        oauth = OAuth1(
            self.twitter.get("api_key", ""),
            client_secret=self.twitter.get("api_secret", ""),
            resource_owner_key=self.twitter.get("access_token", ""),
            resource_owner_secret=self.twitter.get("access_token_secret", "")
        )
        return oauth
        
    def analyze_profile(self):
        """Analyze current profile for optimization opportunities"""
        current = self.profile["current"]
        
        analysis = {
            "score": 0,
            "issues": [],
            "recommendations": []
        }
        
        # Check name
        if len(current.get("name", "")) < 3:
            analysis["issues"].append("Name too short")
            analysis["recommendations"].append("Use a clear, memorable name")
        else:
            analysis["score"] += 20
            
        # Check bio
        bio = current.get("bio", "")
        if len(bio) < 50:
            analysis["issues"].append("Bio too short (under 50 chars)")
            analysis["recommendations"].append("Add a compelling bio (50-160 chars)")
        else:
            analysis["score"] += 25
            
        if "AI" not in bio and "automation" not in bio.lower():
            analysis["recommendations"].append("Include AI-related keywords")
        else:
            analysis["score"] += 15
            
        # Check for emojis in bio
        if "🤖" not in bio and "🚀" not in bio and "💡" not in bio:
            analysis["recommendations"].append("Add relevant emojis")
        else:
            analysis["score"] += 10
            
        # Check location
        if not current.get("location"):
            analysis["issues"].append("No location set")
            analysis["recommendations"].append("Add location (e.g., Berlin, Germany)")
        else:
            analysis["score"] += 10
            
        # Check website
        if not current.get("website"):
            analysis["issues"].append("No website/link")
            analysis["recommendations"].append("Add a link to your project or portfolio")
        else:
            analysis["score"] += 20
            
        return analysis
        
    def generate_optimized_profile(self):
        """Generate optimized profile options"""
        
        options = [
            {
                "type": "growth_focused",
                "name": "🤖 AI Automation Builder",
                "bio": "Building AI agents that automate everything 🚀\n\nPOD • Trading • Growth\n\nDM for collaborations 🤝",
                "location": "Berlin, Germany",
                "website": "https://twitter.com/EmpireHazeClaw"
            },
            {
                "type": "personal_brand",
                "name": "Nico | AI Agent Builder",
                "bio": "🎯 Building automated systems with AI\n\n📈 POD Business\n🤖 OpenClaw Agent\n💡 Sharing my journey\n\nFollow for daily AI tips!",
                "location": "Berlin, Germany",
                "website": ""
            },
            {
                "type": "business",
                "name": "AI Automation Expert 🤖",
                "bio": "Helping businesses scale with AI 🚀\n\n• AI Agent Setup\n• Automation Consulting\n• Digital Products\n\nDM for inquiries 📩",
                "location": "Germany",
                "website": ""
            }
        ]
        
        return options
        
    def apply_optimization(self, option_type):
        """Apply an optimization profile"""
        options = self.generate_optimized_profile()
        
        selected = None
        for opt in options:
            if opt["type"] == option_type:
                selected = opt
                break
                
        if not selected:
            return False, "Option not found"
            
        # Log the change
        self.profile["history"].append({
            "timestamp": datetime.now().isoformat(),
            "type": option_type,
            "changes": selected
        })
        
        self.profile["optimizations"].append({
            "applied": datetime.now().isoformat(),
            "type": option_type,
            "status": "ready"
        })
        
        self.save_profile()
        
        return True, selected
        
    def get_recommended_optimization(self):
        """Get the best recommended optimization"""
        analysis = self.analyze_profile()
        
        # Score thresholds
        if analysis["score"] < 50:
            return "growth_focused"
        elif analysis["score"] < 75:
            return "personal_brand"
        else:
            return "business"
            
    def get_current_stats(self):
        """Get current profile stats"""
        analysis = self.analyze_profile()
        
        return {
            "score": analysis["score"],
            "issues": len(analysis["issues"]),
            "recommendations": len(analysis["recommendations"]),
            "optimizations_applied": len(self.profile.get("optimizations", []))
        }
        
    def generate_report(self):
        """Generate full profile report"""
        analysis = self.analyze_profile()
        stats = self.get_current_stats()
        
        report = "📊 **Profile Optimization Report**\n\n"
        
        report += f"**📈 Score:** {stats['score']}/100\n\n"
        
        if analysis["issues"]:
            report += "**⚠️ Issues:**\n"
            for issue in analysis["issues"]:
                report += f"  • {issue}\n"
            report += "\n"
            
        if analysis["recommendations"]:
            report += "**💡 Recommendations:**\n"
            for rec in analysis["recommendations"]:
                report += f"  • {rec}\n"
            report += "\n"
            
        report += f"**🔧 Optimizations applied:** {stats['optimizations_applied']}\n"
        
        return report

if __name__ == "__main__":
    optimizer = ProfileOptimizer()
    
    print("📊 **Twitter Profile Optimizer**\n")
    
    # Analyze current profile
    print(optimizer.generate_report())
    
    print("\n" + "="*50)
    print("\n🎯 **Recommended Optimization:**")
    recommended = optimizer.get_recommended_optimization()
    print(f"  {recommended}")
    
    print("\n📋 **Available Optimizations:**")
    for opt in optimizer.generate_optimized_profile():
        print(f"\n  **{opt['type']}**:")
        print(f"  Name: {opt['name']}")
        print(f"  Bio: {opt['bio'][:80]}...")
        
    print("\n" + "="*50)
    print("\n💡 To apply an optimization, tell me which type!")
