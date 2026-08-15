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
  { gate: "H", name: "Hadamard", color: "bg-ink-blue/10 border-ink-blue text-ink-blue", desc: "Superposition |+⟩" },
  { gate: "X", name: "Pauli-X", color: "bg-ink-red/10 border-ink-red text-ink-red", desc: "Bit flip (NOT)" },
  { gate: "Y", name: "Pauli-Y", color: "bg-paper-warm border-pencil text-ink", desc: "Bit & Phase flip" },
  { gate: "Z", name: "Pauli-Z", color: "bg-ink-amber/10 border-ink-amber text-ink-amber", desc: "Phase flip (|1⟩ → -|1⟩)" },
  { gate: "S", name: "S Gate", color: "bg-paper-warm border-pencil text-ink", desc: "π/2 Phase rotation" },
  { gate: "T", name: "T Gate", color: "bg-ink-teal/10 border-ink-teal text-ink-teal", desc: "π/4 Universal gate" },
  { gate: "RX", name: "Rx(θ)", color: "bg-paper-warm border-pencil text-ink", desc: "X-axis rotation" },
  { gate: "RY", name: "Ry(θ)", color: "bg-paper-warm border-pencil text-ink", desc: "Y-axis rotation" },
  { gate: "RZ", name: "Rz(θ)", color: "bg-paper-warm border-pencil text-ink", desc: "Z-axis rotation" },
  { gate: "CNOT", name: "CNOT", color: "bg-paper-warm border-pencil text-ink", desc: "2-Qubit Entangler" },
  { gate: "SWAP", name: "SWAP", color: "bg-paper-warm border-pencil text-ink", desc: "State Exchanger" },
] as const;

