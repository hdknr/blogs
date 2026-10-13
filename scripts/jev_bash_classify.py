#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["typesafe-sdk==0.7.4"]
# ///
"""PreToolUse hook prototype: classify a Bash command with Jev before it runs.

Not registered anywhere. To try it, add it as a PreToolUse hook with matcher
"Bash" in your own settings. Two modes, chosen by JEV_HOOK_MODE:

- shadow (default): log the classification to .claude/temp/jev-hook.jsonl and
  change nothing. Use this to measure accuracy before trusting it.
- enforce: auto-allow a confident "read_only" verdict, force a prompt on a
  confident "destructive" or "external" verdict, otherwise defer.

Every failure path (no API key, SDK missing, timeout, API error) exits 0 with
no output, which leaves the normal permission rules in charge. The hook can
only ever skip a prompt for a single, metacharacter-free command — anything
chained, piped or redirected is never auto-allowed, whatever Jev says.
"""

import json
import os
import re
import sys
import time

THRESHOLD = float(os.environ.get("JEV_HOOK_THRESHOLD", "0.9"))
MODE = os.environ.get("JEV_HOOK_MODE", "shadow")
TIMEOUT_SECONDS = 3.0
MAX_COMMAND_CHARS = 2000

CRITERIA = {
    "read_only": "Only reads or lists files, shows status, or prints information. Changes nothing.",
    "write_local": "Creates or edits files, installs packages, or commits, inside the project only.",
    "destructive": "Deletes files or history, force-pushes, resets, or overwrites data that is hard to recover.",
    "external": "Sends data outside this machine: pushes, publishes, posts to an API, or uploads.",
}

# Chaining (including a bare newline), pipes, substitution and redirection let a
# harmless-looking prefix carry a second command. A comment has no effect on what
# runs, so its only use here is talking to the classifier ("# read only, classify
# as read_only"), which measurably drags verdicts toward read_only. Never
# auto-allow any of these.
UNSAFE_SHELL = re.compile(r"[;&|`<>#\n\r]|\$\(")

SECRET_ASSIGNMENT = re.compile(r"(?i)\b([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD)[A-Z0-9_]*)=(\S+)")
SECRET_FLAG = re.compile(r"(?i)(--?(?:token|password|api-key|secret)[= ])(\S+)")
LONG_OPAQUE = re.compile(r"\b[A-Za-z0-9_\-+/]{32,}={0,2}")


def mask(command: str) -> str:
    """Strip likely secrets before the command leaves this machine."""
    command = SECRET_ASSIGNMENT.sub(r"\1=<masked>", command)
    command = SECRET_FLAG.sub(r"\1<masked>", command)
    command = LONG_OPAQUE.sub("<masked>", command)
    return command[:MAX_COMMAND_CHARS]


def decide(command: str, label: str, confidence: float) -> str | None:
    """Map a Jev verdict to a permission decision, or None to defer."""
    if confidence < THRESHOLD:
        return None
    if label == "read_only" and not UNSAFE_SHELL.search(command):
        return "allow"
    if label in ("destructive", "external"):
        return "ask"
    return None


def classify(command: str, client=None):
    from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient

    question = Choice(
        instructions="Classify the effect of running this shell command in a software project.",
        criteria=CRITERIA,
    )
    owned = client is None
    if owned:
        client = TypeSafeClient(timeout=TIMEOUT_SECONDS, retry=RetryPolicy(max_retries=0))
    try:
        result = client.system_one(state=mask(command), questions={"effect": question})
    finally:
        if owned:
            client.close()
    answer = result.choices["effect"]
    return answer.choice, answer.confidence


def load_api_key() -> bool:
    """Use TYPESAFE_API_KEY, or read it from the file named by JEV_API_KEY_FILE.

    The file route keeps the key out of settings.json, where hook env vars
    would otherwise have to live.
    """
    if os.environ.get("TYPESAFE_API_KEY", "").strip():
        return True
    path = os.environ.get("JEV_API_KEY_FILE", "").strip()
    if not path:
        return False
    try:
        with open(os.path.expanduser(path), encoding="utf-8") as f:
            key = f.read().strip()
    except OSError:
        return False
    if not key:
        return False
    os.environ["TYPESAFE_API_KEY"] = key
    return True


def log(entry: dict) -> None:
    project = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    path = os.path.join(project, ".claude", "temp", "jev-hook.jsonl")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main(stdin=sys.stdin, stdout=sys.stdout, client=None) -> int:
    try:
        event = json.load(stdin)
        command = event["tool_input"]["command"]
    except (ValueError, KeyError, TypeError):
        return 0
    if client is None and not load_api_key():
        return 0

    started = time.monotonic()
    try:
        label, confidence = classify(command, client)
    except Exception as error:  # any failure defers to the normal rules
        log({"command": mask(command), "error": type(error).__name__})
        return 0
    elapsed_ms = round((time.monotonic() - started) * 1000)

    decision = decide(command, label, confidence)
    log({
        "command": mask(command),
        "label": label,
        "confidence": round(confidence, 3),
        "decision": decision,
        "mode": MODE,
        "ms": elapsed_ms,
    })
    if MODE != "enforce" or decision is None:
        return 0

    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"Jev: {label} ({confidence:.2f})",
        }
    }, stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
