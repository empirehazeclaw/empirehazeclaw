#!/usr/bin/env python3
"""
Landing Page Generator Agent — EmpireHazeClaw Marketing System
Generates high-converting landing page HTML with dark theme, SEO-optimized.
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
LANDING_DIR = DATA_DIR / "landing_pages"
PAGES_DB = LANDING_DIR / "pages.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
LANDING_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LANDING-PAGE] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "landing_page.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("landing_page")


# ── Database ─────────────────────────────────────────────────────────────────
def load_pages() -> dict:
    if PAGES_DB.exists():
        try:
            return json.loads(PAGES_DB.read_text())
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load pages.json: %s", e)
    return {"pages": {}, "version": "1.0"}


def save_pages(data: dict) -> None:
    PAGES_DB.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ── HTML Generators ──────────────────────────────────────────────────────────
def generate_hero_section(headline: str, subheadline: str, cta_text: str, cta_url: str,
                          badge: str = "", dark: bool = True) -> str:
    badge_html = f'<span class="hero-badge">{badge}</span>' if badge else ""
    return f"""
  <section class="hero">
    <div class="hero-bg"></div>
    <div class="container">
      {badge_html}
      <h1 class="hero-title">{headline}</h1>
      <p class="hero-subtitle">{subheadline}</p>
      <div class="hero-cta">
        <a href="{cta_url}" class="btn btn-primary btn-lg">{cta_text}</a>
        <span class="hero-trust">No credit card required · Free trial</span>
      </div>
    </div>
  </section>"""


def generate_features_section(features: list, title: str = "What You Get") -> str:
    items = "\n".join(
        f"""        <div class="feature-card">
          <div class="feature-icon">{f.get('icon', '✓')}</div>
          <h3>{f.get('title', '')}</h3>
          <p>{f.get('description', '')}</p>
        </div>"""
        for f in features
    )
    return f"""
  <section class="features">
    <div class="container">
      <h2 class="section-title">{title}</h2>
      <div class="features-grid">
{items}
      </div>
    </div>
  </section>"""


def generate_social_proof_section(testimonials: list, stats: list) -> str:
    testimonials_html = "\n".join(
        f"""        <div class="testimonial-card">
          <p class="testimonial-text">"{t.get('quote', '')}"</p>
          <div class="testimonial-author">
            <strong>{t.get('name', 'Customer')}</strong>
            <span>{t.get('role', '')}</span>
          </div>
        </div>"""
        for t in testimonials
    )
    stats_html = "\n".join(
        f'<div class="stat"><strong>{s.get("value","")}</strong><span>{s.get("label","")}</span></div>'
        for s in stats
    )
    return f"""
  <section class="social-proof">
    <div class="container">
      <div class="stats-row">
{stats_html}
      </div>
      <h2 class="section-title">Loved by Early Users</h2>
      <div class="testimonials-grid">
{testimonials_html}
      </div>
    </div>
  </section>"""


def generate_pricing_section(plans: list, highlight_index: int = 1) -> str:
    plans_html = []
    for i, plan in enumerate(plans):
        highlighted = " pricing-card-highlight" if i == highlight_index else ""
        badge = '<span class="popular-badge">Most Popular</span>' if i == highlight_index else ""
        features_li = "\n".join(f'<li>✓ {f}</li>' for f in plan.get("features", []))
        plans_html.append(f"""
        <div class="pricing-card{highlighted}">
          {badge}
          <h3>{plan.get('name', '')}</h3>
          <div class="price">{plan.get('price', '')}<span>/{plan.get('period', 'mo')}</span></div>
          <p class="price-desc">{plan.get('description', '')}</p>
          <ul class="price-features">{features_li}</ul>
          <a href="{plan.get('cta_url', '#')}" class="btn {'btn-primary' if i == highlight_index else 'btn-outline'}">{plan.get('cta', 'Get Started')}</a>
        </div>""")
    return f"""
  <section class="pricing">
    <div class="container">
      <h2 class="section-title">Simple, Transparent Pricing</h2>
      <div class="pricing-grid">
        {"".join(plans_html)}
      </div>
    </div>
  </section>"""


def generate_faq_section(faqs: list) -> str:
    faqs_html = "\n".join(
        f"""        <div class="faq-item">
          <h3>{faq.get('question', '')}</h3>
          <p>{faq.get('answer', '')}</p>
        </div>"""
        for faq in faqs
    )
    return f"""
  <section class="faq">
    <div class="container">
      <h2 class="section-title">Frequently Asked Questions</h2>
      <div class="faq-list">
{faqs_html}
      </div>
    </div>
  </section>"""


def generate_cta_section(headline: str, subtext: str, cta_text: str, cta_url: str) -> str:
    return f"""
  <section class="final-cta">
    <div class="container">
      <h2>{headline}</h2>
      <p>{subtext}</p>
      <a href="{cta_url}" class="btn btn-primary btn-lg">{cta_text}</a>
    </div>
  </section>"""


def generate_footer(brand: str, links: list) -> str:
    links_html = "\n".join(f'<a href="{l.get("url","#")}">{l.get("label","")}</a>' for l in links)
    return f"""
  <footer>
    <div class="container">
      <div class="footer-brand">{brand}</div>
      <div class="footer-links">
{links_html}
      </div>
      <p class="footer-copy">&copy; {datetime.now(timezone.utc).year} {brand}. All rights reserved.</p>
    </div>
  </footer>"""


def generate_landing_page(
    headline: str,
    subheadline: str,
    cta_text: str,
    cta_url: str,
    features: list,
    testimonials: list,
    stats: list,
    plans: list,
    faqs: list,
    brand: str = "EmpireHazeClaw",
    badge: str = "",
    final_cta_headline: str = "Ready to Get Started?",
    final_cta_subtext: str = "Join thousands of users who already trust us.",
    footer_links: list = None,
) -> str:
    if footer_links is None:
        footer_links = [
            {"label": "Privacy", "url": "/privacy"},
            {"label": "Terms", "url": "/terms"},
            {"label": "Contact", "url": "/contact"},
        ]

    css = """<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a0f;--bg2:#111118;--bg3:#1a1a24;--accent:#6c63ff;--accent2:#ff6584;--text:#e8e8f0;--text2:#9090a8;--radius:12px}
