# project_update

Update a project's frontmatter fields (status, priority, tags, etc.)

## Request

```json
mcp_actions_update
{
  "action": "project_update",
  "params": {
    "properties": {
      "file": {
        "type": "string",
        "description": "Project filename (e.g. 'fix-leaking-kitchen-faucet.md')"
      },
      "status": {
        "type": "string",
        "description": "New status value"
      },
      "priority": {
        "type": "string",
        "description": "New priority: low, medium, high"
      },
      "tags": {
        "type": "array",
        "description": "Replace tags list"
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
    "file": {
      "type": "string",
      "description": "Project filename"
    },
    "updated_fields": {
      "type": "array",
      "description": "List of fields that were changed"
    }
  }
}
```
