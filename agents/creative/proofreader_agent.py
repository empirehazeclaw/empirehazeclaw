#!/usr/bin/env python3
"""
Proofreader Agent
EmpireHazeClaw Creative Suite

Proofreads and edits text content. Checks grammar, style, tone consistency.
Integrität: honest correction, no spin — tell it like it is.
"""

import argparse
import json
import logging
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "creative"
LOG_DIR = BASE_DIR / "logs"
DICTIONARY_FILE = DATA_DIR / "glossary.json"
EDITS_FILE = DATA_DIR / "proofread_history.json"

LOG_FILE = LOG_DIR / "proofreader.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("Proofreader")


def load_json(path: Path):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", path, e)
    return {} if "glossary" in str(path) else []


def save_json(path: Path, data) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", path, e)
        return False


def load_glossary() -> dict:
    data = load_json(DICTIONARY_FILE)
    return data if isinstance(data, dict) else {}


def save_glossary(data: dict) -> bool:
    return save_json(DICTIONARY_FILE, data)


def load_history() -> list:
    data = load_json(EDITS_FILE)
    return data if isinstance(data, list) else []


def save_history(data: list) -> bool:
    return save_json(EDITS_FILE, data)


# ─── Proofreading Rules ───────────────────────────────────────────────────────
GRAMMAR_RULES = [
    (r"\bi\b", "I", "lowercase 'i' should be capitalised"),
    (r"\bi'm\b", "I'm", "contraction 'i'm' should be \"I'm\""),
    (r"\bdont\b", "don't", "missing apostrophe in contraction"),
    (r"\bcant\b", "can't", "missing apostrophe in contraction"),
    (r"\bwont\b", "won't", "missing apostrophe in contraction"),
    (r"\bwouldnt\b", "wouldn't", "missing apostrophe in contraction"),
    (r"\bcouldnt\b", "couldn't", "missing apostrophe in contraction"),
    (r"\bshouldnt\b", "shouldn't", "missing apostrophe in contraction"),
    (r"\bhasnt\b", "hasn't", "missing apostrophe in contraction"),
    (r"\bhavent\b", "haven't", "missing apostrophe in contraction"),
    (r"\bisnt\b", "isn't", "missing apostrophe in contraction"),
    (r"\barent\b", "aren't", "missing apostrophe in contraction"),
    (r"\bdoesnt\b", "doesn't", "missing apostrophe in contraction"),
    (r"\bdidnt\b", "didn't", "missing apostrophe in contraction"),
    (r"\bwere\b(?!\s)", "we're", "possible confusion: 'were' vs 'we're'"),
    (r"\btheir\b (?=\w)", "they're", "possible confusion: 'their' vs 'they're'"),
    (r"\byoure\b", "you're", "missing apostrophe"),
    (r"\bthats\b", "that's", "missing apostrophe"),
    (r"\bwhats\b", "what's", "missing apostrophe"),
    (r"\bhes\b", "he's", "missing apostrophe"),
    (r"\bshes\b", "she's", "missing apostrophe"),
    (r"\bits\b(?=\s+(?:a|an|the|that|this|really|not|just|just))", "It's", "possible 'its' vs 'it's' confusion"),
    (r"\b(\w+)\s+\1\b", r"\1", "duplicate word detected"),
    (r"\s{2,}", " ", "multiple spaces"),
    (r"\.\s*\.", "…", "consecutive periods → ellipsis or single"),
    (r"!\s*!", "!", "consecutive exclamation marks"),
    (r"\?\s*\?", "?", "consecutive question marks"),
    (r"\"(\w+)\"", r"'\1'", "straight quotes → curly/single quotes for phrases"),
    (r"(\w)\.\.\.(\w)", r"\1...\2", "spacing around ellipsis"),
    (r"(\w)---(\w)", r"\1 — \2", "em-dash should have spaces"),
    (r"(\w)–(\w)", r"\1 — \2", "en-dash should have spaces"),
]

STYLE_RULES = {
    "weasel_words": [r"\bvery\b", r"\breally\b", r"\bquite\b", r"\bsomewhat\b", r"\bmaybe\b", r"\bperhaps\b"],
    "filler_words": [r"\bliterally\b(?!\s+used)", r"\bbasically\b", r"\bhonestly\b", r"\bdefinitely\b(?!\s+(?:won|would))"],
    "passive": [r"\bwas\b\s+\w+ed\b", r"\bwere\b\s+\w+ed\b"],
    "too_long_sentence": r".{200,}",
}

TONE_CHECKS = {
    "formal": {
        "allowed": ["therefore", "however", "furthermore", "consequently", "nevertheless"],
        "forbidden": ["awesome", "cool", "gonna", "wanna", "gotta", "kinda", "stuff", "things"],
    },
    "casual": {
        "allowed": ["awesome", "cool", "gonna", "wanna", "gotta", "stuff", "things"],
        "forbidden": ["therefore", "consequently", "hence", "hereby"],
    },
}


