#!/bin/bash
# Codex Subagent to OpenClaw Skill Converter
# Usage: ./codex-to-openclaw.sh <category> <agent-name>

CATEGORIES=(
    "01-core-development"
    "02-language-specialists"
    "03-infrastructure"
    "04-quality-security"
    "05-data-ai"
    "06-developer-experience"
    "07-specialized-domains"
    "08-business-product"
    "09-meta-orchestration"
    "10-research-analysis"
)

BASE_URL="https://raw.githubusercontent.com/VoltAgent/awesome-codex-subagents/main/categories"
OUTPUT_DIR="/home/clawbot/.openclaw/workspace/skills"
CODEX_AGENTS_DIR="/home/clawbot/.codex/agents"

mkdir -p "$OUTPUT_DIR" "$CODEX_AGENTS_DIR"

# Download and install all agents from a category
download_category() {
    local category="$1"
    echo "📥 Downloading category: $category"
    
    # Get list of TOML files in category
    local files=$(curl -sL "https://api.github.com/repos/VoltAgent/awesome-codex-subagents/contents/categories/$category" | \
        python3 -c "import sys,json; [print(f['name']) for f in json.load(sys.stdin) if f['name'].endswith('.toml')]" 2>/dev/null)
    
    for file in $files; do
        local agent_name="${file%.toml}"
        echo "  📥 $agent_name"
        
        # Download TOML
        curl -sL "$BASE_URL/$category/$file" -o "$CODEX_AGENTS_DIR/$file"
        
        # Convert to OpenClaw Skill
        python3 << PYTHON_SCRIPT
import tomli
import sys

toml_file = "$CODEX_AGENTS_DIR/$file"
skill_name = "$agent_name"
output_dir = "$OUTPUT_DIR/$skill_name"

try:
    with open(toml_file, 'rb') as f:
        data = tomli.load(f)
    
    # Extract metadata
    name = data.get('name', skill_name)
    description = data.get('description', 'Converted from VoltAgent Codex Subagent')
    model = data.get('model', '')
    sandbox = data.get('sandbox_mode', 'unknown')
    
    # Extract developer instructions
    dev = data.get('developer_instructions', {})
    working_mode = dev.get('working_mode', 'Standard development practices.')
    focus_areas = dev.get('focus_areas', [])
    quality_checks = dev.get('quality_checks', [])
    return_format = dev.get('return_format', '')
    do_not = dev.get('do_not', [])
    
    # Build SKILL.md
    skill_md = f"""# {name.title()} Skill

**When to use:** {description}

**Source:** Converted from VoltAgent/awesome-codex-subagents
**Original Model:** {model}
**Sandbox Mode:** {sandbox}

## Instructions

{working_mode}

"""
    
    if focus_areas:
        skill_md += "### Focus Areas\\n"
        for area in focus_areas:
            skill_md += f"- {area}\\n"
        skill_md += "\\n"
    
    if quality_checks:
        skill_md += "### Quality Checks\\n"
        for check in quality_checks:
            skill_md += f"- {check}\\n"
        skill_md += "\\n"
    
    if return_format:
        skill_md += f"### Return Format\\n{return_format}\\n\\n"
    
    if do_not:
        skill_md += "### Do NOT\\n"
        for d in do_not:
            skill_md += f"- {d}\\n"
        skill_md += "\\n"
    
    # Save SKILL.md
    import os
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/SKILL.md", 'w') as f:
        f.write(skill_md)
    
    print(f"    ✅ Created: {skill_name}")
    
except Exception as e:
    print(f"    ❌ Error: {e}")
PYTHON_SCRIPT
    
    done
}

# Download ALL categories
for cat in "${CATEGORIES[@]}"; do
    download_category "$cat"
done

echo ""
echo "✅ All Codex Subagents downloaded and converted to OpenClaw Skills!"
echo "📁 Location: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR" | head -20
