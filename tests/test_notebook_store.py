"""Tests for saving, restoring and exporting the learner's notebook."""
from frontend import notebook_store as nb
from frontend.learning_content import LESSONS


def test_sanitize_rejects_malformed_and_hostile_data():
    data = nb.sanitize({
        "completed_lessons": ["qubit", {"x": 1}, "qubit", 7],
        "quiz_answers": {"qubit": 2, "flip": "1", "bad": True, "huge": 99},
        "notes": {"qubit": "hi", "flip": 3, "blank": "   ", "long": "x" * (nb.MAX_TEXT + 50)},
        "selected_lesson": -4,
        "learning_stage": True,
        "unknown": "ignored",
    })
    assert data["completed_lessons"] == ["qubit", "7"]
    assert data["quiz_answers"] == {"qubit": 2}
    assert data["notes"]["qubit"] == "hi" and "flip" not in data["notes"] and "blank" not in data["notes"]
    assert len(data["notes"]["long"]) == nb.MAX_TEXT
    assert data["selected_lesson"] == 0 and data["learning_stage"] == 0
    assert "unknown" not in data
    assert nb.sanitize("not a dict") == nb.empty()
    assert nb.loads("{not json") == nb.empty()


def test_round_trip_through_json():
    data = nb.empty()
    data.update({"completed_lessons": ["qubit"], "notes": {"qubit": "arrow on a globe ✎"}, "selected_lesson": 3})
    assert nb.loads(nb.dumps(data)) == nb.sanitize(data)


def test_merge_keeps_saved_work_and_prefers_this_session():
    saved = nb.empty()
    saved.update({
        "completed_lessons": ["qubit", "flip"],
        "notes": {"qubit": "old note", "flip": "kept"},
        "lesson_max_stage": {"qubit": 5, "flip": 2},
        "selected_lesson": 2,
        "learning_stage": 3,
    })
    current = nb.empty()
    current.update({"completed_lessons": ["measurement"], "notes": {"qubit": "new note"}, "lesson_max_stage": {"flip": 4}})
    merged = nb.merge(current, saved)
    assert merged["completed_lessons"] == ["qubit", "flip", "measurement"]
    assert merged["notes"] == {"qubit": "new note", "flip": "kept"}
    assert merged["lesson_max_stage"] == {"qubit": 5, "flip": 4}
    # A fresh session resumes where the saved notebook left off.
    assert (merged["selected_lesson"], merged["learning_stage"]) == (2, 3)


def test_merge_keeps_position_once_the_learner_has_moved():
    saved = nb.empty()
    saved.update({"selected_lesson": 2, "learning_stage": 3})
    current = nb.empty()
    current.update({"selected_lesson": 5, "learning_stage": 1})
    merged = nb.merge(current, saved)
    assert (merged["selected_lesson"], merged["learning_stage"]) == (5, 1)


def test_apply_resets_text_widgets_so_restored_text_shows():
    state = {"task_qubit": "stale", "margin_qubit": "stale", "reflection_qubit": "stale", "other": 1}
    restored = nb.empty()
    restored["notes"] = {"qubit": "restored"}
    nb.apply(state, restored)
    assert state["notes"] == {"qubit": "restored"}
    assert not any(key.startswith(nb.WIDGET_PREFIXES) for key in state)
    assert state["other"] == 1


def test_markdown_write_up_includes_only_lessons_with_work():
    data = nb.empty()
    first = LESSONS[0]
    data.update({
        "completed_lessons": [first["id"]],
        "quiz_answers": {first["id"]: first["quiz"]["answer"]},
        "reflections": {first["id"]: "Measurement samples the arrow."},
        "code_attempts": {first["id"]: "qc = QuantumCircuit(2)"},
        "tasks_passed": [first["id"]],
    })
    text = nb.to_markdown(data, LESSONS)
    assert f"## 1. {first['title']} ✓" in text
    assert "(correct)" in text and "Measurement samples the arrow." in text
    assert "```python\nqc = QuantumCircuit(2)\n```" in text
    assert LESSONS[1]["title"] not in text


def test_reading_mode_is_validated_and_merged():
    assert nb.sanitize({"reading_mode": "<script>"})["reading_mode"] == "notebook"
    saved, current = nb.empty(), nb.empty()
    saved["reading_mode"] = "plain"
    assert nb.merge(current, saved)["reading_mode"] == "plain"  # keep the saved choice
    current["reading_mode"] = "plain"
    saved["reading_mode"] = "notebook"
    assert nb.merge(current, saved)["reading_mode"] == "plain"  # a change made now wins
