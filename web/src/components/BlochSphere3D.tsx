"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { BlochCoords } from "@/lib/quantum_simulator";
import { quantumAudio } from "@/lib/quantum_audio";
import {
  RotateCcw,
  Compass,
  Activity,
  Eye,
} from "lucide-react";

interface BlochSphere3DProps {
  blochCoords: Record<number, BlochCoords>;
  numQubits: number;
  activeQubit: number;
  onSelectQubit: (q: number) => void;
  onApplyPresetState?: (stateName: string) => void;
}

export const BlochSphere3D: React.FC<BlochSphere3DProps> = ({
  blochCoords,
  numQubits,
  activeQubit,
  onSelectQubit,
  onApplyPresetState,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const vectorArrowRef = useRef<THREE.ArrowHelper | null>(null);
  const tipGlowMeshRef = useRef<THREE.Mesh | null>(null);
  const dropLineRef = useRef<THREE.Line | null>(null);
  const projDiscRef = useRef<THREE.Mesh | null>(null);
  const autoRotateRef = useRef<boolean>(false);
  const [isAutoRotating, setIsAutoRotating] = useState(false);

  const coords = blochCoords[activeQubit] || {
    x: 0,
    y: 0,
    z: 1,
    r: 1,
    theta: 0,
    phi: 0,
    purity: 1,
  };

  const targetVectorRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 1, 0));
  const currentVectorRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 1, 0));

  // Initialize Scene
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight || 420;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    camera.position.set(2.6, 2.0, 2.8);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    container.innerHTML = "";
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xfffaf0, 0.8);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(3, 4, 3);
    scene.add(directionalLight);

    // 1. Paper-style Sphere
    const sphereGeo = new THREE.SphereGeometry(1, 48, 48);
    const sphereMat = new THREE.MeshPhysicalMaterial({
      color: 0xE8E2D6,
      transmission: 0.9,
      transparent: true,
      opacity: 0.15,
      roughness: 0.2,
      clearcoat: 0.1,
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
    scene.add(sphereMesh);

    // 2. Wireframe Latitudinal & Longitudinal Cage
    const wireGeo = new THREE.WireframeGeometry(new THREE.SphereGeometry(1.002, 24, 24));
    const wireMat = new THREE.LineBasicMaterial({
      color: 0x8B8680,
      transparent: true,
      opacity: 0.2,
    });
    const wireMesh = new THREE.LineSegments(wireGeo, wireMat);
    scene.add(wireMesh);

    // 3. Faint Equatorial Disk (Phase Plane)
    const diskGeo = new THREE.CircleGeometry(0.99, 64);
    const diskMat = new THREE.MeshBasicMaterial({
      color: 0xB8860B,
      transparent: true,
      opacity: 0.05,
      side: THREE.DoubleSide,
    });
    const diskMesh = new THREE.Mesh(diskGeo, diskMat);
    diskMesh.rotation.x = Math.PI / 2;
    scene.add(diskMesh);

    // Equator Ring Border
    const ringGeo = new THREE.RingGeometry(0.985, 1.015, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xB8860B,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide,
    });
    const equatorRing = new THREE.Mesh(ringGeo, ringMat);
    equatorRing.rotation.x = Math.PI / 2;
    scene.add(equatorRing);

    // 4. Prime Meridian Ring (Zero Phase Line)
    const meridianMat = ringMat.clone();
    meridianMat.color.setHex(0x2C2C2C);
    meridianMat.opacity = 0.15;
    const meridianRing = new THREE.Mesh(ringGeo, meridianMat);
    scene.add(meridianRing);

    // 5. Coordinate Axes
    const createLaserAxis = (
      dir: THREE.Vector3,
      color: number,
      opacity: number = 0.65,
      len = 1.38
    ): THREE.ArrowHelper => {
      const arrow = new THREE.ArrowHelper(
        dir.clone().normalize(),
        new THREE.Vector3(0, 0, 0),
        len,
        color,
        0.09,
        0.05
      );
      if (!Array.isArray(arrow.line.material)) {
        arrow.line.material.transparent = true;
        arrow.line.material.opacity = opacity;
      }
      scene.add(arrow);
      return arrow;
    };

    createLaserAxis(new THREE.Vector3(0, 1, 0), 0x1B4B8A, 0.8);   // +Z (|0>) ink-blue
    createLaserAxis(new THREE.Vector3(0, -1, 0), 0x6B6560, 0.5);  // -Z (|1>) ink-light
    createLaserAxis(new THREE.Vector3(1, 0, 0), 0xC13628, 0.7);   // +X ink-red
    createLaserAxis(new THREE.Vector3(-1, 0, 0), 0xC13628, 0.3);  // -X lighter opacity
    createLaserAxis(new THREE.Vector3(0, 0, -1), 0x1A7A6D, 0.7);  // +Y ink-teal
    createLaserAxis(new THREE.Vector3(0, 0, 1), 0x1A7A6D, 0.3);   // -Y lighter opacity

    // 6. Dynamic Statevector Arrow
    const stateArrow = new THREE.ArrowHelper(
      new THREE.Vector3(0, 1, 0),
      new THREE.Vector3(0, 0, 0),
      1.0,
      0x1B4B8A,
      0.16,
      0.09
    );
    scene.add(stateArrow);
    vectorArrowRef.current = stateArrow;

    // Tip Particle
    const tipGeo = new THREE.SphereGeometry(0.045, 16, 16);
    const tipMat = new THREE.MeshBasicMaterial({ color: 0x1B4B8A });
    const tipMesh = new THREE.Mesh(tipGeo, tipMat);
    scene.add(tipMesh);
    tipGlowMeshRef.current = tipMesh;

    // 7. Orthogonal Projection Drop Lines
    const lineMat = new THREE.LineDashedMaterial({
      color: 0xB8860B,
      dashSize: 0.04,
      gapSize: 0.03,
      transparent: true,
      opacity: 0.7,
    });
    const dropGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 0, 0),
    ]);
    const dropLine = new THREE.Line(dropGeo, lineMat);
    scene.add(dropLine);
    dropLineRef.current = dropLine;

    // Projection shadow disk on XY plane
    const projGeo = new THREE.RingGeometry(0.01, 0.05, 16);
    const projMat = new THREE.MeshBasicMaterial({
      color: 0xB8860B,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6,
    });
    const projDisc = new THREE.Mesh(projGeo, projMat);
    projDisc.rotation.x = Math.PI / 2;
    scene.add(projDisc);
    projDiscRef.current = projDisc;

    // Drag / Orbit Interaction
    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };
    const spherical = new THREE.Spherical().setFromVector3(camera.position);

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouse = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMouse.x;
      const deltaY = e.clientY - prevMouse.y;
      prevMouse = { x: e.clientX, y: e.clientY };

      spherical.theta -= deltaX * 0.007;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi - deltaY * 0.007));
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
    let clockTime = 0;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      clockTime += 0.02;

      // Smooth SLERP Vector interpolation
      if (vectorArrowRef.current) {
        currentVectorRef.current.lerp(targetVectorRef.current, 0.14);
        const len = currentVectorRef.current.length();

        if (len > 0.001) {
          const dir = currentVectorRef.current.clone().normalize();
          vectorArrowRef.current.setDirection(dir);
          vectorArrowRef.current.setLength(len, 0.15, 0.08);

          if (tipGlowMeshRef.current) {
            tipGlowMeshRef.current.position.copy(currentVectorRef.current);
            const scale = 1 + Math.sin(clockTime * 4) * 0.2;
            tipGlowMeshRef.current.scale.set(scale, scale, scale);
          }

          if (dropLineRef.current) {
            const tip = currentVectorRef.current;
            const proj = new THREE.Vector3(tip.x, 0, tip.z);
            const pts = [tip, proj, new THREE.Vector3(0, 0, 0)];
            dropLineRef.current.geometry.setFromPoints(pts);
            dropLineRef.current.computeLineDistances();
          }

          if (projDiscRef.current) {
            projDiscRef.current.position.set(currentVectorRef.current.x, 0, currentVectorRef.current.z);
          }
        }
      }

      // Auto rotation mode
      if (autoRotateRef.current) {
        spherical.theta += 0.006;
        camera.position.setFromSpherical(spherical);
        camera.lookAt(0, 0, 0);
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 420;
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

  // Update target coordinates
  useEffect(() => {
    const x3 = coords.x;
    const y3 = coords.z; // Z is UP in 3D
    const z3 = -coords.y;

    targetVectorRef.current.set(x3, y3, z3);

    if (vectorArrowRef.current) {
      if (coords.purity > 0.95) {
        vectorArrowRef.current.setColor(0x1B4B8A);
        if (tipGlowMeshRef.current) {
          (tipGlowMeshRef.current.material as THREE.MeshBasicMaterial).color.setHex(0x1B4B8A);
        }
      } else {
        vectorArrowRef.current.setColor(0xB8860B);
        if (tipGlowMeshRef.current) {
          (tipGlowMeshRef.current.material as THREE.MeshBasicMaterial).color.setHex(0xB8860B);
        }
      }
    }
  }, [coords]);

  const thetaDeg = ((coords.theta * 180) / Math.PI).toFixed(1);
  const phiDeg = ((coords.phi * 180) / Math.PI).toFixed(1);
  const purityPct = (coords.purity * 100).toFixed(0);
  const isEntangled = coords.purity < 0.95;

  const toggleAutoRotate = () => {
    const next = !isAutoRotating;
    setIsAutoRotating(next);
    autoRotateRef.current = next;
  };

  const resetCamera = () => {
    if (cameraRef.current) {
      cameraRef.current.position.set(2.6, 2.0, 2.8);
      cameraRef.current.lookAt(0, 0, 0);
    }
  };

  return (
    <div className="relative w-full h-[460px] paper-card rounded-xl overflow-hidden flex flex-col group">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b pencil-divider bg-paper-warm z-10">
        <h2 className="section-title">Bloch Sphere Representation</h2>

        {/* Qubit Selector Tabs */}
        <div className="flex items-center gap-1.5 bg-paper p-1 rounded border border-pencil">
          {Array.from({ length: numQubits }).map((_, q) => (
            <button
              key={q}
              onClick={() => {
                onSelectQubit(q);
                quantumAudio.playGatePulse("S");
              }}
              className={`px-3 py-1 rounded text-xs font-sans font-medium transition-all flex items-center gap-1 ${
                activeQubit === q
                  ? "bg-ink-blue text-paper-warm shadow-sm scale-105"
                  : "text-ink-faint hover:text-ink hover:bg-paper-warm"
              }`}
            >
              <span>q{q}</span>
              {blochCoords[q] && blochCoords[q].purity < 0.95 && (
                <span className="w-1.5 h-1.5 rounded-full bg-ink-amber animate-pulse" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 3D Three.js WebGL Stage */}
      <div
        ref={containerRef}
        className="w-full flex-1 cursor-grab active:cursor-grabbing relative bg-paper"
      />

      {/* Floating Tactical Overlay: Polar Angles & Pure/Mixed Badge */}
      <div className="absolute top-14 left-4 pointer-events-none text-sm font-sans bg-paper-warm px-3 py-2 rounded border border-pencil shadow-card">
        <div className="text-ink font-medium flex items-center gap-1.5 border-b border-pencil pb-1 mb-1">
          <Compass className="w-4 h-4" />
          <span>Coordinates</span>
        </div>
        <div className="text-ink font-serif text-base">
          θ = <strong>{thetaDeg}°</strong>, φ = <strong>{phiDeg}°</strong>
        </div>
      </div>

      <div className="absolute top-14 right-4 pointer-events-none text-sm font-sans bg-paper-warm px-3 py-2 rounded border border-pencil shadow-card text-right">
        <div className="text-ink-faint font-medium flex items-center justify-end gap-1.5 border-b border-pencil pb-1 mb-1">
          <Activity className="w-4 h-4 text-ink" />
          <span>Purity</span>
        </div>
        <div className="flex items-center justify-end gap-2 font-serif text-base">
          <span
            className={`font-semibold ${
              isEntangled ? "text-ink-amber" : "text-ink-teal"
            }`}
          >
            {isEntangled ? "Mixed State" : "Pure State"}
          </span>
          <span className="text-ink-faint text-xs font-sans">({purityPct}%)</span>
        </div>
      </div>

      {/* Quick State Presets & View Controls */}
      <div className="px-5 py-3 bg-paper-warm border-t border-pencil flex flex-wrap items-center justify-between gap-3 text-sm z-10">
        {/* Pauli Expectations */}
        <div className="flex items-center gap-4 text-ink-faint font-sans">
          <div className="flex items-center gap-1.5">
            <span>⟨X⟩:</span>
            <span className="font-mono bg-paper px-2 py-0.5 rounded border border-pencil text-ink-red">
              {coords.x.toFixed(3)}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span>⟨Y⟩:</span>
            <span className="font-mono bg-paper px-2 py-0.5 rounded border border-pencil text-ink-teal">
              {coords.y.toFixed(3)}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span>⟨Z⟩:</span>
            <span className="font-mono bg-paper px-2 py-0.5 rounded border border-pencil text-ink-blue">
              {coords.z.toFixed(3)}
            </span>
          </div>
        </div>

        {/* View Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleAutoRotate}
            className={`ink-btn flex items-center gap-1.5 ${
              isAutoRotating ? "bg-ink-faint/10" : ""
            }`}
          >
            <Eye className="w-4 h-4" />
            <span>Auto Orbit</span>
          </button>
          <button
            onClick={resetCamera}
            className="ink-btn flex items-center justify-center p-2"
            title="Reset Camera View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
