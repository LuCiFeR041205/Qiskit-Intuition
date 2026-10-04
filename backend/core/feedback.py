"""Tester feedback, filed as GitHub issues.

With ``FEEDBACK_GITHUB_TOKEN`` set (a fine-grained token with "Issues: write"
on the repository), feedback is posted directly as an issue. Without it, the
app offers a pre-filled "new issue" link the tester opens themselves.
``FEEDBACK_GITHUB_REPO`` (owner/name) overrides the target repository.
"""

from __future__ import annotations

import os
from urllib.parse import urlencode

import requests

DEFAULT_REPO = "LuCiFeR041205/Qiskit-Intuition"
KINDS = ["Confusing explanation", "Bug", "Idea", "Something I liked"]
MIN_LENGTH = 10
MAX_LENGTH = 4000


def build_report(kind: str, message: str, context: dict[str, str]) -> dict[str, str]:
    """Return {"title", "body"} for an issue. ``context`` is page/lesson/stage info."""
    message = (message or "").strip()[:MAX_LENGTH]
    first_line = message.splitlines()[0] if message else ""
    summary = first_line[:60] + ("…" if len(first_line) > 60 else "")
    where = context.get("lesson") or context.get("page", "")
    title = f"[Feedback] {kind}: {summary}" + (f" ({where})" if where else "")
    details = "\n".join(f"- **{key.capitalize()}:** {value}" for key, value in context.items() if value)
    body = f"{message}\n\n---\n{details}\n\n_Sent from the in-app feedback form._"
    return {"title": title, "body": body}


def validate(message: str) -> str | None:
    """An error message for the tester, or None if the feedback can be sent."""
    text = (message or "").strip()
    if len(text) < MIN_LENGTH:
        return f"Please write at least {MIN_LENGTH} characters so the team can act on it."
    if len(text) > MAX_LENGTH:
        return f"Please keep it under {MAX_LENGTH} characters."
    return None


def issue_link(report: dict[str, str], repo: str | None = None) -> str:
    repo = repo or os.getenv("FEEDBACK_GITHUB_REPO", DEFAULT_REPO)
    # Keep the URL a safe length; GitHub truncates very long query strings.
    query = urlencode({"title": report["title"], "body": report["body"][:1500]})
    return f"https://github.com/{repo}/issues/new?{query}"


def submit(report: dict[str, str]) -> dict[str, str]:
    """File the issue if a token is configured.

    Returns {"status": "filed", "url"} on success, otherwise
    {"status": "link", "url"} with a pre-filled issue link (and "error" if
    posting was attempted and failed).
    """
    repo = os.getenv("FEEDBACK_GITHUB_REPO", DEFAULT_REPO)
    token = os.getenv("FEEDBACK_GITHUB_TOKEN", "").strip()
    if not token:
        return {"status": "link", "url": issue_link(report, repo)}
    try:
        response = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            json={"title": report["title"], "body": report["body"]},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10,
        )
        response.raise_for_status()
        return {"status": "filed", "url": response.json().get("html_url", "")}
    except (requests.RequestException, ValueError) as exc:
        return {"status": "link", "url": issue_link(report, repo), "error": type(exc).__name__}
