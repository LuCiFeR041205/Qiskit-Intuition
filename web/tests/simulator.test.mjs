import assert from "node:assert";
import { simulateCircuit, calculateFidelity } from "../src/lib/quantum_simulator.js";

// Test 1: Ground state |00>
const res0 = simulateCircuit(2, []);
assert.strictEqual(res0.statevector[0].r, 1);
assert.strictEqual(res0.statevector[0].i, 0);
assert.strictEqual(res0.blochAngles[0].z, 1);
console.log("✓ Test 1 Passed: Ground state |00> is exact");

// Test 2: Pauli-X gate on q0 -> |01>
const resX = simulateCircuit(2, [{ id: "1", gate: "X", target: 0 }]);
assert.strictEqual(Math.round(resX.statevector[1].r), 1);
assert.strictEqual(resX.blochAngles[0].z, -1);
console.log("✓ Test 2 Passed: Pauli-X flips qubit 0 to |1> with z = -1");

// Test 3: Hadamard on q0 -> 1/sqrt(2) (|00> + |01>)
const resH = simulateCircuit(2, [{ id: "2", gate: "H", target: 0 }]);
assert.ok(Math.abs(resH.statevector[0].r - Math.SQRT1_2) < 1e-5);
assert.ok(Math.abs(resH.statevector[1].r - Math.SQRT1_2) < 1e-5);
assert.ok(Math.abs(resH.blochAngles[0].x - 1) < 1e-5);
console.log("✓ Test 3 Passed: Hadamard creates maximum X-axis superposition");

// Test 4: Bell State (H on q0, CNOT 0->1) -> 1/sqrt(2) (|00> + |11>)
const resBell = simulateCircuit(2, [
  { id: "1", gate: "H", target: 0 },
  { id: "2", gate: "CNOT", target: 1, control: 0 },
]);
assert.ok(Math.abs(resBell.statevector[0].r - Math.SQRT1_2) < 1e-5);
assert.ok(Math.abs(resBell.statevector[3].r - Math.SQRT1_2) < 1e-5);
assert.ok(resBell.blochAngles[0].purity < 0.01); // Maximally mixed subsystem
assert.ok(resBell.blochAngles[1].purity < 0.01);
console.log("✓ Test 4 Passed: Bell state entanglement exhibits zero subsystem purity");

// Test 5: Target Fidelity calculation
const fidelity = calculateFidelity(resBell.statevector, [Math.SQRT1_2, 0, 0, Math.SQRT1_2]);
assert.ok(Math.abs(fidelity - 1.0) < 1e-5);
console.log("✓ Test 5 Passed: Quantum fidelity calculation matches 100%");

console.log("\n ALL 5 QUANTUM ENGINE SIMULATOR TESTS PASSED SUCCESSFULLY!");
