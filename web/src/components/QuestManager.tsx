"use client";

import React, { useEffect, useState } from "react";
import { Complex, calculateFidelity } from "@/lib/quantum_simulator";
import confetti from "canvas-confetti";
import { Target, Trophy, ChevronRight, HelpCircle, CheckCircle2, Award } from "lucide-react";

export interface Quest {
  id: string;
  title: string;
  level: string;
  description: string;
  hints: string[];
  targetState: number[]; // Target amplitude vector
  numQubitsRequired: number;
}

export const QUESTS: Quest[] = [
  {
    id: "q1",
    title: "Quest 1: The Quantum Flip",
    level: "Level 1: Classical Analogs",
    description: "Flip Qubit 0 from state |00⟩ to state |01⟩ (Qubit 0 = 1). This is the quantum equivalent of a classical NOT gate.",
    hints: ["Apply the Pauli-X gate on Qubit 0."],
    targetState: [0, 1, 0, 0],
    numQubitsRequired: 2,
  },
  {
    id: "q2",
    title: "Quest 2: Into Superposition",
    level: "Level 1: Classical Analogs",
    description: "Create an equal quantum superposition on Qubit 0: |+0⟩ = 1/√2 (|00⟩ + |01⟩).",
    hints: ["Use the Hadamard (H) gate on Qubit 0."],
    targetState: [0.70710678, 0.70710678, 0, 0],
    numQubitsRequired: 2,
  },
  {
    id: "q3",
    title: "Quest 3: Spooky Action (Bell State)",
    level: "Level 2: Entanglement",
    description: "Entangle Qubit 0 and Qubit 1 to construct the famous Bell state |Φ+⟩ = 1/√2 (|00⟩ + |11⟩).",
    hints: [
      "Step 1: Put Qubit 0 in superposition with Hadamard (H).",
      "Step 2: Entangle with Qubit 1 using CNOT (Control: q0, Target: q1).",
    ],
    targetState: [0.70710678, 0, 0, 0.70710678],
    numQubitsRequired: 2,
  },
  {
    id: "q4",
    title: "Quest 4: Quantum Phase Inversion",
    level: "Level 2: Entanglement",
    description: "Construct the singlet Bell state |Ψ-⟩ = 1/√2 (|01⟩ - |10⟩) with an inverted relative quantum phase.",
    hints: [
      "Apply Pauli-X to both qubits, then Hadamard, then CNOT.",
    ],
    targetState: [0, 0.70710678, -0.70710678, 0],
    numQubitsRequired: 2,
  },
];

interface QuestManagerProps {
  statevector: Complex[];
  onLoadQuestRequirements: (numQubits: number) => void;
}

export const QuestManager: React.FC<QuestManagerProps> = ({
  statevector,
  onLoadQuestRequirements,
}) => {
  const [currentQuestIdx, setCurrentQuestIdx] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [completedQuests, setCompletedQuests] = useState<string[]>([]);

  const quest = QUESTS[currentQuestIdx];
  const fidelity = calculateFidelity(statevector, quest ? quest.targetState : []);
  const isComplete = fidelity > 0.98;

  useEffect(() => {
    if (quest) {
      onLoadQuestRequirements(quest.numQubitsRequired);
    }
  }, [currentQuestIdx]);

  useEffect(() => {
    if (isComplete && quest && !completedQuests.includes(quest.id)) {
      setCompletedQuests((prev) => [...prev, quest.id]);
      // Trigger festive quantum confetti celebration
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ["#00F0FF", "#00FF9D", "#FFB800"],
        });
      } catch {}
    }
  }, [isComplete, quest, completedQuests]);

  const handleNextQuest = () => {
    if (currentQuestIdx < QUESTS.length - 1) {
      setCurrentQuestIdx((prev) => prev + 1);
      setShowHint(false);
    }
  };

  const fidelityPct = (fidelity * 100).toFixed(1);

  return (
    <div className="w-full bg-gradient-to-b from-surface-100/90 to-surface-300/90 rounded-xl border border-hud-border/40 overflow-hidden shadow-2xl backdrop-blur-md p-4 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-hud-border/20 pb-3">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-quantum-cyan" />
          <span className="font-mono text-xs font-bold tracking-wider text-quantum-cyan uppercase">
            Active Quantum Objective
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-xs font-mono text-hud-muted">
          <Trophy className="w-3.5 h-3.5 text-quantum-gold" />
          <span>
            {completedQuests.length} / {QUESTS.length} Completed
          </span>
        </div>
      </div>

      {quest ? (
        <div className="flex flex-col gap-3">
          {/* Quest Title & Level */}
          <div>
            <div className="text-[10px] font-mono text-quantum-gold uppercase font-bold tracking-wider">
              {quest.level}
            </div>
            <h3 className="text-base font-display font-bold text-hud-text mt-0.5">
              {quest.title}
            </h3>
            <p className="text-xs text-hud-muted font-sans leading-relaxed mt-1">
              {quest.description}
            </p>
          </div>

          {/* Live Fidelity Scanner Gauge */}
          <div className="bg-surface-300/90 p-3 rounded-lg border border-hud-subtle/30 font-mono text-xs">
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-hud-muted">Quantum Target Fidelity:</span>
              <span
                className={`font-bold ${
                  isComplete ? "text-quantum-green text-sm" : "text-quantum-cyan"
                }`}
              >
                {fidelityPct}% {isComplete && "✓ STATE ACHIEVED"}
              </span>
            </div>
            {/* Progress bar */}
            <div className="w-full h-2 bg-surface-50 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  isComplete
                    ? "bg-gradient-to-r from-quantum-green to-emerald-300 shadow-lg shadow-quantum-green/50"
                    : "bg-gradient-to-r from-quantum-cyan to-quantum-gold"
                }`}
                style={{ width: `${Math.min(fidelity * 100, 100)}%` }}
              />
            </div>
          </div>

          {/* Socratic Hint Accordion */}
          <div>
            <button
              onClick={() => setShowHint(!showHint)}
              className="text-[11px] font-mono text-quantum-cyan hover:text-quantum-cyan/80 flex items-center gap-1"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>{showHint ? "Hide Socratic Hint" : "Need a physics hint?"}</span>
            </button>
            {showHint && (
              <div className="mt-2 p-2.5 rounded-lg bg-surface-200 border border-hud-border/20 text-xs font-mono text-hud-muted space-y-1">
                {quest.hints.map((h, i) => (
                  <div key={i}>• {h}</div>
                ))}
              </div>
            )}
          </div>

          {/* Completion Celebration / Next Button */}
          {isComplete && (
            <div className="flex items-center justify-between p-3 rounded-lg bg-quantum-green/10 border border-quantum-green/30">
              <div className="flex items-center gap-2 text-quantum-green font-mono text-xs font-bold">
                <CheckCircle2 className="w-4 h-4" />
                <span>Objective Complete!</span>
              </div>
              {currentQuestIdx < QUESTS.length - 1 && (
                <button
                  onClick={handleNextQuest}
                  className="px-3 py-1.5 rounded-lg bg-quantum-green text-background font-mono text-xs font-bold flex items-center gap-1 hover:scale-105 transition-all shadow-md shadow-quantum-green/20"
                >
                  <span>Next Quest</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-6 text-quantum-green font-mono text-sm font-bold flex flex-col items-center gap-2">
          <Award className="w-8 h-8 text-quantum-gold animate-bounce" />
          <span>All Quantum Quests Mastered!</span>
        </div>
      )}
    </div>
  );
};
