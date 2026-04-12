# project_pdf

Generate a formatted PDF from a project file, keeping sections together on pages. Do not assume page_size or page_ordering — if the user doesn't specify them, use AskUserQuestion to ask before generating.

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
        "description": "Page size: letter, a4, legal, a5, halfletter. Ask the user if not specified."
      },
      "page_ordering": {
        "type": "string",
        "description": "Page ordering: normal, saddle-stitch, 2-up. Ask the user if not specified."
      }
    },
    "required": [
      "file",
      "page_size",
      "page_ordering"
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
