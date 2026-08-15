"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Bot,
  CircuitBoard,
  Code2,
  FlaskConical,
  Plus,
  RotateCcw,
  Send,
  Sparkles,
  X,
} from "lucide-react";
import type { GateName, GateOp } from "@/lib/quantum_simulator";
import { cAbs2, simulateCircuit } from "@/lib/quantum_simulator";

type View = "learn" | "lab" | "code";
type ChatMessage = { role: "user" | "assistant"; content: string };
type FormulaKind = "qubit" | "hadamard" | "interference" | "bell";

const LESSONS = [
  {
    title: "Qubits and measurement",
    section: "Foundations",
    duration: "12 min",
    summary: "Understand what a state predicts and why one measurement is only one sample.",
    objectives: ["Read |0⟩ and |1⟩", "Connect amplitudes to probabilities", "Separate statevectors from shot counts"],
    paragraphs: [
      "A qubit has an amplitude for |0⟩ and an amplitude for |1⟩. Squaring each amplitude's magnitude gives the probability of that measurement outcome.",
      "Measurement returns one classical result. Repeating a prepared circuit estimates its distribution; it does not reveal a hidden classical value that was there all along.",
    ],
    formula: "qubit" as FormulaKind,
    checkpoint: "If P(0)=0.75, what happens to the observed fraction of zeros as the number of shots increases?",
    preset: "Ground state",
  },
  {
    title: "Superposition with H",
    section: "Single-qubit gates",
    duration: "15 min",
    summary: "Use one gate to connect a circuit diagram, statevector, and 50/50 measurement distribution.",
    objectives: ["Predict H|0⟩", "Explain 50/50 outcomes", "Show that H is its own inverse"],
    paragraphs: [
      "The Hadamard gate mixes the |0⟩ and |1⟩ amplitudes. From |0⟩, it creates an equal superposition called |+⟩.",
      "Applying H twice returns the qubit to |0⟩. The amplitudes recombine, so this is interference—not classical randomness being added and removed.",
    ],
    formula: "hadamard" as FormulaKind,
    checkpoint: "Why is one H unpredictable at measurement while two H gates give 0 with certainty?",
    preset: "Superposition",
  },
  {
    title: "Phase and interference",
    section: "Quantum behaviour",
    duration: "18 min",
    summary: "Change a hidden relative phase and then turn it into a visible measurement result.",
    objectives: ["Distinguish phase from probability", "Explain why Z can look invisible", "Build H-Z-H"],
    paragraphs: [
      "Z changes the sign of the |1⟩ amplitude. That relative phase does not change immediate computational-basis probabilities.",
      "In H-Z-H, the last H recombines the amplitude paths. They cancel for |0⟩ and reinforce for |1⟩, so phase becomes observable.",
    ],
    formula: "interference" as FormulaKind,
    checkpoint: "Why can Z matter even if the probability bars do not move immediately?",
    preset: "Interference",
  },
  {
    title: "Entanglement",
    section: "Two-qubit systems",
    duration: "20 min",
    summary: "Build a Bell state and interpret joint probabilities without the usual spooky shortcuts.",
    objectives: ["Build H then CNOT", "Read 00 and 11 jointly", "Distinguish entanglement from correlation"],
    paragraphs: [
      "Put q0 in superposition, then use it as CNOT's control. The two branches become |00⟩ and |11⟩.",
      "The pair has a precise pure state even though either qubit by itself has no pure Bloch direction. The amplitudes belong to the whole system.",
    ],
    formula: "bell" as FormulaKind,
    checkpoint: "Why can the pair be pure while each qubit viewed alone is mixed?",
    preset: "Bell state",
  },
];

const PRESETS: Record<string, { qubits: number; gates: GateOp[] }> = {
  "Ground state": { qubits: 1, gates: [] },
  Superposition: { qubits: 1, gates: [{ id: "h0", gate: "H", target: 0 }] },
  Interference: {
    qubits: 1,
    gates: [
      { id: "h1", gate: "H", target: 0 },
      { id: "z1", gate: "Z", target: 0 },
      { id: "h2", gate: "H", target: 0 },
    ],
  },
  "Bell state": {
    qubits: 2,
    gates: [
      { id: "bh", gate: "H", target: 0 },
      { id: "bcx", gate: "CNOT", target: 1, control: 0 },
    ],
  },
};

