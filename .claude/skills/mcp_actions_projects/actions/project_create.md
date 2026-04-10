# project_create

Create a new home project file with standard frontmatter

## Request

```json
mcp_actions_create
{
  "action": "project_create",
  "params": {
    "properties": {
      "title": {
        "type": "string",
        "description": "Project title (e.g. 'Fix leaking kitchen faucet')"
      },
      "status": {
        "type": "string",
        "description": "Initial status (default: idea)"
      },
      "priority": {
        "type": "string",
        "description": "Priority: low, medium, high (default: medium)"
      },
      "tags": {
        "type": "array",
        "description": "Tags for categorization (e.g. ['plumbing', 'kitchen'])"
      }
    },
    "required": [
      "title"
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
      "description": "Path to the created project file"
    },
    "title": {
      "type": "string",
      "description": "Project title"
    }
  }
}
```
