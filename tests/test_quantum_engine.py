"""Tests for the quantum engine: circuit building, probabilities, Bloch
angles, and Qiskit export.

Targets the current backend.engine.QuantumEngine (FastAPI backend layout).
"""
import math

import pytest
from qiskit.quantum_info import Statevector

from backend.core.quantum_engine import QuantumEngine


def make_bell():
    engine = QuantumEngine(num_qubits=2)
    engine.add_gate("H", 0)
    engine.add_gate("CNOT", 1, control=0)
    return engine


def test_bell_probabilities():
    engine = make_bell()
    probs = engine.get_probabilities()
    assert probs["00"] == pytest.approx(0.5, abs=1e-6)
    assert probs["11"] == pytest.approx(0.5, abs=1e-6)
    assert probs.get("01", 0.0) < 1e-9
    assert probs.get("10", 0.0) < 1e-9


def test_hadamard_qubit_zero_probability():
    engine = QuantumEngine(num_qubits=1)
    engine.add_gate("H", 0)
    # |+> has 50% chance of reading 0
    assert probs_zero(engine, 0) == pytest.approx(0.5, abs=1e-6)


def test_x_gate_flips_probability():
    engine = QuantumEngine(num_qubits=1)
    engine.add_gate("X", 0)
    # |1> never reads 0
    assert probs_zero(engine, 0) < 1e-9


def test_bell_angles_purity():
    engine = make_bell()
    angles = engine.run_simulation()
    # Each qubit alone is maximally mixed: Bloch radius ~ 0
    assert angles[0]["purity"] < 0.05
    assert angles[1]["purity"] < 0.05


def test_ry_rotation_odds():
    engine = QuantumEngine(num_qubits=1)
    engine.add_rotation("RY", 0, math.pi / 3)
    # P(0) = cos^2(pi/6) = 0.75
    assert probs_zero(engine, 0) == pytest.approx(0.75, abs=1e-4)


def test_rz_keeps_odds():
    engine = QuantumEngine(num_qubits=1)
    engine.add_gate("H", 0)
    before = probs_zero(engine, 0)
    engine.add_rotation("RZ", 0, 1.234)
    after = probs_zero(engine, 0)
    assert before == pytest.approx(after, abs=1e-9)


def test_circuit_build_matches_qiskit():
    engine = make_bell()
    qc = engine.build_circuit()
    assert qc.num_qubits == 2
    assert len(qc.data) == 2
    sv = Statevector(qc)
    assert sv.probabilities_dict()["00"] == pytest.approx(0.5, abs=1e-6)


def test_qiskit_code_export():
    engine = make_bell()
    code = engine.get_qiskit_code()
    assert "qc = QuantumCircuit(2)" in code
    assert "qc.h(0)" in code
    assert "qc.cx(0, 1)" in code


def test_clear():
    engine = make_bell()
    engine.clear()
    assert engine.gates == []
    # Empty circuit = |00>, so q0 reads 0 with certainty
    assert probs_zero(engine, 0) == pytest.approx(1.0, abs=1e-9)


def probs_zero(engine, qubit):
    """Probability that `qubit` reads 0, summed over all basis states."""
    probs = engine.get_probabilities()
    total = 0.0
    for basis, p in probs.items():
        if basis[qubit] == "0":
            total += p
    return total
