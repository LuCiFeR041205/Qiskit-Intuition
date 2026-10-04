"""Headless smoke test of the Streamlit app across many reruns.

Regression test for a segfault in Qiskit's Rust extension when Streamlit ran
Qiskit from a fresh thread on each rerun (see backend/core/qiskit_thread.py).
Before the fix this process crashed on the second rerun that built a circuit.
"""
from pathlib import Path

import pytest

from frontend.learning_content import LESSONS

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
APP = str(Path(__file__).resolve().parents[1] / "app.py")


def _run(at):
    at.run()
    assert not at.exception, at.exception
    return at


def test_every_lesson_stage_renders_across_reruns():
    at = _run(AppTest.from_file(APP, default_timeout=90))
    for index, lesson in enumerate(LESSONS):
        at.session_state["selected_lesson"] = index
        at.session_state["pending_nav"] = "Learning path"
        for stage in range(6):
            at.session_state["learning_stage"] = stage
            if stage == 2:
                at.session_state["num_qubits"] = 2
                at.session_state["gates"] = [
                    {"gate": "H", "target": 0, "control": None},
                    {"gate": "CNOT", "target": 1, "control": 0},
                ]
            _run(at)
        assert at.title[0].value == lesson["title"]


def test_playground_and_notebook_pages_render():
    at = _run(AppTest.from_file(APP, default_timeout=90))
    for page in ["Playground", "My notebook", "Course map"]:
        at.session_state["pending_nav"] = page
        _run(at)


def test_easy_read_mode_renders_lessons():
    at = _run(AppTest.from_file(APP, default_timeout=90))
    at.session_state["reading_mode"] = "plain"
    at.session_state["pending_nav"] = "Learning path"
    for stage in (0, 2, 4):
        at.session_state["learning_stage"] = stage
        _run(at)
    assert any("Atkinson Hyperlegible" in block.value for block in at.markdown)
