import html
import streamlit as st
import streamlit.components.v1 as components

def render_bloch_sphere(theta, phi, qubit_name="q"):
    """
    Renders an interactive 3D Bloch sphere using Three.js inside Streamlit.
    
    Parameters:
    - theta: Polar angle in radians (0 to PI).
    - phi: Azimuthal angle in radians (0 to 2*PI).
    - qubit_name: The name of the qubit to display on the HUD overlay.
    """
    try:
        theta = float(theta)
    except (TypeError, ValueError):
        theta = 0.0
        
    try:
        phi = float(phi)
    except (TypeError, ValueError):
        phi = 0.0

    safe_qubit_name = html.escape(str(qubit_name))

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qiskit Intuition Lab: Bloch Sphere</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background:
                linear-gradient(145deg, #06110f, #131225),
                repeating-linear-gradient(90deg, rgba(0, 240, 255, 0.06) 0 1px, transparent 1px 42px);
            color: #00F0FF;
            font-family: 'Courier New', Courier, monospace;
        }
        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        /* Glowing HUD overlays */
        .hud-overlay {
            position: absolute;
            pointer-events: none;
            font-size: 11px;
            color: rgba(0, 240, 255, 0.9);
            text-shadow: 0 0 5px rgba(0, 240, 255, 0.6);
            border: 1px solid rgba(0, 240, 255, 0.2);
            background: rgba(5, 10, 21, 0.75);
            padding: 8px 12px;
            border-radius: 2px;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.15);
        }
        .hud-title {
            top: 10px;
            left: 10px;
            border-left: 3px solid #00F0FF;
        }
        .hud-coords {
            bottom: 10px;
            left: 10px;
            border-left: 3px solid #ff0055;
        }
        .hud-angles {
            bottom: 10px;
            right: 10px;
            border-right: 3px solid #00F0FF;
            text-align: right;
        }
        .hud-legend {
            top: 10px;
            right: 10px;
            border-right: 3px solid #00ff88;
        }
        .hud-border {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            border: 1px solid rgba(0, 240, 255, 0.15);
            box-shadow: inset 0 0 30px rgba(0, 240, 255, 0.05);
        }
        .hud-corner {
            position: absolute;
            width: 10px;
            height: 10px;
            border-color: #00F0FF;
            border-style: solid;
            pointer-events: none;
        }
        .top-left { top: 5px; left: 5px; border-width: 2px 0 0 2px; }
        .top-right { top: 5px; right: 5px; border-width: 2px 2px 0 0; }
        .bottom-left { bottom: 5px; left: 5px; border-width: 0 0 2px 2px; }
        .bottom-right { bottom: 5px; right: 5px; border-width: 0 2px 2px 0; }
    </style>
