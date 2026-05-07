#!/usr/bin/env python3
"""Call the Anthropic-compatible proxy with a PR diff and print a review.

Reads:
  argv[1] — path to the diff file
  ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN — env vars

Stdout: a markdown comment ready to be posted to the PR.
Always exits 0 — review failures become a comment, not a CI red.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

MAX_DIFF_CHARS = 80_000
MODEL = os.environ.get("REVIEW_MODEL", "claude-sonnet-4-6")
TIMEOUT_S = 180


def build_prompt(diff: str) -> str:
    return f"""You are reviewing a pull request for the Shortlink demo (FastAPI + Vite/React/TS).

Focus on:
- Correctness of new behaviour
- Security (URL validation, SQLAlchemy ORM only, no shell/SQL injection)
- Test coverage for new logic
- Obvious code smells

Skip nitpicks. Be concise. Use markdown headings and bullet points.
End with a single-line verdict, e.g. "**Verdict:** ship it" or "**Verdict:** needs changes".

Diff:
```diff
{diff[:MAX_DIFF_CHARS]}
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
    return "".join(block.get("text", "") for block in data.get("content", []))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: review_pr.py <diff_file>", file=sys.stderr)
        return 2

    diff = open(sys.argv[1]).read()
    if not diff.strip():
        print("## 🤖 Claude review\n\nNo diff to review.")
        return 0

    try:
        text = call_api(build_prompt(diff))
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:2000]
        print(f"## ⚠️ Claude review failed\n\nHTTP {e.code}\n\n```\n{body}\n```")
        return 0
    except Exception as e:
        print(f"## ⚠️ Claude review failed\n\n```\n{type(e).__name__}: {e}\n```")
        return 0

    print("## 🤖 Claude review\n")
    print(text)
    print(f"\n<sub>Model: `{MODEL}` · base: `{os.environ['ANTHROPIC_BASE_URL']}`</sub>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
