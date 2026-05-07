#!/usr/bin/env python3
"""Ask Claude for a unified-diff patch that fixes the failed CI logs.

Usage:
  auto_fix_ci.py <failed_log_file> [<branch_diff_file>]

The optional branch_diff_file should contain `git diff origin/main..HEAD`
so Claude has both the failure AND the changes that introduced it.
Without it, Claude often refuses because it can't see the source.

Stdout:
  Either a unified diff (lines starting with `diff --git`) ready to feed
  to `git apply`, OR the literal `NO_AUTOFIX_AVAILABLE` on the first
  line followed by a one-sentence reason on the second line.

Always exits 0 — the caller decides what to do based on the first line.
"""

from __future__ import annotations

import sys
import urllib.error

from _claude_api import call_claude

MAX_LOG_CHARS = 60_000


PROMPT = """You are an automated CI fixer for the Shortlink demo
(FastAPI backend + Vite/React/TS frontend).

You will see TWO things below:
  1. The diff of the changes the developer made on this branch (vs main)
  2. The failed CI log

Together these are usually enough context: pinpoint which line in the
diff caused the failure and write a minimal patch that fixes it. Do NOT
ask for more files — work with what is shown.

If — and ONLY if — the fix is small, obvious, and confined to source
code under `backend/` or `frontend/src/`, output a unified diff that
resolves it.

Strict rules:
- Output ONLY the diff. No explanation, no markdown fences, no preamble.
- Use standard `diff --git a/<path> b/<path>` format that `git apply`
  can consume directly.
- Keep the patch minimal — only the lines actually needed for the fix.
- NEVER touch: `.github/`, `Dockerfile`, `fly.toml`, `scripts/`,
  `pyproject.toml`, `package.json`, `package-lock.json`, lockfiles,
  config files, or anything outside `backend/` and `frontend/src/`.
- If the failure looks like a flaky test, env issue, network problem,
  CI config problem, or anything you cannot fix safely with a tiny
  source-only patch, output exactly:

    NO_AUTOFIX_AVAILABLE
    <one sentence saying why>

  Nothing else.

Branch diff (changes on this PR vs main):
```
{branch_diff}
```

Failed log:
```
{log}
```
"""


def strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("NO_AUTOFIX_AVAILABLE")
        print("usage: auto_fix_ci.py <log_file> [<branch_diff_file>]")
        return 0

    log = open(sys.argv[1]).read()
    if not log.strip():
        print("NO_AUTOFIX_AVAILABLE")
        print("Empty failed-log file")
        return 0

    branch_diff = ""
    if len(sys.argv) == 3:
        try:
            branch_diff = open(sys.argv[2]).read()
        except OSError:
            branch_diff = ""

    try:
        text = call_claude(
            PROMPT.format(
                log=log[:MAX_LOG_CHARS],
                branch_diff=branch_diff[:MAX_LOG_CHARS] or "(no branch diff provided)",
            ),
            max_tokens=4096,
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print("NO_AUTOFIX_AVAILABLE")
        print(f"API call failed: {type(e).__name__}: {e}")
        return 0
    except Exception as e:
        print("NO_AUTOFIX_AVAILABLE")
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return 0

    cleaned = strip_fences(text)
    if not cleaned:
        print("NO_AUTOFIX_AVAILABLE")
        print("Empty response from model")
        return 0

    print(cleaned)
    return 0


if __name__ == "__main__":
    sys.exit(main())
