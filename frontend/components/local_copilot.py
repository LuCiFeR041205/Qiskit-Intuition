import json

import streamlit.components.v1 as components


# ── Easy Edit Zone ──
# Tweak these values when you want to contribute to A.C.E.'s model, tone, or UI copy.
ACE_MODEL_ID = "onnx-community/Qwen2.5-0.5B-Instruct"
ACE_TRANSFORMERS_CDN = "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0"
ACE_HEADER_TITLE = "A.C.E. LOCAL LLM"
ACE_READY_LABEL = "MODEL READY"
ACE_LOADED_LABEL = "LOCAL LLM READY"
ACE_LOADING_LABEL = "LOADING MODEL"
ACE_FALLBACK_LABEL = "FALLBACK"
ACE_INPUT_PLACEHOLDER = "Ask about gates, Qiskit, or circuits..."
ACE_WELCOME_MESSAGE = (
    "Greetings Explorer. I am A.C.E., a local language model copilot. "
    "I can use the current lesson, visual circuit, and sandbox preview without any API key."
)

ACE_SYSTEM_PROMPT = """You are A.C.E. (Advanced Copilot Engine), a helpful local AI tutor inside a Qiskit learning lab.
Explain quantum computing clearly, physically, and concisely.
Use short Qiskit examples when helpful.
Address the learner as Explorer.
Treat the user's latest message as the main task. Do not keep answering an older topic unless the user asks you to.
You may only claim to see the visual circuit when the provided Current Lab Context says what is in the circuit.
If the user asks about the current lesson, visual circuit, or sandbox code, answer from Current Lab Context first.
When explaining the S gate: it is a phase gate. It leaves |0> unchanged and maps |1> to i|1>. It does not flip |0> to |1>.
If you are uncertain, say what to test in the lab rather than pretending.
Ensure you offer code examples when the user asks about specific gates, circuits, or Qiskit functions.
Do not use Markdown headings, hashtags, tables, or bold markers. Keep formatting clean and simple, but include symbols as needed.
Use plain state notation like |0>, |1>, |+>, and i|1>. Avoid LaTeX commands.
Answer in 2-5 short paragraphs or bullets. Finish every response with one useful next action when appropriate."""

ACE_GENERATION_SETTINGS = {
    "max_new_tokens": 320,
    "temperature": 0.35,
    "top_p": 0.85,
    "repetition_penalty": 1.25,
}


