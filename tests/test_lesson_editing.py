"""Tests for Content Studio text formats and validation."""
from frontend import lesson_editing as le
from frontend.intuition import WIDGETS
from frontend.learning_content import LESSONS, PRESETS


def form_for(lesson: dict) -> dict:
    """The form a Content Studio author would see for ``lesson``."""
    question, options, explanations = le.quiz_to_text(lesson.get("quiz"))
    qiskit, task = lesson.get("qiskit", {}), lesson.get("code_task", {})
    return {
        "title": lesson["title"], "eyebrow": lesson["eyebrow"], "duration": lesson["duration"],
        "summary": lesson["summary"], "objectives": "\n".join(lesson["objectives"]),
        "intuition": "\n\n".join(lesson["intuition"]), "explanation": "\n\n".join(lesson["explanation"]),
        "latex": lesson["latex"], "misconception": lesson["misconception"], "checkpoint": lesson["checkpoint"],
        "try_this": "\n".join(lesson["try_this"]), "preset": lesson["preset"],
        "widget_type": lesson["widget"]["type"], "widget_caption": lesson["widget"].get("caption", ""),
        "quiz_question": question, "quiz_options": options, "quiz_explanations": explanations,
        "qiskit_intro": qiskit.get("intro", ""), "qiskit_code": qiskit.get("code", ""),
        "qiskit_notes": le.pairs_to_text(qiskit.get("notes", [])),
        "task_prompt": task.get("prompt", ""), "task_starter": task.get("starter", ""),
        "task_solution": task.get("solution", ""), "task_hint": task.get("hint", ""),
        "task_match": task.get("match", "state"), "task_required_ops": ", ".join(task.get("required_ops", [])),
        "key_ideas": le.ideas_to_text(lesson["key_ideas"]), "watch_for": le.watch_to_text(lesson["watch_for"]),
    }


def parse(lesson, form):
    return le.parse_lesson_edits(lesson, form, presets=set(PRESETS), widget_types=set(WIDGETS))


def test_every_lesson_round_trips_through_the_editor_unchanged():
    for lesson in LESSONS:
        updated, errors = parse(lesson, form_for(lesson))
        assert errors == [], (lesson["id"], errors)
        for field in ("quiz", "key_ideas", "watch_for", "try_this", "intuition", "preset"):
            assert updated[field] == lesson[field], (lesson["id"], field)
        assert [tuple(n) for n in updated["qiskit"]["notes"]] == [tuple(n) for n in lesson["qiskit"]["notes"]]
        assert updated["code_task"]["solution"].strip() == lesson["code_task"]["solution"].strip()


def test_quiz_validation_catches_author_mistakes():
    _, errors = le.text_to_quiz("Q?", "A\nB", "why A")
    assert any("Mark exactly one" in e for e in errors)
    assert any("one explanation per quiz option" in e for e in errors)
    quiz, errors = le.text_to_quiz("Q?", "A\n*B", "no\nyes")
    assert errors == [] and quiz["answer"] == 1 and quiz["options"] == ["A", "B"]


def test_rubric_lines_are_parsed_and_lower_cased():
    ideas, errors = le.text_to_ideas("Mentions shots | Shot, Repeat | use many shots\nbroken line")
    assert ideas == [{"idea": "Mentions shots", "terms": ["shot", "repeat"], "hint": "use many shots"}]
    assert len(errors) == 1


def test_unknown_preset_and_missing_title_are_rejected():
    lesson = LESSONS[0]
    form = form_for(lesson)
    form.update({"title": "  ", "preset": "No such circuit"})
    _, errors = parse(lesson, form)
    assert any("title" in e for e in errors) and any("No such circuit" in e for e in errors)
