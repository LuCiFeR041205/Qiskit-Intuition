"use client";

import React, { useState, useEffect } from "react";
import { GateOp } from "@/lib/quantum_simulator";
import { quantumAudio } from "@/lib/quantum_audio";
import {
  Play,
  Pause,
  RotateCcw,
  Trash2,
  Copy,
  Check,
  Code2,
  Sparkles,
  Download,
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
  { gate: "H", name: "Hadamard", color: "bg-ink-blue text-white", desc: "Superposition |+⟩" },
  { gate: "X", name: "Pauli-X", color: "bg-ink-red text-white", desc: "Bit flip (NOT)" },
  { gate: "Y", name: "Pauli-Y", color: "bg-ink-red/80 text-white", desc: "Bit & Phase flip" },
  { gate: "Z", name: "Pauli-Z", color: "bg-ink-amber text-white", desc: "Phase flip (|1⟩ → -|1⟩)" },
  { gate: "S", name: "S Gate", color: "bg-ink-amber/80 text-ink", desc: "π/2 Phase rotation" },
  { gate: "T", name: "T Gate", color: "bg-ink-teal text-white", desc: "π/4 Universal gate" },
  { gate: "RX", name: "Rx(θ)", color: "bg-ink-light text-white", desc: "X-axis rotation" },
  { gate: "RY", name: "Ry(θ)", color: "bg-ink-light text-white", desc: "Y-axis rotation" },
  { gate: "RZ", name: "Rz(θ)", color: "bg-ink-light text-white", desc: "Z-axis rotation" },
  { gate: "CNOT", name: "CNOT", color: "bg-ink-blue/80 text-white", desc: "2-Qubit Entangler" },
  { gate: "SWAP", name: "SWAP", color: "bg-ink text-white", desc: "State Exchanger" },
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
  const [rotationAngle, setRotationAngle] = useState(0.5);
  const [copiedCode, setCopiedCode] = useState(false);
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  // Auto-play timeline animation
  useEffect(() => {
    if (!isPlaying || gates.length === 0) return;

    const timer = setInterval(() => {
      onSelectStep((activeStep + 1) % gates.length);
      const currentGate = gates[(activeStep + 1) % gates.length];
      if (currentGate) {
        quantumAudio.playGatePulse(currentGate.gate);
      }
    }, 850);

    return () => clearInterval(timer);
  }, [isPlaying, activeStep, gates, onSelectStep]);

  const handleAdd = () => {
    quantumAudio.playGatePulse(selectedGate);
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

  const handleDownload = () => {
    const blob = new Blob([qiskitCode], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "quantum_circuit_qiskit.py";
    a.click();
    URL.revokeObjectURL(url);
  };

  const maxSteps = Math.max(gates.length + 3, 8);

  return (
    <div className="paper-card w-full rounded-2xl overflow-hidden flex flex-col">
      {/* Top Header & Presets */}
      <div className="flex flex-wrap items-center justify-between px-5 py-4 border-b border-pencil/30 gap-3 bg-paper-warm">
        <h2 className="section-title text-ink m-0">Circuit Composer</h2>

        {/* Preset Experiments */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-0.5 text-xs font-mono">
          <span className="text-ink-light mr-1 text-[11px]">Lab Presets:</span>
          {["Bell State", "Superposition", "GHZ 3-Qubit", "Quantum Teleportation", "Grover"].map((p) => (
            <button
              key={p}
              onClick={() => {
                onLoadPreset(p);
                quantumAudio.playGatePulse("CNOT");
              }}
              className="ink-btn px-3 py-1 text-[11px] whitespace-nowrap"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Play/Pause Auto-Scrubber */}
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            disabled={gates.length <= 1}
            className={`ink-btn px-3 py-1.5 font-mono text-xs flex items-center gap-1.5 transition-all ${
              isPlaying
                ? "bg-ink-teal text-white border-transparent"
                : "disabled:opacity-40"
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isPlaying ? "Pause" : "Play Flow"}</span>
          </button>

          <button
            onClick={() => {
              onUndoGate();
              quantumAudio.playGatePulse("Z");
            }}
            disabled={gates.length === 0}
            className="ink-btn p-1.5 disabled:opacity-40"
            title="Undo last gate"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => {
              onResetCircuit();
              quantumAudio.playGatePulse("X");
            }}
            disabled={gates.length === 0}
            className="ink-btn p-1.5 disabled:opacity-40 hover:text-ink-red"
            title="Reset Circuit"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => setShowCodeModal(!showCodeModal)}
            className="ink-btn px-3 py-1.5 font-mono text-xs flex items-center gap-1.5"
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Python Export</span>
          </button>
        </div>
      </div>

      {/* Visual Circuit Schematic Matrix */}
      <div className="ruled-bg p-5 overflow-x-auto relative min-h-[240px]">
        {/* Time indices */}
        <div className="flex items-center ml-14 mb-4 gap-3 font-mono text-[11px] text-ink-light">
          {Array.from({ length: maxSteps }).map((_, stepIdx) => (
            <button
              key={stepIdx}
              onClick={() => {
                onSelectStep(stepIdx);
                quantumAudio.playGatePulse("S");
              }}
              className={`w-12 text-center py-1 rounded transition-all ${
                activeStep === stepIdx
                  ? "text-ink-blue font-bold border-b border-ink-blue"
                  : "hover:text-ink"
              }`}
            >
              t{stepIdx}
            </button>
          ))}
        </div>

        {/* Qubit Wires */}
        <div className="flex flex-col gap-7 relative">
          {Array.from({ length: numQubits }).map((_, q) => (
            <div key={q} className="flex items-center relative h-11">
              {/* Qubit label */}
              <div className="w-12 font-serif text-sm font-bold text-ink shrink-0 flex items-center gap-1.5">
                <span>q{q}</span>
                <span className="text-[11px] text-ink-light font-mono">
                  |0⟩
                </span>
              </div>

              {/* Wire Line */}
              <div className="flex-1 h-[1px] bg-pencil relative flex items-center gap-3 pl-2">
                {/* Gate Slots */}
                {Array.from({ length: maxSteps }).map((_, stepIdx) => {
                  const gateAtStep = gates[stepIdx];
                  const isCurrent = activeStep === stepIdx;
                  const isPast = stepIdx <= activeStep;

                  if (!gateAtStep) {
                    return (
                      <div
                        key={stepIdx}
                        onClick={() => {
                          onSelectStep(stepIdx);
                          quantumAudio.playGatePulse("S");
                        }}
                        className={`w-12 h-10 rounded-md border border-dashed border-pencil hover:border-ink cursor-pointer flex items-center justify-center transition-all bg-paper/50 ${
                          isCurrent ? "border-solid border-ink-blue bg-paper border-2" : ""
                        }`}
                      >
                        <div className="w-1 h-1 rounded-full bg-pencil/50" />
                      </div>
                    );
                  }

                  const isTarget = gateAtStep.target === q;
                  const isControl = gateAtStep.control === q;
                  const is2Qubit = gateAtStep.gate === "CNOT" || gateAtStep.gate === "SWAP";

                  if (isTarget) {
                    const gateDef = GATE_DEFINITIONS.find(g => g.gate === gateAtStep.gate);
                    return (
                      <div
                        key={stepIdx}
                        onClick={() => {
                          onSelectStep(stepIdx);
                          quantumAudio.playGatePulse(gateAtStep.gate);
                        }}
                        className={`w-12 h-10 rounded-md border border-ink/20 flex flex-col items-center justify-center font-serif text-sm cursor-pointer transition-all transform hover:scale-105 ${
                          gateDef?.color || "bg-paper text-ink"
                        } ${!isPast ? "opacity-40" : "opacity-100"} ${
                          isCurrent ? "border-2 border-ink-blue scale-105" : ""
                        }`}
                      >
                        <span>{gateAtStep.gate}</span>
                        {gateAtStep.angle !== undefined && (
                          <span className="text-[9px] font-mono font-normal">
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
                        onClick={() => {
                          onSelectStep(stepIdx);
                          quantumAudio.playGatePulse("CNOT");
                        }}
                        className={`w-12 h-10 flex items-center justify-center cursor-pointer ${
                          !isPast ? "opacity-40" : "opacity-100"
                        }`}
                      >
                        <div className="w-3 h-3 rounded-full bg-ink flex items-center justify-center">
                          {gateAtStep.gate === "SWAP" && <div className="w-1 h-1 rounded-full bg-paper" />}
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div
                      key={stepIdx}
                      onClick={() => onSelectStep(stepIdx)}
                      className="w-12 h-10 flex items-center justify-center cursor-pointer"
                    >
                      <div className="w-1 h-1 rounded-full bg-pencil/30" />
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Gate Palette Bar */}
      <div className="p-4 bg-paper-warm border-t border-pencil/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Gate Selection Chips */}
        <div className="flex flex-wrap items-center gap-2">
          {GATE_DEFINITIONS.map((def) => (
            <button
              key={def.gate}
              onClick={() => {
                setSelectedGate(def.gate);
                quantumAudio.playGatePulse(def.gate);
              }}
              className={`key-btn px-3 py-1.5 font-serif text-sm transition-all ${
                selectedGate === def.gate
                  ? "bg-ink-blue text-white border-transparent"
                  : ""
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
            <span className="text-ink-light">Target:</span>
            <select
              value={targetQubit}
              onChange={(e) => setTargetQubit(Number(e.target.value))}
              className="bg-paper border border-pencil text-ink rounded-md px-2 py-1 outline-none font-bold focus:border-ink-blue"
            >
              {Array.from({ length: numQubits }).map((_, q) => (
                <option key={q} value={q}>
                  q{q}
                </option>
              ))}
            </select>
          </div>

          {/* Control selector */}
          {(selectedGate === "CNOT" || selectedGate === "SWAP") && (
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-ink-light">Control:</span>
              <select
                value={controlQubit}
                onChange={(e) => setControlQubit(Number(e.target.value))}
                className="bg-paper border border-pencil text-ink rounded-md px-2 py-1 outline-none font-bold focus:border-ink-blue"
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

          {/* Angle Slider */}
          {(selectedGate === "RX" || selectedGate === "RY" || selectedGate === "RZ") && (
            <div className="flex items-center gap-2 text-xs font-mono bg-paper px-3 py-1 rounded-md border border-pencil">
              <span className="text-ink-light">θ:</span>
              <input
                type="range"
                min="-2"
                max="2"
                step="0.125"
                value={rotationAngle}
                onChange={(e) => setRotationAngle(Number(e.target.value))}
                className="w-24 accent-ink-blue"
              />
              <span className="text-ink font-bold">{rotationAngle}π</span>
            </div>
          )}

          {/* Add Gate CTA */}
          <button
            onClick={handleAdd}
            className="ink-btn bg-ink text-white hover:bg-ink-light hover:text-white px-5 py-2 font-mono text-xs flex items-center gap-1.5"
          >
            <Sparkles className="w-4 h-4" />
            <span>Apply {selectedGate}</span>
          </button>
        </div>
      </div>

      {/* Qiskit Code Modal */}
      {showCodeModal && (
        <div className="p-5 bg-paper-deep border-t border-pencil/30 font-mono text-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-ink font-bold flex items-center gap-2">
              <Code2 className="w-4 h-4" /> Exported Qiskit 1.0+ Python Script
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={handleDownload}
                className="ink-btn px-3 py-1 flex items-center gap-1.5"
              >
                <Download className="w-3 h-3" />
                <span>Download .py</span>
              </button>
              <button
                onClick={handleCopy}
                className="ink-btn px-3 py-1 flex items-center gap-1.5"
              >
                {copiedCode ? <Check className="w-3 h-3 text-ink-teal" /> : <Copy className="w-3 h-3" />}
                <span>{copiedCode ? "Copied" : "Copy Code"}</span>
              </button>
            </div>
          </div>
          <pre className="p-4 rounded-md bg-paper text-ink overflow-x-auto text-xs border border-pencil leading-relaxed shadow-inner">
            {qiskitCode}
          </pre>
        </div>
      )}
    </div>
  );
};
