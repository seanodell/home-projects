import frontmatter

from _projects import PROJECTS_DIR

VERB_GROUP = "fetch"
SKILL_GROUP = "projects"

SCHEMA = {
    "description": "List home projects, optionally filtered by status, priority, or tag",
    "input": {
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by status (e.g. 'idea', 'planning', 'in-progress')",
            },
            "priority": {
                "type": "string",
                "description": "Filter by priority: low, medium, high",
            },
            "tag": {
                "type": "string",
                "description": "Filter by tag (e.g. 'plumbing')",
            },
        },
        "required": [],
    },
    "output": {
        "properties": {
            "projects": {
                "type": "array",
                "description": "List of projects with frontmatter fields",
            },
            "count": {
                "type": "integer",
                "description": "Number of matching projects",
            },
        },
    },
}


def run(status=None, priority=None, tag=None, **kwargs):
    if not PROJECTS_DIR.is_dir():
        return {"projects": [], "count": 0}

    projects = []
    for filepath in sorted(PROJECTS_DIR.glob("*.md")):
        try:
            post = frontmatter.load(str(filepath))
        except Exception:
            continue

        meta = dict(post.metadata)
        meta["file"] = filepath.name

        if status and meta.get("status") != status:
            continue
        if priority and meta.get("priority") != priority:
            continue
        if tag and tag not in meta.get("tags", []):
            continue

        projects.append(meta)

    return {"projects": projects, "count": len(projects)}
