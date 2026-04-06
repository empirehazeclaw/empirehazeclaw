#!/usr/bin/env python3
"""
Translation Agent
Document translation, glossary management, translation memory, multi-language support.
"""
import argparse
import json
import logging
import os
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("openclaw.translation")

DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "translation"
DATA_DIR.mkdir(parents=True, exist_ok=True)

GLOSSARY_FILE = DATA_DIR / "glossary.json"
MEMORY_FILE = DATA_DIR / "memory.json"
LANGUAGES_FILE = DATA_DIR / "languages.json"

# MyMemory API (free, 1000 words/day)
MYMEMORY_URL = "https://api.mymemory.translated.net/get"


# ISO 639-1 language codes + names
LANGUAGES = {
    "en": "English", "de": "German", "es": "Spanish", "fr": "French",
    "it": "Italian", "pt": "Portuguese", "ru": "Russian", "zh": "Chinese",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "nl": "Dutch",
    "pl": "Polish", "tr": "Turkish", "hi": "Hindi", "sv": "Swedish",
    "da": "Danish", "fi": "Finnish", "no": "Norwegian", "cs": "Czech",
    "el": "Greek", "he": "Hebrew", "th": "Thai", "vi": "Vietnamese",
    "id": "Indonesian", "ms": "Malay", "ro": "Romanian", "hu": "Hungarian",
    "uk": "Ukrainian", "bg": "Bulgarian", "hr": "Croatian", "sk": "Slovak",
}


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.warning("Failed to load %s: %s", path, e)
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=str))


@dataclass
class GlossaryEntry:
    source_lang: str
    target_lang: str
    source_term: str
    target_term: str
    context: str = ""
    domain: str = ""  # general, tech, legal, medical, business
    created: str = ""


@dataclass
class MemoryEntry:
    source_lang: str
    target_lang: str
    source_text: str
    target_text: str
    quality: float = 1.0  # 0-1
    use_count: int = 0
    created: str = ""


