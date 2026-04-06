#!/usr/bin/env python3
"""
Meeting Notes Agent
Captures, organizes, and retrieves meeting notes with action items.
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/personal")
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "meeting_notes.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

NOTES_FILE = DATA_DIR / "meeting_notes.json"
TASKS_FILE = DATA_DIR / "meeting_tasks.json"


def load_json(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {path}: {e}")
    return default if default is not None else {}


def save_json(path: Path, data: Any) -> bool:
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except IOError as e:
        logger.error(f"Error saving {path}: {e}")
        return False


def parse_datetime_safe(dt_str: str) -> datetime:
    """Safely parse datetime string."""
    formats = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.utcnow()


def extract_action_items(text: str) -> list[dict]:
    """Extract action items from meeting notes."""
    items = []
    lines = text.split('\n')
    
    # Patterns for action items
    action_patterns = [
        r"^[-•*]\s*(.+)",
        r"^(\d+[.)]\s*(.+))",
        r"(?:TODO|TASK|ACTION)[:\s]+(.+)",
        r"(?:@|assigned to|responsible)[:\s]*(\w+)",
    ]
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check for due date
        due_match = re.search(r"(?:due|by|until)[:\s]*(\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", line_stripped, re.IGNORECASE)
        due_date = None
        if due_match:
            try:
                due_date = parse_datetime_safe(due_match.group(1)).strftime("%Y-%m-%d")
            except Exception:
                pass
        
        # Check for assignee
        assignee_match = re.search(r"(?:@|assigned to|owner)[:\s]*(\w+)", line_stripped, re.IGNORECASE)
        assignee = assignee_match.group(1) if assignee_match else None
        
        # Check if line looks like an action item
        is_action = any(re.match(p, line_stripped, re.IGNORECASE) for p in action_patterns)
        keywords = ["todo", "task", "action", "will", "should", "needs to", "must", "follow up", "complete"]
        if not is_action and any(kw in line_stripped.lower() for kw in keywords):
            is_action = True
        
        if is_action and len(line_stripped) > 5:
            task_id = f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
            items.append({
                "id": task_id,
                "description": re.sub(r"^[-•*\d.)]+", "", line_stripped).strip(),
                "due_date": due_date,
                "assignee": assignee,
                "status": "pending",
                "source_line": i + 1
            })
    
    return items


def extract_decisions(text: str) -> list[str]:
    """Extract decisions made during meeting."""
    decisions = []
    lines = text.split('\n')
    
    decision_keywords = ["decided", "decision", "agreed", "approved", "confirmed", "resolved", "will proceed", "concluded"]
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        if any(kw in line_stripped.lower() for kw in decision_keywords):
            # Clean up the line
            cleaned = re.sub(r"^[-•*\d.)]+", "", line_stripped).strip()
            if cleaned:
                decisions.append(cleaned)
    
    return decisions


def extract_participants(text: str) -> list[str]:
    """Extract meeting participants."""
    participants = []
    patterns = [
        r"(?:attendees|participants|present|invited)[:\s]*([^\n]+)",
        r"(?:@|\b)[A-Z][a-z]+\s+[A-Z][a-z]+",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            names = re.split(r"[,;&]|and\b", m)
            for name in names:
                name = name.strip()
                if len(name) > 2 and len(name) < 50:
                    participants.append(name)
    
    return list(set(participants))[:20]


def extract_key_topics(text: str) -> list[str]:
    """Extract key discussion topics."""
    topics = []
    lines = text.split('\n')
    
    topic_markers = ["discuss", "topic", "agenda", "subject", "regarding", "re:", "about:"]
    
    for line in lines:
        line_stripped = line.strip()
        if len(line_stripped) < 3:
            continue
        
        # Look for heading-like patterns
        if re.match(r"^#{1,3}\s+(.+)", line_stripped):
            topic = re.sub(r"^#{1,3}\s+", "", line_stripped).strip()
            topics.append(topic)
        elif re.match(r"^[A-Z][A-Z\s]{5,}:", line_stripped):
            topics.append(line_stripped.rstrip(':'))
        elif any(m in line_stripped.lower() for m in topic_markers) and len(line_stripped) < 100:
            topics.append(line_stripped)
    
    return list(set(topics))[:10]


def create_note(title: str, content: str, meeting_date: str = None, 
                participants: list = None, tags: list = None) -> dict:
    """Create a new meeting note."""
    note_id = f"note_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    
    # Extract entities from content
    action_items = extract_action_items(content)
    decisions = extract_decisions(content)
    topics = extract_key_topics(content)
    
    if not participants:
        participants = extract_participants(content)
    
    note = {
        "id": note_id,
        "title": title,
        "content": content,
        "meeting_date": meeting_date or datetime.utcnow().strftime("%Y-%m-%d"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "participants": participants,
        "tags": tags or [],
        "action_items": action_items,
        "decisions": decisions,
        "topics": topics,
        "word_count": len(content.split())
    }
    
    # Save tasks from action items
    if action_items:
        tasks_data = load_json(TASKS_FILE, {"tasks": []})
        for item in action_items:
            item["note_id"] = note_id
            item["note_title"] = title
            tasks_data["tasks"].append(item)
        save_json(TASKS_FILE, tasks_data)
    
    # Save note
    notes = load_json(NOTES_FILE, {"notes": []})
    notes["notes"].append(note)
    save_json(NOTES_FILE, notes)
    
    logger.info(f"Note created: {note_id}")
    return note


def update_note(note_id: str, updates: dict) -> bool:
    """Update an existing note."""
    notes = load_json(NOTES_FILE, {"notes": []})
    
    for note in notes["notes"]:
        if note.get("id") == note_id:
            note.update(updates)
            note["updated_at"] = datetime.utcnow().isoformat()
            
            # Re-extract if content changed
            if "content" in updates:
                note["action_items"] = extract_action_items(updates["content"])
                note["decisions"] = extract_decisions(updates["content"])
                note["word_count"] = len(updates["content"].split())
            
            save_json(NOTES_FILE, notes)
            return True
    
    return False


def delete_note(note_id: str) -> bool:
    """Delete a note."""
    notes = load_json(NOTES_FILE, {"notes": []})
    original_count = len(notes["notes"])
    notes["notes"] = [n for n in notes["notes"] if n.get("id") != note_id]
    
    if len(notes["notes"]) < original_count:
        save_json(NOTES_FILE, notes)
        # Also remove related tasks
        tasks_data = load_json(TASKS_FILE, {"tasks": []})
        tasks_data["tasks"] = [t for t in tasks_data["tasks"] if t.get("note_id") != note_id]
        save_json(TASKS_FILE, tasks_data)
        return True
    return False


def search_notes(query: str, tag: str = None, date_from: str = None, date_to: str = None) -> list[dict]:
    """Search notes by query and filters."""
    notes = load_json(NOTES_FILE, {"notes": []}).get("notes", [])
    
    results = []
    query_lower = query.lower()
    
    for note in notes:
        # Date filter
        if date_from:
            try:
                if parse_datetime_safe(note.get("meeting_date", "")).isoformat() < date_from:
                    continue
            except Exception:
                pass
        
        if date_to:
            try:
                if parse_datetime_safe(note.get("meeting_date", "")).isoformat() > date_to:
                    continue
            except Exception:
                pass
        
        # Tag filter
        if tag:
            if tag.lower() not in [t.lower() for t in note.get("tags", [])]:
                continue
        
        # Text search
        if query:
            searchable = f"{note.get('title', '')} {note.get('content', '')} {' '.join(note.get('tags', []))}"
            if query_lower in searchable.lower():
                results.append(note)
        else:
            results.append(note)
    
    return sorted(results, key=lambda x: x.get("meeting_date", ""), reverse=True)


def get_tasks(status: str = None, assignee: str = None) -> list[dict]:
    """Get action items/tasks."""
    tasks = load_json(TASKS_FILE, {"tasks": []}).get("tasks", [])
    
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    if assignee:
        tasks = [t for t in tasks if assignee.lower() in str(t.get("assignee", "")).lower()]
    
    return sorted(tasks, key=lambda x: x.get("due_date", "9999-12-31"))


def update_task(task_id: str, updates: dict) -> bool:
    """Update a task."""
    tasks_data = load_json(TASKS_FILE, {"tasks": []})
    
    for task in tasks_data["tasks"]:
        if task.get("id") == task_id:
            task.update(updates)
            save_json(TASKS_FILE, tasks_data)
            return True
    
    return False


def cmd_create(args):
    """Create a new meeting note."""
    title = args.title
    if not title:
        title = input("Meeting Title: ").strip()
        if not title:
            print("Title is required")
            return
    
    print("\n📝 Enter meeting notes (Ctrl+D or Ctrl+C to finish):")
    print("   (Include action items with '- ', 'TODO:', or '@person')\n")
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    
    content = '\n'.join(lines)
    participants_str = args.participants or ""
    participants = [p.strip() for p in participants_str.split(",") if p.strip()]
    
    tags_str = args.tags or ""
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    
    note = create_note(
        title=title,
        content=content,
        meeting_date=args.date,
        participants=participants,
        tags=tags
    )
    
    print(f"\n✅ Note created: {note['id']}")
    print(f"   Title: {note['title']}")
    print(f"   Action Items: {len(note['action_items'])}")
    print(f"   Decisions: {len(note['decisions'])}")
    print(f"   Participants: {len(note['participants'])}")


def cmd_list(args):
    """List meeting notes."""
    notes = load_json(NOTES_FILE, {"notes": []}).get("notes", [])
    
    if args.tag:
        notes = [n for n in notes if args.tag.lower() in [t.lower() for t in n.get("tags", [])]]
    
    if args.date:
        notes = [n for n in notes if n.get("meeting_date", "").startswith(args.date)]
    
    if not notes:
        print("No meeting notes found")
        return
    
    print(f"\n{'='*70}")
    print(f"MEETING NOTES: {len(notes)}")
    print(f"{'='*70}\n")
    
    for note in sorted(notes, key=lambda x: x.get("meeting_date", ""), reverse=True):
        date = note.get("meeting_date", "N/A")
        action_count = len(note.get("action_items", []))
        decision_count = len(note.get("decisions", []))
        
        print(f"📋 {date} | {note.get('title', 'Untitled')}")
        print(f"   ID: {note.get('id')}")
        print(f"   Tasks: {action_count} | Decisions: {decision_count}")
        if note.get("tags"):
            print(f"   Tags: {', '.join(note['tags'])}")
        if note.get("participants"):
            print(f"   Participants: {', '.join(note['participants'][:5])}")
        print()


def cmd_view(args):
    """View a specific note."""
    notes = load_json(NOTES_FILE, {"notes": []}).get("notes", [])
    note = next((n for n in notes if n.get("id") == args.note_id), None)
    
    if not note:
        print(f"Note not found: {args.note_id}")
        return
    
    print(f"\n{'='*70}")
    print(f"{note.get('title', 'Untitled')}")
    print(f"{'='*70}")
    print(f"Date: {note.get('meeting_date', 'N/A')}")
    print(f"Participants: {', '.join(note.get('participants', []) or ['None'])}")
    print(f"Tags: {', '.join(note.get('tags', []) or ['None'])}")
    print()
    print("--- CONTENT ---")
    print(note.get("content", ""))
    print()
    
    if note.get("action_items"):
        print("--- ACTION ITEMS ---")
        for i, item in enumerate(note["action_items"], 1):
            status = "✅" if item.get("status") == "completed" else "⬜"
            due = f" (Due: {item['due_date']})" if item.get("due_date") else ""
            print(f"  {status} {i}. {item.get('description', '')}{due}")
            if item.get("assignee"):
                print(f"      @ {item['assignee']}")
        print()
    
    if note.get("decisions"):
        print("--- DECISIONS ---")
        for d in note["decisions"]:
            print(f"  ✓ {d}")
        print()


def cmd_search(args):
    """Search notes."""
    if not args.query:
        print("Error: --query is required")
        return
    
    results = search_notes(args.query, tag=args.tag, date_from=args.from_date, date_to=args.to_date)
    
    if not results:
        print(f"No notes found matching: {args.query}")
        return
    
    print(f"\n{'='*70}")
    print(f"SEARCH RESULTS: {len(results)} notes")
    print(f"Query: {args.query}")
    print(f"{'='*70}\n")
    
    for note in results:
        print(f"📋 {note.get('meeting_date', 'N/A')} | {note.get('title', 'Untitled')}")
        print(f"   ID: {note.get('id')}")
        # Show context around match
        content = note.get("content", "")[:200]
        print(f"   Preview: {content}...")
        print()


def cmd_tasks(args):
    """Show action items/tasks."""
    tasks = get_tasks(status=args.status, assignee=args.assignee)
    
    if not tasks:
        status_str = f" with status '{args.status}'" if args.status else ""
        print(f"No tasks found{status_str}")
        return
    
    print(f"\n{'='*70}")
    print(f"TASKS: {len(tasks)}")
    print(f"{'='*70}\n")
    
    for task in tasks:
        status_icon = {"pending": "⬜", "completed": "✅", "overdue": "🔴"}.get(task.get("status", ""), "⬜")
        due = task.get("due_date", "No due date")
        print(f"{status_icon} [{task.get('id')}]")
        print(f"   {task.get('description', '')}")
        print(f"   Due: {due} | Assigned: {task.get('assignee', 'Unassigned')}")
        print(f"   From: {task.get('note_title', 'N/A')}")
        print()


def cmd_complete(args):
    """Mark a task as completed."""
    if update_task(args.task_id, {"status": "completed", "completed_at": datetime.utcnow().isoformat()}):
        print(f"✅ Task {args.task_id} marked as completed")
    else:
        print(f"❌ Task not found: {args.task_id}")


def cmd_export(args):
    """Export notes."""
    notes = load_json(NOTES_FILE, {"notes": []}).get("notes", [])
    export_data = {"notes": notes, "exported_at": datetime.utcnow().isoformat()}
    
    output_path = Path(args.output) if args.output else DATA_DIR / f"notes_export_{datetime.utcnow().strftime('%Y%m%d')}.json"
    save_json(output_path, export_data)
    print(f"✅ Exported {len(notes)} notes to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Meeting Notes Agent - Capture and organize meeting notes with action items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --create --title "Sprint Planning"
  %(prog)s --list
  %(prog)s --list --tag planning
  %(prog)s --view --note-id note_xxx
  %(prog)s --search --query "budget"
  %(prog)s --tasks
  %(prog)s --tasks --status pending
  %(prog)s --complete --task-id task_xxx
  %(prog)s --export --output my_notes.json
        """
    )
    
    parser.add_argument("--create", action="store_true", help="Create a new meeting note")
    parser.add_argument("--title", type=str, help="Meeting title")
    parser.add_argument("--date", type=str, help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--participants", type=str, help="Comma-separated participants")
    parser.add_argument("--tags", type=str, help="Comma-separated tags")
    
    parser.add_argument("--list", action="store_true", help="List all notes")
    parser.add_argument("--tag", type=str, help="Filter by tag")
    
    parser.add_argument("--view", action="store_true", help="View a specific note")
    parser.add_argument("--note-id", type=str, help="Note ID to view")
    
    parser.add_argument("--search", action="store_true", help="Search notes")
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--from-date", type=str, help="From date (ISO)")
    parser.add_argument("--to-date", type=str, help="To date (ISO)")
    
    parser.add_argument("--tasks", action="store_true", help="Show action items")
    parser.add_argument("--status", type=str, choices=["pending", "completed", "overdue"], help="Filter by status")
    parser.add_argument("--assignee", type=str, help="Filter by assignee")
    
    parser.add_argument("--complete", action="store_true", help="Mark task as completed")
    parser.add_argument("--task-id", type=str, help="Task ID to complete")
    
    parser.add_argument("--export", action="store_true", help="Export all notes")
    parser.add_argument("--output", type=str, help="Output file path")
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.create:
        cmd_create(args)
    elif args.view:
        cmd_view(args)
    elif args.search:
        cmd_search(args)
    elif args.tasks:
        cmd_tasks(args)
    elif args.complete:
        cmd_complete(args)
    elif args.export:
        cmd_export(args)
    elif args.list:
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
