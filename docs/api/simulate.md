# Simulate API Router — Technical Documentation

## 1. Module Overview

**Module:** `backend/routers/simulate.py`  
**Project:** Qiskit Intuition  
**Architectural Layer:** API / Presentation Layer  
**Framework:** FastAPI  
**Communication Protocol:** HTTP  
**Response Format:** JSON

### 1.1 Purpose

The `simulate.py` module provides HTTP endpoints for quantum circuit simulation and Qiskit code generation.

It acts as an interface between client applications and the quantum simulation engine, allowing users to submit quantum gate configurations, retrieve simulation results, visualise quantum circuits, and export their circuits as Qiskit code.

### 1.2 Responsibilities

The module is responsible for:

- Exposing endpoints for quantum circuit simulation and code export.
- Validating circuit configurations using Pydantic models.
- Initialising the quantum engine with the requested number of qubits.
- Converting validated gate models into the dictionary format expected by the engine.
- Delegating quantum computations to the quantum engine.
- Retrieving statevectors, Bloch angles, measurement probabilities, and circuit figures.
- Encoding generated circuit figures as Base64 strings.
- Returning structured JSON responses.
- Handling unexpected exceptions during request processing.

The module does not directly implement quantum gate operations, statevector calculations, or quantum simulation algorithms.

---

## 2. Architectural Integration

The module belongs to the API layer of Qiskit Intuition's modular architecture.

It delegates quantum simulation and code generation to the `QuantumEngine` class, maintaining separation between HTTP request handling and quantum computing logic.

### 2.1 Internal Dependencies

| Dependency | Responsibility |
|---|---|
| `backend.core.quantum_engine` | Provides the `QuantumEngine` class responsible for managing quantum circuit data, performing simulations, retrieving quantum states and probabilities, generating circuit figures, and exporting Qiskit code. |

### 2.2 External Dependencies

| Library | Purpose |
|---|---|
| `fastapi.APIRouter` | Defines and registers HTTP endpoints. |
| `fastapi.HTTPException` | Represents HTTP errors. |
| `pydantic.BaseModel` | Defines request validation schemas. |
| `pydantic.Field` | Enforces field constraints and default values. |
| `typing.List` | Defines typed collections of quantum gates. |
| `typing.Optional` | Defines optional gate parameters. |
| `base64` | Encodes PNG figures into Base64 strings. |
| `io.BytesIO` | Provides an in-memory binary buffer for figure serialization. |
| `matplotlib` | Configures the non-interactive plotting backend. |
| `matplotlib.pyplot` | Saves and closes generated figures. |

### 2.3 Matplotlib Configuration

The module configures Matplotlib to use the `Agg` backend:

```python
matplotlib.use("Agg")
```

This backend supports figure rendering without requiring a graphical display, making it suitable for server-side applications.

---

## 3. Request Models

The module defines two Pydantic models for representing quantum gates and simulation requests.

### 3.1 GateModel

**Purpose:** Represents an individual quantum gate and its configuration.

| Field | Type | Required | Description |
|---|---|---|---|
| `gate` | `str` | Yes | Identifier of the quantum gate to apply. |
| `target` | `int` | Yes | Target qubit index, constrained to 0–9. |
| `control` | `int \| None` | No | Optional control qubit index, constrained to 0–9 when provided. Defaults to `None`. |
| `angle` | `float \| None` | No | Optional rotation angle. Defaults to `None`. |

**Example gate:**

```json
{
  "gate": "h",
  "target": 0,
  "control": null,
  "angle": null
}
```

The model validates the data types and numerical constraints of the gate configuration.

It does not restrict `gate` to a predefined set of supported operations or verify whether the specified qubit indices are valid for the requested circuit size.

### 3.2 SimulateRequest

**Purpose:** Represents a quantum circuit configuration submitted for simulation or code export.

| Field | Type | Required | Description |
|---|---|---|---|
| `gates` | `list[GateModel]` | Yes | Collection of quantum gates, limited to a maximum of 100 elements. |
| `num_qubits` | `int` | No | Number of qubits in the circuit, ranging from 1 to 10. Defaults to `2`. |
| `noisy` | `bool` | No | Enables the noisy probability calculation option. Defaults to `False`. |

**Example request:**

```json
{
  "gates": [
    {
      "gate": "h",
      "target": 0
    },
    {
      "gate": "cx",
      "target": 1,
      "control": 0
    }
  ],
  "num_qubits": 2,
  "noisy": false
}
```

This example represents a two-qubit circuit configuration using a Hadamard gate followed by a controlled-X gate, assuming the quantum engine supports these identifiers.

The `noisy` parameter is used by the simulation endpoint when retrieving probabilities. It is not used by the code export endpoint.

---

## 4. API Endpoints

The module exposes two HTTP POST endpoints.

