#!/usr/bin/env python3
"""
News Article Agent — Generate SEO-optimized news articles and blog posts
Version: 1.0
Usage: python3 news_article_agent.py --task <task> [options]
"""

import argparse
import json
import logging
import sys
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# Logging Setup
LOG_DIR = "/home/clawbot/.openclaw/workspace/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [NEWS_ARTICLE] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "news_article.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class NewsArticleAgent:
    """Generate SEO-optimized news articles and blog posts."""

    ARTICLE_TEMPLATES = {
        "news": {
            "structure": "lead -> context -> quotes -> analysis -> future",
            "tone": "informative, objective, timely"
        },
        "blog": {
            "structure": "hook -> problem -> solution -> examples -> CTA",
            "tone": "engaging, educational, conversational"
        },
        "howto": {
            "structure": "intro -> prerequisites -> steps -> tips -> conclusion",
            "tone": "clear, instructive, thorough"
        },
        "listicle": {
            "structure": "intro -> item 1 -> item 2 -> ... -> conclusion",
            "tone": "engaging, scannable, valuable"
        },
        "opinion": {
            "structure": "thesis -> arguments -> evidence -> conclusion",
            "tone": "thoughtful, persuasive, personal"
        }
    }

    def __init__(self):
        self.log = log
        self.optimal_word_count = 1500  # For SEO

    def generate_article(self, title: str, topic: str, article_type: str = "blog",
                        target_keywords: List[str] = None, tone: str = "professional") -> Dict[str, Any]:
        """Generate a complete news article or blog post."""

        template = self.ARTICLE_TEMPLATES.get(article_type, self.ARTICLE_TEMPLATES["blog"])

        # Generate article content
        sections = self._generate_sections(topic, article_type, target_keywords)

        # Build full article
        article_content = self._build_article(
            title=title,
            topic=topic,
            article_type=article_type,
            sections=sections,
            tone=tone
        )

        # Generate metadata
        metadata = self._generate_metadata(title, topic, target_keywords, article_content)

        return {
            "title": title,
            "topic": topic,
            "type": article_type,
            "content": article_content,
            "sections": sections,
            "meta": metadata,
            "stats": {
                "word_count": len(article_content.split()),
                "reading_time_minutes": len(article_content.split()) // 200,
                "generated_at": datetime.now().isoformat()
            }
        }

    def generate_blog_post(self, title: str, topic: str, target_keywords: List[str] = None,
                          num_sections: int = 5) -> Dict[str, Any]:
        """Generate a blog post with specific structure."""

        sections = []
        for i in range(num_sections):
            sections.append({
                "heading": f"Section {i+1}: {topic} Insight {i+1}",
                "content": self._generate_paragraph(topic, i),
                "keyword_optimized": target_keywords[i % len(target_keywords)] if target_keywords else None
            })

        article = "\n\n".join([f"## {s['heading']}\n\n{s['content']}" for s in sections])

        return {
            "title": title,
            "content": f"# {title}\n\n## Introduction\n{self._generate_intro(topic)}\n\n{article}\n\n## Conclusion\n{self._generate_conclusion(topic)}",
            "sections": sections,
            "meta": self._generate_metadata(title, topic, target_keywords, "")
        }

    def generate_news_story(self, headline: str, context: str, quotes: List[Dict] = None,
                           source: str = "News Staff") -> Dict[str, Any]:
        """Generate a news-style article with quotes and attribution."""

        story = f"""**{headline}**

{context}

"""

        if quotes:
            story += "## Key Quotes\n\n"
            for quote in quotes:
                story += f"> \"{quote.get('text', '')}\"\n>\n> — *{quote.get('author', 'Source')}, {quote.get('role', '')}*\n\n"

        story += f"""
## Analysis

This development comes at a time when {topic_from_context(context)} continues to evolve.

## Background

{self._generate_background(context)}

---

*This article was generated for informational purposes. Always verify facts with primary sources.*

*Published: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*
"""

        return {
            "headline": headline,
            "content": story,
            "type": "news",
            "quotes": quotes or [],
            "source": source
        }

    def generate_seo_metadata(self, title: str, content: str,
                            keywords: List[str]) -> Dict[str, Any]:
        """Generate SEO metadata for an article."""

        # Extract meta description (first 160 chars)
        sentences = content.split('.')
        meta_desc = sentences[0][:160] if sentences else content[:160]
        if len(meta_desc) == 160:
            meta_desc += "..."

        # Generate slug
        slug = self._generate_slug(title)

        # Generate tags
        tags = self._extract_tags(content, keywords)

        return {
            "title": title,
            "meta_description": meta_desc,
            "slug": slug,
            "keywords": keywords,
            "tags": tags,
            "canonical_url": f"https://example.com/blog/{slug}"
        }

    def generate_social_share_text(self, article: Dict[str, Any],
                                   platform: str = "twitter") -> Dict[str, Any]:
        """Generate social media share text for article."""

        title = article.get("title", "")
        url = article.get("meta", {}).get("canonical_url", "https://example.com")

        if platform == "twitter":
            text = f"{title}\n\nRead more: {url}\n\n#article"
            if len(text) > 280:
                text = f"{title[:200]}...\n\nRead more: {url}"
        elif platform == "linkedin":
            text = f"Just published: {title}\n\nA new article exploring key insights and takeaways.\n\nLink in comments."
        else:
            text = f"New article: {title}\n\n{url}"

        return {
            "platform": platform,
            "text": text,
            "character_count": len(text),
            "optimal": len(text) <= 280 if platform == "twitter" else True
        }

    def _generate_sections(self, topic: str, article_type: str,
                          keywords: List[str] = None) -> List[Dict[str, str]]:
        """Generate article sections based on type."""

        templates = {
            "news": ["Breaking News", "Background", "Analysis", "Future Outlook"],
            "blog": ["Introduction", "Main Point 1", "Main Point 2", "Main Point 3", "Conclusion"],
            "howto": ["Introduction", "Prerequisites", "Step 1", "Step 2", "Tips", "Conclusion"],
            "listicle": ["Introduction"] + [f"Item {i}" for i in range(1, 6)] + ["Conclusion"],
            "opinion": ["Thesis", "Argument 1", "Argument 2", "Counter-argument", "Conclusion"]
        }

        section_names = templates.get(article_type, templates["blog"])

        return [
            {"name": name, "content": self._generate_paragraph(topic, i)}
            for i, name in enumerate(section_names)
        ]

    def _build_article(self, title: str, topic: str, article_type: str,
                      sections: List[Dict], tone: str) -> str:
        """Build complete article from sections."""

        article = f"# {title}\n\n"

        for i, section in enumerate(sections):
            article += f"## {section['name']}\n\n{section['content']}\n\n"

        return article

    def _generate_intro(self, topic: str) -> str:
        """Generate article introduction."""

        return f"""In today's rapidly evolving landscape, understanding {topic} has become more important than ever.

This comprehensive guide explores the key aspects of {topic}, providing insights that will help you navigate this space with confidence.

Whether you're just getting started or looking to deepen your understanding, this article covers everything you need to know."""

    def _generate_paragraph(self, topic: str, index: int) -> str:
        """Generate a paragraph of content."""

        templates = [
            f"{topic} represents a significant opportunity for those willing to invest the time to understand its nuances. In this section, we explore the fundamental concepts that underpin {topic} and why it matters.",
            f"Building on the foundations, let's examine how {topic} applies in real-world scenarios. Understanding these practical applications will give you a competitive edge.",
            f"One of the most important aspects of {topic} is its impact on the broader ecosystem. We'll analyze the key factors that contribute to success in this area.",
            f"Implementation is where many fall short. Here's what you need to know to effectively leverage {topic} in your own context.",
            f"The future of {topic} holds exciting possibilities. As we look ahead, several trends are emerging that will shape the landscape."
        ]

        return templates[index % len(templates)]

    def _generate_conclusion(self, topic: str) -> str:
        """Generate article conclusion."""

        return f"""Understanding {topic} is an ongoing journey, not a destination.

The key takeaways from this article are:
1. {topic} requires consistent effort and attention
2. Real-world application is essential for mastery
3. Staying updated with trends is crucial

We hope this guide has provided valuable insights. Feel free to share your thoughts in the comments below.
"""

    def _generate_background(self, context: str) -> str:
        """Generate background context for news story."""

        return f"""This story develops as interest in {topic_from_context(context)} continues to grow.

Industry experts have noted that recent changes reflect broader trends that have been building for some time.

Further developments are expected in the coming weeks and months.
"""

    def _generate_metadata(self, title: str, topic: str, keywords: List[str],
                          content: str) -> Dict[str, Any]:
        """Generate SEO metadata."""

        return {
            "meta_title": title[:60] if len(title) > 60 else title,
            "meta_description": content[:160] if content else f"Learn about {topic}",
            "slug": self._generate_slug(title),
            "keywords": keywords or [topic],
            "author": "Content Team",
            "published_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat()
        }

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""

        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug.strip('-')
        return slug[:50]

    def _extract_tags(self, content: str, keywords: List[str]) -> List[str]:
        """Extract relevant tags from content."""

        if not keywords:
            return ["article", "blog", "news"]

        return list(set(keywords[:5] + ["article"]))[:6]


