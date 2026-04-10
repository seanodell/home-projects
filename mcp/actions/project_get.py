import frontmatter

from _projects import PROJECTS_DIR

VERB_GROUP = "fetch"
SKILL_GROUP = "projects"

SCHEMA = {
    "description": "Get a project's frontmatter as structured data",
    "input": {
        "properties": {
            "file": {
                "type": "string",
                "description": "Project filename (e.g. 'fix-leaking-kitchen-faucet.md')",
            },
        },
        "required": ["file"],
    },
    "output": {
        "properties": {
            "title": {
                "type": "string",
                "description": "Project title",
            },
            "status": {
                "type": "string",
                "description": "Current status",
            },
            "priority": {
                "type": "string",
                "description": "Priority level",
            },
            "tags": {
                "type": "array",
                "description": "Project tags",
            },
            "created": {
                "type": "string",
                "description": "Creation date",
            },
            "updated": {
                "type": "string",
                "description": "Last updated date",
            },
        },
    },
}


def run(file, **kwargs):
    filepath = PROJECTS_DIR / file
    if not filepath.exists():
        return {"error": f"Project not found: {file}"}

    post = frontmatter.load(str(filepath))
    meta = dict(post.metadata)
    meta["file"] = file
    return meta
