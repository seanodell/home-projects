import json
import sys

from protocol import parse_message, is_notification, make_response, make_error
from discovery import discover_actions
from dispatch import build_tool_list, handle_tools_call
from skills import generate_all_skill_docs

SERVER_INFO = {
    "name": "mcp-actions",
    "version": "0.1.0",
}
PROTOCOL_VERSION = "2024-11-05"


def handle_initialize(msg):
    return make_response(msg["id"], {
        "protocolVersion": PROTOCOL_VERSION,
        "serverInfo": SERVER_INFO,
        "capabilities": {"tools": {}},
    })


def handle_ping(msg):
    return make_response(msg["id"], {})


def handle_tools_list(msg):
    actions = discover_actions(reload=True)
    tools = build_tool_list(actions)
    return make_response(msg["id"], {"tools": tools})


def handle_tools_call_msg(msg):
    params = msg.get("params", {})
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})
    result = handle_tools_call(tool_name, arguments)
    return make_response(msg["id"], result)


METHODS = {
    "initialize": handle_initialize,
    "ping": handle_ping,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call_msg,
}


def main():
    # Startup: discover actions and generate skill docs
    actions = discover_actions()
    generate_all_skill_docs(actions)
    print(f"[server] loaded {len(actions)} actions, skill docs written", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = parse_message(line)
        except Exception as e:
            # Can't parse — write error if we can extract an id
            resp = make_error(None, -32700, f"Parse error: {e}")
            sys.stdout.write(resp + "\n")
            sys.stdout.flush()
            continue

        if is_notification(msg):
            continue

        method = msg.get("method", "")
        handler = METHODS.get(method)
        if handler:
            try:
                resp = handler(msg)
            except Exception as e:
                resp = make_error(msg["id"], -32603, f"Internal error: {e}")
        else:
            resp = make_error(msg["id"], -32601, f"Method not found: {method}")

        sys.stdout.write(resp + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
