import json

from discovery import discover_actions, group_by_verb

TOOL_PREFIX = "mcp_actions_"


def build_tool_list(actions):
    tools = []
    for verb, verb_actions in sorted(group_by_verb(actions).items()):
        action_lines = []
        enum_values = []
        for name in sorted(verb_actions):
            mod = verb_actions[name]
            desc = mod.SCHEMA.get("description", "")
            action_lines.append(f"- {name}: {desc}")
            enum_values.append(name)

        tools.append({
            "name": f"{TOOL_PREFIX}{verb}",
            "description": "\n".join(action_lines),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action module name to call",
                        "enum": enum_values,
                    },
                    "params": {
                        "type": "object",
                        "description": "Action-specific parameters",
                    },
                },
                "required": ["action"],
            },
        })
    return tools


def handle_tools_call(tool_name, arguments):
    actions = discover_actions(reload=True)
    verb_groups = group_by_verb(actions)

    action_name = arguments.get("action")
    params = arguments.get("params", {})

    if action_name not in actions:
        return _error_result(f"Unknown action: {action_name}")

    mod = actions[action_name]
    expected_tool = f"{TOOL_PREFIX}{mod.VERB_GROUP}"
    if tool_name != expected_tool:
        return _error_result(
            f"Action {action_name} belongs to tool {expected_tool}, not {tool_name}"
        )

    try:
        result = mod.run(**params)
    except TypeError as e:
        return _error_result(f"Invalid parameters: {e}")
    except Exception as e:
        return _error_result(f"{type(e).__name__}: {e}")

    return _success_result(result)


def _success_result(data):
    return {
        "content": [{"type": "text", "text": json.dumps(data)}],
    }


def _error_result(message):
    return {
        "content": [{"type": "text", "text": json.dumps({"error": message})}],
        "isError": True,
    }