| Endpoint | Handler | Response Format | Description |
|---|---|---|---|
| `/simulate` | `simulate()` | JSON | Executes a quantum circuit simulation and returns its results. |
| `/export` | `export_circuit()` | JSON | Generates Qiskit code from a quantum circuit configuration. |

The paths are relative to the router and may include an additional prefix when registered in the main FastAPI application.

### 4.1 POST /simulate

**Handler:** `simulate()`  
**Request Model:** `SimulateRequest`  
**Response Format:** JSON

#### Description

Processes a quantum circuit configuration using the quantum engine and returns its statevector, Bloch angles, measurement probabilities, and circuit visualisation.

#### Execution Flow

1. Receives an HTTP POST request containing the circuit configuration.
2. Validates the request using the `SimulateRequest` model.
3. Initialises `QuantumEngine` with the requested number of qubits.
4. Iterates through the supplied gate configurations.
5. Converts each gate into a dictionary containing its identifier, target, control, and optional angle.
6. Appends each gate dictionary to `engine.gates`.
7. Retrieves the circuit statevector using `get_statevector()`.
8. Executes `run_simulation()` to obtain Bloch angles.
9. Retrieves probabilities using `get_probabilities(noisy=req.noisy)`.
10. Generates the circuit figure using `get_circuit_figure()`.
11. Converts the figure into a Base64-encoded PNG string.
12. Converts statevector amplitudes into string representations.
13. Returns the simulation results as JSON.

#### Example Request

```http
POST /simulate
Content-Type: application/json
```

```json
{
  "gates": [
    {
      "gate": "h",
      "target": 0
    }
  ],
  "num_qubits": 1,
  "noisy": false
}
```

#### Example Response

```json
{
  "statevector": [
    "(0.7071067811865476+0j)",
    "(0.7071067811865475+0j)"
  ],
  "bloch_angles": [],
  "probabilities": {
    "0": 0.5,
    "1": 0.5
  },
  "circuit_figure": "<base64-encoded-png>"
}
```

This response is illustrative of the expected quantum state for a Hadamard operation on a qubit initially in the zero state.

The exact structure of `bloch_angles` and `probabilities`, as well as the numerical precision of the statevector, depends on the `QuantumEngine` implementation.

### 4.2 POST /export

**Handler:** `export_circuit()`  
**Request Model:** `SimulateRequest`  
**Response Format:** JSON

#### Description

Converts a submitted quantum circuit configuration into Qiskit source code using the quantum engine.

#### Execution Flow

1. Receives an HTTP POST request containing a circuit configuration.
2. Validates the request against `SimulateRequest`.
3. Initialises `QuantumEngine` with the specified number of qubits.
4. Converts the supplied gates into dictionaries.
5. Appends each gate configuration to `engine.gates`.
6. Invokes `get_qiskit_code()` to generate source code.
7. Returns the generated code in a JSON response.

#### Example Request

```http
POST /export
Content-Type: application/json
```

```json
{
  "gates": [
    {
      "gate": "h",
      "target": 0
    }
  ],
  "num_qubits": 1
}
```

#### Example Response

```json
{
  "code": "from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nqc.h(0)"
}
```

The generated code shown above is illustrative. The exact output depends on the implementation of `QuantumEngine.get_qiskit_code()`.

The endpoint returns the generated source code as a string rather than as a downloadable file.

---

## 5. Response Structure

The module returns different JSON structures depending on the requested operation.

### 5.1 Simulation Response

| Field | Expected Type | Description |
|---|---|---|
| `statevector` | `list[str]` | String representations of complex statevector amplitudes. |
| `bloch_angles` | Engine-defined | Bloch angle data returned by the simulation engine. |
| `probabilities` | Engine-defined | Probability data returned by the quantum engine. |
| `circuit_figure` | `str` | Base64-encoded PNG representation of the circuit, or an empty string if figure conversion fails. |

The statevector is obtained from `sv.data`, with each amplitude converted to a string.

The router does not transform the values returned by `run_simulation()` or `get_probabilities()`.

### 5.2 Export Response

| Field | Expected Type | Description |
|---|---|---|
| `code` | Engine-defined, expected `str` | Generated Qiskit source code returned by `get_qiskit_code()`. |

The router forwards the result of `get_qiskit_code()` directly without additional formatting.

### 5.3 Figure Encoding

The module defines a helper function:

```python
def fig_to_base64(fig):
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str
    except Exception:
        return ""
```

**Purpose:** Converts a Matplotlib figure into a Base64-encoded PNG string.

**Behaviour:**

1. Creates an in-memory binary buffer.
2. Saves the supplied figure in PNG format.
3. Moves the buffer position to its beginning.
4. Reads the PNG binary content.
5. Encodes the content into Base64.
6. Decodes the encoded bytes into a UTF-8 string.
7. Closes the figure using Matplotlib.
8. Returns the encoded string.

