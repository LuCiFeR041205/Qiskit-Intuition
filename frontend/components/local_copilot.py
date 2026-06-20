import streamlit.components.v1 as components

def render_local_copilot(height=600, compact=False):
    """
    Renders an offline AI Copilot directly in the browser.
    No API keys required. Uses local intent rules so it stays reliable on Spaces.
    """
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>A.C.E. Offline Copilot</title>
        <style>
            :root {
                --bg: #050a15;
                --panel: rgba(10, 26, 25, 0.95);
                --border: rgba(101, 244, 212, 0.3);
                --cyan: #00F0FF;
                --pink: #ff0055;
                --text: #eafffa;
            }
            body {
                margin: 0;
                padding: 12px;
                font-family: 'Inter', -apple-system, sans-serif;
                background-color: transparent;
                color: var(--text);
                height: 100vh;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
            }
            .copilot-container {
                flex-grow: 1;
                background: linear-gradient(145deg, rgba(6,17,15,0.9), rgba(19,18,36,0.9));
                border: 1px solid var(--border);
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                box-shadow: 0 0 20px rgba(0, 240, 255, 0.1);
                overflow: hidden;
                position: relative;
            }
            .header {
                padding: 12px 16px;
                background: rgba(0, 240, 255, 0.05);
                border-bottom: 1px solid var(--border);
                font-family: 'Courier New', monospace;
                font-weight: bold;
                color: var(--cyan);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .status-indicator {
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 12px;
                background: rgba(255, 0, 85, 0.2);
                color: var(--pink);
                border: 1px solid var(--pink);
            }
            .status-indicator.ready {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border: 1px solid #00ff88;
            }
            .chat-history {
                flex-grow: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .message {
                max-width: 85%;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.5;
            }
            .msg-user {
                align-self: flex-end;
                background: rgba(0, 240, 255, 0.15);
                border: 1px solid rgba(0, 240, 255, 0.3);
                border-bottom-right-radius: 0;
            }
            .msg-ai {
                align-self: flex-start;
                background: rgba(255, 0, 85, 0.1);
                border: 1px solid rgba(255, 0, 85, 0.3);
                border-bottom-left-radius: 0;
            }
            .input-area {
                padding: 16px;
                background: rgba(0,0,0,0.4);
                border-top: 1px solid var(--border);
                display: flex;
                gap: 8px;
            }
            input {
                flex-grow: 1;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(101, 244, 212, 0.5);
                color: white;
                padding: 10px 14px;
                border-radius: 6px;
                outline: none;
                font-family: inherit;
                transition: 0.3s;
            }
            input:focus {
                border-color: var(--cyan);
                box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
            }
            button {
                background: var(--cyan);
                color: #000;
                border: none;
                padding: 0 20px;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.2s;
            }
            button:hover {
                box-shadow: 0 0 15px var(--cyan);
                transform: scale(1.02);
            }
            button:disabled {
                background: #555;
                color: #999;
                cursor: not-allowed;
                box-shadow: none;
            }
            .progress-container {
                padding: 10px 16px;
                background: rgba(0, 240, 255, 0.05);
                border-bottom: 1px solid var(--border);
                display: none;
            }
            .progress-text {
                font-size: 11px;
                color: var(--cyan);
                margin-bottom: 4px;
                font-family: monospace;
            }
            .progress-bar-bg {
                height: 4px;
                background: rgba(255,255,255,0.1);
                border-radius: 2px;
                overflow: hidden;
            }
            .progress-bar-fill {
                height: 100%;
                background: var(--cyan);
                width: 0%;
                transition: width 0.2s;
            }
            body.compact {
                padding: 0;
                height: 100vh;
            }
            body.compact .copilot-container {
                border-radius: 8px;
                box-shadow: none;
            }
            body.compact .header {
                padding: 8px 10px;
                font-size: 12px;
            }
            body.compact .status-indicator {
                font-size: 9px;
                padding: 3px 6px;
            }
            body.compact .chat-history {
                padding: 10px;
                gap: 8px;
            }
            body.compact .message {
                max-width: 100%;
                padding: 8px 10px;
                font-size: 12px;
                line-height: 1.4;
            }
            body.compact .input-area {
                padding: 10px;
                display: grid;
                grid-template-columns: 1fr;
            }
            body.compact input {
                min-width: 0;
                padding: 9px 10px;
                font-size: 12px;
            }
            body.compact button {
                min-height: 34px;
                padding: 0 12px;
                font-size: 12px;
            }
            body.compact .progress-container {
                padding: 8px 10px;
            }
        </style>
    </head>
    <body class="__COMPACT_CLASS__">
        <div class="copilot-container">
            <div class="header">
                <div>A.C.E. LOCAL</div>
                <div class="status-indicator" id="status-badge">LOCAL READY</div>
            </div>
            <div class="progress-container" id="progress-container">
                <div class="progress-text" id="progress-text">Downloading WebGPU weights (one-time)...</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="progress-bar"></div>
                </div>
            </div>
            <div class="chat-history" id="chat">
                <div class="message msg-ai">Greetings Explorer. I am A.C.E., running locally with no external account. Ask about gates, superposition, entanglement, measurement, Qiskit code, or what to try next.</div>
            </div>
            <div class="input-area">
                <input type="text" id="user-input" placeholder="Ask about gates, Qiskit, or circuits...">
                <button id="send-btn">SEND</button>
            </div>
        </div>

        <script>
            const chatDiv = document.getElementById('chat');
            const inputEl = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const statusBadge = document.getElementById('status-badge');
            const progressContainer = document.getElementById('progress-container');
            const progressText = document.getElementById('progress-text');

            let chatHistory = [
                { role: 'system', content: 'You are A.C.E. (Advanced Copilot Engine), a helpful AI assistant in a quantum computing lab built with Qiskit and Streamlit. You explain quantum concepts concisely and excitedly.' }
            ];

            function addMessage(role, text) {
                const msg = document.createElement('div');
                msg.className = `message ${role === 'user' ? 'msg-user' : 'msg-ai'}`;
                msg.textContent = text;
                chatDiv.appendChild(msg);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }

            function buildOfflineResponse(text) {
                const q = text.toLowerCase();

                if (q.includes('hadamard') || q.includes(' h ') || q.includes('superposition')) {
                    return 'A Hadamard gate is the classic superposition move: it rotates |0> toward an equal blend of |0> and |1>. In the lab, use H when you want probability to split before interference or entanglement.';
                }
                if (q.includes('cnot') || q.includes('cx') || q.includes('entangle')) {
                    return 'CNOT is the main entangling tool. The control qubit decides whether the target flips. After H on the control, CNOT can create linked outcomes where the two qubits must be described as one shared state.';
                }
                if (q.includes('measure') || q.includes('measurement') || q.includes('shots')) {
                    return 'Measurement turns quantum amplitudes into classical counts. A statevector shows the hidden amplitudes before measurement; shots show sampled outcomes after repeated measurement.';
                }
                if (q.includes('phase') || q.includes('z gate') || q.includes('rz') || q.includes('s gate') || q.includes('t gate')) {
                    return 'Phase gates usually do not change immediate 0/1 probabilities by themselves. They change relative phase, which matters when later gates make paths interfere.';
                }
                if (q.includes('qiskit') || q.includes('code') || q.includes('python')) {
                    return 'Read Qiskit code as a circuit recipe: import tools, create QuantumCircuit, apply gates in order, then simulate, inspect, or measure. The visual composer and exported code should match line by line.';
                }
                if (q.includes('bloch')) {
                    return 'The Bloch sphere shows a single qubit as a direction. North is |0>, south is |1>, the equator is balanced superposition, and rotation around the vertical axis changes phase.';
                }
                if (q.includes('what should i do') || q.includes('next') || q.includes('practice')) {
                    return 'Try this: add H to q0, then CNOT from q0 to q1, then inspect probabilities. Before running it, predict which basis states should appear and which should vanish.';
                }

                return 'Offline A.C.E. can help with the core lab ideas: gates rotate qubits, phase controls interference, CNOT links qubits, and measurement turns the state into classical results. Ask me about a specific gate, circuit, or Qiskit line.';
            }

            async function handleSend() {
                const text = inputEl.value.trim();
                if (!text) return;

                inputEl.value = '';
                inputEl.disabled = true;
                sendBtn.disabled = true;
                
                addMessage('user', text);
                chatHistory.push({ role: 'user', content: text });

                // Create a placeholder for AI response
                const responseDiv = document.createElement('div');
                responseDiv.className = 'message msg-ai';
                responseDiv.textContent = 'Thinking...';
                chatDiv.appendChild(responseDiv);
                chatDiv.scrollTop = chatDiv.scrollHeight;

                window.setTimeout(() => {
                    const generatedText = buildOfflineResponse(text);
                    responseDiv.textContent = generatedText;
                    chatHistory.push({ role: 'assistant', content: generatedText });
                    inputEl.disabled = false;
                    sendBtn.disabled = false;
                    inputEl.focus();
                }, 160);
            }

            sendBtn.addEventListener('click', handleSend);
            inputEl.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleSend();
            });

            progressContainer.style.display = 'none';
            statusBadge.classList.add('ready');
            inputEl.focus();
        </script>
    </body>
    </html>
    """
    html_code = html_code.replace("__COMPACT_CLASS__", "compact" if compact else "")
    components.html(html_code, height=height, scrolling=compact)
