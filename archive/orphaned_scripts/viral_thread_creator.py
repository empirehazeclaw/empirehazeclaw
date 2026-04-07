#!/usr/bin/env python3
"""
Viral Thread Creator
Automatically creates and posts viral threads
"""

import json
import os
import random
from datetime import datetime

THREADS_FILE = "/home/clawbot/.openclaw/logs/viral_threads.json"

class ViralThreadCreator:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        if os.path.exists(THREADS_FILE):
            with open(THREADS_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "templates": [
                    {
                        "id": 1,
                        "topic": "AI Automation",
                        "title": "How I built a 6-figure side hustle with AI",
                        "parts": 7,
                        "hooks": [
                            "🧵 How I made $10K/month with AI (without coding)",
                            "🧵 I automated 80% of my business. Here's how:",
                            "🧵 The AI tools that changed my life (2026 edition)"
                        ]
                    },
                    {
                        "id": 2,
                        "topic": "Productivity",
                        "title": "Productivity secrets",
                        "parts": 5,
                        "hooks": [
                            "I used to work 10 hours/day. Now I work 3. 🧵",
                            "The 5 productivity habits that changed everything",
                            "How to 10x your output (without working more)"
                        ]
                    },
                    {
                        "id": 3,
                        "topic": "POD Business",
                        "title": "Print-on-Demand Guide",
                        "parts": 6,
                        "hooks": [
                            "🧵 I started a POD business with $0. Here's how:",
                            "How to make $1K/month with POD (step by step)",
                            "The best POD niches for 2026"
                        ]
                    },
                    {
                        "id": 4,
                        "topic": "Tech Stack",
                        "title": "My AI Tech Stack",
                        "parts": 8,
                        "hooks": [
                            "🧵 My AI tool stack for 2026 (complete guide)",
                            "The exact tools I use to automate everything",
                            "Best AI tools for entrepreneurs (2026)"
                        ]
                    },
                    {
                        "id": 5,
                        "topic": "Growth",
                        "title": "Follower Growth",
                        "parts": 5,
                        "hooks": [
                            "How I grew to 1K followers in 30 days 🧵",
                            "The Twitter growth strategy that actually works",
                            "I gained 500 followers in a week. Here's how:"
                        ]
                    }
                ],
                "posted_threads": [],
                "scheduled_threads": [],
                "stats": {
                    "total_posted": 0,
                    "total_likes": 0,
                    "total_retweets": 0,
                    "total_replies": 0
                }
            }
            self.save_data()
            
    def save_data(self):
        with open(THREADS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def generate_thread_content(self, template_id):
        """Generate full thread content from template"""
        
        # Template content library
        threads = {
            1: {  # AI Automation
                "hook": "🧵 How I made $10K/month with AI (without coding)",
                "parts": [
                    "I was working 10 hours/day on admin work.\n\nReplying to emails.\nScheduling meetings.\nDoing 'research'.\n\nI was BUSY but not PRODUCTIVE.",
                    "Then I discovered AI agents.\n\nNow my AI:\n✓ Answers emails\n✓ Schedules meetings\n✓ Does research\n✓ Posts to social media\n\nI work 3 hours/day.",
                    "The best part?\n\nI didn't write a single line of code.\n\nI used no-code tools and AI platforms to build my automation stack.",
                    "Here's my stack:\n\n🤖 OpenClaw - AI agents\n🧠 ChatGPT - Research & writing\n🎨 Leonardo.ai - Design\n⚡ Make.com - Workflows\n📊 Notion - Knowledge\n\nTotal: ~$50/month",
                    "The results after 6 months:\n\n📈 Revenue: +300%\n⏰ Time saved: 7 hours/day\n💰 Extra income: $10K/month\n\nNot bad for a KFZ mechanic turned AI entrepreneur.",
                    "But here's the truth:\n\nYou don't need to be a coder.\n\nYou need to be willing to learn and experiment.\n\nStart with ONE automation.\nAdd more over time.",
                    "Your turn:\n\nWhat's ONE task you'd love to automate?\n\nDrop it in the comments 👇\n\nI'll help you figure out how!\n\n#AI #Automation #Entrepreneur #SideHustle"
                ]
            },
            2: {  # Productivity
                "hook": "I used to work 10 hours/day. Now I work 3. 🧵",
                "parts": [
                    "My old routine:\n6:00 Wake up\n6:30 Emails (2 hours)\n8:30 Meetings (3 hours)\n11:30 Admin tasks\n...\n10:00 Finally done\n\nI was exhausted.",
                    "Then I asked myself:\n\n'What if AI could do 80% of this?'\n\nSo I built an AI system that handles:\n- Email filtering & drafting\n- Meeting scheduling\n- Research\n- Social media\n\nNow I focus on CREATION.",
                    "The key insight:\n\nDon't optimize your work.\nAutomate it.\n\nYour brain is for CREATING, not computing.",
                    "My new routine:\n6:00 Wake up\n6:15 AI has filtered my emails\n6:30 AI has scheduled my day\n7:00 Deep work (no interruptions)\n12:00 AI has posted my content\n\nI work 3 hours.\nI produce 10x more.",
                    "The takeaway:\n\nWork SMARTER, not HARDER.\n\nAI is your co-pilot.\nUse it.\n\n#Productivity #AI #Automation"
                ]
            },
            3: {  # POD Business
                "hook": "🧵 I started a POD business with $0. Here's how:",
                "parts": [
                    "Print-on-Demand = sell designs without inventory.\n\nYou create.\nPlatform prints & ships.\nYou get the profit.\n\nZero upfront cost.\nZero risk.",
                    "Step 1: Find a niche\n\nI chose: Exotic pets + Tech vibes\n\nWhy? Low competition, high demand.\n\nAxolotl, Fennec Fox, Hedgehogs = gold mines.",
                    "Step 2: Create designs\n\nLeonardo.ai = game changer.\n\nGenerate 100 designs in an hour.\nPick the best.\n\nNo design skills needed.",
                    "Step 3: List on Etsy + Printify\n\nFree to start.\n20 free listings.\nPrintful/Printify handles everything.",
                    "Step 4: Scale\n\nStart with 10 designs.\nTest what sells.\nDouble down on winners.\n\nMy result:\n$500/month in 3 months.\n$2K/month in 6 months.",
                    "The opportunity:\n\nPOD + AI = unlimited products.\n\nYour imagination is the limit.\n\nStart today.\n\n#POD #PrintOnDemand #Etsy #SideHustle"
                ]
            },
            4: {  # Tech Stack
                "hook": "🧵 My AI tool stack for 2026 (complete guide)",
                "parts": [
                    "1 year ago, I was a complete tech newbie.\n\nNow I run an AI-powered business.\n\nHere's exactly what I use 👇",
                    "🤖 AI Agents\n- OpenClaw: My main agent system\n- AgentGPT: Quick automations\n- AutoGPT: Research tasks\n\nThese do 80% of my work.",
                    "🧠 LLMs\n- ChatGPT: Everything else\n- Claude: Coding & analysis\n- Gemini: Research & search\n\nEach has special strengths.",
                    "🎨 Content Creation\n- Leonardo.ai: Images & designs\n- CapCut: Video editing\n- Canva: Quick graphics\n\nCreate 10x faster.",
                    "⚡ Automation\n- Make.com: Workflows\n- Zapier: Integrations\n- n8n: Self-hosted automation\n\nConnect everything.",
                    "📊 Business\n- Notion: Knowledge base\n- QuickBooks: Finance\n- Google: Everything else\n\nStay organized.",
                    "💰 Total cost: ~$100/month\n\nValue generated: $10K+/month\n\nThe ROI is insane.\n\nStart with ONE tool.\nAdd more as you grow.\n\n#AI #Tools #TechStack"
                ]
            },
            5: {  # Growth
                "hook": "How I grew to 1K followers in 30 days 🧵",
                "parts": [
                    "I started with 0 followers.\n\n30 days later: 1K followers.\n\nNot viral fame, but real, engaged followers.\n\nHere's exactly what I did 👇",
                    "1. Post DAILY\n\nConsistency > Quality (at first)\n\nI posted 2-3 times every day.\n\nAlgorithm rewards activity.",
                    "2. Engage FIRST\n\nBefore posting, I engaged.\n\n30 minutes of genuine interactions.\n\nLiked, commented, replied.\n\nThis built my network.",
                    "3. Hooks matter\n\nFirst 3 words = everything.\n\nExample:\n❌ 'Here's my thoughts on AI'\n✅ 'I made $10K with AI'\n\nBe specific. Be bold.",
                    "4. Use threads\n\nThreads get 3x more reach.\n\nPeople save them.\nShare them.\n\nWrite value-packed threads.",
                    "5. Follow smart\n\nFollow 50 relevant accounts/day.\n\n30% follow back.\n\nThat's 15 new followers daily.\n\n30 days = 450 followers.",
                    "The formula is simple:\n\nPost valuable content daily\n+ Engage genuinely\n+ Be consistent\n\n= Growth\n\nNo tricks. Just work.\n\n#Growth #Twitter #SocialMedia"
                ]
            }
        }
        
        return threads.get(template_id, threads[1])
        
    def select_thread_template(self):
        """Select a random thread template"""
        return random.choice(self.data["templates"])
        
    def create_thread(self, template_id=None):
        """Create a new thread"""
        if not template_id:
            template = self.select_thread_template()
            template_id = template["id"]
        
        # Generate full thread content with hooks
        full_content = self.generate_thread_content(template_id)
            
        thread = {
            "id": len(self.data["posted_threads"]) + 1,
            "template_id": template_id,
            "hook": full_content["hook"],
            "parts": full_content["parts"],
            "created": datetime.now().isoformat(),
            "status": "draft",
            "posted_parts": 0
        }
        
        return thread
        
    def post_thread(self, thread):
        """Post a thread (would use Twitter API in production)"""
        # In production, this would post to Twitter
        
        self.data["posted_threads"].append({
            "thread_id": thread["id"],
            "posted_at": datetime.now().isoformat(),
            "parts_posted": len(thread["parts"]),
            "status": "posted"
        })
        
        self.data["stats"]["total_posted"] += 1
        
        self.save_data()
        
        return {
            "success": True,
            "thread_id": thread["id"],
            "parts": len(thread["parts"])
        }
        
    def schedule_thread(self, thread, post_time):
        """Schedule a thread for later"""
        self.data["scheduled_threads"].append({
            "thread": thread,
            "scheduled_for": post_time,
            "created": datetime.now().isoformat()
        })
        self.save_data()
        
    def get_thread_ideas(self):
        """Get ideas for new threads"""
        return [t["hooks"][0] for t in self.data["templates"]]
        
    def get_stats(self):
        """Get thread stats"""
        return self.data["stats"]
        
    def generate_report(self):
        """Generate viral thread report"""
        stats = self.data["stats"]
        ideas = self.get_thread_ideas()
        
        report = "🧵 **Viral Thread Creator**\n\n"
        report += f"**📊 Stats:**\n"
        report += f"  Threads posted: {stats['total_posted']}\n"
        report += f"  Total likes: {stats['total_likes']}\n"
        report += f"  Total RTs: {stats['total_retweets']}\n\n"
        
        report += "**💡 Thread Ideas:**\n"
        for idea in ideas:
            report += f"  • {idea}\n"
            
        return report

if __name__ == "__main__":
    creator = ViralThreadCreator()
    
    print(creator.generate_report())
    
    print("\n" + "="*50)
    print("\n🎯 **Creating a new thread...**\n")
    
    thread = creator.create_thread()
    print(f"Hook: {thread['hook']}\n")
    print(f"Parts: {len(thread['parts'])}\n")
    
    print("Thread Preview:")
    for i, part in enumerate(thread["parts"][:2], 1):
        print(f"\n--- Part {i} ---")
        print(part[:150] + "...")
