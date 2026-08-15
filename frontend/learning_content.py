"""Small, outcome-focused curriculum used by the Streamlit learning app."""

LESSONS = [
    {
        "id": "measurement",
        "number": 1,
        "title": "Qubits and measurement",
        "eyebrow": "Foundations",
        "duration": "12 min",
        "summary": "Learn what a qubit state describes and why measurement is a sample, not a peek at a hidden classical bit.",
        "objectives": [
            "Read |0⟩ and |1⟩ as computational-basis states.",
            "Separate a quantum state from a measurement outcome.",
            "Use repeated shots to estimate probabilities.",
        ],
        "explanation": [
            "A qubit is described by two complex amplitudes, one for |0⟩ and one for |1⟩. The squared magnitudes of those amplitudes add to one and set the probabilities of the two outcomes.",
            "Measurement produces one classical result. To learn a distribution, prepare and measure the same circuit many times. This is why Qiskit distinguishes an exact statevector from sampled counts.",
        ],
        "equation": "|psi> = alpha|0> + beta|1>,   P(0)=|alpha|^2,   P(1)=|beta|^2",
        "latex": r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle,\qquad P(0)=|\alpha|^2,\quad P(1)=|\beta|^2",
        "misconception": "A superposition is not a qubit rapidly switching between 0 and 1. Its amplitudes can interfere, which ordinary classical uncertainty cannot do.",
        "preset": "Start at |0>",
        "checkpoint": "If a state has P(0)=0.75, what should happen to the observed fraction of zeros as the number of shots increases?",
    },
    {
        "id": "superposition",
        "number": 2,
        "title": "Superposition with H",
        "eyebrow": "Single-qubit gates",
        "duration": "15 min",
        "summary": "Use the Hadamard gate to create balanced amplitudes and connect the circuit, statevector, and measurement view.",
        "objectives": [
            "Predict H|0⟩ and H|1⟩.",
            "Explain why balanced amplitudes give 50/50 measurement odds.",
            "Recognize that H is its own inverse.",
        ],
        "explanation": [
            "The Hadamard gate mixes the |0⟩ and |1⟩ amplitudes. Applied to |0⟩, it creates |+⟩, so both outcomes have probability one half.",
            "Apply H a second time and the amplitudes recombine to |0⟩. That reversible return is the first useful example of quantum interference.",
        ],
        "equation": "H|0> = (|0> + |1>)/sqrt(2) = |+>",
        "latex": r"H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle",
        "misconception": "H does not always create randomness. Its result depends on the input state; H applied twice cancels exactly.",
        "preset": "Superposition",
        "checkpoint": "Why does measuring after one H look random while measuring after two H gates is always 0?",
    },
    {
        "id": "phase",
        "number": 3,
        "title": "Phase and interference",
        "eyebrow": "Quantum behaviour",
        "duration": "18 min",
        "summary": "Make relative phase visible by converting it back into measurement probability.",
        "objectives": [
            "Distinguish amplitude magnitude from phase.",
            "Explain why Z may leave immediate probabilities unchanged.",
            "Build H-Z-H as a simple interference experiment.",
        ],
        "explanation": [
            "A Z gate changes the sign of the |1⟩ amplitude. On a basis state that sign is not visible in measurement probabilities, but on a superposition it changes how amplitudes combine later.",
            "In H-Z-H, the first H creates two paths, Z flips the phase of one path, and the last H recombines them. The result is |1⟩, demonstrating destructive interference for |0⟩ and constructive interference for |1⟩.",
        ],
        "equation": "H Z H |0> = |1>",
        "latex": r"HZH\,|0\rangle = |1\rangle",
        "misconception": "A gate can change the quantum state without changing the current measurement bars. Relative phase becomes observable only through interference.",
        "preset": "Interference",
        "checkpoint": "Why can Z matter even when the probability chart does not move immediately after it is applied?",
    },
    {
        "id": "entanglement",
        "number": 4,
        "title": "Entanglement and correlation",
        "eyebrow": "Two-qubit systems",
        "duration": "20 min",
        "summary": "Create a Bell state and learn why the pair has definite structure even when each qubit alone does not.",
        "objectives": [
            "Use H followed by CNOT to build a Bell state.",
            "Read joint probabilities such as 00 and 11.",
            "Separate entanglement from ordinary correlation.",
        ],
        "explanation": [
            "Start q0 in a superposition, then use it as the control of CNOT. The two branches become |00⟩ and |11⟩. Neither qubit has its own pure state, but the pair has a precise joint state.",
            "The key is not merely that the outcomes match. The amplitudes belong to the pair and preserve phase relationships that can be tested in other measurement bases.",
        ],
        "equation": "Bell state = (|00> + |11>)/sqrt(2)",
        "latex": r"|\Phi^{+}\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}",
        "misconception": "Correlated results alone do not prove entanglement. Entanglement is a property of the joint state across different possible measurement bases.",
        "preset": "Bell state",
        "checkpoint": "Why do the individual Bloch vectors shrink in a Bell state even though the two-qubit state is perfectly pure?",
    },
    {
        "id": "algorithms",
        "number": 5,
        "title": "From circuits to algorithms",
        "eyebrow": "Problem solving",
        "duration": "20 min",
        "summary": "See how useful quantum circuits prepare, transform, and amplify information rather than simply trying every answer at once.",
        "objectives": [
            "Identify state preparation, an oracle, interference, and readout.",
            "Explain amplitude amplification without the parallel-universes shortcut.",
            "Recognize when a quantum speedup claim needs a complexity comparison.",
        ],
        "explanation": [
            "Most quantum algorithms have a readable structure: prepare amplitudes, encode a problem-dependent phase, interfere paths, and measure. The algorithm succeeds when unwanted amplitudes cancel and useful ones grow.",
            "Grover search is the cleanest example. Its oracle marks a candidate by phase and its diffuser amplifies that candidate. Repeating the pair about sqrt(N) times gives a quadratic improvement over unstructured classical search.",
        ],
        "equation": "prepare -> mark phase -> interfere -> measure",
        "latex": r"|\psi\rangle \xrightarrow{\text{prepare}} O_f|\psi\rangle \xrightarrow{\text{interfere}} \text{measure}",
        "misconception": "A quantum computer does not reveal every branch of a superposition. Measurement returns one sample, so the circuit must shape the distribution first.",
        "preset": "Interference",
        "checkpoint": "What job does interference perform between an oracle and measurement?",
    },
    {
        "id": "hardware",
        "number": 6,
        "title": "Noise and real hardware",
        "eyebrow": "Execution",
        "duration": "15 min",
        "summary": "Compare ideal predictions with noisy samples and understand what transpilation changes before a circuit reaches hardware.",
        "objectives": [
            "Distinguish statevector simulation, shot noise, and device noise.",
            "Explain why connectivity and native gates matter.",
            "Use an ideal result as a baseline for hardware experiments.",
        ],
        "explanation": [
            "Real devices have imperfect gates, readout errors, and decoherence. Even an ideal simulator produces sampling variation when run with a finite number of shots; device noise adds systematic changes on top.",
            "Before execution, Qiskit transpiles a circuit into the device's supported gates and connectivity. A mathematically equivalent circuit can therefore become deeper and noisier on a particular backend.",
        ],
        "equation": "observed error = sampling variation + device noise + compilation overhead",
        "latex": r"\varepsilon_{\mathrm{observed}} \approx \varepsilon_{\mathrm{sampling}} + \varepsilon_{\mathrm{device}} + \varepsilon_{\mathrm{compile}}",
        "misconception": "Error mitigation estimates a better answer from noisy data; it does not protect quantum information the way fault-tolerant error correction does.",
        "preset": "Bell state",
        "checkpoint": "Why should you compare noisy results with an ideal simulation of the same circuit?",
    },
]


