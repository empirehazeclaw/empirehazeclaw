#!/usr/bin/env python3
"""
Template Manager Agent - EmpireHazeClaw
Manages email templates with variables, categories, and preview functionality.
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "templates"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_FILE = DATA_DIR / "templates.json"
LOG_FILE = LOGS_DIR / "template_manager.log"

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TemplateMgr")


def load_templates():
    """Load templates from JSON file."""
    if TEMPLATES_FILE.exists():
        try:
            with open(TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Corrupted templates.json, creating new one")
            return {"templates": {}}
    return {"templates": {}}


def save_templates(data):
    """Save templates to JSON file."""
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def create_template(name, subject, body, category="general", variables=None, description=None):
    """Create a new email template."""
    templates = load_templates()
    
    # Extract variables from body if not provided
    if variables is None:
        variables = re.findall(r'\{\{(\w+)\}\}', body + subject)
        variables = list(set(variables))
    
    template = {
        "name": name,
        "subject": subject,
        "body": body,
        "category": category,
        "variables": variables,
        "description": description or "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "use_count": 0
    }
    
    templates["templates"][name] = template
    save_templates(templates)
    logger.info(f"Created template: {name}")
    return template


def update_template(name, **kwargs):
    """Update an existing template."""
    templates = load_templates()
    
    if name not in templates["templates"]:
        raise ValueError(f"Template '{name}' not found")
    
    template = templates["templates"][name]
    
    # Update fields
    for key in ['subject', 'body', 'category', 'description']:
        if key in kwargs:
            template[key] = kwargs[key]
    
    # Recalculate variables if body or subject changed
    if 'body' in kwargs or 'subject' in kwargs:
        body = template.get('body', '')
        subject = template.get('subject', '')
        variables = re.findall(r'\{\{(\w+)\}\}', body + subject)
        template['variables'] = list(set(variables))
    
    template['updated_at'] = datetime.now().isoformat()
    
    save_templates(templates)
    logger.info(f"Updated template: {name}")
    return template


def render_template(name, variables):
    """Render a template with provided variables."""
    templates = load_templates()
    
    if name not in templates["templates"]:
        raise ValueError(f"Template '{name}' not found")
    
    template = templates["templates"][name]
    
    # Update use count
    templates["templates"][name]['use_count'] = template.get('use_count', 0) + 1
    save_templates(templates)
    
    # Render subject
    rendered_subject = template['subject']
    for var, value in variables.items():
        rendered_subject = rendered_subject.replace(f'{{{{{var}}}}}', str(value))
    
    # Render body
    rendered_body = template['body']
    for var, value in variables.items():
        rendered_body = rendered_body.replace(f'{{{{{var}}}}}', str(value))
    
    return {
        "subject": rendered_subject,
        "body": rendered_body
    }


def list_templates(category=None):
    """List all templates, optionally filtered by category."""
    templates = load_templates()
    all_templates = templates.get("templates", {})
    
    if category:
        filtered = {k: v for k, v in all_templates.items() if v.get("category") == category}
        return filtered
    
    return all_templates


def get_categories():
    """Get list of all categories."""
    templates = load_templates()
    categories = set()
    for t in templates.get("templates", {}).values():
        if t.get("category"):
            categories.add(t["category"])
    return sorted(list(categories))


def delete_template(name):
    """Delete a template."""
    templates = load_templates()
    if name in templates["templates"]:
        del templates["templates"][name]
        save_templates(templates)
        logger.info(f"Deleted template: {name}")
        return True
    return False


def preview_template(name, sample_values=None):
    """Preview a template with sample or placeholder values."""
    templates = load_templates()
    
    if name not in templates["templates"]:
        raise ValueError(f"Template '{name}' not found")
    
    template = templates["templates"][name]
    
    if sample_values is None:
        # Use placeholder values
        sample_values = {var: f"[{var}]" for var in template.get("variables", [])}
    
    rendered = render_template(name, sample_values)
    return {
        "name": name,
        "variables": template.get("variables", []),
        "rendered_subject": rendered["subject"],
        "rendered_body": rendered["body"]
    }


def import_template(file_path):
    """Import template from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            if "templates" in data:
                templates = load_templates()
                templates["templates"].update(data["templates"])
                save_templates(templates)
                return f"Imported {len(data['templates'])} templates"
            elif "name" in data:
                # Single template
                create_template(
                    data["name"],
                    data.get("subject", ""),
                    data.get("body", ""),
                    data.get("category", "imported"),
                    data.get("variables"),
                    data.get("description")
                )
                return f"Imported template: {data['name']}"
        
        return "Invalid template file format"
    except Exception as e:
        raise ValueError(f"Failed to import: {e}")


def export_template(name, file_path):
    """Export a template to JSON file."""
    templates = load_templates()
    
    if name not in templates["templates"]:
        raise ValueError(f"Template '{name}' not found")
    
    with open(file_path, 'w') as f:
        json.dump(templates["templates"][name], f, indent=2)
    
    return f"Exported template to {file_path}"