export const CircuitComposer: React.FC<CircuitComposerProps> = ({
  gates,
  numQubits,
  activeStep,
  onAddGate,
  onRemoveGate,
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
  const [dragOverCell, setDragOverCell] = useState<{ q: number; stepIdx: number } | null>(null);

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

  const handleDragStartGate = (e: React.DragEvent, gate: string) => {
    e.dataTransfer.setData("gate", gate);
    // Optional ghost image styling could go here
  };

  const handleDragStartExistingGate = (e: React.DragEvent, gateId: string) => {
    e.dataTransfer.setData("existing_gate", gateId);
  };

  const handleDrop = (e: React.DragEvent, q: number, stepIdx: number) => {
    e.preventDefault();
    setDragOverCell(null);
    const gateName = e.dataTransfer.getData("gate") as GateOp["gate"];
    const existingGateId = e.dataTransfer.getData("existing_gate");

    if (existingGateId) {
      // Logic for reordering: remove the old one, add a new one at the end
      // (Circuit backend treats appending as adding, so we do what we can)
      const gateToMove = gates.find(g => g.id === existingGateId);
      if (gateToMove) {
        onRemoveGate(existingGateId);
        onAddGate({
          gate: gateToMove.gate,
          target: q,
          control: gateToMove.control,
          angle: gateToMove.angle,
        });
        quantumAudio.playGatePulse(gateToMove.gate);
      }
    } else if (gateName) {
      onAddGate({
        gate: gateName,
        target: q,
        control: (gateName === "CNOT" || gateName === "SWAP") ? controlQubit : undefined,
        angle: (gateName === "RX" || gateName === "RY" || gateName === "RZ") ? rotationAngle * Math.PI : undefined,
      });
      quantumAudio.playGatePulse(gateName);
    }
  };

  const maxSteps = Math.max(gates.length + 3, 8);

  return (
    <div className="paper-card w-full rounded-2xl overflow-hidden flex flex-col">
      {/* Top Header & Presets */}
      <div className="flex flex-wrap items-center justify-between px-5 py-4 border-b border-pencil/30 bg-paper-warm gap-3">
        <h2 className="section-title text-ink m-0">Circuit Composer</h2>

        {/* Preset Experiments */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-0.5 text-xs font-sans">
          <span className="text-ink-light mr-1">Presets:</span>
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
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            disabled={gates.length <= 1}
            className={`ink-btn px-3 py-1.5 font-sans text-xs flex items-center gap-1.5 transition-all ${
              isPlaying ? "bg-ink-teal text-white" : "disabled:opacity-40"
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isPlaying ? "Pause" : "Play"}</span>
          </button>

          <button
            onClick={() => {
              onUndoGate();
              quantumAudio.playGatePulse("Z");
            }}
            disabled={gates.length === 0}
            className="ink-btn p-1.5 disabled:opacity-40"
            title="Undo"
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
            title="Reset"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => setShowCodeModal(!showCodeModal)}
            className="ink-btn px-3 py-1.5 font-sans text-xs flex items-center gap-1.5"
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Code</span>
          </button>
        </div>
      </div>

      {/* Drag and Drop Gate Palette */}
      <div className="px-5 py-4 bg-paper border-b border-pencil/30 flex flex-wrap gap-2 items-center">
        <span className="text-sm font-serif text-ink mr-2">Palette:</span>
        {GATE_DEFINITIONS.map((def) => (
          <div
            key={def.gate}
            draggable="true"
            onDragStart={(e) => handleDragStartGate(e, def.gate)}
            className="key-btn px-3 py-1.5 font-mono text-sm cursor-grab active:cursor-grabbing hover:bg-paper-warm"
            title={def.desc}
          >
            {def.gate}
          </div>
        ))}
      </div>

      {/* Visual Circuit Schematic Matrix */}
      <div className="ruled-bg p-5 overflow-x-auto relative min-h-[240px]">
        {/* Time indices */}
        <div className="flex items-center ml-14 mb-4 gap-3 font-mono text-[11px] text-ink-light">
          {Array.from({ length: maxSteps }).map((_, stepIdx) => (
            <div
              key={stepIdx}
              className={`w-12 flex flex-col items-center justify-center gap-1 transition-all ${
                activeStep === stepIdx ? "text-ink-blue font-bold" : ""
              }`}
            >
              <span>t{stepIdx}</span>
              {activeStep === stepIdx && <div className="w-2 h-2 rounded-full bg-ink-blue" />}
            </div>
          ))}
        </div>

        {/* Qubit Wires */}
        <div className="flex flex-col gap-7 relative">
          {Array.from({ length: numQubits }).map((_, q) => (
            <div key={q} className="flex items-center relative h-11">
              {/* Qubit label */}
              <div className="w-12 font-serif text-sm font-bold text-ink shrink-0 flex items-center gap-1.5">
                <span>q{q}</span>
                <span className="text-[11px] text-ink-light font-mono">|0⟩</span>
              </div>

              {/* Wire Line */}
              <div className="flex-1 h-[1px] bg-pencil relative flex items-center gap-3 pl-2">
                {/* Gate Slots */}
                {Array.from({ length: maxSteps }).map((_, stepIdx) => {
                  const gateAtStep = gates[stepIdx];
                  const isCurrent = activeStep === stepIdx;
                  const isPast = stepIdx <= activeStep;
                  const isDragOver = dragOverCell?.q === q && dragOverCell?.stepIdx === stepIdx;

                  if (!gateAtStep) {
                    return (
                      <div
                        key={stepIdx}
                        onDragOver={(e) => {
                          e.preventDefault();
                          setDragOverCell({ q, stepIdx });
                        }}
                        onDragLeave={() => setDragOverCell(null)}
                        onDrop={(e) => handleDrop(e, q, stepIdx)}
                        className={`w-12 h-10 rounded-md flex items-center justify-center transition-all ${
                          isDragOver ? "border-2 border-dashed border-ink-blue bg-paper-warm/50" : "border border-transparent"
                        }`}
                      />
                    );
                  }

                  const isTarget = gateAtStep.target === q;
                  const isControl = gateAtStep.control === q;
                  const is2Qubit = gateAtStep.gate === "CNOT" || gateAtStep.gate === "SWAP";

                  // Draw vertical connection for 2-qubit gates on the control qubit
                  let verticalLine = null;
                  if (isControl && is2Qubit) {
                    const qDist = Math.abs(gateAtStep.control! - gateAtStep.target);
                    const lineLen = qDist * 72; // h-11(44) + gap-7(28) = 72px
                    const isControlAbove = gateAtStep.control! < gateAtStep.target;
                    verticalLine = (
                      <div
                        className="absolute w-[1px] bg-ink"
                        style={{
                          height: `${lineLen}px`,
                          top: isControlAbove ? '50%' : `calc(50% - ${lineLen}px)`,
                          left: '50%',
                          zIndex: 0,
                        }}
                      />
                    );
                  }

                  if (isTarget) {
                    const gateDef = GATE_DEFINITIONS.find(g => g.gate === gateAtStep.gate);
                    const boxStyle = gateDef?.color || "bg-paper-warm border-pencil text-ink";
                    const displayLabel = gateAtStep.gate === "CNOT" ? "⊕" : gateAtStep.gate === "SWAP" ? "×" : gateAtStep.gate;

                    return (
                      <div
                        key={stepIdx}
                        draggable="true"
                        onDragStart={(e) => handleDragStartExistingGate(e, gateAtStep.id)}
                        onDoubleClick={() => onRemoveGate(gateAtStep.id)}
                        onDragOver={(e) => {
                          e.preventDefault();
                          setDragOverCell({ q, stepIdx });
                        }}
                        onDragLeave={() => setDragOverCell(null)}
                        onDrop={(e) => handleDrop(e, q, stepIdx)}
                        className={`relative w-12 h-10 flex flex-col items-center justify-center cursor-grab active:cursor-grabbing transition-all animate-spring-in ${
                          isDragOver ? "border-2 border-dashed border-ink-blue bg-paper-warm/50" : ""
                        }`}
                      >
                        <div className={`w-10 h-10 flex flex-col items-center justify-center border font-mono text-sm z-10 ${boxStyle} ${!isPast ? "opacity-50" : "opacity-100"} ${isCurrent ? "border-2 border-ink-blue" : ""}`}>
                          <span>{displayLabel}</span>
                          {gateAtStep.angle !== undefined && (
                            <span className="text-[9px] font-mono font-normal">
                              {(gateAtStep.angle / Math.PI).toFixed(2)}π
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  }

                  if (isControl && is2Qubit) {
                    return (
                      <div
                        key={stepIdx}
                        onDragOver={(e) => {
                          e.preventDefault();
                          setDragOverCell({ q, stepIdx });
                        }}
                        onDragLeave={() => setDragOverCell(null)}
                        onDrop={(e) => handleDrop(e, q, stepIdx)}
                        className={`relative w-12 h-10 flex items-center justify-center ${
                          !isPast ? "opacity-50" : "opacity-100"
                        } ${isDragOver ? "border-2 border-dashed border-ink-blue bg-paper-warm/50" : ""}`}
                      >
                        {verticalLine}
                        <div className="w-3 h-3 rounded-full bg-ink flex items-center justify-center z-10 relative">
                          {gateAtStep.gate === "SWAP" && <div className="w-1 h-1 rounded-full bg-paper" />}
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div
                      key={stepIdx}
                      onDragOver={(e) => {
                        e.preventDefault();
                        setDragOverCell({ q, stepIdx });
                      }}
                      onDragLeave={() => setDragOverCell(null)}
                      onDrop={(e) => handleDrop(e, q, stepIdx)}
                      className={`w-12 h-10 flex items-center justify-center ${
                        isDragOver ? "border-2 border-dashed border-ink-blue bg-paper-warm/50" : ""
                      }`}
                    />
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Target & Control Selectors (Manual Entry) */}
      <div className="p-4 bg-paper-warm border-t border-pencil/30 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-serif text-ink">Manual Apply:</span>
          <select
            value={selectedGate}
            onChange={(e) => setSelectedGate(e.target.value as GateOp["gate"])}
            className="bg-paper border border-pencil text-ink rounded-md px-2 py-1 outline-none font-mono text-sm focus:border-ink-blue"
          >
            {GATE_DEFINITIONS.map(def => (
              <option key={def.gate} value={def.gate}>{def.gate} - {def.name}</option>
            ))}
          </select>
        </div>

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
                <option key={q} value={q}>q{q}</option>
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
                    <option key={q} value={q}>q{q}</option>
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
            className="ink-btn bg-ink-blue text-white hover:bg-ink-blue/90 px-4 py-1.5 font-sans text-sm flex items-center gap-1.5"
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
              <Code2 className="w-4 h-4" /> Exported Qiskit Script
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
                <span>{copiedCode ? "Copied" : "Copy"}</span>
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
