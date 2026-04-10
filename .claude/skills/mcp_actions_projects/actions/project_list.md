# project_list

List home projects, optionally filtered by status, priority, or tag

## Request

```json
mcp_actions_fetch
{
  "action": "project_list",
  "params": {
    "properties": {
      "status": {
        "type": "string",
        "description": "Filter by status (e.g. 'idea', 'planning', 'in-progress')"
      },
      "priority": {
        "type": "string",
        "description": "Filter by priority: low, medium, high"
      },
      "tag": {
        "type": "string",
        "description": "Filter by tag (e.g. 'plumbing')"
      }
    },
    "required": []
  }
}
```

## Response

```json
{
  "properties": {
    "projects": {
      "type": "array",
      "description": "List of projects with frontmatter fields"
    },
    "count": {
      "type": "integer",
      "description": "Number of matching projects"
    }
  }
}
```
