import streamlit.components.v1 as components

def render_local_copilot(height=600):
    """
    Renders an offline AI Copilot using Transformers.js directly in the browser.
    No API keys required. Runs a quantized instruction model via WebGL/WASM.
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
        </style>
    </head>
    <body>
        <div class="copilot-container">
            <div class="header">
                <div>A.C.E. OFFLINE PROTOCOL</div>
                <div class="status-indicator" id="status-badge">LOADING NEURAL CORE</div>
            </div>
            <div class="progress-container" id="progress-container">
                <div class="progress-text" id="progress-text">Downloading WebGPU weights (one-time)...</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="progress-bar"></div>
                </div>
            </div>
            <div class="chat-history" id="chat">
                <div class="message msg-ai">Greetings Explorer! I am A.C.E., running 100% locally in your browser. I don't need API keys to help you learn quantum physics. How can I assist you today?</div>
            </div>
            <div class="input-area">
                <input type="text" id="user-input" placeholder="Ask about quantum circuits..." disabled>
                <button id="send-btn" disabled>SEND</button>
            </div>
        </div>

        <script type="module">
            // Import transformers.js from CDN
            import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers';

            // Configure env to use browser cache
            env.allowLocalModels = false;
            env.useBrowserCache = true;

            const chatDiv = document.getElementById('chat');
            const inputEl = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const statusBadge = document.getElementById('status-badge');
            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');

            let generator = null;
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

            async function initModel() {
                try {
                    // Using a small instruct model for browser feasibility
                    // 'Xenova/Qwen1.5-0.5B-Chat' or 'onnx-community/gemma-3-270m-it-ONNX'
                    const modelId = 'onnx-community/gemma-3-270m-it-ONNX';
                    
                    progressContainer.style.display = 'block';
                    
                    generator = await pipeline('text-generation', modelId, {
                        dtype: 'q4', // Quantized 4-bit for smaller size/speed
                        progress_callback: (info) => {
                            if (info.status === 'progress') {
                                progressBar.style.width = `${info.progress}%`;
                                progressText.textContent = `Downloading ${info.file}: ${Math.round(info.progress)}%`;
                            } else if (info.status === 'done') {
                                progressText.textContent = `Loaded ${info.file}`;
                            }
                        }
                    });

                    progressContainer.style.display = 'none';
                    statusBadge.textContent = 'ONLINE [LOCAL]';
                    statusBadge.classList.add('ready');
                    inputEl.disabled = false;
                    sendBtn.disabled = false;
                    inputEl.focus();

                } catch (err) {
                    console.error(err);
                    statusBadge.textContent = 'ERROR LOADING';
                    progressText.textContent = 'Error: ' + err.message;
                    progressText.style.color = 'var(--pink)';
                }
            }

            async function handleSend() {
                const text = inputEl.value.trim();
                if (!text || !generator) return;

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

                try {
                    // Generate response
                    const out = await generator(chatHistory, {
                        max_new_tokens: 150,
                        temperature: 0.7,
                        top_p: 0.9,
                        repetition_penalty: 1.1
                    });
                    
                    // The output contains the full chat history if passed as array, 
                    // we extract the last generated message.
                    const generatedText = out[0].generated_text[out[0].generated_text.length - 1].content;
                    
                    responseDiv.textContent = generatedText;
                    chatHistory.push({ role: 'assistant', content: generatedText });

                } catch (err) {
                    console.error(err);
                    responseDiv.textContent = "I experienced a quantum decoherence error. Please try again.";
                }

                inputEl.disabled = false;
                sendBtn.disabled = false;
                inputEl.focus();
            }

            sendBtn.addEventListener('click', handleSend);
            inputEl.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleSend();
            });

            // Start initialization
            initModel();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=False)
