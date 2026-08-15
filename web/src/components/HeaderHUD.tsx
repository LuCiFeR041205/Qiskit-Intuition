"use client";

import React, { useState } from "react";
import { quantumAudio } from "@/lib/quantum_audio";
import { Atom, Activity, Volume2, VolumeX, CloudLightning, Sparkles } from "lucide-react";

interface HeaderHUDProps {
  numQubits: number;
  onChangeNumQubits: (n: number) => void;
  noisy: boolean;
  onToggleNoisy: (noisy: boolean) => void;
  depth: number;
  entanglingLinks: number;
  activeBasisCount: number;
}

export const HeaderHUD: React.FC<HeaderHUDProps> = ({
  numQubits,
  onChangeNumQubits,
  noisy,
  onToggleNoisy,
  depth,
  entanglingLinks,
  activeBasisCount,
}) => {
  const [muted, setMuted] = useState(quantumAudio.getMuted());

  const handleToggleMute = () => {
    const next = quantumAudio.toggleMute();
    setMuted(next);
  };

  return (
    <header className="w-full bg-paper border-b border-pencil sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand Logo & Title */}
        <div className="flex items-center gap-3.5">
          <div className="flex items-center justify-center">
            <Atom className="w-6 h-6 text-ink-light" />
          </div>
          <div>
            <div className="flex items-baseline gap-2.5">
              <h1 className="font-serif font-bold text-lg sm:text-xl text-ink tracking-tight">
                Qiskit Intuition
              </h1>
              <span className="font-serif italic text-[11px] text-ink-light">
                § Laboratory Notebook
              </span>
            </div>
            <p className="text-xs font-sans text-ink-faint">
              Interactive Physics Telemetry &amp; Bloch Workstation
            </p>
          </div>
        </div>

        {/* Telemetry Metric Strip */}
        <div className="hidden lg:flex items-center gap-2 font-mono text-xs text-ink-faint">
          <span>n = {numQubits} qubits</span>
          <span>·</span>
          <span>depth {depth}</span>
          <span>·</span>
          <span>{entanglingLinks} entangling</span>
          <span>·</span>
          <span>{activeBasisCount} bases</span>
        </div>

        {/* Controls: Channels + Noise + Audio */}
        <div className="flex items-center gap-3">
          {/* Audio Synthesizer Toggle */}
          <button
            onClick={handleToggleMute}
            className="ink-btn p-1.5 flex items-center justify-center"
            title={muted ? "Unmute Audio" : "Mute Audio"}
          >
            {muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>

          {/* Qubit Count */}
          <div className="flex items-center gap-1.5 font-mono text-xs text-ink-light">
            <span>Wires:</span>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4].map((n) => (
                <button
                  key={n}
                  onClick={() => {
                    onChangeNumQubits(n);
                    quantumAudio.playGatePulse("H");
                  }}
                  className={`ink-btn px-2 py-0.5 ${
                    numQubits === n ? "bg-ink text-paper" : ""
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* Hardware Noise Toggle */}
          <button
            onClick={() => onToggleNoisy(!noisy)}
            className={`ink-btn flex items-center gap-1.5 px-3 py-1 text-xs ${
              noisy ? "text-ink-red font-bold" : ""
            }`}
            title="Toggle realistic quantum hardware decoherence"
          >
            <CloudLightning className="w-4 h-4" />
            <span className="hidden sm:inline">Noise:</span>
            <span>{noisy ? "ON" : "OFF"}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
