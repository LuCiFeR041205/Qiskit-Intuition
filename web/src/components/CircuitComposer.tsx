"use client";

import React, { useState } from "react";
import { GateOp } from "@/lib/quantum_simulator";
import {
  Play,
  RotateCcw,
  Trash2,
  Copy,
  Check,
  Code2,
  Zap,
  Sliders,
  Sparkles,
} from "lucide-react";

interface CircuitComposerProps {
  gates: GateOp[];
  numQubits: number;
  activeStep: number;
  onAddGate: (op: Omit<GateOp, "id">) => void;
  onRemoveGate: (id: string) => void;
  onUndoGate: () => void;
  onResetCircuit: () => void;
  onLoadPreset: (presetName: string) => void;
  onSelectStep: (step: number) => void;
  qiskitCode: string;
}

const GATE_DEFINITIONS = [
  { gate: "H", name: "Hadamard", color: "bg-quantum-cyan text-background", desc: "Superposition creator" },
  { gate: "X", name: "Pauli-X", color: "bg-quantum-coral text-white", desc: "Bit flip (NOT)" },
  { gate: "Y", name: "Pauli-Y", color: "bg-quantum-coral/80 text-white", desc: "Bit & phase flip" },
  { gate: "Z", name: "Pauli-Z", color: "bg-quantum-gold text-background", desc: "Phase flip (|1⟩ → -|1⟩)" },
  { gate: "S", name: "S Gate", color: "bg-amber-400 text-background", desc: "π/2 Phase rotation" },
  { gate: "T", name: "T Gate", color: "bg-quantum-green text-background", desc: "π/4 Universal gate" },
  { gate: "RX", name: "Rx(θ)", color: "bg-purple-500 text-white", desc: "X-axis rotation" },
  { gate: "RY", name: "Ry(θ)", color: "bg-purple-500 text-white", desc: "Y-axis rotation" },
  { gate: "RZ", name: "Rz(θ)", color: "bg-purple-500 text-white", desc: "Z-axis rotation" },
  { gate: "CNOT", name: "CNOT", color: "bg-sky-400 text-background", desc: "2-Qubit Entangler" },
  { gate: "SWAP", name: "SWAP", color: "bg-indigo-400 text-white", desc: "State Exchanger" },
] as const;