const GATES: GateName[] = ["H", "X", "Y", "Z", "S", "T", "RX", "RY", "RZ", "CNOT"];

function Ket({ value }: { value: string }) {
  const content = /^\d+$/.test(value) ? <mn>{value}</mn> : <mi>{value}</mi>;
  return <mrow><mo>|</mo>{content}<mo>⟩</mo></mrow>;
}

function MathFormula({ kind }: { kind: FormulaKind }) {
  if (kind === "qubit") {
    return (
      <math className="math-formula" display="block" aria-label="psi equals alpha ket zero plus beta ket one; probability zero equals magnitude alpha squared; probability one equals magnitude beta squared">
        <mrow>
          <Ket value="ψ" /><mo>=</mo><mi>α</mi><Ket value="0" /><mo>+</mo><mi>β</mi><Ket value="1" />
          <mspace width="1.4em" />
          <mi>P</mi><mo>(</mo><mn>0</mn><mo>)</mo><mo>=</mo><msup><mrow><mo>|</mo><mi>α</mi><mo>|</mo></mrow><mn>2</mn></msup>
          <mo>,</mo><mspace width="0.8em" />
          <mi>P</mi><mo>(</mo><mn>1</mn><mo>)</mo><mo>=</mo><msup><mrow><mo>|</mo><mi>β</mi><mo>|</mo></mrow><mn>2</mn></msup>
        </mrow>
      </math>
    );
  }

  if (kind === "hadamard") {
    return (
      <math className="math-formula" display="block" aria-label="H ket zero equals ket zero plus ket one over square root of two, equals ket plus">
        <mrow>
          <mi>H</mi><Ket value="0" /><mo>=</mo>
          <mfrac><mrow><Ket value="0" /><mo>+</mo><Ket value="1" /></mrow><msqrt><mn>2</mn></msqrt></mfrac>
          <mo>=</mo><Ket value="+" />
        </mrow>
      </math>
    );
  }

  if (kind === "interference") {
    return (
      <math className="math-formula" display="block" aria-label="H Z H ket zero equals ket one">
        <mrow><mi>H</mi><mi>Z</mi><mi>H</mi><Ket value="0" /><mo>=</mo><Ket value="1" /></mrow>
      </math>
    );
  }

  return (
    <math className="math-formula" display="block" aria-label="Bell state phi plus equals ket zero zero plus ket one one over square root of two">
      <mrow>
        <mo>|</mo><msup><mi>Φ</mi><mo>+</mo></msup><mo>⟩</mo><mo>=</mo>
        <mfrac><mrow><Ket value="00" /><mo>+</mo><Ket value="11" /></mrow><msqrt><mn>2</mn></msqrt></mfrac>
      </mrow>
    </math>
  );
}

function localCoach(question: string, code: string, gates: GateOp[]): string {
  const lower = question.toLowerCase();
  const sequence = gates.map((gate) => gate.gate).join(" → ") || "no gates";
  if (lower.includes("current circuit") || lower.includes("my circuit")) {
    const entangling = gates.some((gate) => gate.gate === "CNOT") && gates.some((gate) => gate.gate === "H");
    return `Your current circuit is ${sequence}. ${entangling ? "Because H appears before CNOT, this circuit can create entanglement rather than a simple conditional flip." : "Predict the basis-state probabilities before adding another operation."}`;
  }
  if (lower.includes("review") || lower.includes("explain my code")) {
    const notes = ["The imports select the circuit and exact-state tools."];
    if (code.includes("QuantumCircuit")) notes.push("QuantumCircuit creates the register that gates act on in order.");
    if (code.includes(".h(")) notes.push("H mixes |0⟩ and |1⟩ amplitudes.");
    if (code.includes(".cx(")) notes.push("CX conditionally flips its target and can entangle the pair when its control is in superposition.");
    if (code.includes("Statevector.from_instruction")) notes.push("Statevector evaluates the ideal pre-measurement state exactly.");
    return `${notes.join(" ")} Next: write down the expected probability dictionary, then compare it with the output.`;
  }
  if (lower.includes("bell") || lower.includes("entangl")) {
    return "Build a Bell state with H on q0 followed by CX(0, 1). The result is (|00⟩ + |11⟩)/√2: each qubit alone is mixed, while the pair is pure. Load the Bell preset and verify that 01 and 10 have zero probability.";
  }
  if (lower.includes("phase") || lower.includes("z gate")) {
    return "Relative phase changes how amplitudes combine later. Compare H-H with H-Z-H: Z does not move the immediate probability bars, but the final H converts its phase change into a deterministic |1⟩ result.";
  }
  return "Ask me to explain the current circuit, review the Qiskit code, or connect a gate to the resulting amplitudes. A useful next question is: “Why does H-Z-H end at |1⟩?”";
}

