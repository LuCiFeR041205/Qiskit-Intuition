"use client";

import React, { useEffect, useState } from "react";
import { Complex, calculateFidelity } from "@/lib/quantum_simulator";
import { quantumAudio } from "@/lib/quantum_audio";
import confetti from "canvas-confetti";
import { Target, Trophy, ChevronRight, HelpCircle, CheckCircle2, Award, Sparkles } from "lucide-react";

export interface Quest {
  id: string;
  title: string;
  level: string;
  description: string;
  hints: string[];
  targetState: number[];
  numQubitsRequired: number;
}

export const QUESTS: Quest[] = [
  {
    id: "q1",
    title: "Quest 1: The Quantum Flip",
    level: "Phase 1: Single Qubit Kinematics",
    description: "Flip Qubit 0 from ground state |00⟩ to excited state |01⟩ (Qubit 0 = 1). Observe the vector rotate from the North pole to the South pole.",
    hints: ["Apply the Pauli-X gate on Qubit 0."],
    targetState: [0, 1, 0, 0],
    numQubitsRequired: 2,
  },
  {
    id: "q2",
    title: "Quest 2: Maximum Superposition",
    level: "Phase 1: Single Qubit Kinematics",
    description: "Create an equal coherent superposition on Qubit 0: |+0⟩ = 1/√2 (|00⟩ + |01⟩). Watch the Bloch arrow point directly along the +X equator.",
    hints: ["Use the Hadamard (H) gate on Qubit 0."],
    targetState: [0.70710678, 0.70710678, 0, 0],
    numQubitsRequired: 2,
  },
  {
    id: "q3",
    title: "Quest 3: Spooky Action (Bell State)",
    level: "Phase 2: Quantum Entanglement",
    description: "Entangle Qubit 0 and Qubit 1 to construct the EPR Bell state |Φ+⟩ = 1/√2 (|00⟩ + |11⟩). Notice how individual subsystem purity drops to 0%!",
    hints: [
      "Step 1: Put Qubit 0 in superposition with Hadamard (H).",
      "Step 2: Entangle with Qubit 1 using CNOT (Control: q0, Target: q1).",
    ],
    targetState: [0.70710678, 0, 0, 0.70710678],
    numQubitsRequired: 2,
  },
  {
    id: "q4",
    title: "Quest 4: Phase-Inverted Singlet State",
    level: "Phase 2: Quantum Entanglement",
    description: "Construct the singlet Bell state |Ψ-⟩ = 1/√2 (|01⟩ - |10⟩) with an inverted relative quantum phase (180° phase clock shift).",
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
      quantumAudio.playSuccessFanfare();
      try {
        confetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.6 },
          colors: ["#1B4B8A", "#1A7A6D", "#B8860B", "#C13628"],
        });
      } catch {}
    }
  }, [isComplete, quest, completedQuests]);

  const handleNextQuest = () => {
    if (currentQuestIdx < QUESTS.length - 1) {
      setCurrentQuestIdx((prev) => prev + 1);
      setShowHint(false);
      quantumAudio.playGatePulse("H");
    }
  };

  const fidelityPct = (fidelity * 100).toFixed(1);

  return (
    <div className="paper-card dog-ear p-5 flex flex-col gap-4 w-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 pencil-divider border-b">
        <h2 className="section-title text-ink font-serif text-lg">
          Exercises & Challenges
        </h2>

        <div className="flex items-center gap-1.5 text-sm font-mono text-ink-amber">
          <Trophy className="w-4 h-4" />
          <span>
            {completedQuests.length} / {QUESTS.length} completed
          </span>
        </div>
      </div>

      {quest ? (
        <div className="flex flex-col gap-4">
          {/* Title & Level */}
          <div>
            <div className="font-serif italic text-ink-light text-xs">
              {quest.level}
            </div>
            <h3 className="font-serif font-bold text-ink mt-1 text-lg">
              {quest.title}
            </h3>
            <p className="font-sans text-ink-light leading-relaxed mt-2 text-sm">
              {quest.description}
            </p>
          </div>

          {/* Live Fidelity Scanner Gauge */}
          <div className="font-mono text-xs">
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-ink-light">Target Fidelity:</span>
              <span
                className={`font-bold ${
                  isComplete ? "text-ink-teal" : "text-ink"
                }`}
              >
                {fidelityPct}% {isComplete && "✓"}
              </span>
            </div>
            {/* Progress bar */}
            <div className="w-full h-1.5 bg-paper-ruled rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  isComplete ? "bg-ink-teal" : "bg-ink-blue"
                }`}
                style={{ width: `${Math.min(fidelity * 100, 100)}%` }}
              />
            </div>
          </div>

          {/* Socratic Hint Accordion */}
          <div>
            <button
              onClick={() => setShowHint(!showHint)}
              className="ink-btn flex items-center gap-1.5 text-xs"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>{showHint ? "Hide hint" : "Need a hint?"}</span>
            </button>
            {showHint && (
              <div className="mt-3 bg-paper-warm border-l-2 border-pencil pl-3 py-2 font-serif italic text-sm text-ink-light space-y-2">
                {quest.hints.map((h, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="text-ink-amber font-bold">·</span>
                    <span>{h}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Completion Celebration */}
          {isComplete && (
            <div className="flex items-center justify-between p-3.5 bg-paper-warm border-l-4 border-ink-teal mt-2">
              <div className="flex items-center gap-2 text-ink-teal font-sans font-bold text-sm">
                <CheckCircle2 className="w-5 h-5" />
                <span>State Verified</span>
              </div>
              {currentQuestIdx < QUESTS.length - 1 && (
                <button
                  onClick={handleNextQuest}
                  className="ink-btn bg-ink-blue text-paper hover:bg-ink flex items-center gap-1.5 text-xs font-sans font-bold border-none"
                >
                  <span>Next Exercise</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8 flex flex-col items-center gap-3">
          <Award className="w-12 h-12 text-ink-amber" />
          <span className="font-serif text-ink font-bold text-xl">All Exercises Mastered!</span>
        </div>
      )}
    </div>
  );
};
