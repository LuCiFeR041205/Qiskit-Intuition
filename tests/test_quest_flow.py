"""Integration test for the quest progression flow using the real engine.

The new frontend (frontend/streamlit_app.py) renders quests and checks
fidelity via backend.core.quest_engine. This test exercises that same
pipeline in-process so regressions in the engine or quest targets surface
without a browser.
"""
import numpy as np
import pytest

from backend.core.quantum_engine import QuantumEngine
from backend.core.quest_engine import calculate_fidelity, get_quests, render_quest_tab


def engine_for(gates, num_qubits=2):
    engine = QuantumEngine(num_qubits=num_qubits)
    for name, target, *rest in gates:
        control = rest[0] if rest else None
        engine.add_gate(name, target, control=control)
    return engine


QUEST_SOLUTIONS = {
    "q1": [("X", 0)],
    "q2": [("H", 0)],
    "q3": [("H", 0), ("CNOT", 1, 0)],
}


@pytest.mark.parametrize("quest", get_quests(), ids=lambda q: q["id"])
def test_quest_solution_reaches_target(quest):
    engine = engine_for(QUEST_SOLUTIONS[quest["id"]])
    fid = calculate_fidelity(engine.get_statevector().data, quest["target_state"])
    assert fid > 0.99, f"{quest['id']} solution should reach target (fid={fid:.3f})"


def test_quest_progression_order():
    quests = get_quests()
    assert [q["id"] for q in quests] == ["q1", "q2", "q3"]
    # Each subsequent quest needs the same 2-qubit engine contract
    for q in quests:
        assert len(q["target_state"]) == 4  # 2 qubits -> 4 basis amplitudes


def test_render_quest_tab_runs_with_engine():
    # render_quest_tab uses st.session_state; call it only to ensure it imports
    # and the module wires up. Full UI is covered by the app boot check.
    assert callable(render_quest_tab)