export default function Home() {
  const [view, setView] = useState<View>("learn");
  const [lessonIndex, setLessonIndex] = useState(0);
  const [numQubits, setNumQubits] = useState(2);
  const [gates, setGates] = useState<GateOp[]>(PRESETS["Bell state"].gates);
  const [selectedGate, setSelectedGate] = useState<GateName>("H");
  const [target, setTarget] = useState(0);
  const [control, setControl] = useState(0);
  const result = useMemo(() => simulateCircuit(numQubits, gates), [numQubits, gates]);
  const [code, setCode] = useState(() => simulateCircuit(2, PRESETS["Bell state"].gates).qiskitCode);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [view]);

  const loadPreset = (name: string, openLab = true) => {
    const preset = PRESETS[name];
    setNumQubits(preset.qubits);
    setGates(preset.gates.map((gate) => ({ ...gate })));
    setTarget(0);
    setControl(0);
    setCode(simulateCircuit(preset.qubits, preset.gates).qiskitCode);
    if (openLab) setView("lab");
  };

  const changeQubitCount = (count: number) => {
    setNumQubits(count);
    setGates((current) => current.filter((gate) => gate.target < count && (gate.control === undefined || gate.control < count)));
    setTarget((current) => Math.min(current, count - 1));
    setControl((current) => Math.min(current, count - 1));
  };

  const addGate = () => {
    if (selectedGate === "CNOT" && (numQubits < 2 || target === control)) return;
    const operation: GateOp = {
      id: `${selectedGate}-${Date.now()}`,
      gate: selectedGate,
      target,
      ...(selectedGate === "CNOT" ? { control } : {}),
      ...(["RX", "RY", "RZ"].includes(selectedGate) ? { angle: Math.PI / 2 } : {}),
    };
    setGates((current) => [...current, operation]);
  };

  const askCoach = async (prompt = question) => {
    const clean = prompt.trim();
    if (!clean || asking) return;
    setQuestion("");
    setMessages((current) => [...current, { role: "user", content: clean }]);
    setAsking(true);
    let reply = "";
    const apiBase = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
    if (apiBase) {
      try {
        const response = await fetch(`${apiBase}/agent/tutor`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: clean, code, gates, num_qubits: numQubits, lesson_title: LESSONS[lessonIndex].title }),
        });
        if (response.ok) reply = (await response.json()).reply;
      } catch {
        reply = "";
      }
    }
    if (!reply) reply = localCoach(clean, code, gates);
    setMessages((current) => [...current, { role: "assistant", content: reply }]);
    setAsking(false);
  };

  const probabilities = result.statevector
    .map((amplitude, index) => ({ basis: index.toString(2).padStart(numQubits, "0"), probability: cAbs2(amplitude) }))
    .filter((item) => item.probability > 0.0001);
  const lesson = LESSONS[lessonIndex];

  return (
    <div className="site-shell">
      <aside className="site-sidebar">
        <div className="site-brand">
          <span className="brand-mark">Q</span>
          <div><strong>Qiskit Intuition</strong><small>Learn by predicting and building</small></div>
        </div>
        <nav aria-label="Primary navigation">
          <button aria-current={view === "learn" ? "page" : undefined} className={view === "learn" ? "active" : ""} onClick={() => setView("learn")}><BookOpen size={18} aria-hidden="true" /><span>Course</span></button>
          <button aria-current={view === "lab" ? "page" : undefined} className={view === "lab" ? "active" : ""} onClick={() => setView("lab")}><CircuitBoard size={18} aria-hidden="true" /><span>Circuit lab</span></button>
          <button aria-current={view === "code" ? "page" : undefined} className={view === "code" ? "active" : ""} onClick={() => setView("code")}><Bot size={18} aria-hidden="true" /><span>Code coach</span></button>
        </nav>
        <div className="sidebar-progress">
          <span>Course progress</span>
          <div><i style={{ width: `${((lessonIndex + 1) / LESSONS.length) * 100}%` }} /></div>
          <small>Lesson {lessonIndex + 1} of {LESSONS.length}</small>
        </div>
        <p className="sidebar-note">The simulator works locally. Set <code>NEXT_PUBLIC_API_URL</code> to connect the Python teaching backend.</p>
      </aside>

      <main className="site-main">
        {view === "learn" && (
          <section>
            <label className="lesson-picker">
              <span>Choose a lesson</span>
              <select value={lessonIndex} onChange={(event) => setLessonIndex(Number(event.target.value))}>
                {LESSONS.map((item, index) => <option value={index} key={item.title}>{index + 1}. {item.title}</option>)}
              </select>
            </label>
            <p className="eyebrow">{lesson.section}</p>
            <h1>{lesson.title}</h1>
            <p className="lede">{lesson.summary}</p>
            <div className="meta-row"><span>Lesson {lessonIndex + 1} of {LESSONS.length}</span><span>{lesson.duration}</span><span>Includes a lab</span></div>
            <div className="learn-grid">
              <article className="prose-section">
                <h2>The core idea</h2>
                {lesson.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
                <div className="formula-card"><span>Key relationship</span><MathFormula kind={lesson.formula} /></div>
              </article>
              <aside className="objective-card">
                <h3>By the end, you can…</h3>
                <ul>{lesson.objectives.map((objective) => <li key={objective}>{objective}</li>)}</ul>
              </aside>
            </div>
            <div className="checkpoint-card"><strong>Checkpoint</strong><p>{lesson.checkpoint}</p></div>
            <div className="action-row">
              <button className="primary" onClick={() => loadPreset(lesson.preset)}><FlaskConical size={17} aria-hidden="true" /><span>Open “{lesson.preset}” in the lab</span><ArrowRight size={16} aria-hidden="true" /></button>
              <button disabled={lessonIndex === 0} onClick={() => setLessonIndex((index) => index - 1)}><ArrowLeft size={16} aria-hidden="true" />Previous</button>
              <button disabled={lessonIndex === LESSONS.length - 1} onClick={() => setLessonIndex((index) => index + 1)}>Next lesson<ArrowRight size={16} aria-hidden="true" /></button>
            </div>
          </section>
        )}

        {view === "lab" && (
          <section>
            <p className="eyebrow">Hands-on simulator</p>
            <h1>Circuit lab</h1>
            <p className="lede">Change one operation at a time. Predict first, then use the probabilities and state readouts to test the prediction.</p>
            <div className="preset-row" aria-label="Worked examples">
              {Object.keys(PRESETS).map((name) => <button key={name} onClick={() => loadPreset(name, false)}><Sparkles size={14} aria-hidden="true" />{name}</button>)}
            </div>
            <div className="builder-card">
              <div className="field"><label>Qubits</label><select value={numQubits} onChange={(event) => changeQubitCount(Number(event.target.value))}>{[1, 2, 3, 4].map((n) => <option key={n}>{n}</option>)}</select></div>
              <div className="field"><label>Gate</label><select value={selectedGate} onChange={(event) => setSelectedGate(event.target.value as GateName)}>{GATES.map((gate) => <option key={gate}>{gate}</option>)}</select></div>
              <div className="field"><label>Target</label><select value={target} onChange={(event) => setTarget(Number(event.target.value))}>{Array.from({ length: numQubits }, (_, q) => <option value={q} key={q}>q{q}</option>)}</select></div>
              {selectedGate === "CNOT" && <div className="field"><label>Control</label><select value={control} onChange={(event) => setControl(Number(event.target.value))}>{Array.from({ length: numQubits }, (_, q) => <option value={q} key={q}>q{q}</option>)}</select></div>}
              <div className="builder-actions">
                <button className="primary" disabled={selectedGate === "CNOT" && (numQubits < 2 || control === target)} onClick={addGate}><Plus size={17} aria-hidden="true" />Add gate</button>
                <button disabled={gates.length === 0} onClick={() => setGates([])} aria-label="Clear circuit"><RotateCcw size={17} aria-hidden="true" />Clear</button>
              </div>
            </div>
            <div className="circuit-strip" aria-label="Current circuit">
              {gates.length === 0 && <p>No gates yet. The register starts in |0…0⟩.</p>}
              {gates.map((gate, index) => (
                <button key={gate.id} aria-label={`Remove ${gate.gate} gate ${index + 1}`} title="Remove gate" onClick={() => setGates((current) => current.filter((item) => item.id !== gate.id))}>
                  <small>{index + 1}</small><strong>{gate.gate}</strong><span>{gate.gate === "CNOT" ? `q${gate.control} → q${gate.target}` : `q${gate.target}`}</span><X className="remove-gate" size={13} aria-hidden="true" />
                </button>
              ))}
            </div>
            <div className="result-grid">
              <article className="panel">
                <h2>Measurement probabilities</h2>
                {probabilities.map((item) => <div className="probability-row" key={item.basis}><code>|{item.basis}⟩</code><div><i style={{ width: `${item.probability * 100}%` }} /></div><span>{(item.probability * 100).toFixed(1)}%</span></div>)}
                <p className="caption">Qiskit displays q0 as the rightmost bit.</p>
              </article>
              <article className="panel">
                <h2>Single-qubit readout</h2>
                {Object.entries(result.blochAngles).map(([qubit, value]) => <div className="readout" key={qubit}><strong>q{qubit}</strong><span>{value.purity > 0.98 ? "pure" : "mixed / entangled"}</span><code>x {value.x.toFixed(2)} · y {value.y.toFixed(2)} · z {value.z.toFixed(2)}</code></div>)}
              </article>
            </div>
            <article className="explanation-card"><strong>Interpretation</strong><p>{gates.length === 0 ? "The circuit is empty, so every qubit remains in |0⟩." : `The sequence is ${gates.map((gate) => gate.gate).join(" → ")}. ${gates.some((gate) => gate.gate === "CNOT") && gates.some((gate) => gate.gate === "H") ? "A superposed control reaches CNOT, so the joint state can be entangled." : "Compare the final bars with the effect you predicted for the last gate."}`}</p></article>
            <details className="code-details">
              <summary>Matching Qiskit code</summary>
              <pre>{result.qiskitCode}</pre>
              <button className="primary" onClick={() => { setCode(result.qiskitCode); setView("code"); }}><Code2 size={17} aria-hidden="true" />Open in code coach<ArrowRight size={16} aria-hidden="true" /></button>
            </details>
          </section>
        )}

        {view === "code" && (
          <section>
            <p className="eyebrow">Context-aware help</p>
            <h1>Code coach</h1>
            <p className="lede">Review the Qiskit program that matches your circuit, then ask about a line, an error, or the underlying quantum state.</p>
            <div className="code-toolbar"><button onClick={() => setCode(result.qiskitCode)}><Code2 size={17} aria-hidden="true" />Use current circuit code</button><span>{process.env.NEXT_PUBLIC_API_URL ? "Connected to teaching backend" : "Using built-in guidance"}</span></div>
            <textarea className="code-editor" aria-label="Qiskit code" value={code} onChange={(event) => setCode(event.target.value)} spellCheck={false} />
            <div className="quick-prompts">{["Explain my code", "Review my code", "Explain my current circuit", "Give me a next exercise"].map((prompt) => <button key={prompt} onClick={() => askCoach(prompt)}><Sparkles size={14} aria-hidden="true" />{prompt}</button>)}</div>
            <div className="chat-log" aria-live="polite">{messages.length === 0 && <p className="empty-chat">The coach receives this code, the current circuit, and the selected lesson.</p>}{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`message ${message.role}`}><small>{message.role === "user" ? "You" : "Coach"}</small><p>{message.content}</p></div>)}</div>
            <div className="prompt-row"><input value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") askCoach(); }} placeholder="Ask about the code, circuit, or lesson" /><button className="primary" disabled={!question.trim() || asking} onClick={() => askCoach()}>{asking ? "Reviewing…" : <><Send size={16} aria-hidden="true" />Ask coach</>}</button></div>
          </section>
        )}
      </main>
    </div>
  );
}