def render_local_copilot(height=600, compact=False, lab_context="No live circuit context is available."):
    """
    Renders an offline AI Copilot directly in the browser.
    No API keys required. Loads a quantized local model in WebGPU-capable browsers.
    """
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>A.C.E.</title>
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
                font-size: 18px;
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
                background: #050a15;
                color: var(--text);
                border: 1px solid rgba(101, 244, 212, 0.5);
                padding: 0 20px;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.2s;
            }
            button:hover {
                background: rgba(0, 240, 255, 0.14);
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
                <div>__ACE_HEADER_TITLE__</div>
                <div class="status-indicator" id="status-badge">__ACE_READY_LABEL__</div>
            </div>
            <div class="progress-container" id="progress-container">
                <div class="progress-text" id="progress-text">Model loads on first message.</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="progress-bar"></div>
                </div>
            </div>
            <div class="chat-history" id="chat">
                <div class="message msg-ai">__ACE_WELCOME_MESSAGE__</div>
            </div>
            <div class="input-area">
                <input type="text" id="user-input" placeholder="__ACE_INPUT_PLACEHOLDER__">
                <button id="send-btn">SEND</button>
            </div>
        </div>

        <script type="module">
            import { pipeline } from "__ACE_TRANSFORMERS_CDN__";

            // Contributor knobs copied from the Python Easy Edit Zone above.
            const MODEL_ID = __ACE_MODEL_ID_JSON__;
            const SYSTEM_PROMPT = __ACE_SYSTEM_PROMPT_JSON__;
            const LAB_CONTEXT = __ACE_LAB_CONTEXT_JSON__;
            const READY_LABEL = __ACE_LOADED_LABEL_JSON__;
            const LOADING_LABEL = __ACE_LOADING_LABEL_JSON__;
            const FALLBACK_LABEL = __ACE_FALLBACK_LABEL_JSON__;
            const GENERATION_SETTINGS = {
                max_new_tokens: __ACE_MAX_NEW_TOKENS__,
                temperature: __ACE_TEMPERATURE__,
                top_p: __ACE_TOP_P__,
                repetition_penalty: __ACE_REPETITION_PENALTY__,
            };

            const chatDiv = document.getElementById('chat');
            const inputEl = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const statusBadge = document.getElementById('status-badge');
            const progressContainer = document.getElementById('progress-container');
            const progressText = document.getElementById('progress-text');
            const progressBar = document.getElementById('progress-bar');

            let generatorPromise = null;
            let modelFailed = false;
            let chatHistory = [];

            function addMessage(role, text) {
                const msg = document.createElement('div');
                msg.className = `message ${role === 'user' ? 'msg-user' : 'msg-ai'}`;
                msg.textContent = text;
                chatDiv.appendChild(msg);
                chatDiv.scrollTop = chatDiv.scrollHeight;
                return msg;
            }

            function setStatus(text, ready = false) {
                statusBadge.textContent = text;
                statusBadge.classList.toggle('ready', ready);
            }

            function updateProgress(data) {
                progressContainer.style.display = 'block';

                if (typeof data?.progress === 'number') {
                    const pct = Math.max(0, Math.min(100, data.progress));
                    progressBar.style.width = `${pct}%`;
                    progressText.textContent = `Loading ${data.file || 'model'}: ${pct.toFixed(0)}%`;
                    return;
                }

                progressText.textContent = `Loading ${data?.file || data?.status || 'model files'}...`;
            }

            function buildFallbackResponse(text) {
                const q = text.toLowerCase();

                if (q.includes('hadamard') || q.includes(' h ') || q.includes('superposition')) {
                    return 'A Hadamard gate is the standard superposition move. From |0>, it creates |+>, an even blend of |0> and |1>. Use H when you want probability to split before interference or before a CNOT can create entanglement.';
                }
                if (q.includes('cnot') || q.includes('cx') || q.includes('entangle')) {
                    return 'CNOT is the main two-qubit linking gate. The control qubit decides whether the target flips. If the control is already in superposition, CNOT can create correlated outcomes such as 00 and 11.';
                }
                if (q.includes('measure') || q.includes('measurement') || q.includes('shots')) {
                    return 'Measurement turns amplitudes into classical results. A statevector shows the exact pre-measurement quantum state; shots show repeated sampled outcomes, so the counts can wobble even when the underlying probabilities are clean.';
                }
                if (q.includes('phase') || q.includes('z gate') || q.includes('rz') || q.includes('s gate') || q.includes('t gate')) {
                    return 'Phase gates usually do not change immediate 0/1 probabilities by themselves. They change relative phase. The S gate leaves |0> unchanged and maps |1> to i|1>; later gates like H can turn that hidden phase into visible interference.';
                }
                if (q.includes('qiskit') || q.includes('code') || q.includes('python')) {
                    return 'Qiskit is a Python toolkit for building quantum circuits. Read Qiskit code as a circuit recipe: import tools, create a QuantumCircuit, apply gates in order, then simulate, inspect the state, or measure.';
                }
                if (q.includes('bloch')) {
                    return 'The Bloch sphere shows one qubit as a direction. North is |0>, south is |1>, the equator is balanced superposition, and rotation around the vertical axis changes phase without immediately changing 0/1 odds.';
                }
                if (q.includes('what should i do') || q.includes('next') || q.includes('practice')) {
                    return 'A good next experiment is: add H on q0, add CNOT from q0 to q1, then inspect probabilities. Before running it, predict which basis states should appear and why.';
                }

                return 'I can still help offline. Ask about a specific gate, circuit, lesson, or Qiskit line and I will ground the answer in the current lab context.';
            }

            function answerKnownTutorQuestion(text) {
                const q = text.toLowerCase();

                if (q.includes('what is qiskit') || q === 'qiskit' || q.includes('explain qiskit')) {
                    return 'Qiskit is an open-source Python toolkit for building and studying quantum circuits. In this lab, think of a QuantumCircuit as the recipe, gates as physical instructions placed on qubits, and simulators as the oven that lets you inspect the result. Try this next: build H on q0 in the Composer, then compare the exported Qiskit code with the visual gate.';
                }

                if (q.includes('what is a qubit') || q.includes('explain qubit')) {
                    return 'A qubit is a two-level quantum system. Unlike a classical bit, it can point anywhere on the Bloch sphere before measurement. The north pole is |0>, the south pole is |1>, and the equator represents balanced superpositions. Try this next: move the Bloch sliders and predict how theta changes measurement odds.';
                }

                if (q.includes('superposition')) {
                    return 'Superposition means the qubit state is not pinned to only |0> or only |1>. It has amplitudes for possible measurement outcomes. The key point is that those amplitudes can interfere later, so superposition is not just classical uncertainty. Try this next: apply H to |0>, then apply H again and watch it return to |0>.';
                }

                if (q.includes('entanglement') || q.includes('entangled')) {
                    return 'Entanglement is shared quantum state. The pair can have a clean structure even when each individual qubit no longer has a pure Bloch vector. A common recipe is H on q0, then CNOT q0 -> q1, creating correlated outcomes. Try this next: build that circuit and look for 00 and 11 probabilities.';
                }

                if (q.includes('s gate')) {
                    return 'The S gate is a phase gate, not a flip. It leaves |0> unchanged and maps |1> to i|1>. By itself it usually does not change measurement odds, but it changes interference when a later gate like H mixes phase back into probability. Try this next: compare H-S-H with just H.';
                }

                if (q.includes('why') && (q.includes('probability') || q.includes('counts'))) {
                    return 'Probabilities come from amplitudes, while counts come from repeated samples. A perfect 50/50 state will not always produce perfectly equal counts because sampling has randomness. Try this next: run the same circuit with more shots and watch the distribution stabilize.';
                }

                return null;
            }

            function answerCircuitVisibilityQuestion(text) {
                const q = text.toLowerCase();
                const isVisibilityQuestion =
                    q.includes('can you see') ||
                    q.includes('do you see') ||
                    q.includes('just added') ||
                    q.includes('visual circuit') ||
                    q.includes('current circuit');

                if (!isVisibilityQuestion) {
                    return null;
                }

                const context = LAB_CONTEXT.trim();
                if (!context || context.toLowerCase().includes('no gates')) {
                    return 'I can only see the circuit state that the app passes into this sidebar. Right now that context says there are no gates in the visual circuit.';
                }

                if ((q.includes('s gate') || q.includes(' s ')) && context.includes('S')) {
                    return `Yes. The current visual circuit context includes an S gate: ${context}. The S gate is a phase gate: it leaves |0> unchanged and maps |1> to i|1>.`;
                }

                return `I can see the circuit context the app passed to me: ${context}.`;
            }

            function answerLabContextQuestion(text) {
                const q = text.toLowerCase();
                const context = LAB_CONTEXT.trim();
                if (!context) {
                    return null;
                }

                if (q.includes('current lesson') || q.includes('what lesson') || q.includes('which module')) {
                    const lessonLine = context.split('\\n').find((line) => line.startsWith('Current lesson:'));
                    const ideaLine = context.split('\\n').find((line) => line.startsWith('Lesson big idea:'));
                    return [lessonLine, ideaLine].filter(Boolean).join(' ');
                }

                if (q.includes('sandbox') || q.includes('my code') || q.includes('current code')) {
                    const sandboxLine = context.split('\\n').find((line) => line.startsWith('Sandbox preview:'));
                    return sandboxLine
                        ? `I can see this sandbox preview from the app: ${sandboxLine.replace('Sandbox preview: ', '')}`
                        : null;
                }

                return null;
            }

            function buildPrompt(userText) {
                const recentTurns = chatHistory.slice(-4);
                const formattedTurns = recentTurns
                    .map((msg) => `<|im_start|>${msg.role}\\n${msg.content}<|im_end|>`)
                    .join('\\n');

                return `<|im_start|>system\\n${SYSTEM_PROMPT}\\n\\nCurrent Lab Context:\\n${LAB_CONTEXT}<|im_end|>\\n${formattedTurns}\\n<|im_start|>user\\n${userText}<|im_end|>\\n<|im_start|>assistant\\n`;
            }

            function cleanGeneratedText(text, prompt) {
                let cleaned = String(text || '');

                if (cleaned.startsWith(prompt)) {
                    cleaned = cleaned.slice(prompt.length);
                }

                return cleaned
                    .replaceAll('<|im_end|>', '')
                    .replaceAll('<|endoftext|>', '')
                    .replace(/^assistant\\s*/i, '')
                    .replace(/^#{1,6}\\s*/gm, '')
                    .replace(/\\*\\*/g, '')
                    .trim();
            }

            async function getGenerator() {
                if (!navigator.gpu) {
                    throw new Error('WebGPU is not available in this browser.');
                }

                if (!generatorPromise) {
                    setStatus(LOADING_LABEL);
                    progressContainer.style.display = 'block';
                    progressBar.style.width = '3%';
                    generatorPromise = pipeline('text-generation', MODEL_ID, {
                        device: 'webgpu',
                        dtype: 'q4',
                        progress_callback: updateProgress,
                    });
                }

                const generator = await generatorPromise;
                setStatus(READY_LABEL, true);
                progressText.textContent = `${MODEL_ID} loaded locally.`;
                progressBar.style.width = '100%';
                return generator;
            }

            async function generateWithLocalModel(text) {
                const generator = await getGenerator();
                const prompt = buildPrompt(text);
                const output = await generator(prompt, {
                    ...GENERATION_SETTINGS,
                    do_sample: true,
                    return_full_text: false,
                });

                const generatedText = Array.isArray(output)
                    ? output[0]?.generated_text
                    : output?.generated_text;

                return cleanGeneratedText(generatedText, prompt) || buildFallbackResponse(text);
            }

            async function handleSend() {
                const text = inputEl.value.trim();
                if (!text) return;

                inputEl.value = '';
                inputEl.disabled = true;
                sendBtn.disabled = true;
                
                addMessage('user', text);

                const responseDiv = addMessage(
                    'assistant',
                    modelFailed ? 'Thinking with fallback...' : 'Loading local model...'
                );

                try {
                    const groundedCircuitAnswer = answerCircuitVisibilityQuestion(text);
                    const groundedLabAnswer = answerLabContextQuestion(text);
                    const knownTutorAnswer = answerKnownTutorQuestion(text);
                    const generatedText = modelFailed
                        ? buildFallbackResponse(text)
                        : groundedCircuitAnswer
                            ? groundedCircuitAnswer
                            : groundedLabAnswer
                                ? groundedLabAnswer
                                : knownTutorAnswer
                                    ? knownTutorAnswer
                                    : await generateWithLocalModel(text);

                    responseDiv.textContent = generatedText;
                    chatHistory.push({ role: 'user', content: text });
                    chatHistory.push({ role: 'assistant', content: generatedText });
                } catch (error) {
                    console.warn('Local model unavailable, using fallback:', error);
                    modelFailed = true;
                    setStatus(FALLBACK_LABEL);
                    progressText.textContent = 'WebGPU model unavailable in this browser. Using offline fallback.';
                    progressBar.style.width = '0%';

                    const fallbackText = buildFallbackResponse(text);
                    responseDiv.textContent = fallbackText;
                    chatHistory.push({ role: 'user', content: text });
                    chatHistory.push({ role: 'assistant', content: fallbackText });
                } finally {
                    inputEl.disabled = false;
                    sendBtn.disabled = false;
                    inputEl.focus();
                }
            }

            sendBtn.addEventListener('click', handleSend);
            inputEl.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleSend();
            });

            progressContainer.style.display = 'block';
            progressText.textContent = 'Model loads on first message.';
            progressBar.style.width = '0%';
            statusBadge.classList.add('ready');
            inputEl.focus();
        </script>
    </body>
    </html>
    """
    replacements = {
        "__COMPACT_CLASS__": "compact" if compact else "",
        "__ACE_HEADER_TITLE__": ACE_HEADER_TITLE,
        "__ACE_READY_LABEL__": ACE_READY_LABEL,
        "__ACE_WELCOME_MESSAGE__": ACE_WELCOME_MESSAGE,
        "__ACE_INPUT_PLACEHOLDER__": ACE_INPUT_PLACEHOLDER,
        "__ACE_TRANSFORMERS_CDN__": ACE_TRANSFORMERS_CDN,
        "__ACE_MODEL_ID_JSON__": json.dumps(ACE_MODEL_ID),
        "__ACE_SYSTEM_PROMPT_JSON__": json.dumps(ACE_SYSTEM_PROMPT),
        "__ACE_LAB_CONTEXT_JSON__": json.dumps(lab_context),
        "__ACE_LOADED_LABEL_JSON__": json.dumps(ACE_LOADED_LABEL),
        "__ACE_LOADING_LABEL_JSON__": json.dumps(ACE_LOADING_LABEL),
        "__ACE_FALLBACK_LABEL_JSON__": json.dumps(ACE_FALLBACK_LABEL),
        "__ACE_MAX_NEW_TOKENS__": str(ACE_GENERATION_SETTINGS["max_new_tokens"]),
        "__ACE_TEMPERATURE__": str(ACE_GENERATION_SETTINGS["temperature"]),
        "__ACE_TOP_P__": str(ACE_GENERATION_SETTINGS["top_p"]),
        "__ACE_REPETITION_PENALTY__": str(ACE_GENERATION_SETTINGS["repetition_penalty"]),
    }
    for placeholder, value in replacements.items():
        html_code = html_code.replace(placeholder, value)

    components.html(html_code, height=height, scrolling=compact)
