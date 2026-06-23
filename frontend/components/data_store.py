GATE_LIBRARY = {
    "H": {
        "label": "Hadamard",
        "family": "Superposition",
        "description": "Splits a basis state onto the equator so measurement can return 0 or 1.",
    },
    "X": {
        "label": "Pauli-X",
        "family": "Bit flip",
        "description": "Rotates the qubit through π around the X axis, swapping |0⟩ and |1⟩.",
    },
    "Y": {
        "label": "Pauli-Y",
        "family": "Bit + phase flip",
        "description": "Flips the basis state and adds a phase twist through the Y axis.",
    },
    "Z": {
        "label": "Pauli-Z",
        "family": "Phase flip",
        "description": "Keeps measurement odds fixed while reflecting phase across the Z axis.",
    },
    "S": {
        "label": "S phase",
        "family": "Phase",
        "description": "Adds a quarter-turn phase, moving equator states around the Bloch sphere.",
    },
    "T": {
        "label": "T phase",
        "family": "Phase",
        "description": "Adds an eighth-turn phase, useful for fine-grained quantum programs.",
    },
    "RX": {
        "label": "Rx rotation",
        "family": "Parameterized",
        "description": "Rotates continuously around the X axis by a chosen angle.",
    },
    "RY": {
        "label": "Ry rotation",
        "family": "Parameterized",
        "description": "Rotates continuously around the Y axis, changing the chance of 0 versus 1.",
    },
    "RZ": {
        "label": "Rz rotation",
        "family": "Parameterized",
        "description": "Rotates continuously around the Z axis, changing phase without changing odds.",
    },
    "CNOT": {
        "label": "Controlled-X",
        "family": "Entangling",
        "description": "Flips the target only when the control is |1⟩, creating conditional motion.",
    },
}

EDUCATIONAL_FOUNDATIONS = {
    "Level 0: Python + Qiskit Setup": {
        "summary": "Start with the code objects learners will touch every time: circuits, qubits, gates, and output.",
        "materials": [
            "A circuit is a recipe, not the quantum state itself.",
            "Qubits are indexed from zero, so q0 is the first qubit.",
            "Gates are appended in order, left to right in the circuit diagram.",
            "Drawing, printing, and exporting circuits are part of the learning loop.",
        ],
        "try_this": "Create one qubit, add H, print the circuit, then explain each line aloud.",
    },
    "Level 1: Quantum Foundations": {
        "summary": "Build physical intuition before algorithms: state, phase, measurement, and entanglement.",
        "materials": [
            "A qubit state can be pictured as a direction on the Bloch sphere.",
            "Superposition changes measurement probabilities only when the state is away from the poles.",
            "Phase can be invisible in raw counts until later gates create interference.",
            "Entanglement means the shared system has structure that individual qubits cannot fully show.",
        ],
        "try_this": "Compare H, Z, and H-Z-H on q0. Watch when phase becomes measurable.",
    },
    "Level 2: Circuit Composer Skills": {
        "summary": "Learn how circuits behave as ordered transformations, not loose collections of gates.",
        "materials": [
            "Gate order matters because rotations around different axes usually do not commute.",
            "Parameterized rotations let circuits move continuously instead of jumping between fixed gates.",
            "Controlled gates can create correlations and can move phase information through a circuit.",
            "Small circuit identities help learners debug larger algorithms later.",
        ],
        "try_this": "Build H then Z, reset, then build Z then H. Compare the Bloch vector and probabilities.",
    },
    "Level 3: Simulation + Noise": {
        "summary": "Separate ideal math from sampled experiments and noisy hardware behavior.",
        "materials": [
            "A statevector is exact simulation data before measurement sampling.",
            "Shots are repeated measurements, so counts fluctuate statistically.",
            "Noise turns clean probability patterns into imperfect distributions.",
            "Transpilation rewrites a circuit so hardware can actually run it.",
        ],
        "try_this": "Run the same H circuit with different shot counts and compare how stable the counts become.",
    },
    "Level 4: Quantum Algorithms": {
        "summary": "Connect gates to algorithm patterns: marking, interference, phase, and optimization.",
        "materials": [
            "Grover search marks a target with phase, then amplifies it with interference.",
            "QFT stores periodic structure in relative phase patterns.",
            "VQE uses a parameterized circuit plus a classical optimizer.",
            "Algorithms are built from small physical effects repeated with intent.",
        ],
        "try_this": "Run the Grover preset, then identify which gates mark the answer and which amplify it.",
    },
    "Level 5: Hardware + Advanced Workflows": {
        "summary": "Prepare learners for real backends, runtime primitives, and error-aware workflows.",
        "materials": [
            "Sampler-style workflows are for outcome distributions.",
            "Estimator-style workflows are for expectation values and observables.",
            "Error mitigation improves estimates but does not fully correct quantum states.",
            "Hardware execution requires backend choice, transpilation, job submission, and result analysis.",
        ],
        "try_this": "Take a composer circuit, export it, and list what would need to change before hardware execution.",
    },
}

