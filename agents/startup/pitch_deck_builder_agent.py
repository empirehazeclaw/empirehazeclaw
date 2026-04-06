#!/usr/bin/env python3
"""
Pitch Deck Builder Agent
Generates startup pitch decks based on business information.
"""

import argparse
import logging
import sys
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/home/clawbot/.openclaw/workspace/logs/pitch_deck_builder.log')
    ]
)
logger = logging.getLogger(__name__)

# Slide templates
SLIDE_TEMPLATES = {
    "title": {
        "title": "Slide Title",
        "content": "Subtitle/tagline",
        "notes": "Start with a powerful, memorable title slide"
    },
    "problem": {
        "title": "The Problem",
        "content": "What pain point are you solving?",
        "subsections": ["Current situation", "Impact of the problem", "Who experiences this?"],
        "notes": "Make investors feel the pain - use data and stories"
    },
    "solution": {
        "title": "Our Solution",
        "content": "How do you solve the problem?",
        "subsections": ["Product/service description", "Unique approach", "Key differentiators"],
        "notes": "Show your unique insight and why now"
    },
    "market": {
        "title": "Market Opportunity",
        "content": "How large is the opportunity?",
        "subsections": ["TAM (Total Addressable Market)", "SAM (Serviceable Available Market)", "SOM (Serviceable Obtainable Market)"],
        "notes": "Use top-down and bottom-up analysis"
    },
    "business_model": {
        "title": "Business Model",
        "content": "How do you make money?",
        "subsections": ["Revenue streams", "Pricing strategy", "Unit economics"],
        "notes": "Show CAC, LTV, and margins"
    },
    "traction": {
        "title": "Traction & Validation",
        "content": "What progress have you made?",
        "subsections": ["Key metrics", "Growth rate", "Customer testimonials", "Partnerships"],
        "notes": "Show momentum and validation"
    },
    "competition": {
        "title": "Competitive Landscape",
        "content": "Who else is addressing this?",
        "subsections": ["Direct competitors", "Indirect competitors", "Your unfair advantage"],
        "notes": "Position yourself clearly"
    },
    "team": {
        "title": "Our Team",
        "content": "Why are you the right team?",
        "subsections": ["Founders & background", "Key advisors", "Team gaps to fill"],
        "notes": "Show relevant experience and passion"
    },
    "financials": {
        "title": "Financial Projections",
        "content": "Where are you going?",
        "subsections": ["Revenue forecast", "Key assumptions", "Path to profitability"],
        "notes": "Be realistic but show ambition"
    },
    "ask": {
        "title": "The Ask",
        "content": "How much are you raising?",
        "subsections": ["Amount", "Valuation", "Use of funds", "Timeline"],
        "notes": "Be specific about what the money achieves"
    },
    "roadmap": {
        "title": "Product Roadmap",
        "content": "What's coming next?",
        "subsections": ["Current state", "Next 12 months", "Milestones"],
        "notes": "Show you have a clear vision"
    },
    "vision": {
        "title": "Vision",
        "content": "Where are you headed?",
        "subsections": ["Long-term mission", "Ultimate goal", "Impact"],
        "notes": "Inspire with the big picture"
    }
}

# Slide order for standard deck
STANDARD_DECK_ORDER = [
    "title", "problem", "solution", "market", "business_model",
    "traction", "competition", "team", "financials", "ask"
]

INVESTOR_DECK_ORDER = [
    "title", "problem", "solution", "market", "business_model",
    "traction", "competition", "team", "roadmap", "vision", "ask"
]

ACCELERATOR_DECK_ORDER = [
    "title", "problem", "solution", "market", "business_model",
    "traction", "team", "ask"
]


