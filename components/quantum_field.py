import streamlit.components.v1 as components


def render_quantum_field():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');

        html, body {
            margin: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #06110f;
        }

        #scene {
            position: relative;
            width: 100vw;
            height: 100vh;
            background:
                linear-gradient(120deg, rgba(8, 22, 20, 0.95), rgba(19, 18, 36, 0.92)),
                repeating-linear-gradient(90deg, rgba(116, 244, 215, 0.07) 0 1px, transparent 1px 72px),
                repeating-linear-gradient(0deg, rgba(246, 200, 95, 0.055) 0 1px, transparent 1px 72px);
        }

        #scene::after {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(
                0deg,
                transparent 0px, transparent 2px,
                rgba(0, 240, 255, 0.018) 2px, rgba(0, 240, 255, 0.018) 4px
            );
            pointer-events: none;
            z-index: 4;
        }

        .copy {
            position: absolute;
            left: clamp(18px, 5vw, 64px);
            top: clamp(18px, 7vh, 56px);
            z-index: 5;
            max-width: 720px;
        }

        .eyebrow {
            color: #72f2d5;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        h1 {
            margin: 0;
            color: #f2fffb;
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(34px, 7vw, 80px);
            font-weight: 700;
            line-height: 0.94;
            letter-spacing: -0.02em;
            text-wrap: balance;
        }

        .cursor {
            display: inline-block;
            color: #72f2d5;
            animation: blink 0.8s step-end infinite;
            font-weight: 300;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }

        p {
            max-width: 580px;
            color: #b9d4ce;
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(13px, 1.8vw, 17px);
            line-height: 1.6;
            margin: 14px 0 0 0;
        }

        .readout {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            max-width: 540px;
            margin-top: 22px;
        }

        .tile {
            border: 1px solid rgba(114, 242, 213, 0.28);
            background: rgba(5, 14, 15, 0.7);
            color: #eafffa;
            padding: 10px 12px;
            border-radius: 6px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(10px);
            font-family: 'JetBrains Mono', monospace;
        }

        .tile strong {
            display: block;
            color: #ffd36f;
            font-size: 18px;
            line-height: 1.1;
        }

        .tile span {
            color: #9dbdb6;
            font-size: 10px;
            letter-spacing: 0.04em;
        }

        .hint {
            position: absolute;
            right: clamp(14px, 4vw, 50px);
            bottom: 14px;
            color: rgba(233, 255, 249, 0.5);
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            z-index: 5;
        }

        @media (max-width: 760px) {
            .readout { grid-template-columns: 1fr; max-width: 280px; }
            p { max-width: 90vw; }
        }
    </style>