CURRICULUM = {
    "Level 0: Python + Qiskit Setup": {
        "Python for Circuits": {
            "big_idea": "Qiskit circuits are Python objects, so learners need functions, lists, loops, and clean notebook habits.",
            "composer": "Read the exported code after each composer action and connect every line to a visual gate.",
            "checkpoint": "What does `qc.h(0)` mean as Python code and as a physical operation?",
            "practice": "Create a QuantumCircuit, add one gate, print it, and draw it.",
            "lesson_text": "Before we manipulate quantum mechanics, we must understand the language of our control system: Python.<br><br>A quantum circuit is essentially a **digital recipe**. Each line of code adds a new instruction (like a physical gate) to our qubits, from left to right. We use Qiskit's `QuantumCircuit` class to initialize our qubits (which default to the standard state |0⟩).<br><br>To write a circuit, we initialize the object, apply operations, and print it:<br><code>from qiskit import QuantumCircuit<br>qc = QuantumCircuit(1) # Create 1 qubit circuit<br>qc.h(0)                # Apply a Hadamard gate to qubit 0<br>print(qc)              # Print a text-based circuit diagram</code><br><br>Just like a baking recipe, the circuit doesn't do anything until we put it in the oven (simulator or hardware) to run it! This tab helps you see exactly how composer actions translate to real Python lines.",
            "tutorial_code": "from qiskit import QuantumCircuit\n\n# Initialize a circuit with 1 qubit and 1 classical bit\nqc = QuantumCircuit(1, 1)\n\n# Apply a Hadamard gate to qubit 0\nqc.h(0)\n\n# Print a text representation of the circuit\nprint('--- Quantum Circuit recipe ---')\nprint(qc)\n",
            "tutor_challenge": "Explorer, what happens if you run `qc.h(0)` twice in a row? Try pasting it in the Sandbox, click Run, and observe the state vector. Does it return back to |0⟩? Why?"
        },
        "Qiskit Objects": {
            "big_idea": "QuantumCircuit, Statevector, AerSimulator, transpiler passes, and backends are the core objects learners reuse everywhere.",
            "composer": "Export a circuit, then paste it into the sandbox and add Statevector inspection.",
            "checkpoint": "Why is a circuit a recipe while a statevector is a simulated physical state?",
            "practice": "Use `QuantumCircuit(2)`, `Statevector.from_instruction(qc)`, and `qc.draw(output='mpl')`.",
            "lesson_text": "Now that we can construct a circuit recipe, let's look at the actual ingredients and baking sheets in Qiskit:<br><br><ul><li><strong>QuantumCircuit</strong>: This is the abstract recipe (the list of gates to be executed).</li><li><strong>Statevector</strong>: This is the exact mathematical description of the qubit's state at any point. Think of it as the perfect, infinite-precision snapshot of a spinning coin before it lands.</li><li><strong>Sampler</strong>: This is the simulator or device execution tool that shoots actual samples (like flipping a coin 1024 times and counting heads vs tails).</li></ul><br>Understanding the difference between the abstract recipe (circuit) and the simulated physical state (statevector) is the first major step to quantum mastery! Try pasting a circuit in the Sandbox and viewing its output.",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\n# Create a 2-qubit circuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n\n# Get the exact simulated statevector representing the circuit state\nsv = Statevector.from_instruction(qc)\nprint('Perfect Statevector Amplitudes:')\nprint(sv.data)\n",
            "tutor_challenge": "If a Statevector is an exact mathematical snapshot of a quantum state, what happens to the Statevector when a measurement gate is added to the circuit? Test it in the Sandbox!"
        }
    },
    "Level 1: Quantum Foundations": {
        "The Qubit": {
            "big_idea": "A qubit is a physical two-level system whose state points somewhere on the Bloch sphere.",
            "composer": "Move theta and phi, then use H, X, and Z to connect symbols to motion.",
            "checkpoint": "If the vector sits at the north pole, what outcome is guaranteed?",
            "practice": "Prepare |0⟩, |1⟩, |+⟩, and |−⟩ in Qiskit and compare their Bloch vectors.",
            "lesson_text": "A classical bit is simple: it is either a <code>0</code> or a <code>1</code>. Think of it as a standard light switch that can only be fully UP or fully DOWN.<br><br>A <strong>quantum bit (qubit)</strong> is represented visually as a three-dimensional sphere (the Bloch Sphere):<br><ul><li>The <strong>North Pole</strong> represents the state |0⟩ (100% chance of measuring 0).</li><li>The <strong>South Pole</strong> represents the state |1⟩ (100% chance of measuring 1).</li><li>The <strong>Equator</strong> and everything in between represent combinations (superpositions) of both!</li></ul><br>By applying rotation gates, we can point our qubit's state vector <em>anywhere</em> on the surface of this sphere. It is a continuous, physical two-level state! Try dragging the sliders below to see the state vector move across the sphere.",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(1)\n# Flip the qubit to the state |1⟩ using a Pauli-X gate\nqc.x(0)\n\nsv = Statevector.from_instruction(qc)\nprint('Statevector at South Pole (|1⟩):')\nprint(sv.data)\n",
            "tutor_challenge": "Explorer, if you start at the North Pole (|0⟩) and apply a Pauli-Y gate instead of a Pauli-X, where does the state vector land on the Bloch sphere? How does its phase angle change?"
        },
        "Superposition": {
            "big_idea": "Superposition means the vector is not at a pole; measurement probabilities come from its projection.",
            "composer": "Apply H to |0⟩ and watch the vector land on the equator.",
            "checkpoint": "Why does a balanced superposition not mean the qubit is secretly both classical values?",
            "practice": "Run a Hadamard circuit with 1024 shots and explain why counts fluctuate.",
            "lesson_text": "Imagine a coin lying flat on a table: it is either heads (|0⟩) or tails (|1⟩). This is classical.<br><br>Now, flick the coin so it spins rapidly on the table. Is it heads? Is it tails? While it is spinning, it is in a <strong>superposition</strong> of both states! Only when you slap your hand down on the coin to stop it (performing a <strong>measurement</strong>) does it force itself to collapse into a classical heads or tails.<br><br>In quantum circuits, the <strong>Hadamard (H) gate</strong> is the 'flick' that starts the qubit spinning, placing it perfectly on the equator of the Bloch sphere, giving it an equal 50/50 chance of collapsing to |0⟩ or |1⟩ upon measurement!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(1)\n# Apply Hadamard to create a balanced superposition state |+⟩\nqc.h(0)\n\nsv = Statevector.from_instruction(qc)\nprint('Superposition Statevector |+⟩:')\nprint(sv.data)\n",
            "tutor_challenge": "What is the probability of measuring 0 versus 1 for a state vector sitting exactly on the equator? Test it on the Composer and check the measurement probabilities."
        },
        "Measurement": {
            "big_idea": "Measurement projects the state onto a classical result and destroys most phase information.",
            "composer": "Compare the probability bars before and after gates that only change phase.",
            "checkpoint": "Which gates change probabilities, and which only change phase?",
            "practice": "Measure X|0⟩, H|0⟩, and ZH|0⟩; compare statevector and sampled counts.",
            "lesson_text": "In the quantum realm, **looking at something changes it!**<br><br>A qubit in superposition is represented by a vector pointing somewhere on the Bloch sphere. When we measure the qubit along the Z-axis, we ask it a simple question: <em>'Are you |0⟩ or |1⟩?'</em><br><br>The qubit <em>must</em> collapse to one of the poles. If the vector was on the equator, it has a 50% chance of collapsing to the North pole (|0⟩) and a 50% chance of collapsing to the South pole (|1⟩). Measurement **destroys** the delicate superposition and turns a rich, continuous sphere state into a classical 0 or 1! Observe how the probability bars reflect this projection.",
            "tutorial_code": "from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nqc.h(0)\n# Measure qubit 0 and store in classical bit 0\nqc.measure_all()\nprint('--- Circuit with Measurement ---')\nprint(qc)\n",
            "tutor_challenge": "If you measure a qubit, get a '0', and then measure it a second time immediately afterward, what state will it be in? Can a measured qubit return to a superposition without another gate?"
        },
        "Entanglement": {
            "big_idea": "Entanglement is shared state: individual qubits can lose a pure vector while the pair stays ordered.",
            "composer": "Apply H on q0, then CNOT q0 → q1 to form a Bell state.",
            "checkpoint": "Why can each single Bloch sphere look mixed while the two-qubit circuit is highly structured?",
            "practice": "Build all four Bell states and identify their measurement correlations.",
            "lesson_text": "Albert Einstein famously called quantum entanglement **'spooky action at a distance.'**<br><br>Imagine you have a pair of magical spinning coins. You keep one, and give the other to a friend who travels to the other side of the universe. If the coins are **entangled**, the moment you stop yours and see 'heads,' your friend's coin instantly stops spinning and collapses into 'tails' — every single time, instantly!<br><br>By applying a Hadamard gate on Qubit 0, and then a **CNOT gate** from Qubit 0 to Qubit 1, we physically link their states. Neither qubit has a pure local state anymore; they are part of a unified, shared quantum system. Look at the 3D Bloch spheres of the qubits when you entangle them—they appear to have a reduced radius, indicating a mixed local state!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(2)\nqc.h(0)      # Superposition control\nqc.cx(0, 1)  # Entangle control to target (creates Bell State)\n\nsv = Statevector.from_instruction(qc)\nprint('Bell State |Phi+⟩ Statevector:')\nprint(sv.data)\n",
            "tutor_challenge": "Look at the individual Bloch spheres on the Composer when you entangle two qubits. Why do their purities drop below 1.0? Can you describe the state of a single entangled qubit without referencing the other?"
        },
    },
    "Level 2: Circuit Composer Skills": {
        "Gate Algebra": {
            "big_idea": "Gates are reversible transformations; order matters because rotations around different axes do not generally commute.",
            "composer": "Compare H then Z versus Z then H and inspect the final vector.",
            "checkpoint": "Why can two circuits with the same gates produce different states?",
            "practice": "Use Qiskit to test XZ versus ZX on |0⟩ and |+⟩.",
            "lesson_text": "Unlike classical algebra where <code>a * b</code> is always equal to <code>b * a</code>, in quantum mechanics, **the order of operations matters!** We call this non-commutativity.<br><br>Because gates are physical rotations in three-dimensional space, rotating 90° around the X-axis and then 90° around the Z-axis lands you in a completely different spot than doing the Z-rotation first! <br><br>For instance, applying a Hadamard then a Z gate points the vector in a different direction than applying a Z then a Hadamard. Try composing both sequences on the Visual Composer and compare their final Bloch vectors!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\n# Circuit A: H then Z\nqcA = QuantumCircuit(1)\nqcA.h(0)\nqcA.z(0)\n\n# Circuit B: Z then H\nqcB = QuantumCircuit(1)\nqcB.z(0)\nqcB.h(0)\n\nprint('State A:', Statevector.from_instruction(qcA).data)\nprint('State B:', Statevector.from_instruction(qcB).data)\n",
            "tutor_challenge": "Why can two circuits with the same gates produce different states? Under what conditions do two gates commute (their order does not matter)?"
        },
        "Phase Kickback": {
            "big_idea": "A controlled operation can push phase information backward into the control qubit.",
            "composer": "Use H gates around controlled operations and inspect the phase-sensitive probabilities.",
            "checkpoint": "What changes when phase becomes visible through interference?",
            "practice": "Build a controlled-Z from H and CNOT, then explain the phase path.",
            "lesson_text": "In classical computing, a controlled gate only affects the target bit. But in the quantum world, it is a two-way street!<br><br>When you perform a controlled operation (like CNOT), you expect the control qubit to affect the target. But if the target is in a superposition state, something magical happens: the target's phase information **'kicks back'** up into the control qubit! <br><br>It is like a weight pulling the string in reverse. Phase kickback is the secret engine behind almost every advanced quantum algorithm, including phase estimation and Shor's algorithm. Add Hadamard gates around a CNOT to see phase kickback in action!",
            "tutorial_code": "from qiskit import QuantumCircuit\n\n# Create a circuit utilizing phase kickback\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.h(1)\nqc.z(1)      # Place target in phase sensitive state\nqc.cx(0, 1)  # Controlled gate kicks target phase back to control qubit 0\nqc.h(0)\nprint(qc)\n",
            "tutor_challenge": "What changes when phase becomes visible through interference? Why does applying H gates on the control qubit before and after a CNOT reveal the kicked-back phase?"
        },
        "Parameterized Rotations": {
            "big_idea": "Rx, Ry, and Rz make circuits tunable, which is the basis of variational algorithms.",
            "composer": "Sweep an angle slider and watch the vector move continuously instead of jumping gate to gate.",
            "checkpoint": "Which rotation changes measurement odds from |0⟩, and which initially hides as phase?",
            "practice": "Create a circuit with a Parameter theta and bind three values.",
            "lesson_text": "Fixed gates like H or X rotate the qubit by exact intervals (like flipping 180°). But what if we want to rotate by just 12° or 45.7°?<br><br>**Parameterized Rotations (Rx, Ry, Rz)** let us rotate the qubit vector continuously by any fraction of a degree. This makes circuits tunable, serving as the foundation of modern machine learning and molecular chemistry simulations on quantum computers.<br><br>Try selecting the Ry gate and sweeping the rotation slider. You will see the vector glide smoothly along the sphere surface rather than jumping!",
            "tutorial_code": "from qiskit import QuantumCircuit\nimport numpy as np\n\nqc = QuantumCircuit(1)\n# Rotate by exactly 45 degrees (pi/4 radians) around Y-axis\nqc.ry(np.pi / 4, 0)\nprint(qc)\n",
            "tutor_challenge": "Which rotation changes measurement odds from |0⟩, and which initially hides as phase? Verify this by comparing Ry and Rz gates on the Composer."
        },
    },
    "Level 3: Simulation + Noise": {
        "Statevector vs Shots": {
            "big_idea": "Statevectors show exact amplitudes, while shot-based simulation imitates repeated experimental sampling.",
            "composer": "Compare probability bars with noisy-looking sampled counts in the sandbox.",
            "checkpoint": "Why can a perfect 50/50 state return 512/512 only rarely?",
            "practice": "Run the same Bell circuit with 128, 1024, and 8192 shots.",
            "lesson_text": "A classical simulator has a massive superpower: it can look 'under the hood' and calculate the exact mathematical **Statevector** of the qubit—representing absolute theoretical perfection.<br><br>But a real quantum computer can only give us a 0 or a 1 when measured. To find the probabilities, we must run the circuit multiple times (called **'shots'**) and count the frequency of outcomes. This introduction of statistical sampling means that even a perfect 50/50 superposition will rarely return exactly 512/512 counts due to standard statistical fluctuations. Try running varying shot counts in the Sandbox!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()\n\nprint('This circuit can be simulated in Aer simulator using run() for custom shots.')\nprint(qc)\n",
            "tutor_challenge": "Why can a perfect 50/50 superposition state return 512/512 counts only rarely? How does the statistical deviation change when the number of shots is increased from 100 to 10,000?"
        },
        "Noise Models": {
            "big_idea": "Real devices introduce decoherence, gate error, and readout error, which turn ideal circuits into distributions.",
            "composer": "Use the Bell circuit as a reference, then add noise in the sandbox.",
            "checkpoint": "What kind of error would reduce Bell-state correlation?",
            "practice": "Use Aer noise tools to add depolarizing or thermal-relaxation noise.",
            "lesson_text": "In theory, quantum circuits are pristine and perfect. In reality, physical quantum computers are highly delicate and prone to errors.<br><br>Thermal fluctuations, magnetic fields, and wire resistance cause **decoherence** (where qubits lose their quantum properties and decay into thermal noise) and **gate errors**. This turns a pure, ideal state vector into a fuzzy, mixed state.<br><br>We use classical simulators equipped with **Noise Models** to anticipate these hardware errors and find ways to write more error-tolerant code. Select a preset in the Sandbox and check how adding noise modifications alters the output distribution.",
            "tutorial_code": "from qiskit_aer.noise import NoiseModel, depolarizing_error\n# We define a simple depolarizing noise model in Python\nnoise_model = NoiseModel()\nerror = depolarizing_error(0.05, 1) # 5% gate error\nnoise_model.add_all_qubit_quantum_error(error, ['h', 'x'])\nprint('Noise model defined successfully with a 5% single-qubit gate error.')\n",
            "tutor_challenge": "What kind of error would reduce Bell-state correlation? Why does thermal relaxation (T1) always drag qubits toward the |0⟩ state?"
        },
        "Transpilation": {
            "big_idea": "Transpilation rewrites an abstract circuit into the basis gates and connectivity of a target backend.",
            "composer": "Export the circuit, transpile it, and compare the before/after depth.",
            "checkpoint": "Why might a simple circuit grow when mapped to real hardware?",
            "practice": "Transpile a 3-qubit circuit for a fake backend or coupling map.",
            "lesson_text": "When you design a circuit, you can use any gate on any qubit. But real physical chips have strict constraints:<br><br><ul><li><strong>Basis Gates</strong>: Physical hardware can only execute a small, native set of gates (often only Rx, Rz, and CNOT). Any other gate (like H or T) must be compiled out of these.</li><li><strong>Connectivity</strong>: You can only run a CNOT between qubits that are physically connected by superconducting wires on the chip.</li></ul><br>**Transpilation** is the compilation process that rewrites your idealized circuit to fit a specific chip's geometry and gate set. Try exporting your composer circuit and transpiling it in the Sandbox!",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager\nfrom qiskit_aer import AerSimulator\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n\nsim = AerSimulator()\npm = generate_preset_pass_manager(optimization_level=1, backend=sim)\ntranspiled_qc = pm.run(qc)\nprint('Transpiled circuit basis gates:', transpiled_qc.basis_gates if hasattr(transpiled_qc, 'basis_gates') else 'Compiled successfully')\n",
            "tutor_challenge": "Why might a simple circuit grow in depth when mapped to real hardware? How does swap gate insertion allow controlled operations between unconnected qubits?"
        },
    },
    "Level 4: Quantum Algorithms": {
        "Grover Intuition": {
            "big_idea": "Grover search alternates marking a target and amplifying its probability through interference.",
            "composer": "Use the sandbox to build small oracle and diffuser circuits.",
            "checkpoint": "Why is the diffuser often described as inversion about the mean?",
            "practice": "Build a two-qubit Grover search and inspect the amplified target probability.",
            "lesson_text": "Grover's Search is one of the crown jewels of quantum computing. It allows searching an unsorted database of size N in just √N steps (a quadratic speedup).<br><br>Rather than checking entries one-by-one, Grover's algorithm puts all database indexes into a uniform superposition and alternates two steps:<br><ol><li><strong>The Oracle</strong>: Negates the phase of the correct answer (marking it without looking).</li><li><strong>The Diffuser</strong>: Performs an 'inversion about the mean' which amplifies the marked item's probability while suppressing all others.</li></ol><br>Repeat this choreography, and the correct answer will rise to a near 100% chance of measurement! Try running the Grover preset in the Sandbox.",
            "tutorial_code": "from qiskit import QuantumCircuit\n# Small 2-qubit Grover circuit finding state |11>\nqc = QuantumCircuit(2)\nqc.h([0, 1])\n# Oracle for |11>\nqc.cz(0, 1)\n# Diffuser\nqc.h([0, 1])\nqc.x([0, 1])\nqc.cz(0, 1)\nqc.x([0, 1])\nqc.h([0, 1])\nprint(qc)\n",
            "tutor_challenge": "Why is the diffuser often described as 'inversion about the mean'? How does the geometry of Grover rotations map onto a two-dimensional subspace?"
        },
        "QFT Intuition": {
            "big_idea": "The quantum Fourier transform converts periodic structure into phase patterns.",
            "composer": "Explore phase gates first; QFT is phase choreography at scale.",
            "checkpoint": "What information is stored in relative phase instead of direct probability?",
            "practice": "Implement a 3-qubit QFT and then reverse the qubit order.",
            "lesson_text": "Just like the classical Fast Fourier Transform (FFT) breaks a complex sound wave down into its individual frequencies, the **Quantum Fourier Transform (QFT)** translates periodic amplitudes into phase frequencies.<br><br>The QFT maps a qubit state from the computational basis (|0⟩, |1⟩) to the phase basis. By encoding periodic patterns across superpositions and executing phase gate rotations, we can extract periodicities with exponential speedup. This forms the mathematical heart of Shor's algorithm for factoring numbers! View the phase rotations on the Bloch spheres when you apply phase-shifting gates.",
            "tutorial_code": "from qiskit import QuantumCircuit\nimport numpy as np\n\n# 2-qubit Quantum Fourier Transform\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cp(np.pi / 2, 0, 1) # Controlled-phase gate\nqc.h(1)\nqc.swap(0, 1)\nprint(qc)\n",
            "tutor_challenge": "What information is stored in relative phase instead of direct probability? How does the QFT enable quantum systems to solve the hidden subgroup problem?"
        },
        "VQE": {
            "big_idea": "Variational Quantum Eigensolver combines parameterized quantum circuits with a classical optimizer.",
            "composer": "Use Ry/Rz layers as a small ansatz and watch parameters change the state.",
            "checkpoint": "Why does VQE need both a quantum circuit and a classical optimizer?",
            "practice": "Build a tiny ansatz and compute expectation values with Qiskit primitives.",
            "lesson_text": "We are currently in the NISQ (Noisy Intermediate-Scale Quantum) era. Since hardware has noise, we use **Hybrid Algorithms** that split the work between classical CPUs and quantum QPUs.<br><br>The **Variational Quantum Eigensolver (VQE)** is the most famous hybrid algorithm. It is used to find the ground state energy of molecules (incredibly useful for drug discovery and chemistry):<br><ol><li>The quantum chip prepares a state using a parameterized circuit (the <em>Ansatz</em>) and measures its energy.</li><li>A classical computer analyzes the energy and uses an optimizer (like gradient descent) to adjust the circuit's angles.</li><li>The cycle repeats until the lowest possible energy state is found!</li></ol>",
            "tutorial_code": "from qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\n\ntheta = Parameter('t')\nqc = QuantumCircuit(1)\n# Setup ansatz with tunable Parameter theta\nqc.ry(theta, 0)\nprint(qc)\n",
            "tutor_challenge": "Why does VQE need both a quantum circuit and a classical optimizer? What is the 'barren plateau' problem, and how does it affect optimizer scaling?"
        },
    },
    "Level 5: Hardware + Advanced Workflows": {
        "Primitives": {
            "big_idea": "Modern Qiskit workflows use primitives such as Sampler and Estimator to run circuit jobs with clear intent.",
            "composer": "Export a circuit, then adapt it to a Sampler or Estimator workflow.",
            "checkpoint": "When do you want counts, and when do you want expectation values?",
            "practice": "Run a Bell circuit through a sampler-style workflow.",
            "lesson_text": "In earlier versions of Qiskit, execution returned raw measurement counts. Modern Qiskit 1.0+ has moved to a more physics-first interface called **Primitives**:<br><br><ul><li><strong>Sampler</strong>: Returns the quasi-probability distribution of the basis states. Use this when you want to get counts or sample outcomes (e.g. key search or cryptography).</li><li><strong>Estimator</strong>: Computes the expectation value of physical operators (observables). Use this when you want to measure physical quantities like energy, magnetization, or expectation values (e.g., in VQE or chemistry).</li></ul><br>Primitives simplify writing hardware-agnostic algorithms by handling error mitigation and hardware layouts behind the scenes!",
            "tutorial_code": "print('Modern Qiskit workflows define: Primitives. Sampler vs Estimator.')\nprint('Example import: from qiskit.primitives import StatevectorSampler, StatevectorEstimator')\n",
            "tutor_challenge": "Explorer, when do you want measurement counts (Sampler) and when do you want expectational physical values (Estimator)? Detail a scenario for each!"
        },
        "Error Mitigation": {
            "big_idea": "Error mitigation estimates better answers from noisy data without fully correcting the quantum state.",
            "composer": "Start with shallow circuits and compare ideal versus noisy expectations.",
            "checkpoint": "Why is mitigation not the same as fault-tolerant error correction?",
            "practice": "Compare raw and mitigated expectation values for a small observable.",
            "lesson_text": "True **Quantum Error Correction (QEC)** requires linking thousands of physical qubits together to form a single, perfect 'logical qubit.' Since we don't have enough physical qubits for this yet, we use **Error Mitigation**.<br><br>Error mitigation uses classical mathematical post-processing to 'extrapolate' what the perfect, zero-noise answer would be based on noisy experiments. Techniques like *Zero Noise Extrapolation (ZNE)* run circuits under intentionally increased noise levels, allowing us to map the noise curve and subtract it. This lets us run utility-scale scientific calculations on noisy hardware today!",
            "tutorial_code": "print('Zero Noise Extrapolation (ZNE) runs circuits at multiple noise gains (e.g. 1x, 3x, 5x error),')\nprint('then extrapolates back to the theoretical zero-noise state mathematically.')\n",
            "tutor_challenge": "Why is error mitigation not the same as fault-tolerant error correction? Why is it limited to shallow or intermediate-depth circuits?"
        },
        "Hardware Execution": {
            "big_idea": "Running on IBM Quantum hardware requires backend selection, transpilation, job submission, and result analysis.",
            "composer": "Treat the composer as the circuit design surface, then export and prepare it for a backend.",
            "checkpoint": "What constraints does a real backend impose that the ideal composer hides?",
            "practice": "Prepare a backend-ready notebook using Qiskit Runtime patterns.",
            "lesson_text": "You have reached the final frontier! You are ready to run your circuits on real quantum computers in the cloud.<br><br>Running on real IBM Quantum superconducting hardware requires these exact steps:<br><ol><li><strong>Authenticate</strong>: Initialize your account using your IBM Quantum API token.</li><li><strong>Select Backend</strong>: Query the IBM service to find a device with the shortest queue and lowest error rate.</li><li><strong>Transpile</strong>: Map your custom circuit specifically to that device's physical coupling map and basis gates.</li><li><strong>Runtime Job</strong>: Submit the transpiled circuit to the IBM execution queue using Qiskit Runtime Sampler/Estimator primitives, and await your results!</li></ol><br>Congratulations on completing the pathway, Explorer! You have built a solid foundation in quantum computing!",
            "tutorial_code": "print('IBM Quantum hardware authentication:')\nprint('from qiskit_ibm_runtime import QiskitRuntimeService')\nprint('# service = QiskitRuntimeService(channel=\"ibm_quantum\", token=\"YOUR_TOKEN\")')\n",
            "tutor_challenge": "What constraints does a real physical hardware chip impose that the ideal simulation environment completely hides?"
        },
    },
}
