"use client";

import React from "react";
import { Atom, Activity, Sliders, Volume2, CloudLightning, ShieldCheck } from "lucide-react";

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
  return (
    <header className="w-full bg-surface-100/90 border-b border-hud-border/40 backdrop-blur-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Brand Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="relative w-9 h-9 rounded-xl bg-quantum-cyan/10 border border-quantum-cyan/40 flex items-center justify-center shadow-lg shadow-quantum-cyan/20">
            <Atom className="w-5 h-5 text-quantum-cyan animate-quantum-spin" />
            <div className="absolute inset-0 rounded-xl bg-quantum-cyan/10 animate-ping opacity-25" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display font-bold text-base sm:text-lg text-hud-text tracking-tight">
                Qiskit <span className="text-quantum-cyan">Intuition</span>
              </h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-quantum-cyan/10 text-quantum-cyan border border-quantum-cyan/30">
                LAB V2.0
              </span>
            </div>
            <p className="text-[11px] font-mono text-hud-muted">
              Interactive Physics &amp; Bloch Telemetry Workstation
            </p>
          </div>
        </div>

        {/* Telemetry Metric Strip */}
        <div className="hidden lg:flex items-center gap-4 font-mono text-xs bg-surface-200/80 px-3.5 py-1.5 rounded-lg border border-hud-subtle/30">
          <div className="flex items-center gap-1.5">
            <span className="text-hud-muted">Qubits:</span>
            <strong className="text-quantum-cyan">{numQubits}</strong>
          </div>
          <div className="w-[1px] h-3.5 bg-hud-subtle/40" />
          <div className="flex items-center gap-1.5">
            <span className="text-hud-muted">Gate Depth:</span>
            <strong className="text-quantum-gold">{depth}</strong>
          </div>
          <div className="w-[1px] h-3.5 bg-hud-subtle/40" />
          <div className="flex items-center gap-1.5">
            <span className="text-hud-muted">Entangling Links:</span>
            <strong className="text-quantum-green">{entanglingLinks}</strong>
          </div>
          <div className="w-[1px] h-3.5 bg-hud-subtle/40" />
          <div className="flex items-center gap-1.5">
            <span className="text-hud-muted">Non-Zero Amplitudes:</span>
            <strong className="text-hud-text">{activeBasisCount}</strong>
          </div>
        </div>

        {/* Controls: Qubits Slider + Noise Toggle */}
        <div className="flex items-center gap-3">
          {/* Qubit Count Slider */}
          <div className="flex items-center gap-2 bg-surface-200/80 px-2.5 py-1.5 rounded-lg border border-hud-subtle/30 font-mono text-xs">
            <span className="text-hud-muted text-[11px]">Channels:</span>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4].map((n) => (
                <button
                  key={n}
                  onClick={() => onChangeNumQubits(n)}
                  className={`w-5 h-5 rounded text-[11px] font-bold transition-all ${
                    numQubits === n
                      ? "bg-quantum-cyan text-background shadow-md shadow-quantum-cyan/20"
                      : "text-hud-muted hover:text-hud-text hover:bg-surface-50"
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* Hardware Noise Simulation Toggle */}
          <button
            onClick={() => onToggleNoisy(!noisy)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-mono text-xs transition-all border ${
              noisy
                ? "bg-quantum-coral/20 border-quantum-coral text-quantum-coral shadow-lg shadow-quantum-coral/20"
                : "bg-surface-200/80 border-hud-subtle/30 text-hud-muted hover:text-hud-text hover:bg-surface-50"
            }`}
            title="Toggle realistic quantum hardware decoherence (T1/T2 thermal relaxation)"
          >
            <CloudLightning className={`w-3.5 h-3.5 ${noisy ? "animate-bounce" : ""}`} />
            <span className="hidden sm:inline">Hardware Noise:</span>
            <strong className="font-bold">{noisy ? "ON" : "OFF"}</strong>
          </button>
        </div>
      </div>
    </header>
  );
};