class PitchDeckBuilderAgent:
    """Agent for generating startup pitch decks."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        self.slide_templates = SLIDE_TEMPLATES.copy()
        logger.info("PitchDeckBuilderAgent initialized")

    def get_slide_template(self, slide_type: str) -> Dict[str, Any]:
        """Get template for a specific slide type."""
        slide_type = slide_type.lower().replace("-", "_").replace(" ", "_")
        if slide_type not in self.slide_templates:
            available = ", ".join(self.slide_templates.keys())
            raise ValueError(f"Unknown slide type: {slide_type}. Available: {available}")
        return self.slide_templates[slide_type].copy()

    def list_slide_types(self) -> List[Dict[str, str]]:
        """List all available slide types."""
        return [
            {"type": k, "title": v["title"], "notes": v.get("notes", "")[:80] + "..."}
            for k, v in self.slide_templates.items()
        ]

    def generate_deck_structure(self, deck_type: str = "standard") -> List[Dict[str, Any]]:
        """Generate a deck structure based on type."""
        deck_type = deck_type.lower()
        if deck_type == "standard":
            order = STANDARD_DECK_ORDER
        elif deck_type == "investor":
            order = INVESTOR_DECK_ORDER
        elif deck_type == "accelerator":
            order = ACCELERATOR_DECK_ORDER
        else:
            raise ValueError(f"Unknown deck type: {deck_type}. Available: standard, investor, accelerator")

        deck = []
        for slide_type in order:
            slide = {
                "slide_number": len(deck) + 1,
                "type": slide_type,
                **self.slide_templates[slide_type]
            }
            deck.append(slide)

        logger.info(f"Generated {deck_type} deck with {len(deck)} slides")
        return deck

    def build_pitch_content(self, business_info: Dict[str, Any], deck_type: str = "standard") -> Dict[str, Any]:
        """Build full pitch deck content from business information."""
        required_fields = ["company_name", "problem", "solution"]
        missing = [f for f in required_fields if f not in business_info or not business_info[f]]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        deck = self.generate_deck_structure(deck_type)
        content = {
            "meta": {
                "company": business_info.get("company_name", "Your Company"),
                "created": datetime.now().isoformat(),
                "deck_type": deck_type,
                "version": "1.0"
            },
            "slides": []
        }

        for slide in deck:
            slide_content = self._populate_slide(slide, business_info)
            content["slides"].append(slide_content)

        logger.info(f"Built pitch deck for {business_info['company_name']}: {len(deck)} slides")
        return content

    def _populate_slide(self, slide: Dict[str, Any], info: Dict[str, Any]) -> Dict[str, Any]:
        """Populate a slide with content from business info."""
        slide_type = slide["type"]
        populated = {
            "slide_number": slide["slide_number"],
            "type": slide_type,
            "title": slide["title"],
            "content": "",
            "bullets": [],
            "subsections": [],
            "notes": slide.get("notes", "")
        }

        if slide_type == "title":
            populated["title"] = info.get("company_name", "Company Name")
            populated["content"] = info.get("tagline", info.get("elevator_pitch", "Your tagline here"))
            if info.get("logo_url"):
                populated["logo"] = info["logo_url"]

        elif slide_type == "problem":
            populated["content"] = info.get("problem", "")
            populated["bullets"] = info.get("problem_details", [])
            if info.get("problem_data"):
                populated["bullets"].insert(0, f"📊 {info['problem_data']}")

        elif slide_type == "solution":
            populated["content"] = info.get("solution", "")
            populated["bullets"] = info.get("solution_features", [])
            if info.get("product_description"):
                populated["subsections"].append({"name": "Product", "content": info["product_description"]})

        elif slide_type == "market":
            populated["content"] = f"TAM: {info.get('tam', 'TBD')}"
            populated["bullets"] = [
                f"📊 TAM: {info.get('tam', 'TBD')}",
                f"📈 SAM: {info.get('sam', 'TBD')}",
                f"🎯 SOM: {info.get('som', 'TBD')}"
            ]
            if info.get("market_data"):
                populated["bullets"].append(f"📈 {info['market_data']}")

        elif slide_type == "business_model":
            populated["content"] = info.get("revenue_model", "")
            populated["bullets"] = [
                f"💰 {info.get('pricing', 'TBD')}",
                f"📈 Unit Economics: {info.get('unit_economics', 'TBD')}"
            ]
            if info.get("revenue_streams"):
                populated["subsections"].append({"name": "Revenue Streams", "content": info["revenue_streams"]})

        elif slide_type == "traction":
            populated["bullets"] = []
            if info.get("metrics"):
                for metric in info["metrics"]:
                    populated["bullets"].append(f"📊 {metric}")
            if info.get("milestones"):
                populated["subsections"].append({"name": "Milestones", "content": info["milestones"]})
            if info.get("testimonials"):
                populated["subsections"].append({"name": "Customer Quotes", "content": info["testimonials"]})

        elif slide_type == "competition":
            populated["content"] = info.get("competitive_advantage", "")
            if info.get("competitors"):
                populated["subsections"].append({"name": "Competitors", "content": info["competitors"]})
            if info.get("unfair_advantage"):
                populated["bullets"].append(f"🏆 {info['unfair_advantage']}")

        elif slide_type == "team":
            populated["bullets"] = []
            if info.get("founders"):
                for founder in info["founders"]:
                    populated["bullets"].append(f"👤 {founder}")
            if info.get("advisors"):
                populated["subsections"].append({"name": "Advisors", "content": info["advisors"]})

        elif slide_type == "financials":
            populated["content"] = "Financial Projections"
            populated["bullets"] = []
            if info.get("revenue_forecast"):
                populated["bullets"].append(f"📈 {info['revenue_forecast']}")
            if info.get("path_to_profitability"):
                populated["bullets"].append(f"🎯 {info['path_to_profitability']}")

        elif slide_type == "ask":
            populated["content"] = f"Raising: {info.get('raise_amount', 'TBD')}"
            populated["bullets"] = [
                f"💵 Raising: {info.get('raise_amount', 'TBD')}",
                f"💎 Valuation: {info.get('valuation', 'TBD')}",
                f"📍 Use of funds: {info.get('use_of_funds', 'TBD')}"
            ]
            if info.get("milestones_achieved"):
                populated["subsections"].append({"name": "What This Achieves", "content": info["milestones_achieved"]})

        elif slide_type == "roadmap":
            populated["bullets"] = []
            if info.get("product_roadmap"):
                populated["bullets"].extend(info["product_roadmap"])
            if info.get("next_milestones"):
                populated["subsections"].append({"name": "Next 12 Months", "content": info["next_milestones"]})

        elif slide_type == "vision":
            populated["content"] = info.get("vision", "")
            if info.get("mission"):
                populated["subsections"].append({"name": "Mission", "content": info["mission"]})
            if info.get("long_term_goals"):
                populated["subsections"].append({"name": "Long-term Goals", "content": info["long_term_goals"]})

        return populated

    def export_markdown(self, content: Dict[str, Any]) -> str:
        """Export pitch deck as Markdown."""
        lines = []
        lines.append(f"# {content['meta']['company']} - Pitch Deck\n")
        lines.append(f"*Generated: {content['meta']['created'][:10]}*\n")
        lines.append(f"*Type: {content['meta']['deck_type']}*\n")
        lines.append("\n---\n")

        for slide in content["slides"]:
            lines.append(f"\n## Slide {slide['slide_number']}: {slide['title']}\n")
            if slide.get("content"):
                lines.append(f"**{slide['content']}**\n")
            if slide.get("bullets"):
                for bullet in slide["bullets"]:
                    lines.append(f"- {bullet}")
            if slide.get("subsections"):
                for subsection in slide["subsections"]:
                    lines.append(f"\n### {subsection['name']}\n")
                    lines.append(f"{subsection['content']}\n")
            if slide.get("notes"):
                lines.append(f"\n> 📝 **Presenter Notes:** {slide['notes']}\n")
            lines.append("\n---\n")

        logger.info("Exported pitch deck as Markdown")
        return "\n".join(lines)

    def export_html(self, content: Dict[str, Any]) -> str:
        """Export pitch deck as HTML presentation."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content['meta']['company']} - Pitch Deck</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; }}
        .slide {{ min-height: 100vh; padding: 60px 80px; display: flex; flex-direction: column; justify-content: center; border-bottom: 1px solid #1e293b; }}
        .slide-number {{ color: #64748b; font-size: 14px; margin-bottom: 20px; }}
        .slide-title {{ font-size: 48px; font-weight: 700; color: #f8fafc; margin-bottom: 30px; }}
        .slide-content {{ font-size: 24px; color: #94a3b8; margin-bottom: 30px; }}
        .bullets {{ list-style: none; }}
        .bullets li {{ font-size: 20px; padding: 10px 0; color: #cbd5e1; }}
        .bullets li::before {{ content: "•"; color: #3b82f6; margin-right: 15px; }}
        .section-title {{ font-size: 20px; color: #64748b; margin: 30px 0 15px; text-transform: uppercase; letter-spacing: 1px; }}
        .notes {{ margin-top: 40px; padding: 20px; background: #1e293b; border-radius: 8px; font-size: 14px; color: #94a3b8; font-style: italic; }}
        h1 {{ font-size: 72px; text-align: center; margin-bottom: 20px; }}
        .tagline {{ font-size: 28px; color: #64748b; text-align: center; }}
        .progress {{ position: fixed; top: 0; left: 0; height: 3px; background: #3b82f6; width: 0%; }}
    </style>
</head>
<body>
<div class="progress" id="progress"></div>
"""

        for slide in content["slides"]:
            html += f"""
    <div class="slide" id="slide-{slide['slide_number']}">
        <div class="slide-number">Slide {slide['slide_number']}</div>
        <h1 class="slide-title">{slide['title']}</h1>
"""
            if slide.get("content"):
                html += f'        <div class="slide-content">{slide["content"]}</div>\n'
            if slide.get("bullets"):
                html += '        <ul class="bullets">\n'
                for bullet in slide["bullets"]:
                    html += f'            <li>{bullet}</li>\n'
                html += '        </ul>\n'
            if slide.get("subsections"):
                for subsection in slide["subsections"]:
                    html += f'        <div class="section-title">{subsection["name"]}</div>\n'
                    html += f'        <p>{subsection["content"]}</p>\n'
            if slide.get("notes"):
                html += f'        <div class="notes">📝 {slide["notes"]}</div>\n'
            html += '    </div>\n'

        html += """
    <script>
        window.addEventListener('scroll', () => {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = (scrollTop / docHeight) * 100;
            document.getElementById('progress').style.width = progress + '%';
        });
    </script>
</body>
</html>
"""
        logger.info("Exported pitch deck as HTML")
        return html

    def save_deck(self, content: Dict[str, Any], output_path: str, format: str = "json") -> str:
        """Save pitch deck to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            with open(output_path, 'w') as f:
                json.dump(content, f, indent=2)
        elif format == "markdown" or format == "md":
            with open(output_path, 'w') as f:
                f.write(self.export_markdown(content))
        elif format == "html":
            with open(output_path, 'w') as f:
                f.write(self.export_html(content))
        else:
            raise ValueError(f"Unknown format: {format}. Available: json, markdown, html")

        logger.info(f"Saved pitch deck to {output_path}")
        return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Pitch Deck Builder - Generate startup pitch decks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-slides
  %(prog)s --slide-template problem --info
  %(prog)s --generate-structure --type investor
  %(prog)s --build --company "MyStartup" --problem "Problem description" --solution "Our solution"
  %(prog)s --export --input deck.json --format markdown --output deck.md
  %(prog)s --interactive
        """
    )

    parser.add_argument("--list-slides", action="store_true", help="List all slide types")
    parser.add_argument("--slide-template", type=str, help="Get template for specific slide type")
    parser.add_argument("--info", action="store_true", help="Show template details")
    parser.add_argument("--generate-structure", action="store_true", help="Generate deck structure")
    parser.add_argument("--type", type=str, default="standard", choices=["standard", "investor", "accelerator"], help="Deck type")
    parser.add_argument("--build", action="store_true", help="Build full pitch deck")
    parser.add_argument("--company", type=str, help="Company name")
    parser.add_argument("--problem", type=str, help="Problem statement")
    parser.add_argument("--solution", type=str, help="Solution description")
    parser.add_argument("--tagline", type=str, help="Company tagline")
    parser.add_argument("--market", type=str, help="Market size (TAM/SAM/SOM)")
    parser.add_argument("--revenue", type=str, help="Revenue model")
    parser.add_argument("--pricing", type=str, help="Pricing strategy")
    parser.add_argument("--raise-amount", type=str, help="Amount to raise")
    parser.add_argument("--valuation", type=str, help="Valuation")
    parser.add_argument("--team", type=str, help="Team members (comma-separated)")
    parser.add_argument("--metrics", type=str, help="Key metrics (comma-separated)")
    parser.add_argument("--export", action="store_true", help="Export deck")
    parser.add_argument("--input", type=str, help="Input JSON file to export")
    parser.add_argument("--format", type=str, default="markdown", choices=["json", "markdown", "html"], help="Export format")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()
    agent = PitchDeckBuilderAgent(verbose=args.verbose)

    try:
        # List slides
        if args.list_slides:
            slides = agent.list_slide_types()
            if args.json:
                print(json.dumps(slides, indent=2))
            else:
                print("\n📊 AVAILABLE SLIDE TYPES:\n" + "-" * 60)
                for slide in slides:
                    print(f"  [{slide['type']}] {slide['title']}")
                    print(f"      {slide['notes']}\n")

        # Slide template info
        elif args.slide_template and args.info:
            template = agent.get_slide_template(args.slide_template)
            if args.json:
                print(json.dumps(template, indent=2))
            else:
                print(f"\n📝 SLIDE TEMPLATE: {template['title']}\n" + "-" * 50)
                print(f"Type: {args.slide_template}")
                print(f"Content: {template['content']}")
                if template.get("subsections"):
                    print(f"\nSubsections:")
                    for sub in template["subsections"]:
                        print(f"  • {sub}")
                print(f"\nNotes: {template.get('notes', 'N/A')}")

        # Generate structure
        elif args.generate_structure:
            deck = agent.generate_deck_structure(args.type)
            if args.json:
                print(json.dumps(deck, indent=2))
            else:
                print(f"\n📑 PITCH DECK STRUCTURE ({args.type})\n" + "-" * 50)
                for slide in deck:
                    print(f"  {slide['slide_number']}. {slide['title']}")

        # Build deck
        elif args.build:
            if not args.company or not args.problem or not args.solution:
                print("Error: --company, --problem, and --solution are required for --build")
                sys.exit(1)

            info = {
                "company_name": args.company,
                "tagline": args.tagline or f"{args.company} - Solving problems",
                "problem": args.problem,
                "solution": args.solution
            }

            # Parse optional fields
            if args.market:
                parts = args.market.split("/")
                if len(parts) >= 3:
                    info["tam"], info["sam"], info["som"] = parts[0], parts[1], parts[2]
            if args.revenue:
                info["revenue_model"] = args.revenue
            if args.pricing:
                info["pricing"] = args.pricing
            if args.raise_amount:
                info["raise_amount"] = args.raise_amount
            if args.valuation:
                info["valuation"] = args.valuation
            if args.team:
                info["founders"] = [t.strip() for t in args.team.split(",")]
            if args.metrics:
                info["metrics"] = [m.strip() for m in args.metrics.split(",")]

            deck = agent.build_pitch_content(info, args.type)
            print(json.dumps(deck, indent=2))

        # Export
        elif args.export:
            if not args.input:
                print("Error: --input is required for --export")
                sys.exit(1)
            if not args.output:
                print("Error: --output is required for --export")
                sys.exit(1)

            with open(args.input, 'r') as f:
                content = json.load(f)

            saved = agent.save_deck(content, args.output, args.format)
            print(f"✅ Saved to: {saved}")

        else:
            parser.print_help()

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
