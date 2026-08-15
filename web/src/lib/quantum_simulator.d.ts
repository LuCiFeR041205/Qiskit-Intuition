export type Complex = { r: number; i: number };
export type GateName = "H" | "X" | "Y" | "Z" | "S" | "T" | "RX" | "RY" | "RZ" | "CNOT";
export type GateOp = { id: string; gate: GateName; target: number; control?: number; angle?: number };
export type BlochReadout = { x: number; y: number; z: number; purity: number; theta: number; phi: number };
export type SimulationResult = {
  statevector: Complex[];
  blochAngles: Record<number, BlochReadout>;
  qiskitCode: string;
};

export function cAbs2(value: Complex): number;
export function simulateCircuit(numQubits: number, gates: GateOp[], noisy?: boolean): SimulationResult;
export function calculateFidelity(state: Complex[], target: Array<number | Complex>): number;