export const CircuitComposer: React.FC<CircuitComposerProps> = ({
  gates,
  numQubits,
  activeStep,
  onAddGate,
  onUndoGate,
  onResetCircuit,
  onLoadPreset,
  onSelectStep,
  qiskitCode,
}) => {
  const [selectedGate, setSelectedGate] = useState<GateOp["gate"]>("H");
  const [targetQubit, setTargetQubit] = useState(0);
  const [controlQubit, setControlQubit] = useState(1);
  const [rotationAngle, setRotationAngle] = useState(0.5); // multiples of pi
  const [copiedCode, setCopiedCode] = useState(false);
  const [showCodeModal, setShowCodeModal] = useState(false);

  const handleAdd = () => {
    onAddGate({
      gate: selectedGate,
      target: targetQubit,
      control: selectedGate === "CNOT" || selectedGate === "SWAP" ? controlQubit : undefined,
      angle:
        selectedGate === "RX" || selectedGate === "RY" || selectedGate === "RZ"
          ? rotationAngle * Math.PI
          : undefined,
    });
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(qiskitCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const maxSteps = Math.max(gates.length + 3, 8);

  return (
    <div className="w-full bg-gradient-to-b from-surface-100/90 to-surface-300/90 rounded-xl border border-hud-border/40 overflow-hidden shadow-2xl backdrop-blur-md flex flex-col">
      {/* Top Header & Presets Bar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-3 bg-surface-200/90 border-b border-hud-border/30 gap-3">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-quantum-cyan animate-pulse" />
          <span className="font-mono text-xs font-bold tracking-wider text-quantum-cyan uppercase">
            Quantum Circuit Timeline
          </span>
        </div>

        {/* Preset Experiments */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-0.5 text-xs font-mono">
          <span className="text-hud-muted mr-1 text-[11px]">Presets:</span>
          {["Bell State", "Superposition", "GHZ 3-Qubit", "Quantum Teleportation", "Grover"].map((p) => (
            <button
              key={p}
              onClick={() => onLoadPreset(p)}
              className="px-2.5 py-1 rounded bg-surface-50 hover:bg-quantum-cyan/20 text-hud-text hover:text-quantum-cyan border border-hud-subtle/30 text-[11px] transition-all whitespace-nowrap"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={onUndoGate}
            disabled={gates.length === 0}
            className="p-1.5 rounded bg-surface-50 hover:bg-surface-50/80 text-hud-text disabled:opacity-40 text-xs flex items-center gap-1 border border-hud-subtle/30"
            title="Undo last gate"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Undo</span>
          </button>
          <button
            onClick={onResetCircuit}
            disabled={gates.length === 0}
            className="p-1.5 rounded bg-surface-50 hover:bg-quantum-coral/20 text-hud-text hover:text-quantum-coral disabled:opacity-40 text-xs flex items-center gap-1 border border-hud-subtle/30"
            title="Reset Circuit"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>
          <button
            onClick={() => setShowCodeModal(!showCodeModal)}
            className="px-2.5 py-1.5 rounded bg-quantum-cyan text-background font-mono text-xs font-bold flex items-center gap-1.5 hover:shadow-lg hover:shadow-quantum-cyan/20 transition-all"
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Qiskit Code</span>
          </button>
        </div>
      </div>

      {/* Visual Circuit Schematic Matrix */}
      <div className="p-4 overflow-x-auto relative min-h-[220px] bg-background/40">
        {/* Time indices */}
        <div className="flex items-center ml-12 mb-3 gap-3 font-mono text-[10px] text-hud-muted">
          {Array.from({ length: maxSteps }).map((_, stepIdx) => (
            <button
              key={stepIdx}
              onClick={() => onSelectStep(stepIdx)}
              className={`w-11 text-center py-0.5 rounded transition-all ${
                activeStep === stepIdx
                  ? "bg-quantum-cyan text-background font-bold"
                  : "hover:text-quantum-cyan hover:bg-surface-50"
              }`}
            >
              t{stepIdx}
            </button>
          ))}
        </div>

        {/* Qubit Wires */}
        <div className="flex flex-col gap-6 relative">
          {Array.from({ length: numQubits }).map((_, q) => (
            <div key={q} className="flex items-center relative h-10">
              {/* Qubit wire label */}
              <div className="w-10 font-mono text-xs font-bold text-quantum-cyan shrink-0 flex items-center gap-1">
                <span>q{q}</span>
                <span className="text-[10px] text-hud-muted font-normal">|0⟩</span>
              </div>

              {/* Horizontal Wire Line */}
              <div className="flex-1 h-[1.5px] bg-quantum-cyan/25 relative flex items-center gap-3 pl-2">
                {/* Gates on wire */}
                {Array.from({ length: maxSteps }).map((_, stepIdx) => {
                  const gateAtStep = gates[stepIdx];
                  const isCurrent = activeStep === stepIdx;
                  const isPast = stepIdx <= activeStep;

                  if (!gateAtStep) {
                    return (
                      <div
                        key={stepIdx}
                        onClick={() => onSelectStep(stepIdx)}
                        className={`w-11 h-9 rounded border border-dashed border-quantum-cyan/15 hover:border-quantum-cyan/50 cursor-pointer flex items-center justify-center transition-all ${
                          isCurrent ? "bg-quantum-cyan/10 ring-1 ring-quantum-cyan" : ""
                        }`}
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-quantum-cyan/20" />
                      </div>
                    );
                  }

                  const isTarget = gateAtStep.target === q;
                  const isControl = gateAtStep.control === q;
                  const is2Qubit = gateAtStep.gate === "CNOT" || gateAtStep.gate === "SWAP";

                  if (isTarget) {
                    return (
                      <div
                        key={stepIdx}
                        onClick={() => onSelectStep(stepIdx)}
                        className={`w-11 h-9 rounded px-1 flex flex-col items-center justify-center font-mono font-bold text-xs shadow-lg cursor-pointer transition-all transform hover:scale-105 ${
                          gateAtStep.gate === "H"
                            ? "bg-quantum-cyan text-background shadow-quantum-cyan/20"
                            : gateAtStep.gate === "X"
                            ? "bg-quantum-coral text-white shadow-quantum-coral/20"
                            : gateAtStep.gate === "CNOT"
                            ? "bg-sky-400 text-background"
                            : "bg-surface-50 text-quantum-cyan border border-quantum-cyan/40"
                        } ${!isPast ? "opacity-35" : "opacity-100"} ${
                          isCurrent ? "ring-2 ring-quantum-gold ring-offset-2 ring-offset-background" : ""
                        }`}
                      >
                        <span>{gateAtStep.gate}</span>
                        {gateAtStep.angle !== undefined && (
                          <span className="text-[8px] font-normal">
                            {(gateAtStep.angle / Math.PI).toFixed(2)}π
                          </span>
                        )}
                      </div>
                    );
                  }

                  if (isControl && is2Qubit) {
                    return (
                      <div
                        key={stepIdx}
                        onClick={() => onSelectStep(stepIdx)}
                        className={`w-11 h-9 flex items-center justify-center cursor-pointer ${
                          !isPast ? "opacity-35" : "opacity-100"
                        }`}
                      >
                        <div className="w-4 h-4 rounded-full bg-quantum-cyan shadow-md shadow-quantum-cyan/50 flex items-center justify-center">
                          <div className="w-1.5 h-1.5 rounded-full bg-background" />
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div
                      key={stepIdx}
                      onClick={() => onSelectStep(stepIdx)}
                      className="w-11 h-9 flex items-center justify-center cursor-pointer"
                    >
                      <div className="w-1 h-1 rounded-full bg-quantum-cyan/20" />
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Gate Palette & Controls Bar */}
      <div className="p-4 bg-surface-200/90 border-t border-hud-border/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Gate Selection Chips */}
        <div className="flex flex-wrap items-center gap-1.5">
          {GATE_DEFINITIONS.map((def) => (
            <button
              key={def.gate}
              onClick={() => setSelectedGate(def.gate)}
              className={`px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition-all ${
                selectedGate === def.gate
                  ? `${def.color} shadow-lg scale-105 ring-2 ring-quantum-cyan/50`
                  : "bg-surface-50 text-hud-text hover:bg-surface-50/80 border border-hud-subtle/30"
              }`}
              title={def.desc}
            >
              {def.gate}
            </button>
          ))}
        </div>

        {/* Target & Control Selectors */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          {/* Target selector */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="text-hud-muted">Target:</span>
            <select
              value={targetQubit}
              onChange={(e) => setTargetQubit(Number(e.target.value))}
              className="bg-surface-300 border border-hud-subtle/50 text-quantum-cyan rounded px-2 py-1 outline-none font-bold"
            >
              {Array.from({ length: numQubits }).map((_, q) => (
                <option key={q} value={q}>
                  q{q}
                </option>
              ))}
            </select>
          </div>

          {/* Control selector for 2-qubit gates */}
          {(selectedGate === "CNOT" || selectedGate === "SWAP") && (
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-hud-muted">Control:</span>
              <select
                value={controlQubit}
                onChange={(e) => setControlQubit(Number(e.target.value))}
                className="bg-surface-300 border border-hud-subtle/50 text-quantum-gold rounded px-2 py-1 outline-none font-bold"
              >
                {Array.from({ length: numQubits })
                  .filter((_, q) => q !== targetQubit)
                  .map((_, q) => (
                    <option key={q} value={q}>
                      q{q}
                    </option>
                  ))}
              </select>
            </div>
          )}

          {/* Angle Slider for parameterized rotations */}
          {(selectedGate === "RX" || selectedGate === "RY" || selectedGate === "RZ") && (
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-hud-muted">θ:</span>
              <input
                type="range"
                min="-2"
                max="2"
                step="0.125"
                value={rotationAngle}
                onChange={(e) => setRotationAngle(Number(e.target.value))}
                className="w-24 accent-quantum-cyan"
              />
              <span className="text-quantum-gold font-bold">{rotationAngle}π</span>
            </div>
          )}

          {/* Add Gate CTA */}
          <button
            onClick={handleAdd}
            className="px-4 py-2 rounded-lg bg-quantum-green hover:bg-quantum-green/90 text-background font-mono text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-quantum-green/20 hover:scale-105 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Apply {selectedGate}</span>
          </button>
        </div>
      </div>

      {/* Qiskit Code Modal / Drawer */}
      {showCodeModal && (
        <div className="p-4 bg-surface-300 border-t border-hud-border/40 font-mono text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="text-quantum-cyan font-bold flex items-center gap-1.5">
              <Code2 className="w-4 h-4" /> Python (Qiskit 1.0+ Equivalent)
            </span>
            <button
              onClick={handleCopy}
              className="px-2.5 py-1 rounded bg-surface-50 hover:bg-surface-50/80 text-hud-text flex items-center gap-1 border border-hud-subtle/30"
            >
              {copiedCode ? <Check className="w-3 h-3 text-quantum-green" /> : <Copy className="w-3 h-3" />}
              <span>{copiedCode ? "Copied" : "Copy Code"}</span>
            </button>
          </div>
          <pre className="p-3 rounded-lg bg-background text-hud-text overflow-x-auto text-[11px] border border-hud-subtle/30">
            {qiskitCode}
          </pre>
        </div>
      )}
    </div>
  );
};
