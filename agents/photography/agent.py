#!/usr/bin/env python3
"""
Photography Agent
Photo editing automation, portfolio management, EXIF metadata, batch processing.
"""
import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("openclaw.photography")

DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "photography"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
PROJECTS_FILE = DATA_DIR / "projects.json"
EDIT_PRESETS_FILE = DATA_DIR / "presets.json"


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
class Photo:
    filename: str
    path: str
    title: str = ""
    tags: list = field(default_factory=list)
    location: str = ""
    camera: str = ""
    lens: str = ""
    aperture: str = ""
    shutter_speed: str = ""
    iso: int = 0
    date_taken: str = ""
    rating: int = 0  # 1-5
    in_portfolio: bool = False
    notes: str = ""


@dataclass
class Project:
    name: str
    description: str = ""
    photos: list = field(default_factory=list)
    status: str = "active"  # active, editing, completed, archived
    created: str = ""
    tags: list = field(default_factory=list)
    output_dir: str = ""


@dataclass
class Preset:
    name: str
    filter_name: str  # brightness, contrast, saturation, grayscale, sepia, sharpen, blur, etc.
    params: dict = field(default_factory=dict)
    description: str = ""


class PhotographyAgent:
    def __init__(self):
        self.portfolio = load_json(PORTFOLIO_FILE, [])
        self.projects = load_json(PROJECTS_FILE, {})
        self.presets = load_json(EDIT_PRESETS_FILE, {})

    # ── Portfolio ──────────────────────────────────────────────

    def add_photo(self, filename: str, path: str, **kwargs):
        photo = Photo(filename=filename, path=path, **kwargs)
        self.portfolio.append(vars(photo))
        save_json(PORTFOLIO_FILE, self.portfolio)
        log.info("Added photo: %s", filename)
        return f"📷 Photo '{filename}' added to portfolio."

    def list_portfolio(self, tag: str = "", rating: int = 0):
        photos = self.portfolio
        if tag:
            photos = [p for p in self.portfolio if tag.lower() in [t.lower() for t in p.get('tags', [])]]
        if rating > 0:
            photos = [p for p in photos if p.get('rating', 0) >= rating]
        if not photos:
            return "No photos found in portfolio."
        lines = [f"📷 Portfolio ({len(photos)} photos):", ""]
        for p in photos:
            stars = "★" * p.get('rating', 0) + "☆" * (5 - p.get('rating', 0))
            lines.append(f"  {stars} {p['filename']} — {p.get('title', 'untitled')}")
            if p.get('tags'):
                lines.append(f"     Tags: {', '.join(p['tags'])}")
            if p.get('location'):
                lines.append(f"     Location: {p['location']}")
        return "\n".join(lines)

    def rate_photo(self, filename: str, rating: int):
        for p in self.portfolio:
            if p['filename'] == filename:
                p['rating'] = max(1, min(5, rating))
                save_json(PORTFOLIO_FILE, self.portfolio)
                log.info("Rated %s: %d stars", filename, rating)
                return f"⭐ {filename} rated {rating}/5."
        return f"❌ Photo '{filename}' not found in portfolio."

    def portfolio_stats(self) -> str:
        total = len(self.portfolio)
        rated = sum(1 for p in self.portfolio if p.get('rating', 0) > 0)
        avg_rating = sum(p.get('rating', 0) for p in self.portfolio) / max(total, 1)
        by_tag = {}
        for p in self.portfolio:
            for t in p.get('tags', []):
                by_tag[t] = by_tag.get(t, 0) + 1
        lines = ["📊 Portfolio Statistics:", ""]
        lines.append(f"  Total photos: {total}")
        lines.append(f"  Rated photos: {rated}")
        lines.append(f"  Average rating: {avg_rating:.1f} ★")
        if by_tag:
            top = sorted(by_tag.items(), key=lambda x: -x[1])[:5]
            lines.append(f"  Top tags: {', '.join(f'{t}({n})' for t, n in top)}")
        return "\n".join(lines)

    # ── Projects ───────────────────────────────────────────────

    def create_project(self, name: str, description: str = "", output_dir: str = "", **kwargs):
        project = Project(name=name, description=description, output_dir=output_dir,
                          created=datetime.now().strftime("%Y-%m-%d"), **kwargs)
        self.projects[name] = vars(project)
        save_json(PROJECTS_FILE, self.projects)
        log.info("Created project: %s", name)
        return f"📁 Project '{name}' created."

    def add_to_project(self, project_name: str, filenames: list):
        if project_name not in self.projects:
            return f"❌ Project '{project_name}' not found."
        proj = self.projects[project_name]
        proj['photos'].extend(filenames)
        save_json(PROJECTS_FILE, self.projects)
        log.info("Added %d photos to project %s", len(filenames), project_name)
        return f"📁 Added {len(filenames)} photo(s) to project '{project_name}'."

    def list_projects(self):
        if not self.projects:
            return "No projects found."
        status_icon = {"active": "🟢", "editing": "🟡", "completed": "✅", "archived": "📦"}
        lines = ["📁 Projects:", ""]
        for name, proj in self.projects.items():
            icon = status_icon.get(proj.get('status', 'active'), "🟢")
            lines.append(f"  {icon} {name} | {proj.get('status', 'active')} | {len(proj.get('photos', []))} photos")
        return "\n".join(lines)

    # ── Edit Presets ───────────────────────────────────────────

    def add_preset(self, name: str, filter_name: str, params: dict, description: str = ""):
        preset = Preset(name=name, filter_name=filter_name, params=params, description=description)
        self.presets[name] = vars(preset)
        save_json(EDIT_PRESETS_FILE, self.presets)
        log.info("Added preset: %s", name)
        return f"🎨 Preset '{name}' saved."

    def list_presets(self):
        if not self.presets:
            return "No presets saved. Add one with: photography add-preset ..."
        lines = ["🎨 Edit Presets:", ""]
        for name, p in self.presets.items():
            lines.append(f"  🎯 {name} | filter: {p['filter_name']} | {p.get('description', '')}")
        return "\n".join(lines)

    # ── Batch Processing (via ImageMagick if available) ────────

    def batch_resize(self, input_dir: str, output_dir: str, width: int = 1920, height: int = 1080):
        """Resize all images in a directory using ImageMagick."""
        try:
            subprocess.run(["convert"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "⚠️ ImageMagick not installed. Install with: sudo apt install imagemagick"

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        input_path = Path(input_dir)
        supported = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}
        files = [f for f in input_path.iterdir() if f.suffix.lower() in supported]

        if not files:
            return f"❌ No supported images found in {input_dir}"

        for f in files:
            out = Path(output_dir) / f.name
            subprocess.run(["convert", str(f), "-resize", f"{width}x{height}>", str(out)],
                           capture_output=True)
        log.info("Batch resized %d images to %dx%d", len(files), width, height)
        return f"✅ Resized {len(files)} images to {width}x{height} in {output_dir}"

    def batch_convert(self, input_dir: str, output_dir: str, format: str = "jpg"):
        """Convert images to a different format."""
        try:
            subprocess.run(["convert"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "⚠️ ImageMagick not installed."

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        input_path = Path(input_dir)
        supported = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}
        files = [f for f in input_path.iterdir() if f.suffix.lower() in supported]

        for f in files:
            out = Path(output_dir) / f"{f.stem}.{format.lower()}"
            subprocess.run(["convert", str(f), str(out)], capture_output=True)
        log.info("Batch converted %d images to %s", len(files), format)
        return f"✅ Converted {len(files)} images to {format.upper()} in {output_dir}"

    # ── Report ─────────────────────────────────────────────────

    def report(self) -> str:
        lines = ["📷 Photography Report — " + datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
        lines.append(f"📊 Portfolio: {len(self.portfolio)} photos | Projects: {len(self.projects)} | Presets: {len(self.presets)}\n")
        lines.append(self.portfolio_stats())
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="photography",
        description="📷 Photography Agent — portfolio, projects, presets, batch processing"
    )
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("add-photo", help="Add a photo to portfolio")
    p.add_argument("--filename", required=True, help="Filename")
    p.add_argument("--path", required=True, help="Full path to file")
    p.add_argument("--title", default="", help="Photo title")
    p.add_argument("--tags", nargs="*", default=[], help="Tags")
    p.add_argument("--location", default="", help="Location taken")
    p.add_argument("--camera", default="", help="Camera model")
    p.add_argument("--rating", type=int, default=0, help="Rating 1-5")

    p = sub.add_parser("list-portfolio", help="List portfolio photos")
    p.add_argument("--tag", default="", help="Filter by tag")
    p.add_argument("--rating", type=int, default=0, help="Min rating filter")

    p = sub.add_parser("rate-photo", help="Rate a photo")
    p.add_argument("--filename", required=True, help="Filename")
    p.add_argument("--rating", type=int, required=True, help="Rating 1-5")

    sub.add_parser("portfolio-stats", help="Portfolio statistics")

    p = sub.add_parser("create-project", help="Create a photography project")
    p.add_argument("--name", required=True, help="Project name")
    p.add_argument("--description", default="", help="Description")
    p.add_argument("--output-dir", default="", help="Output directory")

    p = sub.add_parser("add-to-project", help="Add photos to a project")
    p.add_argument("--project", required=True, help="Project name")
    p.add_argument("--filenames", nargs="+", required=True, help="Filenames")

    sub.add_parser("list-projects", help="List projects")

    p = sub.add_parser("add-preset", help="Save an edit preset")
    p.add_argument("--name", required=True, help="Preset name")
    p.add_argument("--filter", required=True, help="Filter name")
    p.add_argument("--params", default="{}", help="JSON params dict")
    p.add_argument("--description", default="", help="Description")

    sub.add_parser("list-presets", help="List edit presets")

    p = sub.add_parser("batch-resize", help="Batch resize images (requires ImageMagick)")
    p.add_argument("--input-dir", required=True, help="Input directory")
    p.add_argument("--output-dir", required=True, help="Output directory")
    p.add_argument("--width", type=int, default=1920, help="Max width")
    p.add_argument("--height", type=int, default=1080, help="Max height")

    p = sub.add_parser("batch-convert", help="Batch convert image format")
    p.add_argument("--input-dir", required=True, help="Input directory")
    p.add_argument("--output-dir", required=True, help="Output directory")
    p.add_argument("--format", default="jpg", help="Target format")

    sub.add_parser("report", help="Full photography report")

    args = parser.parse_args()
    agent = PhotographyAgent()

    if args.cmd == "add-photo":
        print(agent.add_photo(args.filename, args.path, title=args.title, tags=args.tags,
                              location=args.location, camera=args.camera, rating=args.rating))
    elif args.cmd == "list-portfolio":
        print(agent.list_portfolio(getattr(args, 'tag', ''), getattr(args, 'rating', 0)))
    elif args.cmd == "rate-photo":
        print(agent.rate_photo(args.filename, args.rating))
    elif args.cmd == "portfolio-stats":
        print(agent.portfolio_stats())
    elif args.cmd == "create-project":
        print(agent.create_project(args.name, args.description, args.output_dir))
    elif args.cmd == "add-to-project":
        print(agent.add_to_project(args.project, args.filenames))
    elif args.cmd == "list-projects":
        print(agent.list_projects())
    elif args.cmd == "add-preset":
        params = {}
        if args.params != "{}":
            try:
                params = json.loads(args.params)
            except Exception:
                pass
        print(agent.add_preset(args.name, args.filter, params, args.description))
    elif args.cmd == "list-presets":
        print(agent.list_presets())
    elif args.cmd == "batch-resize":
        print(agent.batch_resize(args.input_dir, args.output_dir, args.width, args.height))
    elif args.cmd == "batch-convert":
        print(agent.batch_convert(args.input_dir, args.output_dir, args.format))
    elif args.cmd == "report":
        print(agent.report())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
