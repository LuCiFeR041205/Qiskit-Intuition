// Small, dependency-free statevector simulator for the interactive web client.

const C = (r = 0, i = 0) => ({ r, i });
const add = (a, b) => C(a.r + b.r, a.i + b.i);
const mul = (a, b) => C(a.r * b.r - a.i * b.i, a.r * b.i + a.i * b.r);
const conj = (a) => C(a.r, -a.i);
export const cAbs2 = (a) => a.r * a.r + a.i * a.i;

function applySingleQubit(state, qubit, matrix) {
  const next = state.map((amp) => C(amp.r, amp.i));
  const mask = 1 << qubit;
  for (let base = 0; base < state.length; base += 1) {
    if ((base & mask) !== 0) continue;
    const paired = base | mask;
    next[base] = add(mul(matrix[0][0], state[base]), mul(matrix[0][1], state[paired]));
    next[paired] = add(mul(matrix[1][0], state[base]), mul(matrix[1][1], state[paired]));
  }
  return next;
}

function applyCnot(state, control, target) {
  if (control === target) return state;
  const next = state.map((amp) => C(amp.r, amp.i));
  const controlMask = 1 << control;
  const targetMask = 1 << target;
  for (let index = 0; index < state.length; index += 1) {
    if ((index & controlMask) !== 0 && (index & targetMask) === 0) {
      const paired = index | targetMask;
      next[index] = C(state[paired].r, state[paired].i);
      next[paired] = C(state[index].r, state[index].i);
    }
  }
  return next;
}

function gateMatrix(gate, angle = Math.PI / 2) {
  const inv = Math.SQRT1_2;
  switch (gate) {
    case "H": return [[C(inv), C(inv)], [C(inv), C(-inv)]];
    case "X": return [[C(), C(1)], [C(1), C()]];
    case "Y": return [[C(), C(0, -1)], [C(0, 1), C()]];
    case "Z": return [[C(1), C()], [C(), C(-1)]];
    case "S": return [[C(1), C()], [C(), C(0, 1)]];
    case "T": return [[C(1), C()], [C(), C(Math.cos(Math.PI / 4), Math.sin(Math.PI / 4))]];
    case "RX": {
      const half = angle / 2;
      return [[C(Math.cos(half)), C(0, -Math.sin(half))], [C(0, -Math.sin(half)), C(Math.cos(half))]];
    }
    case "RY": {
      const half = angle / 2;
      return [[C(Math.cos(half)), C(-Math.sin(half))], [C(Math.sin(half)), C(Math.cos(half))]];
    }
    case "RZ": {
      const half = angle / 2;
      return [
        [C(Math.cos(half), -Math.sin(half)), C()],
        [C(), C(Math.cos(half), Math.sin(half))],
      ];
    }
    default: return [[C(1), C()], [C(), C(1)]];
  }
}

function blochForQubit(state, qubit) {
  const mask = 1 << qubit;
  let p0 = 0;
  let p1 = 0;
  let rho01 = C();
  for (let base = 0; base < state.length; base += 1) {
    if ((base & mask) !== 0) continue;
    const paired = base | mask;
    p0 += cAbs2(state[base]);
    p1 += cAbs2(state[paired]);
    rho01 = add(rho01, mul(state[base], conj(state[paired])));
  }
  const x = 2 * rho01.r;
  const y = -2 * rho01.i;
  const z = p0 - p1;
  const purity = Math.sqrt(x * x + y * y + z * z);
  const theta = purity < 1e-10 ? 0 : Math.acos(Math.max(-1, Math.min(1, z / purity)));
  const phiRaw = Math.atan2(y, x);
  return { x, y, z, purity, theta, phi: phiRaw < 0 ? phiRaw + 2 * Math.PI : phiRaw };
}

function qiskitCode(numQubits, gates) {
  const lines = [
    "from qiskit import QuantumCircuit",
    "from qiskit.quantum_info import Statevector",
    "",
    `qc = QuantumCircuit(${numQubits})`,
  ];
  for (const operation of gates) {
    const gate = operation.gate.toUpperCase();
    if (["H", "X", "Y", "Z", "S", "T"].includes(gate)) {
      lines.push(`qc.${gate.toLowerCase()}(${operation.target})`);
    } else if (["RX", "RY", "RZ"].includes(gate)) {
      lines.push(`qc.${gate.toLowerCase()}(${(operation.angle ?? Math.PI / 2).toFixed(6)}, ${operation.target})`);
    } else if (gate === "CNOT") {
      lines.push(`qc.cx(${operation.control ?? 0}, ${operation.target})`);
    }
  }
  lines.push("", "state = Statevector.from_instruction(qc)", "print(qc.draw(output='text'))", "print(state.probabilities_dict())");
  return lines.join("\n");
}

export function simulateCircuit(numQubits, gates, _noisy = false) {
  const size = 1 << numQubits;
  let statevector = Array.from({ length: size }, (_, index) => C(index === 0 ? 1 : 0));

  for (const operation of gates) {
    const gate = String(operation.gate).toUpperCase();
    if (gate === "CNOT") {
      statevector = applyCnot(statevector, operation.control ?? Math.max(0, 1 - operation.target), operation.target);
    } else {
      statevector = applySingleQubit(statevector, operation.target, gateMatrix(gate, operation.angle));
    }
  }

  const blochAngles = {};
  for (let q = 0; q < numQubits; q += 1) blochAngles[q] = blochForQubit(statevector, q);
  return { statevector, blochAngles, qiskitCode: qiskitCode(numQubits, gates) };
}

export function calculateFidelity(state, target) {
  let overlap = C();
  const size = Math.max(state.length, target.length);
  for (let index = 0; index < size; index += 1) {
    const actual = state[index] ?? C();
    const expectedValue = target[index] ?? 0;
    const expected = typeof expectedValue === "number" ? C(expectedValue) : expectedValue;
    overlap = add(overlap, mul(conj(expected), actual));
  }
  return cAbs2(overlap);
}
