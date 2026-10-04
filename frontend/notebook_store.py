"""Keep a learner's notebook between visits.

Everything a learner produces — progress, predictions, margin notes,
explanations, exercise code — lives in ``st.session_state`` while they work.
This module turns that into a small JSON "notebook" and:

* saves it automatically to the browser's localStorage through a tiny
  component (plain HTML/JS in ``notebook_storage/``, no build step), and
* lets the learner download / upload it as a file, which also works where a
  browser blocks storage inside an embedded page.

The pure helpers (``snapshot``, ``sanitize``, ``merge``) are unit-tested.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

VERSION = 1
MAX_TEXT = 20_000
MAX_ENTRIES = 200

LIST_FIELDS = ("completed_lessons", "tasks_passed")
TEXT_FIELDS = ("notes", "reflections", "code_attempts")
# Text widgets whose contents are mirrored into the notebook dicts above.
WIDGET_PREFIXES = ("task_", "reflection_", "margin_")

_storage = components.declare_component(
    "notebook_storage", path=str(Path(__file__).with_name("notebook_storage"))
)


def empty() -> dict[str, Any]:
    return {
        "version": VERSION,
        "completed_lessons": [],
        "tasks_passed": [],
        "quiz_answers": {},
        "lesson_max_stage": {},
        "notes": {},
        "reflections": {},
        "code_attempts": {},
        "selected_lesson": 0,
        "learning_stage": 0,
    }


def snapshot(state) -> dict[str, Any]:
    """Collect the persistent parts of the session into a notebook dict."""
    data = empty()
    for field in data:
        if field != "version" and field in state:
            data[field] = state[field]
    return sanitize(data)


def _ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item)[:80] for item in value if isinstance(item, (str, int))))[:MAX_ENTRIES]


def _int_map(value: Any, low: int, high: int) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    out = {}
    for key, item in list(value.items())[:MAX_ENTRIES]:
        if isinstance(item, int) and not isinstance(item, bool) and low <= item <= high:
            out[str(key)[:80]] = item
    return out


def _text_map(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key)[:80]: item[:MAX_TEXT]
        for key, item in list(value.items())[:MAX_ENTRIES]
        if isinstance(item, str) and item.strip()
    }


def _bounded_int(value: Any, low: int, high: int) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and low <= value <= high else low


def sanitize(data: Any) -> dict[str, Any]:
    """Coerce untrusted notebook data (from storage or an upload) into a safe shape."""
    if not isinstance(data, dict):
        return empty()
    clean = empty()
    for field in LIST_FIELDS:
        clean[field] = _ids(data.get(field))
    clean["quiz_answers"] = _int_map(data.get("quiz_answers"), 0, 20)
    clean["lesson_max_stage"] = _int_map(data.get("lesson_max_stage"), 0, 10)
    for field in TEXT_FIELDS:
        clean[field] = _text_map(data.get(field))
    clean["selected_lesson"] = _bounded_int(data.get("selected_lesson"), 0, 500)
    clean["learning_stage"] = _bounded_int(data.get("learning_stage"), 0, 10)
    return clean


def merge(current: dict[str, Any], saved: dict[str, Any]) -> dict[str, Any]:
    """Combine a saved notebook with work done in this session.

    Completed work is unioned; for text and answers, what the learner typed in
    this session wins; position comes from the saved notebook unless this
    session has already moved on from the start.
    """
    current, saved = sanitize(current), sanitize(saved)
    merged = empty()
    for field in LIST_FIELDS:
        merged[field] = list(dict.fromkeys([*saved[field], *current[field]]))
    for field in ("quiz_answers", *TEXT_FIELDS):
        merged[field] = {**saved[field], **current[field]}
    stages = dict(saved["lesson_max_stage"])
    for key, stage in current["lesson_max_stage"].items():
        stages[key] = max(stage, stages.get(key, 0))
    merged["lesson_max_stage"] = stages
    fresh = current["selected_lesson"] == 0 and current["learning_stage"] == 0
    source = saved if fresh else current
    merged["selected_lesson"] = source["selected_lesson"]
    merged["learning_stage"] = source["learning_stage"]
    return merged


def apply(state, data: dict[str, Any]) -> None:
    """Load a notebook into the session, resetting text widgets so they show it."""
    for field, value in sanitize(data).items():
        if field != "version":
            state[field] = value
    for key in [key for key in state.keys() if str(key).startswith(WIDGET_PREFIXES)]:
        del state[key]


def has_entry(data: dict[str, Any], lesson_id: str) -> bool:
    return any(
        lesson_id in data[field]
        for field in ("completed_lessons", "tasks_passed", "quiz_answers", *TEXT_FIELDS)
    )


def to_markdown(data: dict[str, Any], lessons: list[dict]) -> str:
    """A readable write-up of the notebook, for sharing or printing."""
    data = sanitize(data)
    lines = ["# My quantum computing lab notebook", ""]
    done = len(set(data["completed_lessons"]) & {lesson["id"] for lesson in lessons})
    lines += [f"Lessons completed: {done} of {len(lessons)}", ""]
    for index, lesson in enumerate(lessons, start=1):
        lesson_id = lesson["id"]
        if not has_entry(data, lesson_id):
            continue
        status = " ✓" if lesson_id in data["completed_lessons"] else ""
        lines += [f"## {index}. {lesson['title']}{status}", ""]
        quiz = lesson.get("quiz")
        answer = data["quiz_answers"].get(lesson_id)
        if quiz and answer is not None and answer < len(quiz["options"]):
            verdict = "correct" if answer == quiz["answer"] else "not quite"
            lines += [f"**Prediction:** {quiz['options'][answer]} ({verdict})", ""]
        if lesson_id in data["reflections"]:
            lines += ["**My explanation:**", "", data["reflections"][lesson_id], ""]
        if lesson_id in data["notes"]:
            lines += ["**Margin notes:**", "", data["notes"][lesson_id], ""]
        if lesson_id in data["code_attempts"]:
            solved = " (solved)" if lesson_id in data["tasks_passed"] else ""
            lines += [f"**My code{solved}:**", "", "```python", data["code_attempts"][lesson_id].rstrip(), "```", ""]
    return "\n".join(lines).rstrip() + "\n"


def dumps(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1)


def loads(text: str) -> dict[str, Any]:
    try:
        return sanitize(json.loads(text))
    except (TypeError, ValueError):
        return empty()


def sync_browser_storage() -> None:
    """Restore the notebook from localStorage once, then keep it saved.

    Call once per run, after the page has rendered, so the save includes this
    run's changes. The first call returns nothing until the browser answers;
    the answer arrives as a rerun.
    """
    state = st.session_state
    with st.container(key="nb-storage"):
        if not state.get("nb_hydrated"):
            stored = _storage(action="load", key="nb_storage_load", default=None)
            if stored is None:
                return
            state.nb_hydrated = True
            state.nb_storage_ok = stored != "__unavailable__"
            if state.nb_storage_ok and stored:
                apply(state, merge(snapshot(state), loads(stored)))
                state.nb_restored = True
                st.rerun()
            return
        if state.get("nb_storage_ok"):
            _storage(action="save", data=dumps(snapshot(state)), key="nb_storage_save", default=None)
