"""Tests for the quest (challenge) system in the new backend layout.

The new app grades quests by statevector fidelity against a target_state
(see backend.core.quest_engine). These tests confirm every quest has a
reachable target and that the engine + fidelity helper agree.
"""
import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from backend.core.quantum_engine import QuantumEngine
from backend.core.quest_engine import calculate_fidelity, get_quests


def build(*gates, num_qubits=2):
    engine = QuantumEngine(num_qubits=num_qubits)
    for gate in gates:
        name, target = gate[0], gate[1]
        control = gate[2] if len(gate) > 2 else None
        engine.add_gate(name, target, control=control)
    return engine


def engine_statevector(engine):
    return engine.get_statevector().data


def test_all_quest_targets_unit_norm():
    for quest in get_quests():
        target = np.array(quest["target_state"], dtype=complex)
        assert np.linalg.norm(target) == pytest.approx(1.0, abs=1e-6), (
            f"{quest['id']} target_state is not normalized"
        )


def test_quest_q1_reachable_with_x():
    quest = get_quests()[0]  # flip q0 to |1>
    engine = build(("X", 0), num_qubits=2)
    fid = calculate_fidelity(engine_statevector(engine), quest["target_state"])
    assert fid > 0.99


def test_quest_q2_reachable_with_h():
    quest = get_quests()[1]  # superposition on q0
    engine = build(("H", 0), num_qubits=2)
    fid = calculate_fidelity(engine_statevector(engine), quest["target_state"])
    assert fid > 0.99


def test_quest_q3_bell_reachable():
    quest = get_quests()[2]  # Bell state
    engine = build(("H", 0), ("CNOT", 1, 0), num_qubits=2)
    fid = calculate_fidelity(engine_statevector(engine), quest["target_state"])
    assert fid > 0.99


def test_empty_circuit_fails_quests():
    engine = build(num_qubits=2)
    for quest in get_quests():
        fid = calculate_fidelity(engine_statevector(engine), quest["target_state"])
        assert fid < 0.99, f"{quest['id']} should fail on an empty circuit"


def test_fidelity_orthogonal_is_zero():
    plus = np.array([1, 1, 0, 0], dtype=complex) / np.sqrt(2)
    minus = np.array([1, -1, 0, 0], dtype=complex) / np.sqrt(2)
    assert calculate_fidelity(plus, minus) < 1e-9