def apply_grammar_rules(text: str) -> tuple[str, list[dict]]:
    """Apply all grammar rules and return corrected text + issues."""
    issues = []
    corrected = text

    for pattern, replacement, description in GRAMMAR_RULES:
        flags = re.IGNORECASE if "(?i)" not in pattern else 0
        new_text, count = re.subn(pattern, replacement, corrected, flags=flags)
        if count > 0:
            corrected = new_text
            issues.append({
                "type": "grammar",
                "rule": description,
                "count": count,
                "severity": "warning",
            })

    # Weasel words
    for pattern in STYLE_RULES["weasel_words"]:
        matches = re.findall(pattern, corrected, re.IGNORECASE)
        if matches:
            issues.append({
                "type": "style",
                "rule": f"weasel word: '{matches[0]}'",
                "count": len(matches),
                "severity": "info",
            })

    # Filler words
    for pattern in STYLE_RULES["filler_words"]:
        matches = re.findall(pattern, corrected, re.IGNORECASE)
        if matches:
            issues.append({
                "type": "style",
                "rule": f"filler word: '{matches[0]}'",
                "count": len(matches),
                "severity": "info",
            })

    # Long sentences
    for match in re.finditer(STYLE_RULES["too_long_sentence"], corrected):
        issues.append({
            "type": "style",
            "rule": "sentence too long (>200 chars)",
            "count": 1,
            "severity": "info",
            "text": match.group()[:80] + "...",
        })

    # Glossary check
    glossary = load_glossary()
    for term, replacement in glossary.items():
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        if pattern.search(corrected):
            corrected = pattern.sub(replacement, corrected)
            issues.append({
                "type": "glossary",
                "rule": f"'{term}' → '{replacement}'",
                "count": 1,
                "severity": "info",
            })

    return corrected, issues


def check_tone(text: str, tone: str) -> list[dict]:
    """Check text for tone consistency."""
    issues = []
    config = TONE_CHECKS.get(tone, {})
    if not config:
        return issues

    for word in config.get("forbidden", []):
        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        if pattern.search(text):
            issues.append({
                "type": "tone",
                "rule": f"'{word}' may not fit a {tone} tone",
                "severity": "info",
            })
    return issues


