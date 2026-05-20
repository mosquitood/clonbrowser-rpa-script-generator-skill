#!/usr/bin/env python3
"""Validate a browser-to-RPA handoff JSON file."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = {
    "status": str,
    "attempt": int,
    "max_attempts": int,
    "task": str,
    "start_url": str,
    "playwright_python": str,
    "steps": list,
    "assumptions": list,
    "warnings": list,
}

REQUIRED_STEP = {
    "intent": str,
    "action": str,
    "locator": (str, type(None)),
    "value": (str, type(None)),
    "wait_for": str,
    "verified": bool,
    "evidence": str,
}

VALID_ACTIONS = {"goto", "click", "fill", "select", "press", "wait", "assert", "extract"}
LOCATOR_ACTIONS = {"click", "fill", "select", "press", "assert", "extract"}
ASYNC_TOKENS = ("async def", "await ", "async with", "async for")
HEADLESS_TRUE_PATTERN = re.compile(r"headless\s*=\s*True\b")
LAUNCH_CALL_PATTERN = re.compile(r"\b(?:chromium|firefox|webkit)\.launch\s*\(")
HEADED_FALSE_PATTERN = re.compile(r"headless\s*=\s*False\b")


def fail(message: str) -> None:
    print(f"handoff invalid: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_type(name: str, value: Any, expected: Any) -> None:
    if not isinstance(value, expected):
        if isinstance(expected, tuple):
            names = ", ".join(t.__name__ for t in expected)
        else:
            names = expected.__name__
        fail(f"{name} must be {names}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_browser_handoff.py <handoff.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8-sig"))

    for key, expected in REQUIRED_TOP_LEVEL.items():
        if key not in data:
            fail(f"missing top-level field: {key}")
        check_type(key, data[key], expected)

    if data["status"] != "success":
        fail("status must be success before RPA generation")

    if isinstance(data["attempt"], bool) or isinstance(data["max_attempts"], bool):
        fail("attempt and max_attempts must be integers, not booleans")

    if data["max_attempts"] != 3:
        fail("max_attempts must be 3")

    if data["attempt"] < 1 or data["attempt"] > data["max_attempts"]:
        fail("attempt must be between 1 and max_attempts")

    if not data["steps"]:
        fail("steps must not be empty")

    if any(token in data["playwright_python"] for token in ASYNC_TOKENS):
        fail("playwright_python must use synchronous style and must not contain async/await syntax")

    playwright_python = data["playwright_python"]
    if HEADLESS_TRUE_PATTERN.search(playwright_python):
        fail("playwright_python must force headed mode and must not contain headless=True")
    if LAUNCH_CALL_PATTERN.search(playwright_python) and not HEADED_FALSE_PATTERN.search(playwright_python):
        fail("playwright_python launch calls must explicitly include headless=False")

    for index, step in enumerate(data["steps"]):
        check_type(f"steps[{index}]", step, dict)
        for key, expected in REQUIRED_STEP.items():
            if key not in step:
                fail(f"steps[{index}] missing field: {key}")
            check_type(f"steps[{index}].{key}", step[key], expected)
        if step["action"] not in VALID_ACTIONS:
            fail(f"steps[{index}].action must be one of {sorted(VALID_ACTIONS)}")
        if step["action"] in LOCATOR_ACTIONS and not step["locator"]:
            fail(f"steps[{index}].locator must be set for action {step['action']}")
        if step["verified"] is not True:
            fail(f"steps[{index}].verified must be true after real page verification")
        if not step["evidence"].strip():
            fail(f"steps[{index}].evidence must describe the real page observation")
        if "fallbacks" in step:
            check_type(f"steps[{index}].fallbacks", step["fallbacks"], list)

    print("handoff valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

