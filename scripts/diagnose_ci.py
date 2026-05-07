#!/usr/bin/env python3
"""Send failed CI logs to Claude and print a markdown diagnosis comment.

Usage:
  diagnose_ci.py <failed_log_file>

Reads:
  CLAUDE_CODE_OAUTH_TOKEN — env var (Max subscription OAuth token)
  GITHUB_RUN_URL, GITHUB_SHA, GITHUB_REPOSITORY — optional, for context

Stdout: markdown ready to post as a PR comment.
Always exits 0 — diagnosis failures degrade to a comment, not a CI red.
"""

from __future__ import annotations

import os
import sys
import urllib.error

from _claude_api import DEFAULT_MODEL as MODEL
from _claude_api import call_claude

MAX_LOG_CHARS = 60_000


def build_prompt(log: str) -> str:
    run_url = os.environ.get("GITHUB_RUN_URL", "")
    sha = os.environ.get("GITHUB_SHA", "")[:7]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    ctx = f"Repo: {repo} · Commit: {sha} · Run: {run_url}\n\n" if repo else ""

    return f"""{ctx}You are diagnosing a failed CI run for the Shortlink demo
(FastAPI backend + Vite/React/TS frontend, GitHub Actions).

The full content below is the failed-step log output (truncated to
{MAX_LOG_CHARS} chars). Identify what went wrong and how to fix it.

Respond in this exact markdown shape:

## 🩺 What failed
One sentence naming the failing job/step.

## Likely root cause
2-4 sentences. Quote the most telling line(s) of the log if helpful.
Distinguish between: source bug · flaky test · environment / config /
network · CI workflow misconfig · dependency drift.

## Suggested fix
Concrete next action. If a code change is obvious, give a unified-diff
snippet (file path + ±lines). If it needs investigation, list what to
check next, in order of likelihood.

## Confidence
`high` / `medium` / `low` — and one sentence why.

Keep the whole reply under ~250 words. No fluff.

Failed log:
```
{log[:MAX_LOG_CHARS]}
```
"""


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: diagnose_ci.py <log_file>", file=sys.stderr)
        return 2

    log = open(sys.argv[1]).read()
    if not log.strip():
        print("## 🩺 CI diagnosis\n\nNo failed-step log was captured.")
        return 0

    try:
        text = call_claude(build_prompt(log))
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:2000]
        print(f"## ⚠️ Diagnosis failed\n\nHTTP {e.code}\n\n```\n{body}\n```")
        return 0
    except Exception as e:
        print(f"## ⚠️ Diagnosis failed\n\n```\n{type(e).__name__}: {e}\n```")
        return 0

    run_url = os.environ.get("GITHUB_RUN_URL", "")
    print(text)
    if run_url:
        print(f"\n<sub>Failed run: {run_url} · model `{MODEL}`</sub>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