</head>
<body>
    <div id="canvas-container">
        <!-- HUD Corners -->
        <div class="hud-corner top-left"></div>
        <div class="hud-corner top-right"></div>
        <div class="hud-corner bottom-left"></div>
        <div class="hud-corner bottom-right"></div>
        <div class="hud-border"></div>

        <!-- HUD Info Panels -->
        <div class="hud-overlay hud-title">
            <div>SYSTEM: QISKIT INTUITION LAB</div>
            <div>COMPONENT: 3D BLOCH SPHERE</div>
            <div style="color: #ffaa00; font-weight: bold; margin-top: 4px;">TARGET QUBIT: {qubit_name}</div>
        </div>

        <div class="hud-overlay hud-legend">
            <div style="color: #ffaa00;">● Z-AXIS (|0⟩ / |1⟩)</div>
            <div style="color: #00F0FF;">● X-AXIS (|+⟩ / |-⟩)</div>
            <div style="color: #00ff88;">● Y-AXIS (|+i⟩ / |-i⟩)</div>
            <div style="color: #ff0055; margin-top: 4px;">● STATE VECTOR |ψ⟩</div>
        </div>

        <div class="hud-overlay hud-coords">
            <div>STATE COORDINATES:</div>
            <div>X: <span id="val-x">0.000</span></div>
            <div>Y: <span id="val-y">0.000</span></div>
            <div>Z: <span id="val-z">0.000</span></div>
        </div>

        <div class="hud-overlay hud-angles">
            <div>POLAR & AZIMUTHAL:</div>
            <div>THETA (θ): <span id="val-theta">0.00°</span></div>
            <div>PHI (φ): <span id="val-phi">0.00°</span></div>
            <div style="color: rgba(0, 240, 255, 0.5); font-size: 9px; margin-top: 4px;">DRAG TO ROTATE MAIN SCENE</div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // Set coordinates from python values
        const theta = {theta};
        const phi = {phi};

        // Compute state vector components
        // x = sin(theta) * cos(phi)
        // y = sin(theta) * sin(phi)
        // z = cos(theta)
        const xVal = Math.sin(theta) * Math.cos(phi);
        const yVal = Math.sin(theta) * Math.sin(phi);
        const zVal = Math.cos(theta);

        // Render on HUD UI
        document.getElementById('val-x').textContent = xVal.toFixed(3);
        document.getElementById('val-y').textContent = yVal.toFixed(3);
        document.getElementById('val-z').textContent = zVal.toFixed(3);
        document.getElementById('val-theta').textContent = ((theta * 180) / Math.PI).toFixed(1) + "°";
        document.getElementById('val-phi').textContent = ((phi * 180) / Math.PI).toFixed(1) + "°";

        // Setup Scene
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        
        // Soft laboratory background glow
        const ambientLight = new THREE.AmbientLight(0x05152a);
        scene.add(ambientLight);

        // Core holographic accent lights
        const dirLight1 = new THREE.DirectionalLight(0x00f0ff, 0.9);
        dirLight1.position.set(5, 10, 7);
        scene.add(dirLight1);

        const dirLight2 = new THREE.DirectionalLight(0xff0055, 0.45);
        dirLight2.position.set(-5, -5, -5);
        scene.add(dirLight2);

        // Camera
        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
        camera.position.set(4, 3.5, 5.5);

        // Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        // OrbitControls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 3;
        controls.maxDistance = 15;

        // Bottom scanning grid to ground the Bloch sphere in holographic space
        const gridHelper = new THREE.GridHelper(10, 20, 0x00f0ff, 0x003344);
        gridHelper.position.y = -2.5;
        gridHelper.material.transparent = true;
        gridHelper.material.opacity = 0.2;
        scene.add(gridHelper);

        // 1. Transparent Wireframe Sphere of radius 2
        const sphereGeo = new THREE.SphereGeometry(2, 32, 24);
        const sphereMat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            wireframe: true,
            transparent: true,
            opacity: 0.075
        });
        const sphere = new THREE.Mesh(sphereGeo, sphereMat);
        scene.add(sphere);

        // Custom high-tech grid rings (Equator, XZ, YZ planes) for clean holographic look
        function createCircumferenceRing(radius, color, rotationAxis, rotationAngle) {
            const points = [];
            for (let i = 0; i <= 64; i++) {
                const angle = (i / 64) * Math.PI * 2;
                points.push(new THREE.Vector3(Math.cos(angle) * radius, Math.sin(angle) * radius, 0));
            }
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({
                color: color,
                transparent: true,
                opacity: 0.3
            });
            const line = new THREE.Line(geometry, material);
            if (rotationAxis === 'x') line.rotateX(rotationAngle);
            if (rotationAxis === 'y') line.rotateY(rotationAngle);
            if (rotationAxis === 'z') line.rotateZ(rotationAngle);
            return line;
        }

        // Equator ring (XZ plane in Three.js)
        const equator = createCircumferenceRing(2, 0x00f0ff, 'x', Math.PI / 2);
        scene.add(equator);

        // Prime meridian (vertical, XY plane in Three.js)
        const meridian1 = createCircumferenceRing(2, 0x00f0ff, 'y', 0);
        scene.add(meridian1);

        // YZ meridian (vertical, YZ plane in Three.js)
        const meridian2 = createCircumferenceRing(2, 0x00f0ff, 'y', Math.PI / 2);
        scene.add(meridian2);

        // 2. Draw Labeled X, Y, Z Axes
        // Standard Bloch Sphere convention: Z vertical, X/Y horizontal.
        // Three.js maps Y-axis to vertical. Therefore:
        // Quantum Z axis => Three.js Y
        // Quantum X axis => Three.js X
        // Quantum Y axis => Three.js Z

        function createAxis(start, end, color) {
            const points = [start, end];
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
            return new THREE.Line(geometry, material);
        }

        // Quantum X (Three.js X)
        const xAxis = createAxis(new THREE.Vector3(-2.2, 0, 0), new THREE.Vector3(2.2, 0, 0), 0x00f0ff);
        scene.add(xAxis);

        // Quantum Y (Three.js Z)
        const yAxis = createAxis(new THREE.Vector3(0, 0, -2.2), new THREE.Vector3(0, 0, 2.2), 0x00ff88);
        scene.add(yAxis);

        // Quantum Z (Three.js Y)
        const zAxis = createAxis(new THREE.Vector3(0, -2.2, 0), new THREE.Vector3(0, 2.2, 0), 0xffaa00);
        scene.add(zAxis);

        // Helper to programmatically draw high-resolution text sprites (avoids font CORS errors)
        function makeTextSprite(message, textColor, scaleX=1.2, scaleY=0.6) {
            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 128;
            const context = canvas.getContext('2d');
            
            // Console layout styling
            context.font = "Bold 36px 'Courier New', Courier, monospace";
            context.fillStyle = textColor;
            context.textAlign = "center";
            context.textBaseline = "middle";
            context.fillText(message, canvas.width / 2, canvas.height / 2);

            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ 
                map: texture, 
                transparent: true,
                depthTest: false
            });
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.scale.set(scaleX, scaleY, 1.0);
            return sprite;
        }

        // Standard quantum state representations at coordinates:
        // Top Z-axis (|0⟩)
        const labelZero = makeTextSprite("|0⟩", "#ffaa00", 1.0, 0.5);
        labelZero.position.set(0, 2.4, 0);
        scene.add(labelZero);

        // Bottom Z-axis (|1⟩)
        const labelOne = makeTextSprite("|1⟩", "#ffaa00", 1.0, 0.5);
        labelOne.position.set(0, -2.4, 0);
        scene.add(labelOne);

        // Positive X-axis (|+⟩)
        const labelPlus = makeTextSprite("|+⟩", "#00f0ff", 1.0, 0.5);
        labelPlus.position.set(2.4, 0, 0);
        scene.add(labelPlus);

        // Negative X-axis (|−⟩)
        const labelMinus = makeTextSprite("|−⟩", "#00f0ff", 1.0, 0.5);
        labelMinus.position.set(-2.4, 0, 0);
        scene.add(labelMinus);

        // Positive Y-axis (|+i⟩)
        const labelPlusI = makeTextSprite("|+i⟩", "#00ff88", 1.2, 0.6);
        labelPlusI.position.set(0, 0, 2.4);
        scene.add(labelPlusI);

        // Negative Y-axis (|-i⟩)
        const labelMinusI = makeTextSprite("|-i⟩", "#00ff88", 1.2, 0.6);
        labelMinusI.position.set(0, 0, -2.4);
        scene.add(labelMinusI);

        // 3. Render State Vector |ψ⟩
        // Quantum (x, y, z) maps to Three.js (x, z, y) based on vertical orientation mapping
        const targetX = 2 * xVal;
        const targetY = 2 * zVal;
        const targetZ = 2 * yVal;

        const targetVec = new THREE.Vector3(targetX, targetY, targetZ);
        const dir = targetVec.clone().normalize();

        // High-contrast neon pink/magenta vector line
        const vectorGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), targetVec]);
        const vectorMat = new THREE.LineBasicMaterial({ 
            color: 0xff0055, 
            linewidth: 3 
        });
        const vectorLine = new THREE.Line(vectorGeo, vectorMat);
        scene.add(vectorLine);

        // Glow indicator tip sphere
        const tipGeo = new THREE.SphereGeometry(0.08, 16, 16);
        const tipMat = new THREE.MeshBasicMaterial({ 
            color: 0xff0055,
            transparent: true,
            opacity: 0.95
        });
        const tipMesh = new THREE.Mesh(tipGeo, tipMat);
        tipMesh.position.copy(targetVec);
        scene.add(tipMesh);

        // Holographic bloom halo at vector tip
        const haloGeo = new THREE.SphereGeometry(0.18, 16, 16);
        const haloMat = new THREE.MeshBasicMaterial({
            color: 0xff0055,
            transparent: true,
            opacity: 0.35,
            blending: THREE.AdditiveBlending
        });
        const haloMesh = new THREE.Mesh(haloGeo, haloMat);
        haloMesh.position.copy(targetVec);
        scene.add(haloMesh);

        // Holographic label for state vector |ψ⟩
        const labelPsi = makeTextSprite("|ψ⟩", "#ff0055", 1.0, 0.5);
        const psiPos = targetVec.clone().add(dir.clone().multiplyScalar(0.4));
        labelPsi.position.copy(psiPos);
        scene.add(labelPsi);

        // Idle animation parameters
        let frameCount = 0;
        
        function animate() {
            requestAnimationFrame(animate);
            frameCount++;
            
            // Halo breathing pulse
            const pulse = 0.8 + 0.25 * Math.sin(frameCount * 0.05);
            haloMesh.scale.set(pulse, pulse, pulse);
            
            // Grid rotation to reflect diagnostic console scanning
            gridHelper.rotation.y += 0.0006;
            
            controls.update();
            renderer.render(scene, camera);
        }
        
        // Adaptive resizing
        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });

        // Initialize anim loop
        animate();
    </script>
</body>
</html>
"""
    # Replace placeholder parameters with exact inputs
    html_code = (html_template
                 .replace("{theta}", f"{theta:.6f}")
                 .replace("{phi}", f"{phi:.6f}")
                 .replace("{qubit_name}", safe_qubit_name))
    
    # Render full canvas component
    components.html(html_code, height=480, scrolling=False)
