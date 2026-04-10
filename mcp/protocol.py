import json


def parse_message(line):
    msg = json.loads(line)
    if msg.get("jsonrpc") != "2.0":
        raise ValueError("Not a JSON-RPC 2.0 message")
    return msg


def is_notification(msg):
    return "id" not in msg


def make_response(msg_id, result):
    return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result})


def make_error(msg_id, code, message):
    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": code, "message": message},
    })
