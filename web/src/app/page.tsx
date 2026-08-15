"use client";

import React, { useState, useMemo } from "react";
import { HeaderHUD } from "@/components/HeaderHUD";
import { BlochSphere3D } from "@/components/BlochSphere3D";
import { WaveformOscilloscope } from "@/components/WaveformOscilloscope";
import { CircuitComposer } from "@/components/CircuitComposer";
import { SocraticCopilot } from "@/components/SocraticCopilot";
import { QuestManager } from "@/components/QuestManager";
import { GateOp, simulateCircuit, cAbs2 } from "@/lib/quantum_simulator";

export default function Home() {
  const [numQubits, setNumQubits] = useState(2);
  const [activeQubit, setActiveQubit] = useState(0);
  const [noisy, setNoisy] = useState(false);
  const [gates, setGates] = useState<GateOp[]>([
    { id: "g1", gate: "H", target: 0 },
    { id: "g2", gate: "CNOT", target: 1, control: 0 },
  ]);
  const [activeStep, setActiveStep] = useState(1); // Pointing to current end by default
  const [latestGateDesc, setLatestGateDesc] = useState<string | null>("CNOT");

  // Keep activeStep clamped to current gate count
  const effectiveStep = Math.min(activeStep, gates.length - 1);

  // Gates evaluated up to the timeline scrubber position
  const activeGates = useMemo(() => {
    if (gates.length === 0 || effectiveStep < 0) return [];
    return gates.slice(0, effectiveStep + 1);
  }, [gates, effectiveStep]);

  // Real-time quantum simulation output
  const simResult = useMemo(() => {
    return simulateCircuit(numQubits, activeGates, noisy);
  }, [numQubits, activeGates, noisy]);

  // Full circuit simulation (for export & metrics)
  const fullSimResult = useMemo(() => {
    return simulateCircuit(numQubits, gates, noisy);
  }, [numQubits, gates, noisy]);

  // Handlers
  const handleAddGate = (op: Omit<GateOp, "id">) => {
    const newOp: GateOp = {
      ...op,
      id: `gate-${Date.now()}-${Math.random()}`,
    };
    const nextGates = [...gates, newOp];
    setGates(nextGates);
    setActiveStep(nextGates.length - 1);
    setLatestGateDesc(`${op.gate} on q${op.target}`);
    setActiveQubit(op.target);
  };

  const handleRemoveGate = (id: string) => {
    const nextGates = gates.filter((g) => g.id !== id);
    setGates(nextGates);
    setActiveStep(Math.max(0, nextGates.length - 1));
  };

  const handleUndoGate = () => {
    if (gates.length === 0) return;
    const nextGates = gates.slice(0, -1);
    setGates(nextGates);
    setActiveStep(Math.max(0, nextGates.length - 1));
  };

  const handleResetCircuit = () => {
    setGates([]);
    setActiveStep(0);
    setLatestGateDesc(null);
  };

  const handleLoadPreset = (presetName: string) => {
    let presetGates: GateOp[] = [];
    let qCount = 2;

    switch (presetName) {
      case "Bell State":
        qCount = 2;
        presetGates = [
          { id: "b1", gate: "H", target: 0 },
          { id: "b2", gate: "CNOT", target: 1, control: 0 },
        ];
        break;
      case "Superposition":
        qCount = 2;
        presetGates = [
          { id: "s1", gate: "H", target: 0 },
          { id: "s2", gate: "H", target: 1 },
        ];
        break;
      case "GHZ 3-Qubit":
        qCount = 3;
        presetGates = [
          { id: "g1", gate: "H", target: 0 },
          { id: "g2", gate: "CNOT", target: 1, control: 0 },
          { id: "g3", gate: "CNOT", target: 2, control: 0 },
        ];
        break;
      case "Quantum Teleportation":
        qCount = 3;
        presetGates = [
          { id: "t1", gate: "RX", target: 0, angle: 1.2 },
          { id: "t2", gate: "H", target: 1 },
          { id: "t3", gate: "CNOT", target: 2, control: 1 },
          { id: "t4", gate: "CNOT", target: 1, control: 0 },
          { id: "t5", gate: "H", target: 0 },
        ];
        break;
      case "Grover":
        qCount = 2;
        presetGates = [
          { id: "gr1", gate: "H", target: 0 },
          { id: "gr2", gate: "H", target: 1 },
          { id: "gr3", gate: "Z", target: 1 }, // Oracle
          { id: "gr4", gate: "H", target: 0 },
          { id: "gr5", gate: "H", target: 1 },
        ];
        break;
    }

    setNumQubits(qCount);
    setGates(presetGates);
    setActiveStep(presetGates.length - 1);
    setLatestGateDesc(`Loaded Preset: ${presetName}`);
  };

  const entanglingCount = gates.filter((g) => g.gate === "CNOT" || g.gate === "SWAP").length;
  const activeBasisCount = Object.values(simResult.probabilities).filter((p) => p > 0.0001).length;

  const circuitSummaryText = gates
    .map((g) => `${g.gate} on q${g.target}${g.control !== undefined ? ` (ctrl: q${g.control})` : ""}`)
    .join(" → ");

  return (
    <div className="min-h-screen bg-background text-hud-text flex flex-col font-sans">
      {/* Top HUD Telemetry Header */}
      <HeaderHUD
        numQubits={numQubits}
        onChangeNumQubits={(n) => {
          setNumQubits(n);
          if (activeQubit >= n) setActiveQubit(n - 1);
        }}
        noisy={noisy}
        onToggleNoisy={setNoisy}
        depth={gates.length}
        entanglingLinks={entanglingCount}
        activeBasisCount={activeBasisCount}
      />

      {/* Main Laboratory Grid */}
      <main className="max-w-7xl mx-auto w-full p-4 sm:p-6 flex-1 flex flex-col gap-6">
        {/* Upper Workspace: 3D Bloch Sphere + Waveform Oscilloscope */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Left: 3D Bloch Sphere (7 Cols) */}
          <div className="lg:col-span-7 flex flex-col">
            <BlochSphere3D
              blochCoords={simResult.blochAngles}
              numQubits={numQubits}
              activeQubit={activeQubit}
              onSelectQubit={setActiveQubit}
            />
          </div>

          {/* Right: Waveform Oscilloscope & Phase Clocks (5 Cols) */}
          <div className="lg:col-span-5 flex flex-col">
            <WaveformOscilloscope
              statevector={simResult.statevector}
              numQubits={numQubits}
            />
          </div>
        </div>

        {/* Lower Workspace: Circuit Composer (8 Cols) + Copilot/Quests (4 Cols) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Circuit Composer Wire Board (7 Cols) */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <CircuitComposer
              gates={gates}
              numQubits={numQubits}
              activeStep={effectiveStep}
              onAddGate={handleAddGate}
              onRemoveGate={handleRemoveGate}
              onUndoGate={handleUndoGate}
              onResetCircuit={handleResetCircuit}
              onLoadPreset={handleLoadPreset}
              onSelectStep={setActiveStep}
              qiskitCode={fullSimResult.qiskitCode}
            />
          </div>

          {/* Right Dock: Quests & Socratic AI Copilot (5 Cols) */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            {/* Quest Objectives */}
            <QuestManager
              statevector={simResult.statevector}
              onLoadQuestRequirements={(qReq) => {
                if (numQubits < qReq) setNumQubits(qReq);
              }}
            />

            {/* Socratic AI Copilot Terminal */}
            <SocraticCopilot
              latestGate={latestGateDesc}
              activeQubit={activeQubit}
              circuitSummary={circuitSummaryText}
            />
          </div>
        </div>
      </main>

      {/* Laboratory Footer */}
      <footer className="w-full bg-surface-200/80 border-t border-hud-border/20 py-3 px-6 text-center font-mono text-[11px] text-hud-muted flex flex-wrap justify-between items-center gap-2">
        <div>
          Qiskit Intuition Lab · Physics-Inspired Quantum Visualization
        </div>
        <div className="flex items-center gap-3">
          <span className="text-quantum-cyan">Qiskit 1.0+ Compatible</span>
          <span>•</span>
          <span className="text-quantum-gold">Three.js 3D Engine</span>
          <span>•</span>
          <span className="text-quantum-green">Client Matrix Solver</span>
        </div>
      </footer>
    </div>
  );
}