If an exception occurs, the function returns an empty string.

The current implementation does not guarantee that the figure is closed when an exception occurs before `plt.close(fig)`.

---

## 6. Error Handling

Both endpoints wrap their main operations in `try-except` blocks.

Unexpected exceptions are converted into HTTP responses with status code `500`.

**Example HTTP error response:**

```json
{
  "detail": "Simulation error description"
}
```

FastAPI and Pydantic automatically handle request validation errors.

### 6.1 Error Scenarios

| Scenario | Expected Behaviour |
|---|---|
| Missing `gates` field | HTTP 422 validation error. |
| More than 100 gates | HTTP 422 validation error. |
| `num_qubits` outside 1–10 | HTTP 422 validation error. |
| Gate target outside 0–9 | HTTP 422 validation error. |
| Control index outside 0–9 | HTTP 422 validation error. |
| Unsupported gate identifier | Depends on the quantum engine; an uncaught exception produces HTTP 500. |
| Quantum simulation exception | HTTP 500. |
| Qiskit code generation exception | HTTP 500. |
| Figure conversion exception | Returns an empty figure string rather than raising an HTTP error. |

### 6.2 Current Limitations

- Internal exception messages are exposed to clients.
- No explicit logging mechanism is implemented.
- Unsupported gate identifiers are not rejected by the request model.
- Target and control indices are not validated against `num_qubits`.
- The same qubit may be supplied as both target and control without router-level rejection.
- Figure conversion errors are silently suppressed.
- Response structures are not enforced through dedicated Pydantic response models.

---

## 7. Security Considerations

The module processes user-supplied quantum circuit configurations and delegates their execution to the quantum engine.

Although the router does not directly execute arbitrary Python source code, circuit simulation may require substantial computational resources.

Relevant safeguards include:

- Restricting circuit size and gate count.
- Validating supported quantum gate identifiers.
- Ensuring target and control qubits belong to the configured circuit.
- Applying execution timeouts and resource limits where necessary.
- Preventing excessive concurrent simulation requests.
- Applying authentication, authorisation, and rate limiting where appropriate.
- Avoiding exposure of internal exception details.

The request model already limits the number of qubits to 10 and the number of gates to 100.

These constraints provide basic input bounds but do not guarantee predictable resource consumption.

Authentication, authorisation, and rate limiting are not implemented directly in the supplied module.

---

## 8. Module Boundaries

### Included Responsibilities

- HTTP endpoint registration.
- Request payload validation.
- Quantum engine initialisation.
- Gate configuration transformation.
- Delegation of simulation and code generation.
- Statevector serialization.
- Circuit figure encoding.
- JSON response construction.
- HTTP exception conversion.

### Excluded Responsibilities

- Implementation of quantum gates.
- Construction of quantum states.
- Statevector computation algorithms.
- Quantum measurement simulation.
- Noise model implementation.
- Quantum circuit drawing logic.
- Qiskit code generation logic.
- Client-side circuit visualisation.

These responsibilities belong to the quantum engine or other application components.

---

## 9. Testing Recommendations

| Test | Expected Result |
|---|---|
| Submit a valid circuit | Returns simulation results as JSON. |
| Submit a single-qubit Hadamard circuit | Produces the expected statevector and probabilities, assuming standard initialisation. |
| Submit a valid controlled-gate circuit | Processes the supplied target and control indices. |
| Submit a circuit with rotation angles | Passes the angle values to the quantum engine. |
| Submit more than 100 gates | Returns HTTP 422. |
| Submit an invalid qubit count | Returns HTTP 422. |
| Submit a target index outside 0–9 | Returns HTTP 422. |
| Submit an unsupported gate | Verifies the quantum engine's error handling. |
| Trigger a simulation exception | Returns HTTP 500. |
| Trigger a figure conversion exception | Returns an empty figure string. |
| Submit a valid export request | Returns generated Qiskit code. |
| Trigger a code generation exception | Returns HTTP 500. |

Router-level unit tests should mock `QuantumEngine` to validate request handling, gate transformation, and response construction independently of quantum simulation algorithms.

Integration tests should additionally verify the behaviour of the actual quantum engine.

---

## 10. Maintenance Notes

When modifying the simulation router:

1. Preserve the separation between API handling and quantum simulation logic.
2. Update Pydantic models when introducing new gate parameters or circuit constraints.
3. Maintain compatibility with the `QuantumEngine` interface.
4. Ensure new gate types are correctly represented in the dictionaries passed to the engine.
5. Review the serialization of simulation results.
6. Maintain consistent figure encoding and resource cleanup.
7. Update endpoint documentation and automated tests when request or response contracts change.
8. Keep simulation and code export behaviour consistent with the supported circuit representation.

Changes to the internal quantum simulation algorithms should not require modifications to this router unless the quantum engine's public interface or return structure changes.
