"""Integrity checks for the intuition-first curriculum content."""
import pytest

from backend.core.exercise_checker import check_code_task
from backend.core.notebook_engine import execute_notebook_code
from backend.core.quantum_engine import QuantumEngine
from frontend.intuition import WIDGETS
from frontend.learning_content import GLOSSARY, LESSONS, PRACTICE, PRESETS, UNITS


def test_lesson_ids_and_numbers_are_unique_and_ordered():
    assert len({lesson["id"] for lesson in LESSONS}) == len(LESSONS)
    assert [lesson["number"] for lesson in LESSONS] == list(range(1, len(LESSONS) + 1))


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson["id"])
def test_lesson_structure(lesson):
    assert lesson["unit"] in {unit["id"] for unit in UNITS}
    assert lesson["preset"] in PRESETS
    assert lesson["widget"]["type"] in WIDGETS
    quiz = lesson["quiz"]
    assert 0 <= quiz["answer"] < len(quiz["options"]) == len(quiz["explanations"])
    assert 0 <= lesson["practice"] < len(PRACTICE)
    for field in ("intuition", "explanation", "objectives", "try_this", "checkpoint", "misconception", "latex"):
        assert lesson[field], field


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson["id"])
def test_worked_example_runs_in_sandbox(lesson):
    result = execute_notebook_code(lesson["qiskit"]["code"])
    assert result["success"], result["error"]
    assert result["stdout"].strip()


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson["id"])
def test_code_task_solution_passes_and_starter_does_not(lesson):
    task = lesson["code_task"]
    assert check_code_task(task["solution"], task)["passed"]
    assert not check_code_task(task["starter"], task)["passed"]


@pytest.mark.parametrize("practice", PRACTICE, ids=lambda item: item["title"])
def test_practice_targets_are_reachable(practice):
    solutions = {
        "Create a fair quantum coin": "Superposition",
        "Make phase visible": "Interference",
        "Build a Bell pair": "Bell state",
        "Tilt to 25%": "Tilted (RY)",
        "Find the marked item": "Grover search (finds 11)",
        "Inspect a variational circuit": "Variational circuit",
    }
    preset = PRESETS[solutions[practice["title"]]]
    assert preset["qubits"] == practice["qubits"]
    engine = QuantumEngine(preset["qubits"])
    engine.gates = [dict(gate) for gate in preset["gates"]]
    actual = engine.get_probabilities()
    for state, probability in practice["target"].items():
        assert abs(actual.get(state, 0.0) - probability) < 0.025


def test_glossary_entries_have_picture_and_definition():
    assert all(term and picture and formal for term, picture, formal in GLOSSARY)
