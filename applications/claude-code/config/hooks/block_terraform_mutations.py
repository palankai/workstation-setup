#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""PreToolUse hook: stop the agent running terraform commands that mutate things.

Csaba reads the plan and runs the mutating commands himself. Claude writes the
code and hands over the commands. Read-only terraform (plan, validate, show,
output) is fine and needs no permission.

Scope: Bash tool calls only. Writing *about* these commands with the Write/Edit
tools -- READMEs, runbooks, docs -- is deliberately unaffected, as is quoting
them back in chat.
"""

import json
import re
import sys

BLOCKED = ("apply", "destroy")

# terraform/tofu (or the `tf` alias) followed by a blocked subcommand, anywhere
# in the command line: after a `cd`, inside `sh -c "..."`, or with global flags
# such as -chdir=. Deliberately broad -- a false positive costs one retry, a
# false negative costs real infrastructure.
PATTERN = re.compile(
    r"\b(?:terraform|tofu|tf)\b(?:\s+-{1,2}[^\s]+)*\s+(?:%s)\b" % "|".join(BLOCKED)
)


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")

    if PATTERN.search(command):
        print(
            "BLOCKED: terraform commands that mutate infrastructure or state are "
            "Csaba's to run, not the agent's.\n"
            "Write the code, then hand over the exact commands in order and say what "
            "the plan should show. Read-only terraform (plan/validate/show/output) "
            "is allowed.\n"
            "Writing docs that mention these commands is fine -- use the Write or "
            "Edit tool rather than a shell heredoc.",
            file=sys.stderr,
        )
        sys.exit(2)  # exit 2 blocks the tool call and shows stderr to Claude

    sys.exit(0)


if __name__ == "__main__":
    main()
