"""Intuition-first curriculum that teaches Qiskit from the ground up.

Every lesson moves through the same six stages:

1. Intuition  – a plain-language picture plus an interactive "feel it" widget.
2. Predict    – a multiple-choice prediction with feedback on every option.
3. Experiment – the worked circuit in the guided builder, with things to try.
4. Formalize  – the math, now that the picture exists.
5. Code it    – the Qiskit API for the idea, then an auto-checked exercise.
6. Reflect    – explain the result in your own words.

Lesson fields used by the Content Studio (title, summary, explanation, ...) are
kept flat so they stay editable; richer fields are optional at render time.
"""

UNITS = [
    {"id": "one-qubit", "title": "One qubit", "blurb": "What a qubit is, how measurement works, and how gates move the state."},
    {"id": "many-qubits", "title": "Many qubits", "blurb": "Registers, bit order, and entanglement — the part with no classical analogue."},
    {"id": "algorithms", "title": "Algorithms", "blurb": "Using interference on purpose to make the right answer likely."},
    {"id": "real-world", "title": "Real hardware & beyond", "blurb": "Noise, compilation, and trainable circuits."},
]

_IMPORTS = "from qiskit import QuantumCircuit\n"

LESSONS = [
    # ------------------------------------------------------------------ Unit 1
    {
        "id": "qubit",
        "number": 1,
        "unit": "one-qubit",
        "title": "What is a qubit?",
        "eyebrow": "Foundations",
        "duration": "10 min",
        "summary": "Start with a picture, not a formula: a qubit is an arrow on a sphere that you can never look at directly.",
        "intuition": [
            "A classical bit is a light switch. It is either off (0) or on (1), and looking at it doesn't change it.",
            "A qubit is more like an **arrow pointing somewhere on a globe**. Straight up (the north pole) is the state |0⟩, straight down is |1⟩, and every other direction is a perfectly valid state too.",
            "The catch: you never see the arrow. When you measure, the qubit only answers **0 or 1**. The closer the arrow is to the north pole, the more likely the answer is 0 — and after answering, the arrow snaps to the pole it reported.",
        ],
        "widget": {
            "type": "bloch_dial",
            "theta": 0.0,
            "caption": "Tilt the arrow away from the north pole. The sphere is the state; the bars are what a measurement would report.",
        },
        "quiz": {
            "question": "The arrow points exactly at the equator. You measure the qubit once. What do you see?",
            "options": [
                "Always 0",
                "Always 1",
                "0 or 1, each with a 50% chance",
                "A value in between, like 0.5",
            ],
            "answer": 2,
            "explanations": [
                "Only the north pole gives 0 with certainty.",
                "Only the south pole gives 1 with certainty.",
                "Right. The equator is equally far from both poles, so both answers are equally likely.",
                "Measurement always returns one classical bit, never a fraction. The 0.5 only appears as a frequency over many repeats.",
            ],
        },
        "preset": "Start at |0>",
        "try_this": [
            "The register starts at |0⟩: the arrow points up and the bar is 100% on 0.",
            "Add **X** on q0. Where did the probability go?",
            "Undo, then add **RY** with angle 0.5π. Compare the bars with the widget you just used.",
        ],
        "objectives": [
            "Picture a qubit state as an arrow on the Bloch sphere.",
            "Separate the state (the arrow) from a measurement outcome (0 or 1).",
            "Create a circuit and inspect its exact state in Qiskit.",
        ],
        "explanation": [
            "Formally, a qubit is described by two complex numbers called amplitudes, α for |0⟩ and β for |1⟩. The squared magnitudes give the measurement probabilities and always add to one.",
            "The arrow picture and the amplitudes describe the same thing: the arrow's angle from the north pole sets how |α|² and |β|² are split, and its direction around the equator records the relative phase between them (you will meet phase in Lesson 6).",
        ],
        "equation": "|psi> = alpha|0> + beta|1>,   |alpha|^2 + |beta|^2 = 1",
        "latex": r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle,\qquad |\alpha|^2 + |\beta|^2 = 1",
        "misconception": "A qubit in superposition is not secretly 0 or 1 and we just don't know which. The arrow genuinely points somewhere in between, and that difference becomes measurable through interference.",
        "qiskit": {
            "intro": "Every Qiskit program starts with a `QuantumCircuit`: an ordered list of instructions for some number of qubits. `Statevector` simulates the circuit exactly and shows the amplitudes — something real hardware can never show you.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "qc = QuantumCircuit(1)       # one qubit, starts in |0>\n"
            "state = Statevector(qc)      # exact amplitudes of the circuit's output\n\n"
            "print(qc.draw())\n"
            "print(state)\n"
            "print(state.probabilities_dict(decimals=3))\n",
            "notes": [
                ("QuantumCircuit(1)", "Create a circuit with one qubit. Qiskit always starts every qubit in |0⟩."),
                ("Statevector(qc)", "Run an exact simulation and return the amplitudes α and β."),
                ("probabilities_dict()", "Square the amplitudes to get the odds of each measurement result."),
            ],
        },
        "code_task": {
            "prompt": "Create a circuit `qc` with **two** qubits and print its statevector. How many amplitudes does it have?",
            "starter": _IMPORTS + "from qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(1)  # change me\nprint(Statevector(qc))\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(2)\n",
            "hint": "Pass the number of qubits to `QuantumCircuit(...)`. Two qubits have 2² = 4 amplitudes.",
        },
        "checkpoint": "If you could only measure a qubit, never see its arrow, how would you estimate where the arrow points?",
        "practice": 0,
    },
    {
        "id": "flip",
        "number": 2,
        "unit": "one-qubit",
        "title": "Flipping a qubit with X",
        "eyebrow": "Your first gate",
        "duration": "10 min",
        "summary": "Gates rotate the arrow. The X gate is a half-turn that swaps the poles — the quantum version of NOT.",
        "intuition": [
            "A **gate** is an action that rotates the arrow. Gates never stretch or shrink it; they only turn it.",
            "The **X gate** spins the sphere half a turn around its left-right (x) axis. The north pole lands on the south pole and vice versa, so |0⟩ ↔ |1⟩. That's exactly a classical NOT.",
            "Because X is a rotation, doing it twice brings you back where you started. Most quantum gates are reversible like this.",
        ],
        "widget": {
            "type": "gate_play",
            "gates": ["X", "Y"],
            "caption": "Press gates and watch the arrow. Try X twice. Then try Y — a half-turn around a different axis.",
        },
        "quiz": {
            "question": "You apply X three times to a qubit that starts in |0⟩. What do you measure?",
            "options": ["0 every time", "1 every time", "0 or 1 at random", "Nothing — the qubit is destroyed"],
            "answer": 1,
            "explanations": [
                "Two X gates cancel, but the third flips it again.",
                "Right. X·X does nothing, so three X's act like one: |0⟩ → |1⟩.",
                "X is a perfect half-turn between the poles; there's no randomness in its result.",
                "Gates are reversible rotations; they never destroy the qubit.",
            ],
        },
        "preset": "Flip with X",
        "try_this": [
            "The worked example applies one X: the bar moves to 100% on 1.",
            "Add a second **X**. Predict before you click.",
            "Try **Y** instead of X. Do the bars look different? (Hold that thought for Lesson 6.)",
        ],
        "objectives": [
            "Describe a gate as a rotation of the Bloch arrow.",
            "Predict the effect of X on |0⟩ and |1⟩.",
            "Apply gates to specific qubits in Qiskit.",
        ],
        "explanation": [
            "X is the matrix [[0, 1], [1, 0]]: it swaps the two amplitudes. α|0⟩ + β|1⟩ becomes β|0⟩ + α|1⟩.",
            "Every gate is a unitary matrix, which means it preserves the total probability and can be undone. Geometrically, every single-qubit gate is a rotation of the Bloch sphere.",
        ],
        "equation": "X|0> = |1>,  X|1> = |0>",
        "latex": r"X = \begin{pmatrix}0 & 1\\ 1 & 0\end{pmatrix},\qquad X|0\rangle = |1\rangle,\quad X|1\rangle = |0\rangle",
        "misconception": "X is not 'measure and flip'. It acts on the whole arrow, including superpositions: X(α|0⟩ + β|1⟩) = β|0⟩ + α|1⟩.",
        "qiskit": {
            "intro": "Gates are methods on the circuit. The argument is the index of the qubit to act on.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "qc = QuantumCircuit(1)\n"
            "qc.x(0)                      # apply X to qubit 0\n\n"
            "print(qc.draw())\n"
            "print(Statevector(qc).probabilities_dict(decimals=3))\n",
            "notes": [
                ("qc.x(0)", "Append an X gate acting on qubit 0. Gates run in the order you add them."),
                ("qc.draw()", "Text drawing of the circuit: time flows left to right."),
            ],
        },
        "code_task": {
            "prompt": "Build `qc` with one qubit that ends in |1⟩ using **three** X gates.",
            "starter": _IMPORTS + "\nqc = QuantumCircuit(1)\n# add gates here\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(1)\nqc.x(0)\nqc.x(0)\nqc.x(0)\n",
            "required_ops": ["x"],
            "hint": "Call `qc.x(0)` three times.",
        },
        "checkpoint": "Why is applying X twice the same as doing nothing?",
        "practice": 0,
    },
    {
        "id": "measurement",
        "number": 3,
        "unit": "one-qubit",
        "title": "Measurement and shots",
        "eyebrow": "Foundations",
        "duration": "12 min",
        "summary": "One measurement gives one bit. Real quantum programs run the same circuit many times — 'shots' — to learn the odds.",
        "intuition": [
            "Imagine a weighted coin. One flip tells you almost nothing about how it's weighted; a thousand flips tell you a lot.",
            "A quantum measurement is one flip. To learn where the arrow points, you **prepare the same state again and again** and measure each copy. Each run is called a **shot**.",
            "With few shots the counts are noisy; with many shots the fractions settle toward the true probabilities.",
        ],
        "widget": {
            "type": "shots",
            "p1": 0.3,
            "caption": "Set the true P(1), then change the number of shots. Re-roll to see how much the result jumps around.",
        },
        "quiz": {
            "question": "A qubit has P(0) = 0.75. You run 4 shots. Which result is impossible?",
            "options": ["3 zeros, 1 one", "4 zeros", "2 zeros, 2 ones", "None of them — all are possible"],
            "answer": 3,
            "explanations": [
                "This is the most likely result, but not the only one.",
                "Likely enough (about 32%) — four zeros is allowed.",
                "Less likely, but possible. Small samples wander.",
                "Right. Every outcome has non-zero probability. Only many shots pin the ratio down.",
            ],
        },
        "preset": "Superposition",
        "try_this": [
            "The example puts q0 on the equator. The bars show the **exact** probabilities — what infinitely many shots would give.",
            "Code it (stage 5) to see real sampled counts that wobble around these bars.",
        ],
        "objectives": [
            "Explain why one measurement cannot reveal a state.",
            "Use shots to estimate probabilities.",
            "Measure and sample a circuit with Qiskit's Sampler primitive.",
        ],
        "explanation": [
            "Measuring in the computational basis returns k with probability |amplitude_k|² and collapses the qubit to |k⟩. Repeating the experiment N times gives counts whose fractions approach the probabilities, with a typical error of about √(p(1−p)/N).",
            "That is why Qiskit separates two tools: `Statevector` (exact, simulation-only) and the `Sampler` primitive (counts from shots, which is what real hardware returns).",
        ],
        "equation": "P(k) = |<k|psi>|^2,  error ~ sqrt(p(1-p)/N)",
        "latex": r"P(k) = |\langle k|\psi\rangle|^2,\qquad \text{error} \approx \sqrt{\tfrac{p(1-p)}{N}}",
        "misconception": "Counts like 512/488 instead of 500/500 don't mean the circuit is wrong — that's shot noise. Compare to the exact probabilities before blaming the circuit.",
        "qiskit": {
            "intro": "`measure_all()` adds a measurement to every qubit. `StatevectorSampler` is a local, ideal Sampler: it returns counts just like hardware would.",
            "code": _IMPORTS
            + "from qiskit.primitives import StatevectorSampler\n\n"
            "qc = QuantumCircuit(1)\n"
            "qc.h(0)                 # put the arrow on the equator (Lesson 4)\n"
            "qc.measure_all()        # measure every qubit\n\n"
            "sampler = StatevectorSampler()\n"
            "result = sampler.run([qc], shots=1000).result()\n"
            "counts = result[0].data.meas.get_counts()\n"
            "print(counts)\n",
            "notes": [
                ("measure_all()", "Add measurements to all qubits, stored in a classical register named `meas`."),
                ("sampler.run([qc], shots=1000)", "Run the circuit 1000 times. Primitives accept a list of circuits."),
                ("result[0].data.meas.get_counts()", "Counts for the first circuit, read from the `meas` register."),
            ],
        },
        "code_task": {
            "prompt": "Prepare |1⟩, measure it, and sample 500 shots. Keep the circuit in `qc` and print the counts — every shot should read 1.",
            "starter": _IMPORTS + "from qiskit.primitives import StatevectorSampler\n\nqc = QuantumCircuit(1)\n# prepare |1>, then measure\n\n# sample and print counts\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(1)\nqc.x(0)\nqc.measure_all()\n",
            "match": "probs",
            "required_ops": ["measure"],
            "hint": "`qc.x(0)`, then `qc.measure_all()`, then copy the sampler lines from the worked example with `shots=500`.",
        },
        "checkpoint": "If a state has P(0)=0.75, what happens to the observed fraction of zeros as the number of shots grows?",
        "practice": 0,
    },
    {
        "id": "superposition",
        "number": 4,
        "unit": "one-qubit",
        "title": "Superposition with H",
        "eyebrow": "Single-qubit gates",
        "duration": "12 min",
        "summary": "The Hadamard gate tips the arrow from a pole onto the equator — and tipping it again brings it back.",
        "intuition": [
            "The **Hadamard (H)** gate is a half-turn around a diagonal axis halfway between x and z.",
            "That diagonal turn carries the north pole to the front of the equator (called |+⟩) and the south pole to the back (|−⟩). Either way, a measurement now gives 50/50.",
            "Here's the surprise: apply H again and the arrow goes **straight back** to the pole. The 'randomness' was never lost — it was a definite direction all along.",
        ],
        "widget": {
            "type": "gate_play",
            "gates": ["H", "X", "Z"],
            "caption": "Press H, then H again. Then try X → H and compare with H alone: same bars, different arrow.",
        },
        "quiz": {
            "question": "Starting from |0⟩ you apply H, then H again, then measure. What do you get?",
            "options": ["0 with 50%, 1 with 50%", "Always 0", "Always 1", "25% each for 00, 01, 10, 11"],
            "answer": 1,
            "explanations": [
                "That's what you'd see after one H. The second H undoes it.",
                "Right. H is its own inverse: H·H = identity, so the arrow returns to |0⟩.",
                "You'd need an X somewhere to end up at |1⟩.",
                "There's only one qubit, so there are only two outcomes.",
            ],
        },
        "preset": "Superposition",
        "try_this": [
            "One H puts the bars at 50/50 and the arrow on the equator.",
            "Add a second **H**. Before clicking, commit: random or certain?",
            "Clear back to one H and add **X** before it. Same bars as |+⟩ — but is it the same state? Check the statevector.",
        ],
        "objectives": [
            "Predict H|0⟩ and H|1⟩.",
            "Explain why balanced amplitudes give 50/50 odds.",
            "Recognize that H is its own inverse.",
        ],
        "explanation": [
            "H maps |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2 and |1⟩ → |−⟩ = (|0⟩ − |1⟩)/√2. Both have amplitudes of size 1/√2, so both outcomes have probability ½.",
            "The minus sign in |−⟩ is invisible to a measurement right now, but the second H turns |+⟩ back into |0⟩ and |−⟩ into |1⟩. That reversible return is your first taste of interference.",
        ],
        "equation": "H|0> = (|0> + |1>)/sqrt(2) = |+>",
        "latex": r"H|0\rangle = \tfrac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle,\qquad H|1\rangle = \tfrac{|0\rangle - |1\rangle}{\sqrt{2}} = |-\rangle",
        "misconception": "H does not 'add randomness'. It's a deterministic rotation; randomness only appears when you measure a state that sits off the poles.",
        "qiskit": {
            "intro": "Same pattern as X: `qc.h(qubit)`. Printing the `Statevector` shows the 1/√2 ≈ 0.707 amplitudes.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "plus = QuantumCircuit(1)\n"
            "plus.h(0)\n\n"
            "back = QuantumCircuit(1)\n"
            "back.h(0)\n"
            "back.h(0)\n\n"
            "print('H|0>  =', Statevector(plus))\n"
            "print('HH|0> =', Statevector(back))\n",
            "notes": [
                ("plus.h(0)", "One Hadamard: amplitudes (0.707, 0.707) — the |+⟩ state."),
                ("back.h(0) twice", "Two Hadamards cancel: amplitudes (1, 0) — back to |0⟩."),
            ],
        },
        "code_task": {
            "prompt": "Prepare the |−⟩ state = (|0⟩ − |1⟩)/√2 in `qc`. Its bars look just like |+⟩, but the checker compares the full state.",
            "starter": _IMPORTS + "\nqc = QuantumCircuit(1)\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(1)\nqc.x(0)\nqc.h(0)\n",
            "required_ops": ["h"],
            "hint": "H sends |1⟩ to |−⟩. How do you get to |1⟩ first?",
        },
        "checkpoint": "Why does measuring after one H look random, while measuring after two H gates is always 0?",
        "practice": 0,
    },
    {
        "id": "rotations",
        "number": 5,
        "unit": "one-qubit",
        "title": "Rotations: dialing in probability",
        "eyebrow": "Single-qubit gates",
        "duration": "12 min",
        "summary": "X and H are fixed half-turns. RY lets you turn the arrow by any angle — and set any probability you like.",
        "intuition": [
            "X and H are like switches with fixed positions. **RY(θ)** is a dial: it rotates the arrow by angle θ around the y axis.",
            "At θ = 0 nothing happens. At θ = π (half a turn) you reach |1⟩ — the same as X. At θ = π/2 you land on the equator — 50/50, like H.",
            "In between, the probability of reading 1 grows smoothly, following sin²(θ/2). That's how real algorithms load numbers into qubits.",
        ],
        "widget": {
            "type": "bloch_dial",
            "theta": 0.6667,
            "show_curve": True,
            "caption": "Turn the dial and watch where you land on the P(1) = sin²(θ/2) curve.",
        },
        "quiz": {
            "question": "Which angle θ makes RY(θ)|0⟩ give P(1) = 25%?",
            "options": ["θ = π/4", "θ = π/3", "θ = π/2", "θ = π"],
            "answer": 1,
            "explanations": [
                "sin²(π/8) ≈ 0.15 — too small. Probability isn't linear in the angle.",
                "Right. sin²(π/6) = (½)² = ¼.",
                "That's the equator: 50%.",
                "That's a full flip to |1⟩: 100%.",
            ],
        },
        "preset": "Tilted (RY)",
        "try_this": [
            "The example applies RY(π/3): about 75% / 25%.",
            "Add another **RY** of 0.33π on the same qubit. Rotations add: where do you end up?",
            "Find an angle that gives exactly 50/50 without using H.",
        ],
        "objectives": [
            "Relate a rotation angle to measurement probability.",
            "Explain why probability is not linear in the angle.",
            "Use parameterized rotation gates in Qiskit.",
        ],
        "explanation": [
            "RY(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩. Note the half-angle: a full turn of the arrow on the sphere corresponds to θ = 2π.",
            "RX and RZ are the same idea around the other axes. Any single-qubit gate can be built from a sequence of these rotations.",
        ],
        "equation": "RY(theta)|0> = cos(theta/2)|0> + sin(theta/2)|1>",
        "latex": r"R_Y(\theta)|0\rangle = \cos\tfrac{\theta}{2}\,|0\rangle + \sin\tfrac{\theta}{2}\,|1\rangle",
        "misconception": "Doubling the angle doesn't double the probability. P(1) = sin²(θ/2) is curved: small angles barely move the odds; angles near π/2 move them fastest.",
        "qiskit": {
            "intro": "Rotation gates take the angle first, then the qubit. Use `numpy.pi` for exact fractions of π.",
            "code": "import numpy as np\n"
            + _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "for theta in [0, np.pi / 3, np.pi / 2, np.pi]:\n"
            "    qc = QuantumCircuit(1)\n"
            "    qc.ry(theta, 0)\n"
            "    p1 = Statevector(qc).probabilities()[1]\n"
            "    print(f'theta = {theta:.3f}  ->  P(1) = {p1:.3f}')\n",
            "notes": [
                ("qc.ry(theta, 0)", "Rotate qubit 0 by angle θ (in radians) around the y axis."),
                ("probabilities()[1]", "The probability array is indexed by outcome; [1] is P(1)."),
            ],
        },
        "code_task": {
            "prompt": "Use a single `ry` gate so that `qc` measures 1 with **25%** probability.",
            "starter": "import numpy as np\n" + _IMPORTS + "\nqc = QuantumCircuit(1)\n",
            "solution": "import numpy as np\n" + _IMPORTS + "qc = QuantumCircuit(1)\nqc.ry(np.pi / 3, 0)\n",
            "match": "probs",
            "required_ops": ["ry"],
            "hint": "You want sin²(θ/2) = 0.25, so sin(θ/2) = 0.5.",
        },
        "checkpoint": "Why does RY(π/2) give 50/50 while RY(π/4) gives only about 15% for outcome 1?",
        "practice": 3,
    },
    {
        "id": "phase",
        "number": 6,
        "unit": "one-qubit",
        "title": "Phase: the hidden direction",
        "eyebrow": "Quantum behaviour",
        "duration": "14 min",
        "summary": "Spin the arrow around the equator and the measurement odds don't change at all. That invisible direction is phase.",
        "intuition": [
            "Measurement only cares about **latitude** — how far up or down the arrow points. But the arrow also has a **longitude**: which way it faces around the equator.",
            "That longitude is called the **phase**. The Z, S and T gates turn the arrow around the vertical axis by 180°, 90° and 45°. They change the phase and leave the odds untouched.",
            "So why care? Because the next gate can turn longitude into latitude. Phase is information that waits to be revealed.",
        ],
        "widget": {
            "type": "bloch_dial",
            "theta": 0.5,
            "phi": 0.0,
            "show_phi": True,
            "caption": "Hold the arrow on the equator and spin φ. The sphere changes; the bars never do.",
        },
        "quiz": {
            "question": "The qubit is in |+⟩ (on the equator). You apply Z. What happens to the measurement probabilities?",
            "options": ["They swap", "They stay 50/50", "They become 100% for 1", "They become 100% for 0"],
            "answer": 1,
            "explanations": [
                "Z only rotates around the vertical axis; latitude, and therefore the odds, stay put.",
                "Right. Z turns |+⟩ into |−⟩ — a different state with identical odds.",
                "Z doesn't move the arrow toward a pole.",
                "Z doesn't move the arrow toward a pole.",
            ],
        },
        "preset": "Phase on the equator",
        "try_this": [
            "The example is H then S: the arrow faces sideways (|+i⟩), bars still 50/50.",
            "Add **Z**, **S**, or **T** gates. Watch the Bloch arrow, not just the bars.",
            "Now add **H** at the end. Suddenly the bars move — Lesson 7 explains why.",
        ],
        "objectives": [
            "Distinguish amplitude magnitude from phase.",
            "Explain why Z, S and T leave immediate probabilities unchanged.",
            "Predict where phase gates move the Bloch arrow.",
        ],
        "explanation": [
            "Z multiplies the |1⟩ amplitude by −1, S by i, and T by e^{iπ/4}. Magnitudes are unchanged, so probabilities are unchanged; only the relative phase φ between the amplitudes moves.",
            "On the Bloch sphere, a general state is cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩: θ is latitude (sets the odds), φ is longitude (the phase).",
        ],
        "equation": "|psi> = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>",
        "latex": r"|\psi\rangle = \cos\tfrac{\theta}{2}|0\rangle + e^{i\varphi}\sin\tfrac{\theta}{2}|1\rangle,\qquad Z = \begin{pmatrix}1&0\\0&-1\end{pmatrix}",
        "misconception": "'The gate did nothing because the bars didn't move' is the classic trap. A gate can change the state without changing the current measurement odds.",
        "qiskit": {
            "intro": "Phase gates: `z`, `s`, `t`, and the general phase gate `p(φ)`. Compare statevectors to see the phase that measurements can't.",
            "code": "import numpy as np\n"
            + _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "qc = QuantumCircuit(1)\n"
            "qc.h(0)\n"
            "qc.s(0)          # quarter turn around z\n\n"
            "state = Statevector(qc)\n"
            "print('amplitudes   :', np.round(state.data, 3))\n"
            "print('probabilities:', state.probabilities_dict(decimals=3))\n",
            "notes": [
                ("qc.s(0)", "Multiply the |1⟩ amplitude by i — a 90° turn around the vertical axis."),
                ("state.data", "The raw complex amplitudes. Note the `1j` that the probabilities hide."),
            ],
        },
        "code_task": {
            "prompt": "Prepare |+i⟩ = (|0⟩ + i|1⟩)/√2 in `qc` — the arrow on the equator facing along +y.",
            "starter": _IMPORTS + "\nqc = QuantumCircuit(1)\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(1)\nqc.h(0)\nqc.s(0)\n",
            "hint": "Get onto the equator first, then a quarter turn around z.",
        },
        "checkpoint": "Why can Z matter even when the probability chart doesn't move right after it?",
        "practice": 1,
    },
    {
        "id": "interference",
        "number": 7,
        "unit": "one-qubit",
        "title": "Interference",
        "eyebrow": "Quantum behaviour",
        "duration": "15 min",
        "summary": "Split, shift, recombine: interference turns hidden phase into a visible result. It's the engine of every quantum algorithm.",
        "intuition": [
            "Think of H as a beam splitter: it sends the state down two paths, |0⟩ and |1⟩. A second H recombines the paths.",
            "If the paths come back **in step**, they reinforce on |0⟩ (constructive interference). If one path was shifted half a wave by Z, they **cancel** on |0⟩ and all the probability lands on |1⟩.",
            "Any shift in between gives anything in between. Quantum algorithms are carefully designed patterns of these cancellations.",
        ],
        "widget": {
            "type": "interference",
            "phi": 0.0,
            "caption": "Circuit: H → P(φ) → H. Slide the phase shift between the two paths.",
        },
        "quiz": {
            "question": "In H → Z → H starting from |0⟩, what do you measure?",
            "options": ["0 always", "1 always", "50/50", "It depends on the shot"],
            "answer": 1,
            "explanations": [
                "That's H → H with no phase shift. Z changes the story.",
                "Right. Z flips the sign of the |1⟩ path, so the paths cancel on |0⟩ and add up on |1⟩.",
                "The phase shift of Z is exactly half a wave — complete cancellation, not a mix.",
                "The outcome is certain; there's nothing random left.",
            ],
        },
        "preset": "Interference",
        "try_this": [
            "H → Z → H ends at |1⟩ with certainty, without any X gate.",
            "Replace Z with **S** (a quarter-wave shift). Predict the bars first.",
            "Replace Z with **RZ** and sweep the angle. Match what you see to the widget's curve.",
        ],
        "objectives": [
            "Explain constructive and destructive interference with amplitudes.",
            "Build H-Z-H as an interference experiment.",
            "Use the general phase gate P(φ) in Qiskit.",
        ],
        "explanation": [
            "After H the amplitudes are (1/√2, 1/√2). P(φ) multiplies the second by e^{iφ}. The final H adds and subtracts them: the |0⟩ amplitude becomes (1 + e^{iφ})/2 and the |1⟩ amplitude (1 − e^{iφ})/2.",
            "So P(0) = cos²(φ/2). At φ = 0 the paths add on |0⟩; at φ = π they cancel there completely.",
        ],
        "equation": "H P(phi) H |0>:  P(0) = cos^2(phi/2)",
        "latex": r"H\,P(\varphi)\,H\,|0\rangle:\qquad P(0) = \cos^2\tfrac{\varphi}{2},\quad HZH|0\rangle = |1\rangle",
        "misconception": "Cancellation is not two particles bumping into each other. It's amplitudes — which can be negative or complex — adding to zero. Probabilities alone could never cancel.",
        "qiskit": {
            "intro": "`qc.p(phi, qubit)` applies a phase shift of φ. Sweep it to trace the interference curve.",
            "code": "import numpy as np\n"
            + _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "for phi in np.linspace(0, 2 * np.pi, 5):\n"
            "    qc = QuantumCircuit(1)\n"
            "    qc.h(0)\n"
            "    qc.p(phi, 0)\n"
            "    qc.h(0)\n"
            "    p0 = Statevector(qc).probabilities()[0]\n"
            "    print(f'phi = {phi:.2f}  ->  P(0) = {p0:.3f}')\n",
            "notes": [
                ("qc.p(phi, 0)", "Shift the phase of the |1⟩ path by φ."),
                ("h → p → h", "Split, shift, recombine: the pattern behind every interferometer."),
            ],
        },
        "code_task": {
            "prompt": "Using H, P(φ) and H, build `qc` whose outcome is an exact **50/50** coin.",
            "starter": "import numpy as np\n" + _IMPORTS + "\nqc = QuantumCircuit(1)\n",
            "solution": "import numpy as np\n" + _IMPORTS + "qc = QuantumCircuit(1)\nqc.h(0)\nqc.p(np.pi / 2, 0)\nqc.h(0)\n",
            "match": "probs",
            "required_ops": ["h", "p"],
            "hint": "You need cos²(φ/2) = ½.",
        },
        "checkpoint": "In H-Z-H, what role does each of the three gates play in producing a certain |1⟩?",
        "practice": 1,
    },
    {
        "id": "bases",
        "unit": "one-qubit",
        "title": "Measuring in other directions",
        "eyebrow": "Quantum behaviour",
        "duration": "12 min",
        "summary": "Measurement doesn't have to ask 'up or down?'. Rotate first, and you can ask 'front or back?' — which finally makes phase readable.",
        "intuition": [
            "So far every measurement asked one question: is the arrow nearer the north pole (0) or the south pole (1)? That's measuring along the **Z axis**.",
            "You can ask about any axis. Measuring along **X** asks 'front (|+⟩) or back (|−⟩)?'; along **Y** asks 'right (|+i⟩) or left (|−i⟩)?'. The odds depend only on how close the arrow is to each end of that axis.",
            "Hardware can only measure along Z, so Qiskit uses the trick from Lesson 7: **rotate** the axis you care about onto Z, then measure. That's how phase — invisible to a Z measurement — becomes readable.",
        ],
        "widget": {
            "type": "basis_measure",
            "theta": 0.5,
            "phi": 0.0,
            "caption": "Move the arrow, then switch the question you ask. The red dashed line is the axis being measured.",
        },
        "quiz": {
            "question": "The qubit is |+⟩ (front of the equator). You measure along X. What do you get?",
            "options": ["'+' every time", "50/50 between '+' and '−'", "'−' every time", "0 or 1 at random"],
            "answer": 0,
            "explanations": [
                "Right. |+⟩ sits exactly at the '+' end of the X axis, so the answer is certain.",
                "That's what a Z measurement of |+⟩ gives. Along X, |+⟩ is a pole, not the equator.",
                "|−⟩ is the other end of the X axis; |+⟩ never answers '−'.",
                "Those are Z-basis answers. Along X the question is '+' or '−' — and here it's certain.",
            ],
        },
        "preset": "Measure |+> along X",
        "try_this": [
            "The example prepares |+⟩ with H, then rotates the X axis onto Z with a second **H**: a certain 0, which means '+'.",
            "Undo the last H to measure along Z instead — now it's 50/50.",
            "Clear, then build **H**, **Z**, **H**: you prepared |−⟩ and measured along X. What does it say now?",
        ],
        "objectives": [
            "Describe a measurement as a question about one axis.",
            "Predict outcomes for X- and Y-basis measurements.",
            "Change basis in Qiskit with H and S† before measuring.",
        ],
        "explanation": [
            "Measuring along an axis n̂ answers '+' with probability (1 + r⃗·n̂)/2, where r⃗ is the Bloch vector. For the Z axis this is just |α|².",
            "H swaps the X and Z axes, so 'H, then measure' is an X measurement. S† followed by H maps the Y axis onto Z. Every basis measurement in Qiskit is 'rotate, then measure in Z'.",
        ],
        "equation": "P(+ along n) = (1 + r.n)/2",
        "latex": r"P(+\ \text{along}\ \hat n) = \frac{1 + \vec r\cdot\hat n}{2},\qquad X\text{ basis: } H\text{, measure},\quad Y\text{ basis: } S^\dagger H\text{, measure}",
        "misconception": "A 50/50 result in Z doesn't mean the qubit is 'random'. |+⟩ is perfectly definite — it just isn't lined up with the question you asked.",
        "qiskit": {
            "intro": "Qiskit measures in Z. To measure along X, apply `h` first; along Y, apply `sdg` then `h`.",
            "code": _IMPORTS
            + "from qiskit.primitives import StatevectorSampler\n\n"
            "def measure_along(axis):\n"
            "    qc = QuantumCircuit(1)\n"
            "    qc.h(0)                 # prepare |+>\n"
            "    if axis == 'X':\n"
            "        qc.h(0)             # rotate X onto Z\n"
            "    elif axis == 'Y':\n"
            "        qc.sdg(0)\n"
            "        qc.h(0)             # rotate Y onto Z\n"
            "    qc.measure_all()\n"
            "    return qc\n\n"
            "sampler = StatevectorSampler()\n"
            "for axis in ['Z', 'X', 'Y']:\n"
            "    counts = sampler.run([measure_along(axis)], shots=1000).result()[0].data.meas.get_counts()\n"
            "    print(axis, counts)\n",
            "notes": [
                ("qc.h(0) before measuring", "Swaps the X and Z axes, so the Z measurement answers the X question."),
                ("qc.sdg(0); qc.h(0)", "Turns the Y axis onto Z."),
                ("'0' / '1'", "After the rotation, 0 means '+' and 1 means '−' along the axis you chose."),
            ],
        },
        "code_task": {
            "prompt": "The starter prepares |+i⟩. Add the gates that rotate the **Y** axis onto Z, so `qc` ends in |0⟩ — a certain '+i' answer.",
            "starter": _IMPORTS + "\nqc = QuantumCircuit(1)\nqc.h(0)\nqc.s(0)       # |+i>\n# rotate the Y axis onto Z here\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(1)\nqc.h(0)\nqc.s(0)\nqc.sdg(0)\nqc.h(0)\n",
            "match": "probs",
            "required_ops": ["sdg"],
            "hint": "`qc.sdg(0)` then `qc.h(0)`.",
        },
        "checkpoint": "Why can an X-basis measurement tell |+⟩ and |−⟩ apart when a Z-basis measurement can't?",
        "practice": 1,
    },
    # ------------------------------------------------------------------ Unit 2
    {
        "id": "registers",
        "number": 8,
        "unit": "many-qubits",
        "title": "Many qubits and bit order",
        "eyebrow": "Multi-qubit systems",
        "duration": "10 min",
        "summary": "n qubits have 2ⁿ possible outcomes. Learn to read Qiskit's bit strings — qubit 0 is on the right.",
        "intuition": [
            "Two qubits can be read as 00, 01, 10 or 11 — four outcomes. Three qubits give eight. Every extra qubit **doubles** the list.",
            "A quantum state has one amplitude for every entry in that list. That doubling is where quantum computers get their room to work.",
            "One convention to lock in now: **Qiskit writes qubit 0 on the right**. Flip only q0 and you'll see `01`, not `10`.",
        ],
        "widget": {"type": "bit_order", "qubits": 3, "caption": "Flip individual qubits and read the bit string Qiskit would print."},
        "quiz": {
            "question": "You build a 2-qubit circuit and apply X to qubit 1 only. Which bit string does Qiskit report?",
            "options": ["01", "10", "11", "00"],
            "answer": 1,
            "explanations": [
                "That would be qubit 0 flipped. Qiskit puts q0 on the right.",
                "Right. Strings read q1 q0, so flipping q1 gives 10.",
                "Only one qubit was flipped.",
                "X definitely flips the qubit it's applied to.",
            ],
        },
        "preset": "Two qubits, q0 flipped",
        "try_this": [
            "The example flips q0 in a 2-qubit register: the result is `01`.",
            "Add **X** on q1. Which string appears now?",
            "Add **H** on both qubits from a fresh start. How many outcomes share the probability?",
        ],
        "objectives": [
            "Count the outcomes of an n-qubit register.",
            "Read Qiskit's little-endian bit strings.",
            "Address individual qubits in multi-qubit circuits.",
        ],
        "explanation": [
            "The state of n qubits lives in a 2ⁿ-dimensional space. For independent qubits, the joint state is the tensor product: (α₀|0⟩ + β₀|1⟩) ⊗ (α₁|0⟩ + β₁|1⟩).",
            "Qiskit orders tensor factors so that qubit 0 is the least significant (rightmost) bit. The basis state |q₁q₀⟩ = |10⟩ means q1 = 1 and q0 = 0.",
        ],
        "equation": "|q1 q0>,  2 qubits -> 4 amplitudes",
        "latex": r"|q_1 q_0\rangle,\qquad n \text{ qubits} \Rightarrow 2^n \text{ amplitudes}",
        "misconception": "2ⁿ amplitudes doesn't mean you can read out 2ⁿ answers. A measurement still returns a single n-bit string.",
        "qiskit": {
            "intro": "Pass a larger number to `QuantumCircuit`. Gates take the index of the qubit they act on.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "qc = QuantumCircuit(3)\n"
            "qc.x(0)          # flip qubit 0\n\n"
            "print(qc.draw())\n"
            "print(Statevector(qc).probabilities_dict(decimals=3))   # {'001': 1.0}\n",
            "notes": [
                ("QuantumCircuit(3)", "Three qubits: 2³ = 8 amplitudes."),
                ("'001'", "Read right to left: q0 = 1, q1 = 0, q2 = 0."),
            ],
        },
        "code_task": {
            "prompt": "Build a 2-qubit `qc` that Qiskit reports as `10`.",
            "starter": _IMPORTS + "\nqc = QuantumCircuit(2)\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(2)\nqc.x(1)\n",
            "hint": "The left digit is qubit 1.",
        },
        "checkpoint": "How many amplitudes does a 10-qubit state have, and why can't you read them all out?",
        "practice": 2,
    },
    {
        "id": "entanglement",
        "number": 9,
        "unit": "many-qubits",
        "title": "Entanglement",
        "eyebrow": "Multi-qubit systems",
        "duration": "18 min",
        "summary": "Use CNOT on a superposition and two qubits stop having their own arrows. They share one state.",
        "intuition": [
            "**CNOT** is a conditional flip: if the control qubit is 1, flip the target. On plain 0s and 1s, it's just classical logic.",
            "Now give it a control that is in superposition. Both branches happen: |00⟩ stays |00⟩ and |10⟩… becomes |11⟩. The pair is now (|00⟩ + |11⟩)/√2 — a **Bell state**.",
            "Measure either qubit and you get a coin flip. Measure both and they **always agree**. Neither qubit has an arrow of its own any more — the information lives in the pair.",
        ],
        "widget": {"type": "entangle", "caption": "Compare 10 shots of two independent coins with 10 shots of a Bell pair."},
        "quiz": {
            "question": "In the Bell state (|00⟩ + |11⟩)/√2 you measure qubit 0 and get 1. What will qubit 1 give?",
            "options": ["0", "1", "50/50", "You can't measure it any more"],
            "answer": 1,
            "explanations": [
                "The state has no 01 or 10 component, so the results can't differ.",
                "Right. Only 00 and 11 have amplitude, so the outcomes always match.",
                "On its own, before anything is measured, yes — but not once its partner gave 1.",
                "You can; it just has a determined answer now.",
            ],
        },
        "preset": "Bell state",
        "try_this": [
            "H then CNOT gives 50% |00⟩ and 50% |11⟩. Look at the Bloch spheres: both arrows have **shrunk to the center**.",
            "Remove the H (undo twice, add CNOT alone). Is the result entangled?",
            "Add **X** on q1 after the CNOT. Which two outcomes remain?",
        ],
        "objectives": [
            "Use H followed by CNOT to build a Bell state.",
            "Read joint probabilities such as 00 and 11.",
            "Explain why entangled qubits have no individual Bloch arrow.",
        ],
        "explanation": [
            "CNOT maps |c, t⟩ → |c, t ⊕ c⟩. Applied to (|0⟩ + |1⟩)/√2 ⊗ |0⟩, it gives (|00⟩ + |11⟩)/√2, which cannot be written as a product of two single-qubit states.",
            "When a state can't be factored, each qubit alone is in a mixed state — its Bloch vector is shorter than 1. For a Bell state it has length 0: each qubit alone is a perfect coin flip, but the pair is perfectly ordered.",
        ],
        "equation": "|Phi+> = (|00> + |11>)/sqrt(2)",
        "latex": r"\mathrm{CNOT}\,(H\otimes I)\,|00\rangle = |\Phi^{+}\rangle = \tfrac{|00\rangle + |11\rangle}{\sqrt{2}}",
        "misconception": "Entanglement can't be used to send messages faster than light. Each side alone sees random results; the correlation only shows up when the results are compared.",
        "qiskit": {
            "intro": "`qc.cx(control, target)` is CNOT. The Bloch-vector shrinkage can be checked with `partial_trace`.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector, partial_trace\n\n"
            "qc = QuantumCircuit(2)\n"
            "qc.h(0)\n"
            "qc.cx(0, 1)      # control q0, target q1\n\n"
            "state = Statevector(qc)\n"
            "print(state.probabilities_dict(decimals=3))\n"
            "print('q0 alone:', partial_trace(state, [1]).purity().real)  # 0.5 = maximally mixed\n",
            "notes": [
                ("qc.cx(0, 1)", "CNOT with control qubit 0 and target qubit 1."),
                ("partial_trace(state, [1])", "Ignore qubit 1 and describe qubit 0 alone. Purity 1 = pure arrow, 0.5 = no arrow at all."),
            ],
        },
        "code_task": {
            "prompt": "Build the Bell state (|01⟩ + |10⟩)/√2 in `qc` — the two qubits always **disagree**.",
            "starter": _IMPORTS + "\nqc = QuantumCircuit(2)\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.x(1)\n",
            "required_ops": ["cx"],
            "hint": "Build the usual Bell pair, then flip one of the qubits.",
        },
        "checkpoint": "Why do the individual Bloch vectors shrink to zero in a Bell state even though the two-qubit state is perfectly pure?",
        "practice": 2,
    },
    {
        "id": "teleportation",
        "unit": "many-qubits",
        "title": "Teleportation",
        "eyebrow": "Multi-qubit systems",
        "duration": "18 min",
        "summary": "Move an unknown qubit state from Alice to Bob with one shared Bell pair and two ordinary bits — without anyone learning what the state is.",
        "intuition": [
            "Alice has a qubit in a state she doesn't know, and she can't copy it — unknown quantum states can't be cloned. But she and Bob share a **Bell pair** from Lesson 10.",
            "Alice entangles her mystery qubit with her half of the pair and measures both. Her two results look completely random, but they tell Bob **which of four simple fixes** — nothing, X, Z, or both — turns his half into her original state.",
            "After Bob's fix, his qubit is exactly Alice's state, and hers has been destroyed by the measurement. The state **moved**; it wasn't copied. And nothing travelled faster than light: Bob had to wait for Alice's message.",
        ],
        "widget": {
            "type": "teleport",
            "caption": "Choose Alice's state and which result she happened to get, then let Bob apply the fix.",
        },
        "quiz": {
            "question": "Before Alice's two bits reach Bob, what can he learn by measuring his qubit?",
            "options": [
                "Alice's state exactly",
                "Nothing useful — his results are 50/50 whatever Alice sent",
                "Alice's two measurement results",
                "Whether the teleportation worked",
            ],
            "answer": 1,
            "explanations": [
                "Without the fix, his qubit is one of four scrambled versions of her state.",
                "Right. Averaged over Alice's four equally likely results, Bob's qubit is a perfect coin flip — which is why teleportation can't send messages faster than light.",
                "Those bits only travel by ordinary communication.",
                "He can't check without knowing the state or the bits.",
            ],
        },
        "preset": "Teleportation",
        "try_this": [
            "q0 starts tilted by RY. Compare the Bloch spheres: after the protocol, **q2 points exactly where q0 started**.",
            "Undo the last two gates (Bob's fixes). q2's arrow shrinks to nothing — without Alice's bits, Bob holds only noise.",
            "Look at q0 at the end: it no longer points where it started. The state moved to q2 — no copy was made.",
        ],
        "objectives": [
            "Explain why an unknown quantum state can't simply be copied.",
            "Follow the teleportation protocol step by step.",
            "Build teleportation in Qiskit using deferred measurement.",
        ],
        "explanation": [
            "The no-cloning theorem forbids copying an unknown state. Teleportation sidesteps it: |ψ⟩ ⊗ |Φ⁺⟩ can be rewritten as four equally weighted terms, each pairing one of Alice's outcomes (m₀, m₁) with Bob holding X^{m₁}Z^{m₀}|ψ⟩.",
            "Bob undoes that with X^{m₁} and then Z^{m₀}. In a simulator you can replace 'measure, then fix if the bit is 1' with controlled gates — CX from q1 and CZ from q0. This is the deferred measurement principle, and the final state is the same.",
        ],
        "equation": "|psi>|Phi+> = 1/2 sum |m0 m1> X^m1 Z^m0 |psi>",
        "latex": r"|\psi\rangle\,|\Phi^+\rangle = \tfrac12 \sum_{m_0, m_1} |m_0 m_1\rangle \otimes X^{m_1} Z^{m_0}|\psi\rangle",
        "misconception": "Teleportation doesn't move matter or beat the speed of light. It needs a classical message, and it moves the state rather than copying it — Alice's original is destroyed.",
        "qiskit": {
            "intro": "On hardware, Bob's fixes depend on mid-circuit measurements. In a simulator you can use deferred measurement: each 'if the bit is 1, apply a gate' becomes a controlled gate.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector, partial_trace, state_fidelity\n\n"
            "qc = QuantumCircuit(3)\n"
            "qc.ry(1.1, 0)          # Alice's mystery state on q0\n"
            "qc.rz(0.7, 0)\n\n"
            "qc.h(1)                # shared Bell pair: q1 (Alice), q2 (Bob)\n"
            "qc.cx(1, 2)\n\n"
            "qc.cx(0, 1)            # Alice entangles her two qubits...\n"
            "qc.h(0)                # ...and would measure q0 and q1 here\n\n"
            "qc.cx(1, 2)            # Bob: X if q1 was 1  (deferred measurement)\n"
            "qc.cz(0, 2)            # Bob: Z if q0 was 1\n\n"
            "original = QuantumCircuit(1)\n"
            "original.ry(1.1, 0)\n"
            "original.rz(0.7, 0)\n"
            "bob = partial_trace(Statevector(qc), [0, 1])\n"
            "print('fidelity with Alice\\'s original:', round(state_fidelity(bob, Statevector(original)), 6))\n",
            "notes": [
                ("qc.h(1); qc.cx(1, 2)", "Make the shared Bell pair."),
                ("qc.cx(0, 1); qc.h(0)", "Alice's half of the protocol, just before her measurements."),
                ("qc.cx(1, 2); qc.cz(0, 2)", "Bob's fixes written as controlled gates (deferred measurement)."),
                ("state_fidelity(...)", "1.0 means Bob's qubit is exactly Alice's original state."),
            ],
        },
        "code_task": {
            "prompt": "The starter teleports q0 to q2, but Bob's fixes are missing. Add them so q2 ends in Alice's state.",
            "starter": _IMPORTS
            + "\nqc = QuantumCircuit(3)\nqc.ry(1.1, 0)\nqc.rz(0.7, 0)\n\nqc.h(1)\nqc.cx(1, 2)\n\nqc.cx(0, 1)\nqc.h(0)\n\n# Bob's fixes go here\n",
            "solution": _IMPORTS
            + "qc = QuantumCircuit(3)\nqc.ry(1.1, 0)\nqc.rz(0.7, 0)\nqc.h(1)\nqc.cx(1, 2)\nqc.cx(0, 1)\nqc.h(0)\nqc.cx(1, 2)\nqc.cz(0, 2)\n",
            "required_ops": ["cz"],
            "hint": "First an X controlled by q1, then a Z controlled by q0, both targeting Bob's q2.",
        },
        "checkpoint": "Why can't Bob use teleportation to receive a message before Alice's bits arrive?",
        "practice": 2,
    },
    # ------------------------------------------------------------------ Unit 3
    {
        "id": "deutsch",
        "unit": "algorithms",
        "title": "Phase kickback: Deutsch's algorithm",
        "eyebrow": "Algorithms",
        "duration": "15 min",
        "summary": "A function hides in a black box. Is it constant or balanced? Classically you must ask twice; a quantum computer can tell with one question.",
        "intuition": [
            "A black box computes a one-bit function f(x). It's either **constant** (same answer for 0 and 1) or **balanced** (different answers). Classically, you have to try both inputs.",
            "Quantumly, feed it both inputs at once in superposition — and put the box's output qubit in |−⟩. Then the answer doesn't change the output qubit at all. Instead it **kicks back** a sign, (−1)^f(x), onto the input. This is **phase kickback**.",
            "A constant f leaves the input at |+⟩; a balanced f flips it to |−⟩. One final H turns that phase difference into a definite 0 or 1 — the trick from Lesson 7. One question, certain answer.",
        ],
        "widget": {
            "type": "deutsch",
            "caption": "Swap the hidden function and compare two classical queries with one quantum query.",
        },
        "quiz": {
            "question": "Deutsch's algorithm measures q0 and gets 1. What do you know?",
            "options": ["f is constant", "f is balanced", "f(0) = 1", "Nothing yet — run it again"],
            "answer": 1,
            "explanations": [
                "Constant functions leave q0 at |+⟩, which the final H turns into 0.",
                "Right. Only a balanced function kicks back opposite signs, giving |−⟩ and then 1 with certainty.",
                "The algorithm reveals how f(0) and f(1) relate, not either value on its own.",
                "The result is deterministic — one run is enough.",
            ],
        },
        "preset": "Deutsch: balanced f(x) = x",
        "try_this": [
            "The example hides f(x) = x (a CNOT). q0 — the right-hand bit — reads 1 in every outcome: balanced.",
            "Undo the final H: q0's arrow sits at the back of the equator (|−⟩). That's the kicked-back phase.",
            "Clear and rebuild without the CNOT — **X** on q1, then **H** on q0, **H** on q1, **H** on q0. f is now constant: what does q0 read?",
        ],
        "objectives": [
            "Explain phase kickback.",
            "Tell constant from balanced functions with a single query.",
            "Build Deutsch's algorithm in Qiskit.",
        ],
        "explanation": [
            "The oracle maps |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩. With the output qubit in |−⟩, flipping y only multiplies by −1, so |x⟩|−⟩ → (−1)^{f(x)}|x⟩|−⟩: the answer moves into the phase of the input.",
            "With the input in |+⟩ you get (|0⟩ + (−1)^{f(0)⊕f(1)}|1⟩)/√2 up to a global sign, and the final H outputs f(0) ⊕ f(1): 0 for constant, 1 for balanced. Deutsch–Jozsa extends this to n input qubits, where any deterministic classical method needs exponentially many queries.",
        ],
        "equation": "U_f|x>|-> = (-1)^f(x) |x>|->",
        "latex": r"U_f\,|x\rangle|-\rangle = (-1)^{f(x)}|x\rangle|-\rangle,\qquad \text{measured } q_0 = f(0)\oplus f(1)",
        "misconception": "The speed-up isn't 'evaluate both inputs and read both answers'. You never learn f(0) or f(1) — only a global property of f, extracted by interference.",
        "qiskit": {
            "intro": "Write the oracle as a small function that adds gates. The rest of the algorithm never changes.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "def deutsch(oracle):\n"
            "    qc = QuantumCircuit(2)\n"
            "    qc.x(1)\n"
            "    qc.h([0, 1])          # q0 = |+>, q1 = |->\n"
            "    oracle(qc)            # one query to the black box\n"
            "    qc.h(0)\n"
            "    return qc\n\n"
            "oracles = {\n"
            "    'constant 0': lambda qc: None,\n"
            "    'constant 1': lambda qc: qc.x(1),\n"
            "    'balanced x': lambda qc: qc.cx(0, 1),\n"
            "    'balanced NOT x': lambda qc: (qc.cx(0, 1), qc.x(1)),\n"
            "}\n"
            "for name, oracle in oracles.items():\n"
            "    p1 = Statevector(deutsch(oracle)).probabilities([0])[1]\n"
            "    print(f'{name:15s} -> q0 reads {round(p1)}')\n",
            "notes": [
                ("qc.x(1); qc.h([0, 1])", "Input in |+⟩, output qubit in |−⟩ — the setup that makes kickback happen."),
                ("oracle(qc)", "The single query. A CNOT computes f(x) = x into the output qubit."),
                ("probabilities([0])", "Measurement odds for q0 alone."),
            ],
        },
        "code_task": {
            "prompt": "Build Deutsch's algorithm for the balanced oracle f(x) = NOT x (a CNOT, then X on q1). Store it in `qc`.",
            "starter": _IMPORTS + "\nqc = QuantumCircuit(2)\n# 1. q0 -> |+>, q1 -> |->\n# 2. the oracle\n# 3. H on q0\n",
            "solution": _IMPORTS + "qc = QuantumCircuit(2)\nqc.x(1)\nqc.h([0, 1])\nqc.cx(0, 1)\nqc.x(1)\nqc.h(0)\n",
            "required_ops": ["cx"],
            "hint": "`qc.x(1)`, `qc.h([0, 1])`, then `qc.cx(0, 1)` and `qc.x(1)`, then `qc.h(0)`.",
        },
        "checkpoint": "Why does putting the output qubit in |−⟩ turn the oracle's answer into a phase on the input?",
        "practice": 1,
    },
    {
        "id": "grover",
        "number": 10,
        "unit": "algorithms",
        "title": "Your first algorithm: Grover search",
        "eyebrow": "Algorithms",
        "duration": "20 min",
        "summary": "Mark the answer with a phase, then use interference to amplify it. With 4 items, one round finds it with certainty.",
        "intuition": [
            "Start with every possible answer equally likely (H on every qubit). Measuring now would be a blind guess.",
            "The **oracle** secretly flips the sign of the correct answer's amplitude. The odds don't change yet — it's a phase, like Lesson 6.",
            "The **diffuser** reflects every amplitude around the average. The marked one, now below average, gets flung far above it; the others shrink. Repeat about √N times and the answer dominates.",
        ],
        "widget": {"type": "grover", "caption": "Pick the database size and step through oracle + diffuser rounds."},
        "quiz": {
            "question": "Right after the oracle marks the answer (and before the diffuser), what does a measurement show?",
            "options": [
                "The marked answer with certainty",
                "The same uniform odds as before",
                "The marked answer is now impossible",
                "Only the unmarked answers",
            ],
            "answer": 1,
            "explanations": [
                "The oracle only changes a sign; it takes the diffuser to turn that into probability.",
                "Right. A sign flip is a phase — invisible to measurement until interference converts it.",
                "Its amplitude is −½ instead of +½; the probability (−½)² = ¼ is unchanged.",
                "Every outcome still has probability ¼.",
            ],
        },
        "preset": "Grover search (finds 11)",
        "try_this": [
            "The worked example searches 4 items for `11`: H on both, an oracle (CZ), then the diffuser. The bars show 100% on 11.",
            "Undo gates from the end, one at a time, to see the state right after the oracle.",
            "Load the preset again and change the oracle (wrap the CZ in X gates on q0) to search for a different item.",
        ],
        "objectives": [
            "Identify state preparation, oracle, diffusion and readout.",
            "Explain amplitude amplification without 'trying every answer at once'.",
            "Build a 2-qubit Grover circuit in Qiskit.",
        ],
        "explanation": [
            "With N items, the uniform state has every amplitude 1/√N. The oracle flips the sign of the marked item; the diffuser 2|s⟩⟨s| − I reflects all amplitudes about their mean.",
            "Each round rotates the state about 2/√N radians toward the answer, so roughly (π/4)√N rounds are needed — a quadratic speed-up over checking items one by one. For N = 4, exactly one round lands on the answer.",
        ],
        "equation": "rounds ~ (pi/4) sqrt(N)",
        "latex": r"|s\rangle = H^{\otimes n}|0\rangle,\qquad (D\,O)^{k}|s\rangle,\quad k \approx \tfrac{\pi}{4}\sqrt{N}",
        "misconception": "A quantum computer doesn't check all answers at once and read them out. It reshapes amplitudes so one measurement is likely to give the right answer.",
        "qiskit": {
            "intro": "CZ (`qc.cz`) flips the phase of |11⟩ — a ready-made oracle. The diffuser is H·X·CZ·X·H on both qubits.",
            "code": _IMPORTS
            + "from qiskit.quantum_info import Statevector\n\n"
            "qc = QuantumCircuit(2)\n"
            "qc.h([0, 1])              # uniform superposition\n\n"
            "qc.cz(0, 1)               # oracle: mark |11>\n\n"
            "qc.h([0, 1])              # diffuser\n"
            "qc.x([0, 1])\n"
            "qc.cz(0, 1)\n"
            "qc.x([0, 1])\n"
            "qc.h([0, 1])\n\n"
            "print(qc.draw())\n"
            "print(Statevector(qc).probabilities_dict(decimals=3))\n",
            "notes": [
                ("qc.h([0, 1])", "Most gate methods accept a list of qubits."),
                ("qc.cz(0, 1)", "Flip the sign of the |11⟩ amplitude — the oracle."),
                ("x · cz · x", "Sandwiching CZ in X gates moves the sign flip to |00⟩; with the H's this reflects about the mean."),
            ],
        },
        "code_task": {
            "prompt": "Change the oracle so the search finds `01` (q1 = 0, q0 = 1). Keep the result in `qc`.",
            "starter": _IMPORTS
            + "\nqc = QuantumCircuit(2)\nqc.h([0, 1])\n\n# oracle: mark |01>\nqc.cz(0, 1)\n\n# diffuser\nqc.h([0, 1])\nqc.x([0, 1])\nqc.cz(0, 1)\nqc.x([0, 1])\nqc.h([0, 1])\n",
            "solution": _IMPORTS
            + "qc = QuantumCircuit(2)\nqc.h([0, 1])\nqc.x(1)\nqc.cz(0, 1)\nqc.x(1)\nqc.h([0, 1])\nqc.x([0, 1])\nqc.cz(0, 1)\nqc.x([0, 1])\nqc.h([0, 1])\n",
            "match": "probs",
            "required_ops": ["cz"],
            "hint": "CZ marks 11. To mark 01, temporarily flip q1 so that 01 looks like 11 to the CZ.",
        },
        "checkpoint": "What job does interference perform between the oracle and the measurement?",
        "practice": 4,
    },
    # ------------------------------------------------------------------ Unit 4
    {
        "id": "hardware",
        "number": 11,
        "unit": "real-world",
        "title": "Noise and real hardware",
        "eyebrow": "Execution",
        "duration": "15 min",
        "summary": "Real qubits are fragile, and your circuit gets rewritten before it runs. Learn to separate ideal results from noise.",
        "intuition": [
            "Every real gate is slightly imperfect, and qubits slowly lose their state to the environment. On the Bloch sphere, noise **shrinks the arrow** toward the center — toward pure randomness.",
            "Before running, your circuit is **transpiled**: rewritten into the few gates the chip actually supports and routed around its wiring. A tidy 2-gate circuit can become 10 native gates — each one a chance for error.",
            "Good practice: always compare hardware results against the ideal simulation of the same circuit.",
        ],
        "widget": {"type": "noise", "caption": "Turn up the noise on a Bell-state experiment and watch the 'impossible' outcomes appear."},
        "quiz": {
            "question": "An ideal Bell circuit never gives 01 or 10. On hardware you see 4% of shots on 01. What is the most likely cause?",
            "options": [
                "The circuit is wrong",
                "Gate and readout noise",
                "Too many shots",
                "Entanglement is breaking the laws of physics",
            ],
            "answer": 1,
            "explanations": [
                "The ideal simulation shows the circuit is right — the extra outcomes come from the device.",
                "Right. Imperfect gates and readout leak probability into outcomes the ideal circuit forbids.",
                "More shots reduce statistical wobble; they don't create new outcomes.",
                "No physics was harmed — this is ordinary device noise.",
            ],
        },
        "preset": "Bell state",
        "noise_toggle": True,
        "try_this": [
            "Switch on **Include device noise** below the builder. Compare the bars with the ideal result.",
            "Add more gates that cancel out (X, X on q0). The ideal answer is unchanged — what does noise do?",
        ],
        "objectives": [
            "Distinguish exact simulation, shot noise, and device noise.",
            "Explain what transpilation does and why depth matters.",
            "Transpile a circuit to a native gate set in Qiskit.",
        ],
        "explanation": [
            "Noise is modelled with channels such as depolarizing noise, which replaces the state with a random one with probability λ: ρ → (1 − λ)ρ + λ I/d. On the Bloch sphere this shrinks the vector by (1 − λ).",
            "Transpilation maps your gates to the device's basis (for example rz, sx, cx) and inserts swaps for qubits that aren't physically connected. Deeper circuits accumulate more noise.",
        ],
        "equation": "rho -> (1 - lambda) rho + lambda I/d",
        "latex": r"\rho \;\to\; (1-\lambda)\,\rho + \lambda\,\tfrac{I}{d}",
        "misconception": "Error mitigation estimates a better answer from noisy data; it doesn't protect the quantum information the way fault-tolerant error correction does.",
        "qiskit": {
            "intro": "`transpile` rewrites a circuit for a target gate set. Compare the original and transpiled versions.",
            "code": _IMPORTS
            + "from qiskit import transpile\n\n"
            "bell = QuantumCircuit(2)\n"
            "bell.h(0)\n"
            "bell.cx(0, 1)\n\n"
            "native = transpile(bell, basis_gates=['rz', 'sx', 'cx'], optimization_level=1)\n"
            "print(native.draw())\n"
            "print('ops before:', dict(bell.count_ops()), 'depth', bell.depth())\n"
            "print('ops after :', dict(native.count_ops()), 'depth', native.depth())\n",
            "notes": [
                ("transpile(..., basis_gates=[...])", "Rewrite every gate using only the listed native gates."),
                ("count_ops() / depth()", "How many gates of each kind, and how many time steps — a rough noise budget."),
            ],
        },
        "code_task": {
            "prompt": "Transpile a GHZ circuit (H on q0, CNOT 0→1, CNOT 1→2) to the basis `['rz', 'sx', 'cx']` and store the **transpiled** circuit in `qc`.",
            "starter": _IMPORTS + "from qiskit import transpile\n\nghz = QuantumCircuit(3)\n# build GHZ here\n\nqc = ghz  # replace with the transpiled circuit\n",
            "solution": _IMPORTS + "from qiskit import transpile\n\nghz = QuantumCircuit(3)\nghz.h(0)\nghz.cx(0, 1)\nghz.cx(1, 2)\nqc = transpile(ghz, basis_gates=['rz', 'sx', 'cx'])\n",
            "match": "probs",
            "required_ops": ["sx", "cx"],
            "hint": "`qc = transpile(ghz, basis_gates=['rz', 'sx', 'cx'])`",
        },
        "checkpoint": "Why should you compare noisy results with an ideal simulation of the same circuit?",
        "practice": 2,
    },
    {
        "id": "real-chip",
        "unit": "real-world",
        "title": "Running on a real chip",
        "eyebrow": "Execution",
        "duration": "15 min",
        "summary": "Real chips only connect some qubits to each other. See how Qiskit maps and routes your circuit, then run it on a simulated IBM-style backend.",
        "intuition": [
            "On a chip, qubits are physical objects laid out on a grid, and a two-qubit gate only works between **neighbours**. The wiring diagram is called the **coupling map**.",
            "If your circuit needs a CNOT between qubits that aren't neighbours, the transpiler inserts **SWAPs** to shuffle states next to each other. Each SWAP costs three CNOTs, and every CNOT adds noise.",
            "So writing good hardware circuits means thinking like the chip: keep interacting qubits close, keep circuits shallow, and always compare with the ideal result.",
        ],
        "widget": {
            "type": "routing",
            "caption": "Pick a circuit and a wiring diagram. These numbers come from Qiskit's real transpiler.",
        },
        "quiz": {
            "question": "Your circuit has one CNOT between q0 and q3, but the chip is wired in a line: q0–q1–q2–q3. What happens when you transpile?",
            "options": [
                "It fails — those qubits can't interact",
                "SWAPs are added, so the chip runs several extra CNOTs",
                "Nothing changes",
                "The CNOT is replaced by a measurement",
            ],
            "answer": 1,
            "explanations": [
                "The transpiler handles this for you by routing.",
                "Right. States are swapped along the line until the qubits are neighbours, which adds several CNOTs.",
                "A CNOT can't be applied directly between qubits that aren't connected.",
                "Routing never changes what the circuit computes.",
            ],
        },
        "preset": "GHZ state",
        "noise_toggle": True,
        "try_this": [
            "The GHZ example chains CNOTs between neighbours — friendly to a line-shaped chip.",
            "Switch on **Include device noise**: the CNOTs' noise shows up as 'impossible' outcomes like 010.",
            "Add a CNOT from q0 to q2 — not neighbours on a line. In the widget above, see what that would cost on a real chip.",
        ],
        "objectives": [
            "Read a coupling map.",
            "Explain why routing adds SWAPs and noise.",
            "Transpile for a backend and run a noisy simulation in Qiskit.",
        ],
        "explanation": [
            "A backend describes its native gates, coupling map and error rates. `transpile` chooses a layout (which physical qubit plays each of your qubits), routes with SWAPs where needed, and rewrites gates into the native set.",
            "On IBM hardware you'd load a real backend with `QiskitRuntimeService` and run with `SamplerV2`. Locally, `GenericBackendV2` is a realistic stand-in, and `AerSimulator.from_backend` imitates its noise.",
        ],
        "equation": "SWAP = CNOT(1,2) CNOT(2,1) CNOT(1,2)",
        "latex": r"\mathrm{SWAP} = \mathrm{CNOT}_{1\to2}\,\mathrm{CNOT}_{2\to1}\,\mathrm{CNOT}_{1\to2}",
        "misconception": "A transpiled circuit that looks different isn't a different computation. Layout and routing permute and rewrite, but the ideal output is the same — only the noise budget changes.",
        "qiskit": {
            "intro": "`GenericBackendV2` is a built-in fake chip with a coupling map and realistic errors. Transpile for it, then simulate its noise with Aer.",
            "code": "from qiskit import QuantumCircuit, transpile\n"
            "from qiskit.providers.fake_provider import GenericBackendV2\n"
            "from qiskit_aer import AerSimulator\n\n"
            "# a 5-qubit chip wired in a line\n"
            "backend = GenericBackendV2(num_qubits=5, coupling_map=[[0, 1], [1, 2], [2, 3], [3, 4]], seed=42)\n\n"
            "qc = QuantumCircuit(3)\n"
            "qc.h(0)\n"
            "qc.cx(0, 1)\n"
            "qc.cx(1, 2)\n"
            "qc.measure_all()\n\n"
            "native = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=7)\n"
            "print('ops:', dict(native.count_ops()), ' depth:', native.depth())\n\n"
            "noisy = AerSimulator.from_backend(backend)\n"
            "counts = noisy.run(native, shots=2000, seed_simulator=1).result().get_counts()\n"
            "print(counts)\n",
            "notes": [
                ("GenericBackendV2(...)", "A fake chip: 5 qubits wired in a line, with made-up but realistic error rates."),
                ("transpile(qc, backend=backend)", "Pick physical qubits, route, and rewrite into the chip's native gates."),
                ("AerSimulator.from_backend(backend)", "A simulator that imitates that chip's noise."),
            ],
            "real_hardware": "from qiskit import transpile\n"
            "from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler\n\n"
            "service = QiskitRuntimeService()          # uses your saved IBM Quantum account\n"
            "backend = service.least_busy(operational=True, simulator=False)\n\n"
            "native = transpile(qc, backend=backend, optimization_level=1)\n"
            "job = Sampler(mode=backend).run([native], shots=2000)\n"
            "print(job.result()[0].data.meas.get_counts())\n",
        },
        "code_task": {
            "prompt": "Transpile the Bell circuit for `backend` and store the **transpiled** circuit in `qc`.",
            "starter": _IMPORTS
            + "from qiskit import transpile\nfrom qiskit.providers.fake_provider import GenericBackendV2\n\n"
            "backend = GenericBackendV2(num_qubits=2, seed=42)\n\nbell = QuantumCircuit(2)\nbell.h(0)\nbell.cx(0, 1)\n\n"
            "qc = bell  # replace with the transpiled circuit\n",
            "solution": _IMPORTS
            + "from qiskit import transpile\nfrom qiskit.providers.fake_provider import GenericBackendV2\n\n"
            "backend = GenericBackendV2(num_qubits=2, seed=42)\nbell = QuantumCircuit(2)\nbell.h(0)\nbell.cx(0, 1)\n"
            "qc = transpile(bell, backend=backend, seed_transpiler=7)\n",
            "match": "probs",
            "required_ops": ["sx"],
            "hint": "`qc = transpile(bell, backend=backend)` — the chip has no H gate, so it becomes rz and sx.",
        },
        "checkpoint": "Why can the same circuit be noisier on one chip than on another, even if every gate is equally good?",
        "practice": 2,
    },
    {
        "id": "qml",
        "number": 12,
        "unit": "real-world",
        "title": "Trainable circuits and quantum ML",
        "eyebrow": "Machine learning",
        "duration": "15 min",
        "summary": "Give a circuit adjustable knobs, measure how wrong it is, and turn the knobs to do better. That's a variational algorithm.",
        "intuition": [
            "In Lesson 5 you set an RY angle by hand to hit a target probability. Now let a computer do it.",
            "A **parameterized circuit** has rotation angles left as variables. A classical optimizer runs the circuit, measures a **cost** (how far the output is from what you want), nudges the angles downhill, and repeats.",
            "This loop powers variational chemistry solvers and quantum machine-learning models. It's the same idea as training a neural network — the model just happens to be a circuit.",
        ],
        "widget": {"type": "variational", "caption": "Pick a target P(1), then train the angle θ by gradient descent. Amber dots trace the path downhill."},
        "quiz": {
            "question": "During training of a variational circuit, what actually changes?",
            "options": ["The number of qubits", "The rotation angles (parameters)", "The order of the gates", "The measurement results of past shots"],
            "answer": 1,
            "explanations": [
                "The circuit's size is fixed when you design it.",
                "Right. The structure stays the same; the optimizer tunes the angles.",
                "The layout (the 'ansatz') is fixed; only its parameters move.",
                "Past data is fixed; training changes the circuit that produces future data.",
            ],
        },
        "preset": "Variational circuit",
        "try_this": [
            "The example is a tiny 2-qubit model: RY on each qubit, a CNOT, then another RY.",
            "Change the first RY angle in small steps and watch the outputs move smoothly — that smoothness is what gradients rely on.",
        ],
        "objectives": [
            "Explain what makes a circuit parameterized.",
            "Describe the train loop: run, measure cost, adjust.",
            "Use Qiskit `Parameter`s and bind values to them.",
        ],
        "explanation": [
            "A variational circuit U(θ) prepares |ψ(θ)⟩. A cost C(θ) — such as the distance between measured and target probabilities — is estimated from shots and minimized by a classical optimizer.",
            "Gradients can be measured on the quantum device itself with the parameter-shift rule: ∂C/∂θ = [C(θ + π/2) − C(θ − π/2)]/2 for rotation gates.",
        ],
        "equation": "theta <- theta - eta * dC/dtheta",
        "latex": r"\theta \leftarrow \theta - \eta\,\frac{\partial C}{\partial \theta},\qquad \frac{\partial C}{\partial \theta} = \frac{C(\theta+\frac{\pi}{2}) - C(\theta-\frac{\pi}{2})}{2}",
        "misconception": "Quantum ML is not automatically better than classical ML. At today's scales it often ties or loses; the point is to understand the mechanism and where it might help.",
        "qiskit": {
            "intro": "`Parameter` creates a symbolic angle. `assign_parameters` binds numbers to it before simulation.",
            "code": "import numpy as np\n"
            + _IMPORTS
            + "from qiskit.circuit import Parameter\n"
            "from qiskit.quantum_info import Statevector\n\n"
            "theta = Parameter('theta')\n"
            "model = QuantumCircuit(1)\n"
            "model.ry(theta, 0)\n\n"
            "def p1(t):\n"
            "    return Statevector(model.assign_parameters({theta: t})).probabilities()[1]\n\n"
            "target = 0.8      # we want P(1) = 0.8\n"
            "value = 0.1       # initial guess for theta\n"
            "for step in range(40):\n"
            "    dp = (p1(value + np.pi / 2) - p1(value - np.pi / 2)) / 2   # parameter-shift rule\n"
            "    grad = 2 * (p1(value) - target) * dp                     # d/dtheta of (p1 - target)^2\n"
            "    value -= 1.0 * grad\n\n"
            "print(f'trained theta = {value:.3f}, P(1) = {p1(value):.3f}')\n",
            "notes": [
                ("Parameter('theta')", "A named placeholder for an angle."),
                ("assign_parameters({theta: t})", "Return a copy of the circuit with a concrete number bound to θ."),
                ("dp = (p1(value + π/2) − p1(value − π/2)) / 2", "The parameter-shift rule: an exact derivative from two extra circuit runs."),
                ("value -= 1.0 * grad", "One gradient-descent step: move the angle downhill on the cost (p1 − target)²."),
            ],
        },
        "code_task": {
            "prompt": "Bind the parameter so the model gives P(1) = **50%**, and store the **bound** circuit in `qc`.",
            "starter": "import numpy as np\n" + _IMPORTS + "from qiskit.circuit import Parameter\n\ntheta = Parameter('theta')\nmodel = QuantumCircuit(1)\nmodel.ry(theta, 0)\n\nqc = model.assign_parameters({theta: 0.0})  # choose the value\n",
            "solution": "import numpy as np\n" + _IMPORTS + "qc = QuantumCircuit(1)\nqc.ry(np.pi / 2, 0)\n",
            "match": "probs",
            "required_ops": ["ry"],
            "hint": "Which RY angle lands on the equator?",
        },
        "checkpoint": "In a variational circuit, what changes during training — and what tells the optimizer which way to change it?",
        "practice": 5,
    },
]

