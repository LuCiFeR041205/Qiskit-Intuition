"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { BlochCoords } from "@/lib/quantum_simulator";
import { RotateCw, Compass, Maximize2, Activity } from "lucide-react";

interface BlochSphere3DProps {
  blochCoords: Record<number, BlochCoords>;
  numQubits: number;
  activeQubit: number;
  onSelectQubit: (q: number) => void;
}

export const BlochSphere3D: React.FC<BlochSphere3DProps> = ({
  blochCoords,
  numQubits,
  activeQubit,
  onSelectQubit,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const vectorArrowRef = useRef<THREE.ArrowHelper | null>(null);
  const projLineRef = useRef<THREE.Line | null>(null);
  const dropLineRef = useRef<THREE.Line | null>(null);

  const coords = blochCoords[activeQubit] || {
    x: 0,
    y: 0,
    z: 1,
    r: 1,
    theta: 0,
    phi: 0,
    purity: 1,
  };

  const targetVectorRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 1, 0)); // Three.js Y is up (Z in Bloch)
  const currentVectorRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 1, 0));

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight || 340;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(2.4, 1.8, 2.6);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = "";
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Ambient & Point Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00f0ff, 2.0);
    dirLight.position.set(5, 5, 5);
    scene.add(dirLight);

    // 1. Semi-transparent Sphere Mesh
    const sphereGeo = new THREE.SphereGeometry(1, 36, 36);
    const sphereMat = new THREE.MeshPhongMaterial({
      color: 0x051329,
      transparent: true,
      opacity: 0.35,
      wireframe: false,
      shininess: 90,
      reflectivity: 0.8,
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
    scene.add(sphereMesh);

    // 2. Wireframe grid overlay
    const wireGeo = new THREE.WireframeGeometry(new THREE.SphereGeometry(1, 18, 18));
    const wireMat = new THREE.LineBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.12,
    });
    const wireMesh = new THREE.LineSegments(wireGeo, wireMat);
    scene.add(wireMesh);

    // 3. Equator Ring (XY Plane in standard coords -> XZ in Three.js)
    const ringGeo = new THREE.RingGeometry(0.99, 1.01, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xffb800,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.45,
    });
    const equatorRing = new THREE.Mesh(ringGeo, ringMat);
    equatorRing.rotation.x = Math.PI / 2;
    scene.add(equatorRing);

    // 4. Prime Meridian Ring (XZ plane in standard coords -> XY in Three.js)
    const meridianMat = ringMat.clone();
    meridianMat.color.setHex(0x00f0ff);
    meridianMat.opacity = 0.25;
    const meridianRing = new THREE.Mesh(ringGeo, meridianMat);
    scene.add(meridianRing);

    // 5. Axes Helpers (Mapped: Bloch Z -> Three.js Y, Bloch X -> Three.js X, Bloch Y -> Three.js -Z)
    const createAxis = (
      dir: THREE.Vector3,
      color: number,
      len = 1.35
    ): THREE.ArrowHelper => {
      const arrow = new THREE.ArrowHelper(
        dir.clone().normalize(),
        new THREE.Vector3(0, 0, 0),
        len,
        color,
        0.08,
        0.05
      );
      if (!Array.isArray(arrow.line.material)) {
        arrow.line.material.transparent = true;
        arrow.line.material.opacity = 0.55;
      }
      scene.add(arrow);
      return arrow;
    };

    createAxis(new THREE.Vector3(0, 1, 0), 0x00f0ff);   // +|0> (Z)
    createAxis(new THREE.Vector3(0, -1, 0), 0x7c4dff);  // -|1> (-Z)
    createAxis(new THREE.Vector3(1, 0, 0), 0xff3366);   // +X |+>
    createAxis(new THREE.Vector3(0, 0, -1), 0x00ff9d);  // +Y |i>

    // 6. Dynamic Statevector Arrow
    const stateArrow = new THREE.ArrowHelper(
      new THREE.Vector3(0, 1, 0),
      new THREE.Vector3(0, 0, 0),
      1.0,
      0x00f0ff,
      0.15,
      0.09
    );
    scene.add(stateArrow);
    vectorArrowRef.current = stateArrow;

    // 7. Projection lines to equatorial plane
    const lineMat = new THREE.LineDashedMaterial({
      color: 0xffb800,
      dashSize: 0.05,
      gapSize: 0.03,
      transparent: true,
      opacity: 0.6,
    });

    const dropGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 0, 0),
    ]);
    const dropLine = new THREE.Line(dropGeo, lineMat);
    scene.add(dropLine);
    dropLineRef.current = dropLine;

    // Orbit Interaction via Drag
    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };
    let spherical = new THREE.Spherical().setFromVector3(camera.position);

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouse = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMouse.x;
      const deltaY = e.clientY - prevMouse.y;
      prevMouse = { x: e.clientX, y: e.clientY };

      spherical.theta -= deltaX * 0.008;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi - deltaY * 0.008));
      camera.position.setFromSpherical(spherical);
      camera.lookAt(0, 0, 0);
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    container.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    // Animation Loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);

      // Smooth SLERP / lerp vector towards target
      if (vectorArrowRef.current) {
        currentVectorRef.current.lerp(targetVectorRef.current, 0.12);
        const len = currentVectorRef.current.length();
        if (len > 0.001) {
          vectorArrowRef.current.setDirection(currentVectorRef.current.clone().normalize());
          vectorArrowRef.current.setLength(len, 0.14, 0.08);
        }

        // Update drop lines
        if (dropLineRef.current) {
          const tip = currentVectorRef.current;
          const proj = new THREE.Vector3(tip.x, 0, tip.z);
          const pts = [tip, proj, new THREE.Vector3(0, 0, 0)];
          dropLineRef.current.geometry.setFromPoints(pts);
          dropLineRef.current.computeLineDistances();
        }
      }

      // Subtle slow passive orbital rotation when not dragging
      if (!isDragging) {
        sphereMesh.rotation.y += 0.0012;
        wireMesh.rotation.y += 0.0012;
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 340;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      container.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
    };
  }, []);

  // Update target coordinates whenever active qubit or blochCoords changes
  useEffect(() => {
    // Map Bloch coordinates to Three.js coordinates:
    // Bloch X -> Three.js X
    // Bloch Y -> Three.js -Z
    // Bloch Z -> Three.js Y
    const x3 = coords.x;
    const y3 = coords.z; // Z is UP
    const z3 = -coords.y;

    targetVectorRef.current.set(x3, y3, z3);

    // Dynamic color change based on purity
    if (vectorArrowRef.current) {
      if (coords.purity > 0.95) {
        vectorArrowRef.current.setColor(0x00f0ff);
      } else {
        vectorArrowRef.current.setColor(0xffb800); // Mixed state yellow/amber
      }
    }
  }, [coords]);

  const thetaDeg = ((coords.theta * 180) / Math.PI).toFixed(1);
  const phiDeg = ((coords.phi * 180) / Math.PI).toFixed(1);
  const purityPct = (coords.purity * 100).toFixed(0);
  const isEntangled = coords.purity < 0.95;

  return (
    <div className="relative w-full h-[380px] bg-gradient-to-b from-surface-100/90 to-surface-300/90 rounded-xl border border-hud-border/40 overflow-hidden shadow-2xl backdrop-blur-md flex flex-col">
      {/* Top Header HUD Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-surface-200/80 border-b border-hud-border/30 z-10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-quantum-cyan animate-ping" />
          <span className="font-mono text-xs font-bold tracking-wider text-quantum-cyan uppercase">
            Bloch Vector Telemetry
          </span>
        </div>

        {/* Qubit Selector Tabs */}
        <div className="flex items-center gap-1 bg-surface-300/80 p-1 rounded-lg border border-hud-subtle/30">
          {Array.from({ length: numQubits }).map((_, q) => (
            <button
              key={q}
              onClick={() => onSelectQubit(q)}
              className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold transition-all ${
                activeQubit === q
                  ? "bg-quantum-cyan text-background shadow-lg shadow-quantum-cyan/20 scale-105"
                  : "text-hud-muted hover:text-hud-text hover:bg-surface-50"
              }`}
            >
              q{q}
            </button>
          ))}
        </div>
      </div>

      {/* 3D Three.js Container */}
      <div
        ref={containerRef}
        className="w-full flex-1 cursor-grab active:cursor-grabbing relative"
      />

      {/* HUD Corner Accents */}
      <div className="absolute top-12 left-3 pointer-events-none text-[11px] font-mono bg-background/80 px-2.5 py-1.5 rounded border border-hud-border/30 backdrop-blur">
        <div className="text-quantum-cyan font-bold flex items-center gap-1.5">
          <Compass className="w-3.5 h-3.5" />
          <span>Polar Angles</span>
        </div>
        <div className="text-hud-text mt-0.5">
          θ = <span className="text-quantum-gold font-bold">{thetaDeg}°</span> | φ ={" "}
          <span className="text-quantum-cyan font-bold">{phiDeg}°</span>
        </div>
      </div>

      <div className="absolute top-12 right-3 pointer-events-none text-[11px] font-mono bg-background/80 px-2.5 py-1.5 rounded border border-hud-border/30 backdrop-blur text-right">
        <div className="text-hud-muted font-medium flex items-center justify-end gap-1">
          <Activity className="w-3 h-3 text-quantum-green" />
          <span>Subsystem Purity</span>
        </div>
        <div className="mt-0.5 flex items-center justify-end gap-1.5">
          <span
            className={`font-bold text-xs ${
              isEntangled ? "text-quantum-gold" : "text-quantum-green"
            }`}
          >
            {isEntangled ? "ENTANGLED (MIXED)" : "PURE VECTOR"}
          </span>
          <span className="text-hud-muted text-[10px]">({purityPct}%)</span>
        </div>
      </div>

      {/* Coordinate Expectations Bar */}
      <div className="px-4 py-2 bg-surface-200/90 border-t border-hud-border/20 flex items-center justify-between text-xs font-mono z-10">
        <div className="flex items-center gap-4 text-hud-muted">
          <span>
            ⟨X⟩: <strong className="text-quantum-coral">{coords.x.toFixed(3)}</strong>
          </span>
          <span>
            ⟨Y⟩: <strong className="text-quantum-green">{coords.y.toFixed(3)}</strong>
          </span>
          <span>
            ⟨Z⟩: <strong className="text-quantum-cyan">{coords.z.toFixed(3)}</strong>
          </span>
        </div>
        <div className="text-[10px] text-hud-muted">
          Drag to Orbit · Real-time R3F
        </div>
      </div>
    </div>
  );
};