def topic_from_context(context: str) -> str:
    """Extract topic from context string."""

    words = context.split()[:5]
    return " ".join(words) if words else "the topic"


def main():
    parser = argparse.ArgumentParser(
        description="News Article Agent — Generate SEO-optimized articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate blog article
  python3 news_article_agent.py --task article --title "The Future of AI" \\
    --topic "Artificial Intelligence" --type blog

  # Generate news story
  python3 news_article_agent.py --task news --headline "Breaking: Tech Merger" \\
    --context "Major tech companies announce partnership"

  # Generate SEO metadata
  python3 news_article_agent.py --task seo-meta --input ./article.json

  # Generate social shares
  python3 news_article_agent.py --task social --input ./article.json --platform twitter
        """
    )

    parser.add_argument("--task", required=True,
                        choices=["article", "blog", "news", "seo-meta", "social"],
                        help="Task to perform")
    parser.add_argument("--title", help="Article title")
    parser.add_argument("--topic", help="Article topic")
    parser.add_argument("--headline", help="News headline")
    parser.add_argument("--context", help="News context/details")
    parser.add_argument("--type", choices=["news", "blog", "howto", "listicle", "opinion"],
                        default="blog", help="Article type")
    parser.add_argument("--keywords", help="Comma-separated keywords")
    parser.add_argument("--quotes", help="JSON array of quotes")
    parser.add_argument("--num-sections", type=int, default=5, help="Number of sections")
    parser.add_argument("--tone", default="professional", help="Article tone")
    parser.add_argument("--platform", choices=["twitter", "linkedin", "facebook"],
                        default="twitter", help="Social platform")
    parser.add_argument("--input", help="Input JSON file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown", "html"], default="json")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    agent = NewsArticleAgent()

    try:
        result = None

        if args.task == "article":
            if not args.title or not args.topic:
                raise ValueError("--title and --topic required")

            keywords = args.keywords.split(",") if args.keywords else None
            result = agent.generate_article(
                title=args.title,
                topic=args.topic,
                article_type=args.type,
                target_keywords=keywords,
                tone=args.tone
            )

        elif args.task == "blog":
            if not args.title or not args.topic:
                raise ValueError("--title and --topic required")

            keywords = args.keywords.split(",") if args.keywords else None
            result = agent.generate_blog_post(
                title=args.title,
                topic=args.topic,
                target_keywords=keywords,
                num_sections=args.num_sections
            )

        elif args.task == "news":
            if not args.headline or not args.context:
                raise ValueError("--headline and --context required")

            quotes = json.loads(args.quotes) if args.quotes else None
            result = agent.generate_news_story(
                headline=args.headline,
                context=args.context,
                quotes=quotes
            )

        elif args.task == "seo-meta":
            if not args.input:
                raise ValueError("--input required")
            with open(args.input, 'r') as f:
                data = json.load(f)
            keywords = args.keywords.split(",") if args.keywords else data.get("meta", {}).get("keywords", [])
            result = agent.generate_seo_metadata(
                title=data.get("title", ""),
                content=data.get("content", ""),
                keywords=keywords
            )

        elif args.task == "social":
            if not args.input:
                raise ValueError("--input required")
            with open(args.input, 'r') as f:
                data = json.load(f)
            result = agent.generate_social_share_text(data, args.platform)

        if result:
            if args.output:
                with open(args.output, 'w') as f:
                    if args.format == "markdown" and "content" in result:
                        f.write(result["content"])
                    else:
                        json.dump(result, f, indent=2)
                log.info(f"Output saved to {args.output}")
            else:
                if args.format == "markdown" and "content" in result:
                    print(result["content"])
                else:
                    print(json.dumps(result, indent=2))
            log.info("Task completed successfully")

    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Task failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
