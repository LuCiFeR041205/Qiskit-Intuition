import streamlit.components.v1 as components


def render_quantum_field():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {
            margin: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #06110f;
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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

        .copy {
            position: absolute;
            left: clamp(18px, 5vw, 64px);
            top: clamp(22px, 9vh, 70px);
            z-index: 5;
            max-width: 760px;
        }

        .eyebrow {
            color: #72f2d5;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        h1 {
            margin: 0;
            color: #f2fffb;
            font-size: clamp(40px, 8vw, 94px);
            line-height: 0.92;
            letter-spacing: 0;
            text-wrap: balance;
        }

        p {
            max-width: 640px;
            color: #b9d4ce;
            font-size: clamp(15px, 2vw, 19px);
            line-height: 1.6;
            margin: 18px 0 0 0;
        }

        .readout {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            max-width: 620px;
            margin-top: 26px;
        }

        .tile {
            border: 1px solid rgba(114, 242, 213, 0.28);
            background: rgba(5, 14, 15, 0.66);
            color: #eafffa;
            padding: 12px 14px;
            border-radius: 8px;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28);
            backdrop-filter: blur(10px);
        }

        .tile strong {
            display: block;
            color: #ffd36f;
            font-size: 20px;
            line-height: 1.1;
        }

        .tile span {
            color: #9dbdb6;
            font-size: 12px;
        }

        .hint {
            position: absolute;
            right: clamp(16px, 5vw, 64px);
            bottom: 20px;
            color: rgba(233, 255, 249, 0.62);
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            z-index: 5;
        }

        @media (max-width: 760px) {
            .readout {
                grid-template-columns: 1fr;
                max-width: 300px;
            }

            p {
                max-width: 92vw;
            }
        }
    </style>
</head>
<body>
    <div id="scene">
        <div class="copy">
            <div class="eyebrow">Qiskit Intuition Lab</div>
            <h1>Physics-first quantum composer</h1>
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
        const container = document.getElementById("scene");
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x06110f, 0.055);

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

        scene.add(new THREE.AmbientLight(0x253d3b, 1.5));
        const key = new THREE.DirectionalLight(0x72f2d5, 1.2);
        key.position.set(5, 8, 5);
        scene.add(key);
        const fill = new THREE.DirectionalLight(0xff6f91, 0.72);
        fill.position.set(-5, -2, -3);
        scene.add(fill);

        const grid = new THREE.GridHelper(15, 30, 0x72f2d5, 0x274542);
        grid.position.y = -1.7;
        grid.material.transparent = true;
        grid.material.opacity = 0.28;
        scene.add(grid);

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
        rings.forEach((item) => scene.add(item));

        const sphereGeo = new THREE.SphereGeometry(2, 48, 32);
        const sphereMat = new THREE.MeshBasicMaterial({
            color: 0x72f2d5,
            wireframe: true,
            transparent: true,
            opacity: 0.11
        });
        const sphere = new THREE.Mesh(sphereGeo, sphereMat);
        scene.add(sphere);

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

        const particles = new THREE.BufferGeometry();
        const positions = [];
        for (let i = 0; i < 380; i++) {
            const radius = 3 + Math.random() * 5.5;
            const theta = Math.random() * Math.PI * 2;
            const y = (Math.random() - 0.5) * 4.6;
            positions.push(Math.cos(theta) * radius, y, Math.sin(theta) * radius);
        }
        particles.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
        const particleMat = new THREE.PointsMaterial({
            color: 0xb8fff2,
            size: 0.025,
            transparent: true,
            opacity: 0.72
        });
        const particleCloud = new THREE.Points(particles, particleMat);
        scene.add(particleCloud);

        let frame = 0;
        function animate() {
            requestAnimationFrame(animate);
            frame += 1;
            sphere.rotation.y += 0.002;
            rings[0].rotation.z += 0.004;
            rings[1].rotation.x += 0.003;
            rings[2].rotation.y -= 0.0035;
            rings[3].rotation.z -= 0.0018;
            grid.rotation.y += 0.0008;
            particleCloud.rotation.y += 0.0009;
            tip.scale.setScalar(1 + Math.sin(frame * 0.06) * 0.12);
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

    components.html(html, height=470, scrolling=False)