def main():
    parser = argparse.ArgumentParser(
        description="Template Manager Agent - Manage email templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a template
  %(prog)s create --name welcome --subject "Welcome {{name}}!" --body "Hello {{name}}, welcome to {{company}}!"
  
  # List all templates
  %(prog)s list
  
  # List templates by category
  %(prog)s list --category marketing
  
  # Render a template
  %(prog)s render --name welcome --vars name=John company=Acme
  
  # Preview a template
  %(prog)s preview --name welcome
  
  # Update a template
  %(prog)s update --name welcome --subject "New Welcome {{name}}!"
  
  # Delete a template
  %(prog)s delete --name welcome
  
  # Get categories
  %(prog)s categories
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new template')
    create_parser.add_argument('--name', required=True, help='Template name')
    create_parser.add_argument('--subject', required=True, help='Email subject (use {{var}} for variables)')
    create_parser.add_argument('--body', required=True, help='Email body (use {{var}} for variables)')
    create_parser.add_argument('--category', default='general', help='Category')
    create_parser.add_argument('--description', help='Description')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List templates')
    list_parser.add_argument('--category', help='Filter by category')
    
    # Render command
    render_parser = subparsers.add_parser('render', help='Render template with variables')
    render_parser.add_argument('--name', required=True, help='Template name')
    render_parser.add_argument('--vars', required=True, help='Variables as key=value pairs (comma-separated)')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview template')
    preview_parser.add_argument('--name', required=True, help='Template name')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update template')
    update_parser.add_argument('--name', required=True, help='Template name')
    update_parser.add_argument('--subject', help='New subject')
    update_parser.add_argument('--body', help='New body')
    update_parser.add_argument('--category', help='New category')
    update_parser.add_argument('--description', help='New description')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete template')
    delete_parser.add_argument('--name', required=True, help='Template name')
    
    # Categories command
    subparsers.add_parser('categories', help='List all categories')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import templates from JSON file')
    import_parser.add_argument('--file', required=True, help='JSON file path')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export template to JSON file')
    export_parser.add_argument('--name', required=True, help='Template name')
    export_parser.add_argument('--file', required=True, help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'create':
            create_template(args.name, args.subject, args.body, args.category, description=args.description)
            print(f"✅ Created template '{args.name}'")
            print(f"   Variables detected: {re.findall(r'\{\{(\w+)\}\}', args.body + args.subject)}")
            return 0
        
        elif args.command == 'list':
            templates = list_templates(args.category)
            if not templates:
                print("No templates found.")
                return 0
            
            cat_msg = f" in category '{args.category}'" if args.category else ""
            print(f"\n📝 Email Templates ({len(templates)}){cat_msg}:")
            print("-" * 70)
            
            for name, t in templates.items():
                vars_list = ", ".join([f"{{{{{v}}}}}" for v in t.get("variables", [])])
                print(f"\n  [{name}]")
                print(f"    Subject: {t.get('subject', 'N/A')[:50]}...")
                print(f"    Category: {t.get('category', 'general')}")
                print(f"    Variables: {vars_list if vars_list else 'None'}")
                print(f"    Used: {t.get('use_count', 0)} times")
            print()
            return 0
        
        elif args.command == 'render':
            # Parse variables
            vars_dict = {}
            for pair in args.vars.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    vars_dict[key.strip()] = value.strip()
            
            rendered = render_template(args.name, vars_dict)
            print(f"\n📄 Rendered Template '{args.name}':")
            print("-" * 50)
            print(f"Subject: {rendered['subject']}")
            print(f"\nBody:\n{rendered['body']}")
            return 0
        
        elif args.command == 'preview':
            preview = preview_template(args.name)
            print(f"\n👁️ Preview: {preview['name']}")
            print("-" * 50)
            print(f"Variables: {preview['variables']}")
            print(f"\nSubject:\n{preview['rendered_subject']}")
            print(f"\nBody:\n{preview['rendered_body']}")
            return 0
        
        elif args.command == 'update':
            update_template(args.name, 
                           subject=args.subject, 
                           body=args.body, 
                           category=args.category,
                           description=args.description)
            print(f"✅ Updated template '{args.name}'")
            return 0
        
        elif args.command == 'delete':
            if delete_template(args.name):
                print(f"✅ Deleted template '{args.name}'")
                return 0
            else:
                print(f"❌ Template '{args.name}' not found")
                return 1
        
        elif args.command == 'categories':
            cats = get_categories()
            print(f"\n📁 Categories ({len(cats)}):")
            for cat in cats:
                count = len([t for t in list_templates(cat).values()])
                print(f"  - {cat}: {count} templates")
            return 0
        
        elif args.command == 'import':
            result = import_template(args.file)
            print(f"✅ {result}")
            return 0
        
        elif args.command == 'export':
            result = export_template(args.name, args.file)
            print(f"✅ {result}")
            return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
