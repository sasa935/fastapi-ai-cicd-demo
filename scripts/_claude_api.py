"""Tiny shared helper for calling Claude via the OAuth (Max subscription) path.

All three CI scripts (diagnose_ci, auto_fix_ci, release_notes) need the same
3-line API call. Centralising it keeps the auth swap to one place.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = os.environ.get("REVIEW_MODEL", "claude-sonnet-4-6")
DEFAULT_TIMEOUT = 180

# OAuth-token rate limits on api.anthropic.com tend to bite; retry a few times.
_RETRIES = 4
_BACKOFF_BASE = 8  # seconds: 8, 16, 32, 64


def _post_once(token: str, body: dict, timeout: int) -> str:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "authorization": f"Bearer {token}",
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "oauth-2025-04-20",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return "".join(block.get("text", "") for block in data.get("content", []))


def call_claude(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 2048,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """POST a single-turn user prompt and return the assistant text.

    Auth comes from CLAUDE_CODE_OAUTH_TOKEN env (sk-ant-oat01-... from
    `claude setup-token` against a Max subscription). Quota is consumed
    against the connected subscription, not API billing.

    Retries on 429 / 5xx with exponential backoff. Other HTTPErrors raise.
    """
    token = os.environ["CLAUDE_CODE_OAUTH_TOKEN"]
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    last_err: Exception | None = None
    for attempt in range(_RETRIES):
        try:
            return _post_once(token, body, timeout)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429 or 500 <= e.code < 600:
                if attempt < _RETRIES - 1:
                    delay = _BACKOFF_BASE * (2**attempt)
                    time.sleep(delay)
                    continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("call_claude exhausted retries without raising")
