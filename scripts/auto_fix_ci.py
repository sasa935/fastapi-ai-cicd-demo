#!/usr/bin/env python3
"""Ask Claude for a unified-diff patch that fixes the failed CI logs.

Usage:
  auto_fix_ci.py <failed_log_file>

Stdout:
  Either a unified diff (lines starting with `diff --git`) ready to feed
  to `git apply`, OR the literal `NO_AUTOFIX_AVAILABLE` on the first
  line followed by a one-sentence reason on the second line.

Always exits 0 — the caller decides what to do based on the first line.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

MAX_LOG_CHARS = 60_000
MODEL = os.environ.get("REVIEW_MODEL", "claude-sonnet-4-6")
TIMEOUT_S = 180


PROMPT = """You are an automated CI fixer for the Shortlink demo
(FastAPI backend + Vite/React/TS frontend).

Below is a failed CI log. If — and ONLY if — the fix is small, obvious,
and confined to source code under `backend/` or `frontend/src/`, output
a unified diff that resolves it.

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

Failed log:
```
{log}
```
"""


def call_api(prompt: str) -> str:
    base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/")
    token = os.environ["ANTHROPIC_AUTH_TOKEN"]
    body = {
        "model": MODEL,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        f"{base}/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": token,
            "authorization": f"Bearer {token}",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        data = json.loads(resp.read())
    return "".join(b.get("text", "") for b in data.get("content", []))


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
    if len(sys.argv) != 2:
        print("NO_AUTOFIX_AVAILABLE")
        print("usage: auto_fix_ci.py <log_file>")
        return 0

    log = open(sys.argv[1]).read()
    if not log.strip():
        print("NO_AUTOFIX_AVAILABLE")
        print("Empty failed-log file")
        return 0

    try:
        text = call_api(PROMPT.format(log=log[:MAX_LOG_CHARS]))
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