class TranslationAgent:
    def __init__(self):
        self.glossary = load_json(GLOSSARY_FILE, {})
        self.memory = load_json(MEMORY_FILE, {})
        self.languages = load_json(LANGUAGES_FILE, LANGUAGES)

    # ── Core Translation ────────────────────────────────────────

    def translate(self, text: str, source_lang: str, target_lang: str,
                  use_glossary: bool = True, use_memory: bool = True) -> str:
        """Translate text using MyMemory API with glossary + memory fallbacks."""
        if not text.strip():
            return ""

        # 1. Check translation memory
        if use_memory:
            mem_key = f"{source_lang}:{target_lang}"
            if mem_key in self.memory:
                for entry in self.memory[mem_key]:
                    if entry['source_text'].lower() == text.lower():
                        entry['use_count'] += 1
                        save_json(MEMORY_FILE, self.memory)
                        log.info("TM hit: %s", text[:50])
                        return entry['target_text']

        # 2. Apply glossary pre-processing
        processed = text
        if use_glossary:
            processed = self._apply_glossary(text, source_lang, target_lang)

        # 3. Call MyMemory API
        try:
            lang_pair = f"{source_lang}|{target_lang}"
            url = f"{MYMEMORY_URL}?{urllib.parse.urlencode({'q': processed, 'langpair': lang_pair})}"
            req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw/1.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            if data.get('responseStatus') == 200:
                result = data['responseData']['translatedText']
                # 4. Apply glossary post-processing
                result = self._apply_glossary(result, target_lang, source_lang)
                # 5. Store in translation memory
                self._store_memory(source_lang, target_lang, text, result)
                return result
            else:
                log.error("MyMemory error: %s", data.get('responseDetails'))
                return f"[Translation error: {data.get('responseDetails', 'API error')}]"
        except urllib.error.URLError as e:
            log.error("Network error: %s", e)
            return f"[Network error: {e}]"
        except Exception as e:
            log.error("Translation error: %s", e)
            return f"[Error: {e}]"

    def _apply_glossary(self, text: str, source_lang: str, target_lang: str) -> str:
        """Replace known terms with glossary equivalents."""
        glos_key = f"{source_lang}:{target_lang}"
        if glos_key not in self.glossary:
            return text
        for entry in self.glossary[glos_key]:
            src = entry['source_term']
            tgt = entry['target_term']
            # Case-insensitive whole-word replacement
            pattern = re.compile(re.escape(src), re.IGNORECASE)
            text = pattern.sub(tgt, text)
        return text

    def _store_memory(self, source_lang: str, target_lang: str, source: str, target: str):
        key = f"{source_lang}:{target_lang}"
        if key not in self.memory:
            self.memory[key] = []
        # Avoid duplicates
        for entry in self.memory[key]:
            if entry['source_text'] == source:
                return
        entry = MemoryEntry(source_lang=source_lang, target_lang=target_lang,
                            source_text=source, target_text=target,
                            created=datetime.now().strftime("%Y-%m-%d"))
        self.memory[key].append(vars(entry))
        save_json(MEMORY_FILE, self.memory)

    # ── Document Translation ───────────────────────────────────

    def translate_file(self, input_path: str, output_path: str,
                        source_lang: str, target_lang: str):
        """Translate a text file."""
        try:
            text = Path(input_path).read_text(encoding="utf-8")
        except Exception as e:
            return f"❌ Could not read {input_path}: {e}"

        log.info("Translating %s (%s→%s)", input_path, source_lang, target_lang)
        result = self.translate(text, source_lang, target_lang)

        try:
            Path(output_path).write_text(result, encoding="utf-8")
            log.info("Saved: %s", output_path)
            return f"✅ Translated and saved to {output_path}"
        except Exception as e:
            return f"❌ Could not write {output_path}: {e}"

    # ── Glossary Management ────────────────────────────────────

    def add_glossary(self, source_lang: str, target_lang: str,
                     source_term: str, target_term: str,
                     context: str = "", domain: str = "general"):
        key = f"{source_lang}:{target_lang}"
        if key not in self.glossary:
            self.glossary[key] = []
        entry = GlossaryEntry(source_lang=source_lang, target_lang=target_lang,
                               source_term=source_term, target_term=target_term,
                               context=context, domain=domain,
                               created=datetime.now().strftime("%Y-%m-%d"))
        self.glossary[key].append(vars(entry))
        save_json(GLOSSARY_FILE, self.glossary)
        log.info("Added glossary: %s → %s (%s)", source_term, target_term, key)
        return f"📖 Glossary entry: {source_term} → {target_term} ({source_lang}→{target_lang})"

    def list_glossary(self, source_lang: str = "", target_lang: str = ""):
        if not self.glossary:
            return "📖 Glossary is empty."
        lines = ["📖 Glossary:", ""]
        for key, entries in self.glossary.items():
            sl, tl = key.split(":")
            if source_lang and sl != source_lang:
                continue
            if target_lang and tl != target_lang:
                continue
            for e in entries:
                lines.append(f"  {e['source_term']} → {e['target_term']} [{sl}→{tl}]")
                if e.get('context'):
                    lines.append(f"    Context: {e['context']}")
                if e.get('domain') and e['domain'] != 'general':
                    lines.append(f"    Domain: {e['domain']}")
        return "\n".join(lines) or "📖 No glossary entries found."

    def import_glossary_csv(self, csv_path: str, source_lang: str, target_lang: str):
        """Import glossary from CSV (format: source,target[,context,domain])"""
        try:
            lines = Path(csv_path).read_text(encoding="utf-8").strip().split("\n")
        except Exception as e:
            return f"❌ Could not read {csv_path}: {e}"

        count = 0
        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                self.add_glossary(source_lang, target_lang, parts[0], parts[1],
                                  context=parts[2] if len(parts) > 2 else "",
                                  domain=parts[3] if len(parts) > 3 else "general")
                count += 1
        return f"📖 Imported {count} glossary entries."

    # ── Translation Memory ─────────────────────────────────────

    def list_memory(self, source_lang: str = "", target_lang: str = ""):
        if not self.memory:
            return "🧠 Translation memory is empty."
        lines = ["🧠 Translation Memory:", ""]
        total = 0
        for key, entries in self.memory.items():
            sl, tl = key.split(":")
            if source_lang and sl != source_lang:
                continue
            if target_lang and tl != tl:
                continue
            for e in entries:
                lines.append(f"  [{sl}→{tl}] \"{e['source_text'][:60]}\" → \"{e['target_text'][:60]}\"")
                total += 1
        lines.append(f"\n  Total entries: {total}")
        return "\n".join(lines)

    def memory_stats(self) -> str:
        total = sum(len(v) for v in self.memory.values())
        lang_pairs = len(self.memory)
        lines = ["🧠 Translation Memory Stats:", ""]
        lines.append(f"  Total entries: {total}")
        lines.append(f"  Language pairs: {lang_pairs}")
        return "\n".join(lines)

    # ── Language Info ──────────────────────────────────────────

    def list_languages(self):
        lines = ["🌐 Supported Languages:", ""]
        for code, name in sorted(self.languages.items()):
            lines.append(f"  {code}: {name}")
        return "\n".join(lines)

    # ── Batch Translation ───────────────────────────────────────

    def batch_translate(self, texts: list, source_lang: str, target_lang: str):
        """Translate a list of texts."""
        results = []
        for i, text in enumerate(texts):
            if text.strip():
                result = self.translate(text, source_lang, target_lang)
                results.append(result)
                log.info("Translated %d/%d", i + 1, len(texts))
            else:
                results.append("")
        return results

    # ── Report ─────────────────────────────────────────────────

    def report(self) -> str:
        total_mem = sum(len(v) for v in self.memory.values())
        total_glos = sum(len(v) for v in self.glossary.values())
        lines = ["🌐 Translation Agent Report — " + datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
        lines.append(f"📊 Memory entries: {total_mem} | Glossary: {total_glos} | Language pairs: {len(self.memory)}")
        lines.append(f"📖 Supported languages: {len(self.languages)}")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="translation",
        description="🌐 Translation Agent — document translation, glossary, translation memory"
    )
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("translate", help="Translate text")
    p.add_argument("--text", required=True, help="Text to translate")
    p.add_argument("--from", dest="source_lang", required=True, help="Source language code (en, de, ...)")
    p.add_argument("--to", dest="target_lang", required=True, help="Target language code")
    p.add_argument("--no-glossary", action="store_true", help="Skip glossary")
    p.add_argument("--no-memory", action="store_true", help="Skip translation memory")

    p = sub.add_parser("translate-file", help="Translate a text file")
    p.add_argument("--input", required=True, help="Input file path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument("--from", dest="source_lang", required=True, help="Source language")
    p.add_argument("--to", dest="target_lang", required=True, help="Target language")

    p = sub.add_parser("add-glossary", help="Add glossary entry")
    p.add_argument("--from", dest="source_lang", required=True, help="Source language code")
    p.add_argument("--to", dest="target_lang", required=True, help="Target language code")
    p.add_argument("--source-term", required=True, help="Source term")
    p.add_argument("--target-term", required=True, help="Target term")
    p.add_argument("--context", default="", help="Context/usage note")
    p.add_argument("--domain", default="general", help="Domain: general, tech, legal, medical, business")

    p = sub.add_parser("list-glossary", help="List glossary entries")
    p.add_argument("--from", dest="source_lang", default="", help="Filter by source language")
    p.add_argument("--to", dest="target_lang", default="", help="Filter by target language")

    p = sub.add_parser("import-glossary-csv", help="Import glossary from CSV")
    p.add_argument("--file", required=True, help="CSV file path")
    p.add_argument("--from", dest="source_lang", required=True, help="Source language")
    p.add_argument("--to", dest="target_lang", required=True, help="Target language")

    p = sub.add_parser("list-memory", help="List translation memory")
    p.add_argument("--from", dest="source_lang", default="", help="Filter")
    p.add_argument("--to", dest="target_lang", default="", help="Filter")

    sub.add_parser("memory-stats", help="Translation memory statistics")

    sub.add_parser("list-languages", help="List supported languages")
    sub.add_parser("report", help="Full translation report")

    args = parser.parse_args()
    agent = TranslationAgent()

    if args.cmd == "translate":
        result = agent.translate(args.text, args.source_lang, args.target_lang,
                                 use_glossary=not args.no_glossary,
                                 use_memory=not args.no_memory)
        print(result)
    elif args.cmd == "translate-file":
        print(agent.translate_file(args.input, args.output, args.source_lang, args.target_lang))
    elif args.cmd == "add-glossary":
        print(agent.add_glossary(args.source_lang, args.target_lang,
                                  args.source_term, args.target_term,
                                  args.context, args.domain))
    elif args.cmd == "list-glossary":
        print(agent.list_glossary(getattr(args, 'source_lang', ''), getattr(args, 'target_lang', '')))
    elif args.cmd == "import-glossary-csv":
        print(agent.import_glossary_csv(args.file, args.source_lang, args.target_lang))
    elif args.cmd == "list-memory":
        print(agent.list_memory(getattr(args, 'source_lang', ''), getattr(args, 'target_lang', '')))
    elif args.cmd == "memory-stats":
        print(agent.memory_stats())
    elif args.cmd == "list-languages":
        print(agent.list_languages())
    elif args.cmd == "report":
        print(agent.report())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
