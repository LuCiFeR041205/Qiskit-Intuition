"""Instant, offline feedback on a learner's written explanation.

Each lesson can define ``key_ideas`` (what a good explanation mentions) and
``watch_for`` (common misconceptions). The reviewer checks which ideas the
text touches, names the missing ones with a hint, and flags misconceptions.
It is deliberately simple and transparent: keyword cues, not grading.
"""

from __future__ import annotations

import re


def _normalize(text: str) -> str:
    text = text.lower().replace("’", "'").replace("−", "-")
    return re.sub(r"\s+", " ", text)


def _mentions(text: str, terms: list[str]) -> bool:
    """True if any cue appears. Cues of one or two letters (like "h" for the
    Hadamard gate) must stand alone as words; longer cues match inside words
    ("interfer" matches "interference")."""
    for term in terms:
        term = term.lower().strip()
        if not term:
            continue
        if len(term) <= 2 and term.isalnum():
            if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text):
                return True
        elif term in text:
            return True
    return False


def review_explanation(text: str, lesson: dict) -> dict:
    """Return {"covered", "missing", "flags", "markdown"} for ``text``."""
    body = _normalize(text or "")
    ideas = lesson.get("key_ideas", [])
    covered = [idea for idea in ideas if _mentions(body, idea["terms"])]
    missing = [idea for idea in ideas if idea not in covered]
    flags = [item for item in lesson.get("watch_for", []) if _mentions(body, item["terms"])]

    lines: list[str] = []
    if not body.strip():
        lines.append("Write a few sentences first — then I can tell you what's there and what's missing.")
    elif not ideas:
        lines.append("Good — now check your explanation against the experiment: does each claim match what you saw?")
    else:
        lines.append(f"**You touched {len(covered)} of {len(ideas)} key ideas.**")
        for idea in covered:
            lines.append(f"- ✓ {idea['idea']}")
        if missing:
            lines.append("")
            lines.append("**Worth adding:**")
            for idea in missing:
                lines.append(f"- {idea['idea']} — {idea['hint']}")
        else:
            lines.append("")
            lines.append("That covers the essentials. Can you point to the exact bar, arrow or amplitude that shows each one?")
    if flags:
        lines.append("")
        lines.append("**Watch out:**")
        for item in flags:
            note = item["note"]
            lines.append(f"- {note[:1].upper()}{note[1:]}")
    return {"covered": covered, "missing": missing, "flags": flags, "markdown": "\n".join(lines)}
