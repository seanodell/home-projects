import importlib
import sys
from pathlib import Path

ACTIONS_DIR = Path(__file__).parent / "actions"
REQUIRED_ATTRS = ("VERB_GROUP", "SKILL_GROUP", "SCHEMA", "run")

# Ensure actions/ is on sys.path so _-prefixed helpers can be imported
_actions_str = str(ACTIONS_DIR)
if _actions_str not in sys.path:
    sys.path.insert(0, _actions_str)


def discover_actions(reload=False):
    actions = {}
    if not ACTIONS_DIR.is_dir():
        return actions

    action_files = sorted(ACTIONS_DIR.glob("*.py"))
    current_names = set()

    for filepath in action_files:
        name = filepath.stem
        if name.startswith("_"):
            continue
        current_names.add(name)
        module_path = f"actions.{name}"
        try:
            if reload and module_path in sys.modules:
                mod = importlib.reload(sys.modules[module_path])
            else:
                mod = importlib.import_module(module_path)
        except Exception as e:
            print(f"[discovery] failed to import {name}: {e}", file=sys.stderr)
            continue

        missing = [a for a in REQUIRED_ATTRS if not hasattr(mod, a)]
        if missing:
            print(f"[discovery] {name} missing: {', '.join(missing)}", file=sys.stderr)
            continue

        actions[name] = mod

    # Clean stale modules from sys.modules
    stale = [
        key for key in sys.modules
        if key.startswith("actions.") and key != "actions"
        and key.split(".", 1)[1] not in current_names
    ]
    for key in stale:
        del sys.modules[key]

    return actions


def group_by_verb(actions):
    groups = {}
    for name, mod in actions.items():
        groups.setdefault(mod.VERB_GROUP, {})[name] = mod
    return groups


def group_by_skill(actions):
    groups = {}
    for name, mod in actions.items():
        groups.setdefault(mod.SKILL_GROUP, {})[name] = mod
    return groups
