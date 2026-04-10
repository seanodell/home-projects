import re
from datetime import date

import frontmatter

from _projects import PROJECTS_DIR

VERB_GROUP = "create"
SKILL_GROUP = "projects"
SKILL_GROUP_DESCRIPTION = "Home project management"

SCHEMA = {
    "description": "Create a new home project file with standard frontmatter",
    "input": {
        "properties": {
            "title": {
                "type": "string",
                "description": "Project title (e.g. 'Fix leaking kitchen faucet')",
            },
            "status": {
                "type": "string",
                "description": "Initial status (default: idea)",
            },
            "priority": {
                "type": "string",
                "description": "Priority: low, medium, high (default: medium)",
            },
            "tags": {
                "type": "array",
                "description": "Tags for categorization (e.g. ['plumbing', 'kitchen'])",
            },
        },
        "required": ["title"],
    },
    "output": {
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to the created project file",
            },
            "title": {
                "type": "string",
                "description": "Project title",
            },
        },
    },
}


def _slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def run(title, status="idea", priority="medium", tags=None, **kwargs):
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    slug = _slugify(title)
    filepath = PROJECTS_DIR / f"{slug}.md"

    if filepath.exists():
        return {"error": f"Project file already exists: {filepath.name}"}

    today = date.today().isoformat()
    post = frontmatter.Post(
        content="",
        title=title,
        status=status,
        priority=priority,
        tags=tags or [],
        created=today,
        updated=today,
    )

    filepath.write_text(frontmatter.dumps(post) + "\n")
    return {"file": str(filepath), "title": title}