</head>
<body>
    <div id="scene">
        <div class="copy">
            <div class="eyebrow">Qiskit Intuition Lab</div>
            <h1><span id="typed-text">Physics-first quantum composer</span><span class="cursor">▊</span></h1>
            <p>Build circuits, watch state vectors move through a 3D field, and learn Qiskit from first qubit experiments to hardware-ready workflows.</p>
            <div class="readout">
                <div class="tile"><strong>01</strong><span>learn the physics</span></div>
                <div class="tile"><strong>02</strong><span>compose circuits</span></div>
                <div class="tile"><strong>03</strong><span>export Qiskit</span></div>
            </div>
        </div>
        <div class="hint">drag the field</div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // ── Typing animation (progressive enhancement) ──
        const fullText = "Physics-first quantum composer";
        const typedEl = document.getElementById("typed-text");
        // Clear the static fallback text and re-type it
        typedEl.textContent = "";
        let charIdx = 0;
        const typeInterval = setInterval(() => {
            if (charIdx < fullText.length) {
                typedEl.textContent += fullText[charIdx];
                charIdx++;
            } else {
                clearInterval(typeInterval);
            }
        }, 50);

        // ── Three.js scene ──
        const container = document.getElementById("scene");
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x06110f, 0.05);

        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 120);
        camera.position.set(4.6, 2.8, 7.2);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.045;
        controls.enablePan = false;
        controls.minDistance = 4;
        controls.maxDistance = 11;
        controls.target.set(1.2, 0.2, 0);

        // ── Lighting ──
        scene.add(new THREE.AmbientLight(0x253d3b, 1.5));
        const key = new THREE.DirectionalLight(0x72f2d5, 1.2);
        key.position.set(5, 8, 5);
        scene.add(key);
        const fill = new THREE.DirectionalLight(0xff6f91, 0.72);
        fill.position.set(-5, -2, -3);
        scene.add(fill);

        // Breathing point light
        const breathLight = new THREE.PointLight(0x65f4d4, 0.5, 20);
        breathLight.position.set(0, 3, 0);
        scene.add(breathLight);

        // ── Grid ──
        const grid = new THREE.GridHelper(15, 30, 0x72f2d5, 0x274542);
        grid.position.y = -1.7;
        grid.material.transparent = true;
        grid.material.opacity = 0.28;
        scene.add(grid);

        // ── Orbital rings ──
        function ring(radius, color, rotation) {
            const points = [];
            for (let i = 0; i <= 160; i++) {
                const t = (i / 160) * Math.PI * 2;
                points.push(new THREE.Vector3(Math.cos(t) * radius, Math.sin(t) * radius, 0));
            }
            const geo = new THREE.BufferGeometry().setFromPoints(points);
            const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.52 });
            const line = new THREE.Line(geo, mat);
            line.rotation.set(rotation[0], rotation[1], rotation[2]);
            return line;
        }

        const rings = [
            ring(2.05, 0x72f2d5, [Math.PI / 2, 0, 0]),
            ring(2.05, 0xffd36f, [0, Math.PI / 2, 0]),
            ring(2.05, 0xff6f91, [0, 0, 0]),
            ring(3.15, 0x9fa3ff, [Math.PI / 2.3, 0.25, 0.15]),
        ];
        rings.forEach(r => scene.add(r));

        // ── Wireframe sphere ──
        const sphereGeo = new THREE.SphereGeometry(2, 48, 32);
        const sphereMat = new THREE.MeshBasicMaterial({ color: 0x72f2d5, wireframe: true, transparent: true, opacity: 0.11 });
        const sphere = new THREE.Mesh(sphereGeo, sphereMat);
        scene.add(sphere);

        // ── State vector ──
        const vectorMat = new THREE.LineBasicMaterial({ color: 0xff6f91, transparent: true, opacity: 0.95 });
        const vectorGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(1.48, 1.12, 0.72)
        ]);
        const vector = new THREE.Line(vectorGeo, vectorMat);
        scene.add(vector);

        const tip = new THREE.Mesh(
            new THREE.SphereGeometry(0.13, 24, 24),
            new THREE.MeshBasicMaterial({ color: 0xff6f91 })
        );
        tip.position.set(1.48, 1.12, 0.72);
        scene.add(tip);

        // ── Static particle cloud ──
        const staticParticles = new THREE.BufferGeometry();
        const staticPos = [];
        for (let i = 0; i < 300; i++) {
            const r = 3 + Math.random() * 5.5;
            const t = Math.random() * Math.PI * 2;
            const y = (Math.random() - 0.5) * 4.6;
            staticPos.push(Math.cos(t) * r, y, Math.sin(t) * r);
        }
        staticParticles.setAttribute("position", new THREE.Float32BufferAttribute(staticPos, 3));
        const staticCloud = new THREE.Points(staticParticles,
            new THREE.PointsMaterial({ color: 0xb8fff2, size: 0.025, transparent: true, opacity: 0.6 })
        );
        scene.add(staticCloud);

        // ── Orbiting particles (trails) ──
        const orbitCount = 40;
        const orbitData = [];
        const orbitGeo = new THREE.BufferGeometry();
        const orbitPositions = new Float32Array(orbitCount * 3);
        for (let i = 0; i < orbitCount; i++) {
            orbitData.push({
                radius: 2.2 + Math.random() * 2.8,
                speed: 0.003 + Math.random() * 0.008,
                phase: Math.random() * Math.PI * 2,
                yOffset: (Math.random() - 0.5) * 3,
                tiltX: (Math.random() - 0.5) * 0.8,
                tiltZ: (Math.random() - 0.5) * 0.8,
            });
        }
        orbitGeo.setAttribute("position", new THREE.Float32BufferAttribute(orbitPositions, 3));
        const orbitCloud = new THREE.Points(orbitGeo,
            new THREE.PointsMaterial({ color: 0xffd36f, size: 0.04, transparent: true, opacity: 0.85 })
        );
        scene.add(orbitCloud);

        // ── Mouse parallax ──
        let mouseX = 0, mouseY = 0;
        let targetX = 0, targetY = 0;
        container.addEventListener("mousemove", (e) => {
            const rect = container.getBoundingClientRect();
            mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
            mouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
        });

        // ── Animation ──
        let frame = 0;
        function animate() {
            requestAnimationFrame(animate);
            frame++;

            // Smooth parallax lerp
            targetX += (mouseX * 0.3 - targetX) * 0.04;
            targetY += (mouseY * 0.3 - targetY) * 0.04;
            staticCloud.position.x = -targetX;
            staticCloud.position.y = -targetY * 0.5;

            // Rotate scene elements
            sphere.rotation.y += 0.002;
            rings[0].rotation.z += 0.004;
            rings[1].rotation.x += 0.003;
            rings[2].rotation.y -= 0.0035;
            rings[3].rotation.z -= 0.0018;
            grid.rotation.y += 0.0008;

            // Tip pulse
            tip.scale.setScalar(1 + Math.sin(frame * 0.06) * 0.12);

            // Breathing light
            breathLight.intensity = 0.5 + Math.sin(frame * 0.025) * 0.35;

            // Update orbiting particles
            const pos = orbitGeo.attributes.position.array;
            for (let i = 0; i < orbitCount; i++) {
                const d = orbitData[i];
                const angle = d.phase + frame * d.speed;
                pos[i * 3] = Math.cos(angle) * d.radius + Math.sin(angle * 0.3) * d.tiltX;
                pos[i * 3 + 1] = d.yOffset + Math.sin(angle * 0.7) * 0.5;
                pos[i * 3 + 2] = Math.sin(angle) * d.radius + Math.cos(angle * 0.3) * d.tiltZ;
            }
            orbitGeo.attributes.position.needsUpdate = true;

            controls.update();
            renderer.render(scene, camera);
        }

        window.addEventListener("resize", () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });

        animate();
    </script>
</body>
</html>"""

    components.html(html, height=400, scrolling=False)