def proofread(
    text: str,
    tone: Optional[str] = None,
    check_grammar: bool = True,
    check_style: bool = True,
    check_tone_flag: bool = False,
    glossary_term_check: bool = True,
) -> dict:
    """Main proofreading function."""
    if not text or not text.strip():
        raise ValueError("No text provided to proofread")

    original = text
    issues = []

    # Apply grammar & style rules
    if check_grammar or check_style:
        corrected, rule_issues = apply_grammar_rules(text)
        issues.extend(rule_issues)
        text = corrected

    # Tone check
    if check_tone_flag and tone:
        issues.extend(check_tone(text, tone))

    # Stats
    words_original = len(original.split())
    words_corrected = len(text.split())
    chars_original = len(original)
    chars_corrected = len(text)

    result = {
        "id": str(uuid.uuid4()),
        "original": original,
        "corrected": text,
        "issues": issues,
        "stats": {
            "words_original": words_original,
            "words_corrected": words_corrected,
            "chars_original": chars_original,
            "chars_corrected": chars_corrected,
            "issues_total": len(issues),
            "grammar_issues": len([i for i in issues if i["type"] == "grammar"]),
            "style_issues": len([i for i in issues if i["type"] == "style"]),
            "tone_issues": len([i for i in issues if i["type"] == "tone"]),
            "glossary_replacements": len([i for i in issues if i["type"] == "glossary"]),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Save to history
    history = load_history()
    history.append(result)
    save_history(history[-100:])  # Keep last 100

    return result


def format_report(result: dict) -> str:
    stats = result["stats"]
    issues = result["issues"]

    lines = [
        "=" * 60,
        "  PROOFREAD REPORT",
        "=" * 60,
        f"  ID: {result['id']}",
        f"  Timestamp: {result['timestamp']}",
        "",
        "  STATS",
        f"  Words : {stats['words_original']} → {stats['words_corrected']}",
        f"  Chars : {stats['chars_original']} → {stats['chars_corrected']}",
        f"  Issues: {stats['issues_total']} total  "
        f"(gram:{stats['grammar_issues']} | style:{stats['style_issues']} | tone:{stats['tone_issues']})",
        "",
    ]

    if issues:
        lines.append("  ISSUES")
        by_type = {}
        for iss in issues:
            by_type.setdefault(iss["type"], []).append(iss)

        for itype in ["grammar", "style", "tone", "glossary"]:
            if itype in by_type:
                lines.append(f"\n  [{itye.upper()}]")
                for iss in by_type[itype]:
                    lines.append(f"    • {iss['rule']} {'(' + str(iss.get('count','')) + ')' if iss.get('count',1) > 1 else ''}")
                    if iss.get("text"):
                        lines.append(f"      \"{iss['text']}\"")
    else:
        lines.append("  ✅ No issues detected")

    lines.extend([
        "",
        "  CORRECTED TEXT",
        "  " + "-" * 56,
    ])
    corrected_lines = result["corrected"].split("\n")
    for line in corrected_lines:
        lines.append(f"  {line}")

    lines.append("=" * 60)
    return "\n".join(lines)


# ─── Glossary Management ───────────────────────────────────────────────────────
def add_glossary_term(term: str, replacement: str) -> dict:
    glossary = load_glossary()
    glossary[term] = replacement
    save_glossary(glossary)
    logger.info("Glossary term added: '%s' → '%s'", term, replacement)
    return {"term": term, "replacement": replacement}


def remove_glossary_term(term: str) -> bool:
    glossary = load_glossary()
    if term in glossary:
        del glossary[term]
        save_glossary(glossary)
        return True
    return False


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_proofread(args):
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        logger.info("Proofreading file: %s", args.file)
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()
        if not text:
            raise ValueError("No text provided. Use --text or --file or pipe text via stdin.")

    result = proofread(
        text=text,
        tone=args.tone,
        check_grammar=not args.skip_grammar,
        check_style=not args.skip_style,
        check_tone_flag=args.check_tone,
    )

    if args.format == "report":
        print(format_report(result))
    elif args.format == "diff":
        print("=== ORIGINAL ===")
        print(result["original"])
        print()
        print("=== CORRECTED ===")
        print(result["corrected"])
    else:
        print(result["corrected"])

    if result["stats"]["issues_total"] > 0 and not args.quiet:
        print(f"\n({result['stats']['issues_total']} issue(s) found — use --format report for details)")


def cmd_add_term(args):
    result = add_glossary_term(args.term, args.replacement)
    print(f"✅ Glossary term added: '{result['term']}' → '{result['replacement']}'")


def cmd_remove_term(args):
    if remove_glossary_term(args.term):
        print(f"✅ Term removed: {args.term}")
    else:
        print(f"⚠️  Term not found: {args.term}")


def cmd_glossary(args):
    glossary = load_glossary()
    if not glossary:
        print("Glossary is empty. Add terms with: proofreader add-term --term X --replacement Y")
        return
    print(f"\n{'Term':<30} {'Replacement':<30}")
    print("-" * 65)
    for term, replacement in glossary.items():
        print(f"  {term:<30} {replacement:<30}")


def cmd_history(args):
    history = load_history()
    if not history:
        print("No history yet.")
        return
    for entry in history[-20:]:
        print(f"\n[{entry['id'][:10]}] {entry['timestamp'][:10]}")
        print(f"  Words: {entry['stats']['words_original']} | Issues: {entry['stats']['issues_total']}")
        print(f"  {entry['corrected'][:80]}...")


def main():
    parser = argparse.ArgumentParser(
        prog="proofreader",
        description="EmpireHazeClaw Proofreader — grammar, style, and tone checking.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  proofreader proofread --text "I dont wanna go to the store"
  proofreader proofread --file README.md --format report
  echo "your text here" | proofreader proofread
  proofreader add-term --term "openclaw" --replacement "OpenClaw"
  proofreader glossary
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pr = sub.add_parser("proofread", help="Proofread text")
    p_pr.add_argument("--text", help="Text to proofread (or use --file or stdin)")
    p_pr.add_argument("--file", help="File to proofread")
    p_pr.add_argument("--tone", choices=["formal", "casual"], help="Expected tone")
    p_pr.add_argument("--check-tone", action="store_true", help="Check tone consistency")
    p_pr.add_argument("--skip-grammar", action="store_true", help="Skip grammar checks")
    p_pr.add_argument("--skip-style", action="store_true", help="Skip style checks")
    p_pr.add_argument("--format", default="corrected", choices=["corrected", "report", "diff"], help="Output format")
    p_pr.add_argument("--quiet", action="store_true", help="Suppress issue summary")
    p_pr.set_defaults(fn=cmd_proofread)

    p_add = sub.add_parser("add-term", help="Add glossary term")
    p_add.add_argument("--term", required=True, help="Term to replace")
    p_add.add_argument("--replacement", required=True, help="Replacement text")
    p_add.set_defaults(fn=cmd_add_term)

    p_rm = sub.add_parser("remove-term", help="Remove glossary term")
    p_rm.add_argument("term", help="Term to remove")
    p_rm.set_defaults(fn=cmd_remove_term)

    p_gloss = sub.add_parser("glossary", help="List glossary terms")
    p_gloss.set_defaults(fn=cmd_glossary)

    p_hist = sub.add_parser("history", help="Show recent proofread history")
    p_hist.set_defaults(fn=cmd_history)

    args = parser.parse_args()
    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
