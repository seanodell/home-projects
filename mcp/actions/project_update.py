from datetime import date

import frontmatter

from _projects import PROJECTS_DIR

VERB_GROUP = "update"
SKILL_GROUP = "projects"

SCHEMA = {
    "description": "Update a project's frontmatter fields (status, priority, tags, etc.)",
    "input": {
        "properties": {
            "file": {
                "type": "string",
                "description": "Project filename (e.g. 'fix-leaking-kitchen-faucet.md')",
            },
            "status": {
                "type": "string",
                "description": "New status value",
            },
            "priority": {
                "type": "string",
                "description": "New priority: low, medium, high",
            },
            "tags": {
                "type": "array",
                "description": "Replace tags list",
            },
        },
        "required": ["file"],
    },
    "output": {
        "properties": {
            "file": {
                "type": "string",
                "description": "Project filename",
            },
            "updated_fields": {
                "type": "array",
                "description": "List of fields that were changed",
            },
        },
    },
}


UPDATABLE = ("status", "priority", "tags")


def run(file, **kwargs):
    filepath = PROJECTS_DIR / file
    if not filepath.exists():
        return {"error": f"Project not found: {file}"}

    post = frontmatter.load(str(filepath))
    updated_fields = []

    for field in UPDATABLE:
        if field in kwargs and kwargs[field] is not None:
            post.metadata[field] = kwargs[field]
            updated_fields.append(field)

    if updated_fields:
        post.metadata["updated"] = date.today().isoformat()
        filepath.write_text(frontmatter.dumps(post) + "\n")

    return {"file": file, "updated_fields": updated_fields}
