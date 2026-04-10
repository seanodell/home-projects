# project_pdf

Generate a formatted PDF from a project file, keeping sections together on pages

## Request

```json
mcp_actions_create
{
  "action": "project_pdf",
  "params": {
    "properties": {
      "file": {
        "type": "string",
        "description": "Project filename (e.g. 'kubota-tractor-maintenance.md')"
      },
      "page_size": {
        "type": "string",
        "description": "Page size: letter, a4, legal, a5, 4x6 (default: letter)"
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
    "pdf": {
      "type": "string",
      "description": "Path to the generated PDF file"
    }
  }
}
```