PRESETS = {
    "Start at |0>": {"qubits": 1, "gates": []},
    "Superposition": {
        "qubits": 1,
        "gates": [{"gate": "H", "target": 0, "control": None}],
    },
    "Interference": {
        "qubits": 1,
        "gates": [
            {"gate": "H", "target": 0, "control": None},
            {"gate": "Z", "target": 0, "control": None},
            {"gate": "H", "target": 0, "control": None},
        ],
    },
    "Bell state": {
        "qubits": 2,
        "gates": [
            {"gate": "H", "target": 0, "control": None},
            {"gate": "CNOT", "target": 1, "control": 0},
        ],
    },
    "GHZ state": {
        "qubits": 3,
        "gates": [
            {"gate": "H", "target": 0, "control": None},
            {"gate": "CNOT", "target": 1, "control": 0},
            {"gate": "CNOT", "target": 2, "control": 1},
        ],
    },
}


PRACTICE = [
    {
        "title": "Create a fair quantum coin",
        "level": "Foundations",
        "qubits": 1,
        "goal": "Build a one-gate circuit whose measurement probabilities are 50% for 0 and 50% for 1.",
        "hint": "Start from |0⟩ and use the gate that moves it to the Bloch-sphere equator.",
        "target": {"0": 0.5, "1": 0.5},
    },
    {
        "title": "Make phase visible",
        "level": "Interference",
        "qubits": 1,
        "goal": "Start from |0⟩ and finish at |1⟩ using H and Z, without using X.",
        "hint": "Split the amplitude, change one path's phase, then recombine the paths.",
        "target": {"0": 0.0, "1": 1.0},
        "required": ["H", "Z"],
        "forbidden": ["X"],
    },
    {
        "title": "Build a Bell pair",
        "level": "Entanglement",
        "qubits": 2,
        "goal": "Create equal probability for 00 and 11, with no probability on 01 or 10.",
        "hint": "Put the control in superposition before applying CNOT.",
        "target": {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5},
        "required": ["H", "CNOT"],
    },
]