# Lessons are numbered by position, so inserting one never needs manual renumbering.
for _number, _lesson in enumerate(LESSONS, start=1):
    _lesson["number"] = _number


PRESETS = {
    "Start at |0>": {"qubits": 1, "gates": []},
    "Flip with X": {"qubits": 1, "gates": [{"gate": "X", "target": 0, "control": None}]},
    "Superposition": {
        "qubits": 1,
        "gates": [{"gate": "H", "target": 0, "control": None}],
    },
    "Tilted (RY)": {
        "qubits": 1,
        "gates": [{"gate": "RY", "target": 0, "control": None, "angle": 1.0471976}],
    },
    "Phase on the equator": {
        "qubits": 1,
        "gates": [
            {"gate": "H", "target": 0, "control": None},
            {"gate": "S", "target": 0, "control": None},
        ],
    },
    "Interference": {
        "qubits": 1,
        "gates": [
            {"gate": "H", "target": 0, "control": None},
            {"gate": "Z", "target": 0, "control": None},
            {"gate": "H", "target": 0, "control": None},
        ],
    },
    "Measure |+> along X": {
        "qubits": 1,
        "gates": [
            {"gate": "H", "target": 0, "control": None},
            {"gate": "H", "target": 0, "control": None},
        ],
    },
    "Teleportation": {
        "qubits": 3,
        "gates": [
            {"gate": "RY", "target": 0, "control": None, "angle": 1.1},
            {"gate": "H", "target": 1, "control": None},
            {"gate": "CNOT", "target": 2, "control": 1},
            {"gate": "CNOT", "target": 1, "control": 0},
            {"gate": "H", "target": 0, "control": None},
            {"gate": "CNOT", "target": 2, "control": 1},
            {"gate": "CZ", "target": 2, "control": 0},
        ],
    },
    "Deutsch: balanced f(x) = x": {
        "qubits": 2,
        "gates": [
            {"gate": "X", "target": 1, "control": None},
            {"gate": "H", "target": 0, "control": None},
            {"gate": "H", "target": 1, "control": None},
            {"gate": "CNOT", "target": 1, "control": 0},
            {"gate": "H", "target": 0, "control": None},
        ],
    },
    "Two qubits, q0 flipped": {"qubits": 2, "gates": [{"gate": "X", "target": 0, "control": None}]},
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
    "Grover search (finds 11)": {
        "qubits": 2,
        "gates": [
            {"gate": "H", "target": 0, "control": None},
            {"gate": "H", "target": 1, "control": None},
            {"gate": "CZ", "target": 1, "control": 0},
            {"gate": "H", "target": 0, "control": None},
            {"gate": "H", "target": 1, "control": None},
            {"gate": "X", "target": 0, "control": None},
            {"gate": "X", "target": 1, "control": None},
            {"gate": "CZ", "target": 1, "control": 0},
            {"gate": "X", "target": 0, "control": None},
            {"gate": "X", "target": 1, "control": None},
            {"gate": "H", "target": 0, "control": None},
            {"gate": "H", "target": 1, "control": None},
        ],
    },
    "Variational circuit": {
        "qubits": 2,
        "gates": [
            {"gate": "RY", "target": 0, "control": None, "angle": 1.5708},
            {"gate": "RY", "target": 1, "control": None, "angle": 1.5708},
            {"gate": "CNOT", "target": 1, "control": 0},
            {"gate": "RY", "target": 0, "control": None, "angle": 0.7854},
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
    {
        "title": "Tilt to 25%",
        "level": "Rotations",
        "qubits": 1,
        "goal": "Using only RY, make outcome 1 appear 25% of the time.",
        "hint": "P(1) = sin²(θ/2). Try an angle near 0.33π.",
        "target": {"0": 0.75, "1": 0.25},
        "required": ["RY"],
    },
    {
        "title": "Find the marked item",
        "level": "Algorithms",
        "qubits": 2,
        "goal": "Build a Grover circuit that finds 11 with certainty.",
        "hint": "H on both, CZ as the oracle, then H, X, CZ, X, H on both as the diffuser.",
        "target": {"00": 0.0, "01": 0.0, "10": 0.0, "11": 1.0},
        "required": ["CZ"],
    },
    {
        "title": "Inspect a variational circuit",
        "level": "Machine learning",
        "qubits": 2,
        "goal": "Rebuild the Variational circuit preset: RY(π/2) on both qubits, CNOT from q0 to q1, then RY(π/4) on q0.",
        "hint": "RY rotates a qubit. CNOT entangles the two qubits. In real QML, the RY angles would be trained.",
        "target": {"00": 0.073, "01": 0.427, "10": 0.073, "11": 0.427},
    },
]

GLOSSARY = [
    ("Qubit", "An arrow on a sphere that answers only 0 or 1 when measured.", "A two-level quantum system with state α|0⟩ + β|1⟩."),
    ("Measurement", "Asking the qubit 'up or down?' — it answers, and snaps to that answer.", "Projection onto the computational basis with probability |amplitude|²."),
    ("Shot", "One run of the circuit ending in one measurement.", "A single sample from the output distribution."),
    ("Gate", "A rotation of the arrow.", "A unitary matrix acting on one or more qubits."),
    ("Superposition", "The arrow points somewhere between the poles.", "A state with non-zero amplitude on more than one basis state."),
    ("Phase", "Which way the arrow faces around the equator — invisible to measurement on its own.", "The complex argument of an amplitude relative to the others."),
    ("Interference", "Paths that reinforce or cancel when recombined.", "Adding complex amplitudes so some grow and others vanish."),
    ("Measurement basis", "Which axis you ask the arrow about.", "The orthonormal basis a measurement projects onto (Z, X, Y, …)."),
    ("Entanglement", "Qubits that share one state instead of having their own arrows.", "A multi-qubit state that cannot be written as a product of single-qubit states."),
    ("Teleportation", "Moving a qubit's state using a shared Bell pair and two phoned-in bits.", "Transferring an unknown state with shared entanglement plus two classical bits; the original is destroyed."),
    ("Phase kickback", "The answer lands as a sign on the input instead of on the output.", "U_f|x⟩|−⟩ = (−1)^f(x)|x⟩|−⟩."),
    ("Oracle", "A black box that marks the answer by flipping its sign.", "A unitary that applies a phase of −1 to marked basis states."),
    ("Transpilation", "Rewriting your circuit into the gates the chip actually has.", "Compilation to a backend's basis gates and connectivity."),
    ("Coupling map", "Which qubits on the chip are wired to each other.", "The graph of physical qubit pairs that support two-qubit gates."),
    ("Noise", "Imperfections that shrink the arrow toward randomness.", "Non-unitary channels such as depolarizing or amplitude damping."),
    ("Parameter", "A knob — a gate angle left as a variable.", "A symbolic value bound to a number before execution."),
]
