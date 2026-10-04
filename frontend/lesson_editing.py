"""Turn lesson fields into editable text for the Content Studio, and back.

Formats are plain text so authors don't need to touch Python:

* lists: one item per line (paragraphs: separated by a blank line)
* quiz options: one per line, the correct one starting with ``*``
* line-by-line notes: ``snippet | meaning``
* rubric ideas: ``idea | cue, cue, cue | hint``
* misconceptions to watch for: ``cue, cue | note``

``parse_lesson_edits`` validates everything and returns (lesson, errors);
the lesson is only meant to be saved when ``errors`` is empty.
"""

from __future__ import annotations

from copy import deepcopy

# Fields are separated by " | " with spaces, so kets like |0⟩ inside the text are safe.
SEP = " | "


def lines(text: str) -> list[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def paragraphs(text: str) -> list[str]:
    return [block.strip() for block in (text or "").split("\n\n") if block.strip()]


def quiz_to_text(quiz: dict | None) -> tuple[str, str, str]:
    """(question, options with * on the answer, explanations)."""
    quiz = quiz or {}
    options = [("*" if index == quiz.get("answer") else "") + option for index, option in enumerate(quiz.get("options", []))]
    return quiz.get("question", ""), "\n".join(options), "\n".join(quiz.get("explanations", []))


def text_to_quiz(question: str, options_text: str, explanations_text: str) -> tuple[dict | None, list[str]]:
    question = question.strip()
    raw = lines(options_text)
    if not question and not raw:
        return None, []
    errors = []
    marked = [index for index, option in enumerate(raw) if option.startswith("*")]
    options = [option.lstrip("*").strip() for option in raw]
    explanations = lines(explanations_text)
    if not question:
        errors.append("The prediction quiz needs a question.")
    if len(options) < 2:
        errors.append("The quiz needs at least two options.")
    if len(marked) != 1:
        errors.append("Mark exactly one quiz option as correct by starting it with *.")
    if len(explanations) != len(options):
        errors.append(f"Write one explanation per quiz option ({len(options)} options, {len(explanations)} explanations).")
    quiz = {"question": question, "options": options, "answer": marked[0] if marked else 0, "explanations": explanations}
    return quiz, errors


def pairs_to_text(pairs: list) -> str:
    return "\n".join(f"{a}{SEP}{b}" for a, b in pairs)


def text_to_pairs(text: str, label: str) -> tuple[list[tuple[str, str]], list[str]]:
    out, errors = [], []
    for line in lines(text):
        parts = [part.strip() for part in line.split(SEP, 1)]
        if len(parts) != 2 or not all(parts):
            errors.append(f'{label}: "{line[:40]}" should look like "snippet | meaning".')
            continue
        out.append((parts[0], parts[1]))
    return out, errors


def ideas_to_text(ideas: list[dict]) -> str:
    return "\n".join(f"{idea['idea']}{SEP}{', '.join(idea['terms'])}{SEP}{idea['hint']}" for idea in ideas)


def text_to_ideas(text: str) -> tuple[list[dict], list[str]]:
    ideas, errors = [], []
    for line in lines(text):
        parts = [part.strip() for part in line.split(SEP)]
        terms = [term.strip().lower() for term in parts[1].split(",") if term.strip()] if len(parts) == 3 else []
        if len(parts) != 3 or not parts[0] or not parts[2] or not terms:
            errors.append(f'Key idea "{line[:40]}" should look like "idea | cue, cue | hint".')
            continue
        ideas.append({"idea": parts[0], "terms": terms, "hint": parts[2]})
    return ideas, errors


def watch_to_text(items: list[dict]) -> str:
    return "\n".join(f"{', '.join(item['terms'])}{SEP}{item['note']}" for item in items)


def text_to_watch(text: str) -> tuple[list[dict], list[str]]:
    items, errors = [], []
    for line in lines(text):
        parts = [part.strip() for part in line.split(SEP, 1)]
        terms = [term.strip().lower() for term in parts[0].split(",") if term.strip()] if len(parts) == 2 else []
        if len(parts) != 2 or not terms or not parts[1]:
            errors.append(f'Misconception "{line[:40]}" should look like "cue, cue | note".')
            continue
        items.append({"terms": terms, "note": parts[1]})
    return items, errors


def parse_lesson_edits(lesson: dict, form: dict, *, presets: set[str], widget_types: set[str]) -> tuple[dict, list[str]]:
    """Apply the Content Studio form (plain strings) to a copy of ``lesson``."""
    updated = deepcopy(lesson)
    errors: list[str] = []

    title = form.get("title", "").strip()
    if not title:
        errors.append("The lesson needs a title.")
    updated.update({
        "title": title or lesson.get("title", ""),
        "eyebrow": form.get("eyebrow", "").strip(),
        "duration": form.get("duration", "").strip(),
        "summary": form.get("summary", "").strip(),
        "objectives": lines(form.get("objectives", "")),
        "intuition": paragraphs(form.get("intuition", "")),
        "explanation": paragraphs(form.get("explanation", "")),
        "latex": form.get("latex", "").strip(),
        "misconception": form.get("misconception", "").strip(),
        "checkpoint": form.get("checkpoint", "").strip(),
        "try_this": lines(form.get("try_this", "")),
    })

    preset = form.get("preset", lesson.get("preset", ""))
    if preset not in presets:
        errors.append(f'Unknown worked-example circuit "{preset}".')
    updated["preset"] = preset

    widget_type = form.get("widget_type", "")
    if widget_type:
        if widget_type not in widget_types:
            errors.append(f'Unknown widget "{widget_type}".')
        widget = dict(lesson.get("widget") or {})
        widget.update({"type": widget_type, "caption": form.get("widget_caption", "").strip()})
        updated["widget"] = widget
    else:
        updated.pop("widget", None)

    quiz, quiz_errors = text_to_quiz(form.get("quiz_question", ""), form.get("quiz_options", ""), form.get("quiz_explanations", ""))
    errors += quiz_errors
    if quiz:
        updated["quiz"] = quiz
    else:
        updated.pop("quiz", None)

    if form.get("qiskit_code", "").strip():
        notes, note_errors = text_to_pairs(form.get("qiskit_notes", ""), "Line-by-line note")
        errors += note_errors
        qiskit = dict(lesson.get("qiskit") or {})
        qiskit.update({"intro": form.get("qiskit_intro", "").strip(), "code": form["qiskit_code"].rstrip() + "\n", "notes": notes})
        updated["qiskit"] = qiskit
    else:
        updated.pop("qiskit", None)

    if form.get("task_prompt", "").strip():
        if not form.get("task_solution", "").strip():
            errors.append("The coding exercise needs a reference solution that leaves its circuit in `qc`.")
        task = dict(lesson.get("code_task") or {})
        task.update({
            "prompt": form["task_prompt"].strip(),
            "starter": form.get("task_starter", "").rstrip() + "\n",
            "solution": form.get("task_solution", "").rstrip() + "\n",
            "hint": form.get("task_hint", "").strip(),
            "match": form.get("task_match", "state"),
            "required_ops": [op.strip().lower() for op in form.get("task_required_ops", "").split(",") if op.strip()],
        })
        updated["code_task"] = task
    else:
        updated.pop("code_task", None)

    ideas, idea_errors = text_to_ideas(form.get("key_ideas", ""))
    watch, watch_errors = text_to_watch(form.get("watch_for", ""))
    errors += idea_errors + watch_errors
    updated["key_ideas"], updated["watch_for"] = ideas, watch
    return updated, errors
