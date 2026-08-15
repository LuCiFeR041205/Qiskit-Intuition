"use client";

import React, { useState, useMemo } from "react";
import { BlochSphere3D } from "@/components/BlochSphere3D";
import { WaveformOscilloscope } from "@/components/WaveformOscilloscope";
import { CircuitComposer } from "@/components/CircuitComposer";
import { SocraticCopilot } from "@/components/SocraticCopilot";
import { QuestManager } from "@/components/QuestManager";
import { GateOp, simulateCircuit, cAbs2 } from "@/lib/quantum_simulator";
import {
  Atom,
  BookOpen,
  Compass,
  CircuitBoard,
  FlaskConical,
  Library,
  Volume2,
  VolumeX,
  CloudLightning,
} from "lucide-react";
import { quantumAudio } from "@/lib/quantum_audio";

type TabId = "intro" | "qubits" | "gates" | "algorithms" | "resources";

const NAV_ITEMS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: "intro", label: "Introduction", icon: <BookOpen className="sidebar-link-icon" /> },
  { id: "qubits", label: "Qubits & States", icon: <Compass className="sidebar-link-icon" /> },
  { id: "gates", label: "Gates & Circuits", icon: <CircuitBoard className="sidebar-link-icon" /> },
  { id: "algorithms", label: "Algorithms", icon: <FlaskConical className="sidebar-link-icon" /> },
  { id: "resources", label: "Resources", icon: <Library className="sidebar-link-icon" /> },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabId>("intro");
  const [numQubits, setNumQubits] = useState(2);
  const [activeQubit, setActiveQubit] = useState(0);
  const [noisy, setNoisy] = useState(false);
  const [gates, setGates] = useState<GateOp[]>([
    { id: "g1", gate: "H", target: 0 },
    { id: "g2", gate: "CNOT", target: 1, control: 0 },
  ]);
  const [activeStep, setActiveStep] = useState(1);
  const [latestGateDesc, setLatestGateDesc] = useState<string | null>("CNOT");
  const [muted, setMuted] = useState(true);

  const effectiveStep = Math.min(activeStep, gates.length - 1);

  const activeGates = useMemo(() => {
    if (gates.length === 0 || effectiveStep < 0) return [];
    return gates.slice(0, effectiveStep + 1);
  }, [gates, effectiveStep]);

  const simResult = useMemo(() => {
    return simulateCircuit(numQubits, activeGates, noisy);
  }, [numQubits, activeGates, noisy]);

  const fullSimResult = useMemo(() => {
    return simulateCircuit(numQubits, gates, noisy);
  }, [numQubits, gates, noisy]);

  const handleAddGate = (op: Omit<GateOp, "id">) => {
    const newOp: GateOp = { ...op, id: `gate-${Date.now()}-${Math.random()}` };
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
          { id: "gr3", gate: "Z", target: 1 },
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

  const circuitSummaryText = gates
    .map((g) => `${g.gate} on q${g.target}${g.control !== undefined ? ` (ctrl: q${g.control})` : ""}`)
    .join(" → ");

  const handleToggleMute = () => {
    const next = quantumAudio.toggleMute();
    setMuted(next);
  };

  return (
    <div className="notebook-shell">
      {/* ─── Left Sidebar (from concept) ─── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Atom className="sidebar-brand-icon" />
          <span className="sidebar-brand-text">Qiskit Intuition</span>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`sidebar-link ${activeTab === item.id ? "active" : ""}`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Sidebar Controls */}
        <div className="px-3 py-2 border-t border-paper-ruled space-y-2">
          {/* Qubit Count */}
          <div className="flex items-center justify-between text-xs font-sans">
            <span className="text-ink-faint">Qubits</span>
            <div className="flex gap-1">
              {[1, 2, 3, 4].map((n) => (
                <button
                  key={n}
                  onClick={() => {
                    setNumQubits(n);
                    if (activeQubit >= n) setActiveQubit(n - 1);
                  }}
                  className={`w-6 h-6 rounded text-xs font-mono font-bold transition-all ${
                    numQubits === n
                      ? "bg-ink-blue text-white"
                      : "bg-paper text-ink-light border border-paper-ruled hover:bg-paper-warm"
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* Noise Toggle */}
          <button
            onClick={() => setNoisy(!noisy)}
            className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-xs font-sans transition-all border ${
              noisy
                ? "bg-ink-red/10 border-ink-red/30 text-ink-red"
                : "bg-paper border-paper-ruled text-ink-light hover:bg-paper-warm"
            }`}
          >
            <span className="flex items-center gap-1.5">
              <CloudLightning className="w-3.5 h-3.5" />
              Decoherence
            </span>
            <span className="font-mono font-bold text-[10px]">{noisy ? "ON" : "OFF"}</span>
          </button>

          {/* Audio Toggle */}
          <button
            onClick={handleToggleMute}
            className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs font-sans bg-paper border border-paper-ruled text-ink-light hover:bg-paper-warm transition-all"
          >
            <span className="flex items-center gap-1.5">
              {muted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
              Sound
            </span>
            <span className="font-mono font-bold text-[10px]">{muted ? "OFF" : "ON"}</span>
          </button>
        </div>

        <div className="sidebar-footer">
          Qiskit 1.0+ · Three.js · v2.0
        </div>
      </aside>

      {/* ─── Main Notebook Content ─── */}
      <div className="notebook-content">
        {/* Page Title (like the concept) */}
        <h1 className="notebook-page-title">Qiskit Intuition</h1>
        <p className="notebook-page-subtitle">
          Interactive quantum mechanics laboratory — explore superposition, entanglement, and interference through real-time simulation.
        </p>

        {/* Content Grid matching concept layout */}
        <div className="flex-1 px-4 sm:px-6 pb-6 flex flex-col gap-5">

          {/* Top Row: Bloch Sphere (left) + Circuit & State Vector (middle) + Waveform (right) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">

            {/* Bloch Sphere — takes left ~5 cols */}
            <div className="lg:col-span-5">
              <BlochSphere3D
                blochCoords={simResult.blochAngles}
                numQubits={numQubits}
                activeQubit={activeQubit}
                onSelectQubit={setActiveQubit}
              />
            </div>

            {/* Circuit + State Vector — middle ~4 cols */}
            <div className="lg:col-span-4 flex flex-col gap-5">
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

            {/* Waveform Analysis — right ~3 cols */}
            <div className="lg:col-span-3">
              <WaveformOscilloscope
                statevector={simResult.statevector}
                numQubits={numQubits}
              />
            </div>
          </div>

          {/* Bottom Row: Exercises + Socratic Copilot */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <QuestManager
              statevector={simResult.statevector}
              onLoadQuestRequirements={(qReq) => {
                if (numQubits < qReq) setNumQubits(qReq);
              }}
            />
            <SocraticCopilot
              latestGate={latestGateDesc}
              activeQubit={activeQubit}
              circuitSummary={circuitSummaryText}
            />
          </div>
        </div>

        {/* Page Footer — like a textbook page number */}
        <footer className="border-t border-paper-ruled py-2 px-6 flex justify-between items-center text-[11px] text-ink-faint font-sans">
          <span className="font-serif italic">Qiskit Intuition — Laboratory Notebook</span>
          <span className="font-mono">
            {numQubits} qubits · depth {gates.length} · {entanglingCount} entangling
          </span>
        </footer>
      </div>
    </div>
  );
}
