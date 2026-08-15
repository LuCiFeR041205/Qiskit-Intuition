"use client";

import React, { useEffect, useRef } from "react";
import { Complex, cAbs2, cPhase } from "@/lib/quantum_simulator";
import { Waves, Sparkles, Activity, Gauge } from "lucide-react";

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

      // 1. Quantum Vacuum Matrix Grid (graph paper style)
      ctx.strokeStyle = "rgba(139, 134, 128, 0.15)";
      ctx.lineWidth = 1;
      const step = 20;

      for (let x = 0; x < width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Centerline Ground State Zero
      ctx.strokeStyle = "rgba(139, 134, 128, 0.3)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();

      // 2. Compute Wave Packets
      const midY = height / 2;
      const realPoints: { x: number; y: number }[] = [];
      const imagPoints: { x: number; y: number }[] = [];
      const probEnvelope: { x: number; y: number }[] = [];

      for (let px = 0; px <= width; px += 2) {
        let realY = 0;
        let imagY = 0;
        let density = 0;
        const normX = (px / width) * Math.PI * 4;

        statevector.forEach((c, idx) => {
          const prob = cAbs2(c);
          if (prob > 0.0001) {
            const phase = cPhase(c);
            const freq = (idx + 1) * 1.6;
            const amp = Math.sqrt(prob);

            // Re(Psi) = amp * cos(k*x - omega*t + phi)
            realY += amp * Math.cos(normX * freq - time * 2.2 + phase);
            // Im(Psi) = amp * sin(k*x - omega*t + phi)
            imagY += amp * Math.sin(normX * freq - time * 2.2 + phase);
            // |Psi(x)|^2 spatial envelope
            density += prob * Math.pow(Math.sin(normX * freq * 0.5), 2);
          }
        });

        realPoints.push({ x: px, y: midY - realY * (height * 0.32) });
        imagPoints.push({ x: px, y: midY - imagY * (height * 0.32) });
        probEnvelope.push({ x: px, y: midY - density * (height * 0.4) });
      }

      // 3. Render Waves
      if (realPoints.length > 0) {
        // Simple fill under the real wave
        ctx.fillStyle = "rgba(27, 75, 138, 0.06)";
        ctx.beginPath();
        ctx.moveTo(realPoints[0].x, realPoints[0].y);
        for (let i = 1; i < realPoints.length; i++) {
          ctx.lineTo(realPoints[i].x, realPoints[i].y);
        }
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fill();

        // Draw Imaginary Wave (ink-red)
        ctx.strokeStyle = "rgba(193, 54, 40, 0.6)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(imagPoints[0].x, imagPoints[0].y);
        for (let i = 1; i < imagPoints.length; i++) {
          ctx.lineTo(imagPoints[i].x, imagPoints[i].y);
        }
        ctx.stroke();

        // Draw Real Wave (ink-blue)
        ctx.strokeStyle = "#1B4B8A";
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(realPoints[0].x, realPoints[0].y);
        for (let i = 1; i < realPoints.length; i++) {
          ctx.lineTo(realPoints[i].x, realPoints[i].y);
        }
        ctx.stroke();
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [statevector]);

  return (
    <div className="paper-card w-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-pencil/30">
        <div className="flex items-center gap-2.5">
          <Waves className="w-4 h-4 text-ink-light" />
          <h3 className="section-title text-sm m-0">State Vector &amp; Amplitudes</h3>
        </div>
      </div>

      {/* Real-time Oscilloscope Canvas */}
      <div className="relative w-full h-[180px] bg-paper">
        <canvas
          ref={canvasRef}
          width={640}
          height={180}
          className="w-full h-full block"
        />
        {/* Real / Imag Wave Legend */}
        <div className="absolute top-2.5 right-3 flex items-center gap-3 text-[10px] font-mono bg-paper-warm px-2.5 py-1 rounded border border-pencil/30 shadow-sm">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-[2px] bg-ink-blue" />
            <span className="text-ink-blue">Re(Ψ)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-[2px] bg-ink-red" />
            <span className="text-ink-red">Im(Ψ)</span>
          </div>
        </div>

        <div className="absolute bottom-2.5 left-3 text-[10px] font-mono text-ink bg-paper-warm px-2.5 py-1 rounded border border-pencil/30 shadow-sm">
          iℏ ∂Ψ/∂t = ĤΨ
        </div>
      </div>

      {/* Basis State Phase Clocks */}
      <div className="p-4 bg-paper-warm/50 border-t border-pencil/30">
        <div className="text-[11px] font-sans text-ink-light mb-2.5 flex items-center justify-between">
          <span>Statevector Basis Probabilities &amp; Relative Phase Clocks</span>
          <span className="text-ink-amber font-mono font-bold">Phase φ = arg(cₖ)</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {statevector.map((c, idx) => {
            const prob = cAbs2(c);
            const phase = cPhase(c);
            const phaseDeg = ((phase * 180) / Math.PI + 360) % 360;
            const basisLabel = idx.toString(2).padStart(numQubits, "0");
            const isActive = prob > 0.001;

            return (
              <div
                key={idx}
                className={`p-2.5 rounded border transition-all flex items-center gap-3 ${
                  isActive
                    ? "bg-paper-warm border-pencil/40 shadow-card"
                    : "bg-paper border-pencil/20 opacity-50"
                }`}
              >
                {/* Circular Phase Clock Dial */}
                <div className="relative w-9 h-9 rounded-full border border-pencil flex items-center justify-center shrink-0">
                  <div
                    className="absolute w-4 h-[1.5px] bg-ink-amber origin-left rounded"
                    style={{
                      transform: `rotate(${phaseDeg}deg)`,
                    }}
                  />
                  <div className="w-1.5 h-1.5 rounded-full bg-ink z-10" />
                </div>

                {/* Outcome Values */}
                <div className="flex-1 min-w-0 font-mono text-xs">
                  <div className="flex justify-between items-center text-ink">
                    <span className="font-bold text-ink-blue">|{basisLabel}⟩</span>
                    <span className="font-bold">{(prob * 100).toFixed(1)}%</span>
                  </div>
                  {/* Probability Bar */}
                  <div className="w-full h-1.5 bg-paper-ruled rounded-sm mt-1 overflow-hidden border border-pencil/20">
                    <div
                      className="h-full bg-ink-blue transition-all duration-300"
                      style={{ width: `${Math.max(prob * 100, 2)}%` }}
                    />
                  </div>
                  <div className="text-[10px] text-ink-light mt-1 flex justify-between">
                    <span className="text-ink-amber font-bold">{phaseDeg.toFixed(0)}°</span>
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
