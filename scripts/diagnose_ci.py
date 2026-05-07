#!/usr/bin/env python3
"""Send failed CI logs to Claude and print a markdown diagnosis comment.

Usage:
  diagnose_ci.py <failed_log_file>

Reads:
  ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN — env vars
  GITHUB_RUN_URL, GITHUB_SHA, GITHUB_REPOSITORY — optional, for context

Stdout: markdown ready to post as a PR comment.
Always exits 0 — diagnosis failures degrade to a comment, not a CI red.
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


def call_api(prompt: str) -> str:
    base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/")
    token = os.environ["ANTHROPIC_AUTH_TOKEN"]

    body = {
        "model": MODEL,
        "max_tokens": 2048,
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
    return "".join(block.get("text", "") for block in data.get("content", []))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: diagnose_ci.py <log_file>", file=sys.stderr)
        return 2

    log = open(sys.argv[1]).read()
    if not log.strip():
        print("## 🩺 CI diagnosis\n\nNo failed-step log was captured.")
        return 0

    try:
        text = call_api(build_prompt(log))
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
