import hashlib
import json
import shutil
from pathlib import Path

from discovery import group_by_skill, group_by_verb

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"
STANDARD_TOOLS = ["Read", "Write", "Edit", "Glob", "Bash", "AskUserQuestion"]
TOOL_PREFIX = "mcp_actions_"


def generate_all_skill_docs(actions):
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    # Remove stale mcp_actions_* directories
    for path in SKILLS_DIR.iterdir():
        if path.is_dir() and path.name.startswith("mcp_actions_"):
            shutil.rmtree(path)

    for skill_name, skill_actions in group_by_skill(actions).items():
        _generate_skill_group(skill_name, skill_actions)


def _generate_skill_group(skill_name, skill_actions):
    folder = SKILLS_DIR / f"mcp_actions_{skill_name}"
    actions_dir = folder / "actions"
    actions_dir.mkdir(parents=True, exist_ok=True)

    sorted_names = sorted(skill_actions)

    # Description from first module alphabetically that defines it
    description = ""
    for name in sorted_names:
        desc = getattr(skill_actions[name], "SKILL_GROUP_DESCRIPTION", None)
        if desc:
            description = desc
            break

    # Collect verb tools used by actions in this skill group
    verb_tools = sorted({
        f"{TOOL_PREFIX}{skill_actions[n].VERB_GROUP}" for n in sorted_names
    })
    allowed_tools = STANDARD_TOOLS + verb_tools

    # Schema hash
    schema_hash = _compute_schema_hash(skill_actions, sorted_names)

    _write_skill_index(folder / "SKILL.md", skill_name, description,
                       allowed_tools, schema_hash, skill_actions, sorted_names)

    for name in sorted_names:
        _write_action_doc(actions_dir / f"{name}.md", name, skill_actions[name])


def _compute_schema_hash(skill_actions, sorted_names):
    raw = "".join(
        json.dumps(skill_actions[n].SCHEMA, sort_keys=True) for n in sorted_names
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def _write_skill_index(path, skill_name, description, allowed_tools, schema_hash,
                        skill_actions, sorted_names):
    lines = [
        "---",
        f"title: mcp_actions_{skill_name}",
        f"description: {description}",
        f"allowed-tools: [{', '.join(allowed_tools)}]",
        f"schema-hash: {schema_hash}",
        "---",
        "",
        "| Action | Description |",
        "|--------|-------------|",
    ]
    for name in sorted_names:
        desc = skill_actions[name].SCHEMA.get("description", "")
        lines.append(f"| {name} | {desc} |")
    lines.append("")
    path.write_text("\n".join(lines))


def _write_action_doc(path, action_name, mod):
    schema = mod.SCHEMA
    verb = mod.VERB_GROUP
    lines = [f"# {action_name}", "", schema.get("description", ""), ""]

    # Request — exact JSON to send via tools/call
    request = {
        "action": action_name,
        "params": schema.get("input", {}),
    }
    lines.append("## Request")
    lines.append("")
    lines.append(f"```json")
    lines.append(f'{TOOL_PREFIX}{verb}')
    lines.append(json.dumps(request, indent=2))
    lines.append(f"```")
    lines.append("")

    # Response — JSON schema of what run() returns
    output_schema = schema.get("output", {})
    if output_schema.get("properties"):
        lines.append("## Response")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(output_schema, indent=2))
        lines.append("```")
        lines.append("")

    path.write_text("\n".join(lines))