body{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.container{max-width:1140px;margin:0 auto;padding:0 24px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.btn{display:inline-block;padding:12px 28px;border-radius:var(--radius);font-weight:600;transition:all .2s;cursor:pointer;border:none;font-size:1rem}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:#5a52e0;transform:translateY(-1px);text-decoration:none}
.btn-outline{border:2px solid var(--accent);color:var(--accent);background:transparent}
.btn-outline:hover{background:var(--accent);color:#fff;text-decoration:none}
.btn-lg{padding:16px 40px;font-size:1.1rem}
.section-title{text-align:center;font-size:2.2rem;margin-bottom:48px}
/* HERO */
.hero{position:relative;padding:120px 0 80px;text-align:center;overflow:hidden}
.hero-bg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(108,99,255,.15) 0%,transparent 70%);pointer-events:none}
.hero-badge{display:inline-block;background:var(--bg3);border:1px solid var(--accent);color:var(--accent);padding:6px 16px;border-radius:99px;font-size:.85rem;margin-bottom:24px}
.hero-title{font-size:clamp(2.5rem,6vw,4.5rem);font-weight:800;line-height:1.1;margin-bottom:20px;background:linear-gradient(135deg,#fff 40%,var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-subtitle{font-size:1.25rem;color:var(--text2);max-width:600px;margin:0 auto 40px}
.hero-cta{display:flex;flex-direction:column;align-items:center;gap:12px}
.hero-trust{color:var(--text2);font-size:.85rem}
/* FEATURES */
.features{padding:80px 0;background:var(--bg2)}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}
.feature-card{background:var(--bg3);padding:32px;border-radius:var(--radius);border:1px solid rgba(255,255,255,.06)}
.feature-icon{font-size:2rem;margin-bottom:16px}
.feature-card h3{font-size:1.2rem;margin-bottom:10px}
.feature-card p{color:var(--text2);font-size:.95rem}
/* SOCIAL PROOF */
.social-proof{padding:80px 0}
.stats-row{display:flex;justify-content:center;gap:64px;margin-bottom:64px;flex-wrap:wrap}
.stat{text-align:center}
.stat strong{display:block;font-size:2.5rem;color:var(--accent)}
.stat span{color:var(--text2)}
.testimonials-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}
.testimonial-card{background:var(--bg2);padding:28px;border-radius:var(--radius);border:1px solid rgba(255,255,255,.06)}
.testimonial-text{font-style:italic;color:var(--text);margin-bottom:16px;font-size:.95rem}
.testimonial-author strong{display:block;color:var(--accent)}
.testimonial-author span{font-size:.85rem;color:var(--text2)}
/* PRICING */
.pricing{padding:80px 0;background:var(--bg2)}
.pricing-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;align-items:start}
.pricing-card{background:var(--bg3);padding:40px 32px;border-radius:var(--radius);border:1px solid rgba(255,255,255,.06);position:relative;text-align:center}
.pricing-card-highlight{border-color:var(--accent);background:linear-gradient(180deg,rgba(108,99,255,.1) 0%,var(--bg3) 100%)}
.popular-badge{position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:var(--accent);color:#fff;padding:4px 20px;border-radius:99px;font-size:.8rem;font-weight:600}
.price{font-size:3rem;font-weight:800;margin:16px 0;span{font-size:1rem;color:var(--text2);font-weight:400}}
.price-desc{color:var(--text2);margin-bottom:20px}
.price-features{list-style:none;text-align:left;margin:24px 0}
.price-features li{padding:6px 0;color:var(--text2)}
/* FAQ */
.faq{padding:80px 0}
.faq-list{max-width:720px;margin:0 auto}
.faq-item{background:var(--bg2);padding:24px;border-radius:var(--radius);margin-bottom:16px;border:1px solid rgba(255,255,255,.06)}
.faq-item h3{font-size:1.1rem;margin-bottom:10px}
.faq-item p{color:var(--text2)}
/* FINAL CTA */
.final-cta{text-align:center;padding:100px 0;background:linear-gradient(180deg,var(--bg) 0%,var(--bg2) 100%)}
.final-cta h2{font-size:2.5rem;margin-bottom:16px}
.final-cta p{color:var(--text2);margin-bottom:32px;font-size:1.1rem}
/* FOOTER */
footer{background:var(--bg2);padding:48px 0;border-top:1px solid rgba(255,255,255,.06)}
.footer-brand{font-size:1.3rem;font-weight:700;margin-bottom:20px}
.footer-links{display:flex;gap:24px;margin-bottom:20px;flex-wrap:wrap}
.footer-links a{color:var(--text2)}
.footer-copy{font-size:.85rem;color:var(--text2)}
/* RESPONSIVE */
@media(max-width:768px){.hero{padding:80px 0 60px}.stats-row{gap:32px}.section-title{font-size:1.7rem}}
</style>"""

    meta_tags = f"""<title>{headline} | {brand}</title>
<meta name="description" content="{subheadline}">"""

    body_parts = []
    body_parts.append(generate_hero_section(headline, subheadline, cta_text, cta_url, badge))
    if features:
        body_parts.append(generate_features_section(features))
    if testimonials or stats:
        body_parts.append(generate_social_proof_section(testimonials, stats))
    if plans:
        body_parts.append(generate_pricing_section(plans))
    if faqs:
        body_parts.append(generate_faq_section(faqs))
    body_parts.append(generate_cta_section(final_cta_headline, final_cta_subtext, cta_text, cta_url))
    body_parts.append(generate_footer(brand, footer_links))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {meta_tags}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
{css}
</head>
<body>
{"".join(body_parts)}
</body>
</html>"""


# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_generate(args: argparse.Namespace) -> None:
    # Load or build params
    if args.json_file:
        params = json.loads(Path(args.json_file).read_text())
    else:
        params = {
            "headline": args.headline,
            "subheadline": args.subheadline,
            "cta_text": args.cta_text,
            "cta_url": args.cta_url,
            "badge": args.badge or "",
            "brand": args.brand or "EmpireHazeClaw",
        }

    # Default features if not provided
    if "features" not in params:
        params["features"] = [
            {"icon": "⚡", "title": "Lightning Fast", "description": "Get results in minutes, not months."},
            {"icon": "🔒", "title": "Secure & Private", "description": "Your data stays yours. Always."},
            {"icon": "📊", "title": "Real Analytics", "description": "Track every click, every conversion."},
            {"icon": "🎯", "title": "Done-for-You", "description": "We handle the hard parts."},
        ]
    if "testimonials" not in params:
        params["testimonials"] = [
            {"quote": "This changed how I run my business. No exaggeration.", "name": "Sarah K.", "role": "Founder"},
            {"quote": "Finally, a tool that actually delivers on its promises.", "name": "Marcus T.", "role": "CEO"},
        ]
    if "stats" not in params:
        params["stats"] = [
            {"value": "10K+", "label": "Users"},
            {"value": "98%", "label": "Satisfaction"},
            {"value": "3x", "label": "ROI Average"},
        ]
    if "plans" not in params:
        params["plans"] = [
            {"name": "Starter", "price": "$0", "period": "mo", "description": "Perfect for trying out", "features": ["Core features", "1 project", "Community support"], "cta": "Get Started", "cta_url": "#"},
            {"name": "Pro", "price": "$29", "period": "mo", "description": "For serious builders", "features": ["Everything in Starter", "Unlimited projects", "Priority support", "Analytics"], "cta": "Get Started", "cta_url": "#"},
            {"name": "Business", "price": "$99", "period": "mo", "description": "For teams and agencies", "features": ["Everything in Pro", "Team access", "Custom integrations", "Dedicated support"], "cta": "Get Started", "cta_url": "#"},
        ]
    if "faqs" not in params:
        params["faqs"] = [
            {"question": "Is there a free trial?", "answer": "Yes — start free, upgrade when you're ready."},
            {"question": "Can I cancel anytime?", "answer": "Absolutely. No lock-in, no questions asked."},
        ]

    html = generate_landing_page(**params)

    page_id = args.page_id or f"page_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    out_path = LANDING_DIR / f"{page_id}.html"
    out_path.write_text(html)

    # Save to database
    pages = load_pages()
    pages["pages"][page_id] = {
        "id": page_id,
        "path": str(out_path),
        "headline": params["headline"],
        "brand": params["brand"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "html": html,
    }
    save_pages(pages)

    print(f"✅ Landing page generated: {out_path}")
    print(f"   Page ID: {page_id}")
    print(f"   Headline: {params['headline']}")
    log.info("Landing page generated: %s", page_id)


def cmd_list(args: argparse.Namespace) -> None:
    pages = load_pages().get("pages", {})
    if not pages:
        print("No landing pages found.")
        return
    print(f"{'ID':<35} {'BRAND':<20} {'GENERATED':<25}")
    print("-" * 85)
    for p in sorted(pages.values(), key=lambda x: x.get("generated_at", ""), reverse=True):
        print(f"{p.get('id',''):<35} {p.get('brand',''):<20} {p.get('generated_at','')[:25]}")


def cmd_preview(args: argparse.Namespace) -> None:
    pages = load_pages().get("pages", {})
    page = pages.get(args.page_id)
    if not page:
        log.error("Page '%s' not found", args.page_id)
        sys.exit(1)
    print(f"Page: {page['id']}")
    print(f"Brand: {page['brand']}")
    print(f"Generated: {page['generated_at']}")
    print(f"Path: {page['path']}")
    print(f"HTML length: {len(page.get('html',''))} chars")


def cmd_export(args: argparse.Namespace) -> None:
    pages = load_pages().get("pages", {})
    page = pages.get(args.page_id)
    if not page:
        log.error("Page '%s' not found", args.page_id)
        sys.exit(1)
    out = Path(args.output) if args.output else Path(f"/tmp/{args.page_id}.html")
    out.write_text(page.get("html", ""))
    print(f"✅ Exported to: {out}")
    log.info("Landing page exported: %s -> %s", args.page_id, out)


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="landing_page_generator_agent.py",
        description="EmpireHazeClaw Landing Page Generator — create high-converting landing pages.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # generate
    p_g = sub.add_parser("generate", help="Generate a new landing page")
    p_g.add_argument("--headline", required=True, help="Main headline")
    p_g.add_argument("--subheadline", required=True, help="Sub-headline / description")
    p_g.add_argument("--cta-text", dest="cta_text", required=True, help="CTA button text")
    p_g.add_argument("--cta-url", dest="cta_url", required=True, help="CTA URL")
    p_g.add_argument("--brand", default="EmpireHazeClaw")
    p_g.add_argument("--badge", help="Hero badge text")
    p_g.add_argument("--page-id", dest="page_id", help="Custom page ID")
    p_g.add_argument("--json-file", dest="json_file", help="Full params JSON file (overrides args)")
    p_g.set_defaults(fn=cmd_generate)

    # list
    p_l = sub.add_parser("list", help="List all generated landing pages")
    p_l.set_defaults(fn=cmd_list)

    # preview
    p_p = sub.add_parser("preview", help="Preview page metadata")
    p_p.add_argument("--page-id", dest="page_id", required=True)
    p_p.set_defaults(fn=cmd_preview)

    # export
    p_e = sub.add_parser("export", help="Export page HTML to a file")
    p_e.add_argument("--page-id", dest="page_id", required=True)
    p_e.add_argument("--output", help="Output file path")
    p_e.set_defaults(fn=cmd_export)

    args = parser.parse_args()

    try:
        args.fn(args)
    except Exception as e:
        log.exception("Command '%s' failed: %s", args.cmd, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
