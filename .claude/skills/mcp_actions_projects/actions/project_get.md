# project_get

Get a project's frontmatter as structured data

## Request

```json
mcp_actions_fetch
{
  "action": "project_get",
  "params": {
    "properties": {
      "file": {
        "type": "string",
        "description": "Project filename (e.g. 'fix-leaking-kitchen-faucet.md')"
      }
    },
    "required": [
      "file"
    ]
  }
}
```

## Response

```json
{
  "properties": {
    "title": {
      "type": "string",
      "description": "Project title"
    },
    "status": {
      "type": "string",
      "description": "Current status"
    },
    "priority": {
      "type": "string",
      "description": "Priority level"
    },
    "tags": {
      "type": "array",
      "description": "Project tags"
    },
    "created": {
      "type": "string",
      "description": "Creation date"
    },
    "updated": {
      "type": "string",
      "description": "Last updated date"
    }
  }
}
```
