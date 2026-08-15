"use client";

import React, { useEffect, useRef } from "react";
import { Complex, cAbs2, cPhase } from "@/lib/quantum_simulator";
import { Radio, Waves, Cpu } from "lucide-react";

interface WaveformOscilloscopeProps {
  statevector: Complex[];
  numQubits: number;
}

export const WaveformOscilloscope: React.FC<WaveformOscilloscopeProps> = ({
  statevector,
  numQubits,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let time = 0;

    const render = () => {
      time += 0.04;
      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);

      // 1. Draw subtle background oscilloscope grid
      ctx.strokeStyle = "rgba(0, 240, 255, 0.06)";
      ctx.lineWidth = 1;
      const gridSize = 24;

      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Centerline
      ctx.strokeStyle = "rgba(0, 240, 255, 0.15)";
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();

      // 2. Compute composite quantum wavefunction wave
      // Psi(x, t) = Sum c_k * sin(k*x - omega_k*t + phi_k)
      const points: { x: number; y: number }[] = [];
      const steps = width;
      const midY = height / 2;

      for (let px = 0; px <= steps; px += 2) {
        let waveY = 0;
        const normX = (px / width) * Math.PI * 4;

        statevector.forEach((c, idx) => {
          const prob = cAbs2(c);
          if (prob > 0.0001) {
            const phase = cPhase(c);
            const freq = (idx + 1) * 1.5;
            // Harmonic wave with amplitude ~ sqrt(prob)
            waveY += Math.sqrt(prob) * Math.sin(normX * freq - time * 2 + phase);
          }
        });

        const screenY = midY - waveY * (height * 0.35);
        points.push({ x: px, y: screenY });
      }

      // 3. Draw glowing wave fill & stroke
      if (points.length > 0) {
        // Gradient fill under the wave
        const grad = ctx.createLinearGradient(0, 0, 0, height);
        grad.addColorStop(0, "rgba(0, 240, 255, 0.2)");
        grad.addColorStop(0.5, "rgba(0, 240, 255, 0.05)");
        grad.addColorStop(1, "rgba(255, 51, 102, 0.08)");

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fill();

        // Glowing Wave Line
        ctx.strokeStyle = "#00F0FF";
        ctx.lineWidth = 2.5;
        ctx.shadowColor = "#00F0FF";
        ctx.shadowBlur = 10;

        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.stroke();

        ctx.shadowBlur = 0; // reset shadow
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [statevector]);

  return (
    <div className="relative w-full bg-gradient-to-b from-surface-100/90 to-surface-300/90 rounded-xl border border-hud-border/40 overflow-hidden shadow-2xl backdrop-blur-md flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-surface-200/80 border-b border-hud-border/30">
        <div className="flex items-center gap-2">
          <Waves className="w-4 h-4 text-quantum-cyan animate-pulse" />
          <span className="font-mono text-xs font-bold tracking-wider text-quantum-cyan uppercase">
            Wavefunction Oscilloscope &amp; Phase Clocks
          </span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono text-hud-muted">
          <span className="w-2 h-2 rounded-full bg-quantum-green animate-ping" />
          <span>LIVE INTERFERENCE</span>
        </div>
      </div>

      {/* Real-time Oscilloscope Canvas */}
      <div className="relative w-full h-[150px] bg-background/50">
        <canvas
          ref={canvasRef}
          width={640}
          height={150}
          className="w-full h-full block"
        />
        <div className="absolute bottom-2 left-3 text-[10px] font-mono text-quantum-cyan/70 bg-background/60 px-2 py-0.5 rounded border border-quantum-cyan/20">
          Ψ(x, t) = Σ cₖ·e⁻ⁱᵂᵗ·sin(kx)
        </div>
      </div>

      {/* Basis State Phase Clocks & Probabilities */}
      <div className="p-3 bg-surface-200/60 border-t border-hud-border/20">
        <div className="text-[11px] font-mono text-hud-muted uppercase tracking-wider mb-2 font-bold flex items-center justify-between">
          <span>Basis Amplitudes &amp; Quantum Phase Clocks</span>
          <span className="text-quantum-gold">Phase φ = arg(cₖ)</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {statevector.map((c, idx) => {
            const prob = cAbs2(c);
            const phase = cPhase(c);
            const phaseDeg = ((phase * 180) / Math.PI + 360) % 360;
            const basisLabel = idx.toString(2).padStart(numQubits, "0");

            return (
              <div
                key={idx}
                className="bg-surface-300/80 p-2 rounded-lg border border-hud-subtle/30 flex items-center gap-2.5 hover:border-quantum-cyan/40 transition-all group"
              >
                {/* Circular Phase Clock Dial */}
                <div className="relative w-8 h-8 rounded-full border border-quantum-cyan/30 flex items-center justify-center bg-surface-100 shrink-0">
                  <div
                    className="absolute w-3.5 h-[2px] bg-quantum-gold origin-left rounded"
                    style={{
                      transform: `rotate(${phaseDeg}deg)`,
                      boxShadow: "0 0 6px #FFB800",
                    }}
                  />
                  <div className="w-1.5 h-1.5 rounded-full bg-quantum-cyan z-10" />
                </div>

                {/* Outcome Values */}
                <div className="flex-1 min-w-0 font-mono text-[11px]">
                  <div className="flex justify-between items-center text-hud-text">
                    <span className="font-bold text-quantum-cyan">|{basisLabel}⟩</span>
                    <span className="font-bold">{(prob * 100).toFixed(1)}%</span>
                  </div>
                  {/* Mini probability progress bar */}
                  <div className="w-full h-1 bg-surface-50 rounded-full mt-1 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-quantum-cyan to-quantum-green transition-all duration-300"
                      style={{ width: `${Math.max(prob * 100, 2)}%` }}
                    />
                  </div>
                  <div className="text-[9px] text-hud-muted mt-0.5 flex justify-between">
                    <span>{phaseDeg.toFixed(0)}°</span>
                    <span>
                      {c.r >= 0 ? "+" : ""}
                      {c.r.toFixed(2)}
                      {c.i >= 0 ? "+" : ""}
                      {c.i.toFixed(2)}i
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
