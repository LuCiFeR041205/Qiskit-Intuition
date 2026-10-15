# Agents API Router - Technical Documentation

## 1. Module Overview

**Module:** `backend/routers/agents.py`  
**Project:** Qiskit Intuition  
**Architectural Layer:** API / Presentation Layer  
**Framework:** FastAPI  
**Communication Protocol:** HTTP / Server-Sent Events (SSE)

### 1.1 Purpose

The `agents.py` module provides HTTP endpoints that expose the AI-powered educational capabilities of Qiskit Intuition.

It acts as an interface between client applications and the underlying AI agents, allowing users to request conceptual explanations, circuit coaching, answer evaluation, code generation, learning challenges, and contextual tutoring.

The module also supports automatic intent classification and request routing to specialised agents.

### 1.2 Responsibilities

The module is responsible for:

- Defining and exposing API endpoints using FastAPI.
- Validating incoming request payloads through Pydantic models.
- Delegating requests to the appropriate AI agents or teaching services.
- Converting generated content into SSE-compatible streams.
- Returning structured JSON responses for contextual tutoring.
- Handling exceptions raised during endpoint execution.

The module does not directly implement AI inference, quantum circuit simulation, or agent-specific educational logic.

---

## 2. Architectural Integration

The module belongs to the API layer of Qiskit Intuition's modular architecture.

It communicates with specialised agents and the teaching assistant service while remaining independent of their internal implementations.

### 2.1 Internal Dependencies

| Dependency | Responsibility |
|---|---|
| `agents.base_agent` | Provides generic AI response streaming. |
| `agents.composer_agent` | Explains quantum circuit operations. |
| `agents.feynman_agent` | Generates conceptual explanations. |
| `agents.qiskit_engineer` | Generates code from concepts and analogies. |
| `agents.router_agent` | Classifies user intent and delegates requests to agents. |
| `agents.socratic_tutor` | Generates educational challenges. |
| `backend.core.teaching_assistant` | Provides contextual, code-aware tutoring. |

### 2.2 External Dependencies

| Library | Purpose |
|---|---|
| `fastapi.APIRouter` | Defines and groups HTTP endpoints. |
| `fastapi.HTTPException` | Represents HTTP errors. |
| `fastapi.responses.StreamingResponse` | Streams responses to clients. |
| `pydantic.BaseModel` | Defines request validation schemas. |
| `pydantic.Field` | Defines model field defaults. |
| `json` | Serialises agent metadata into JSON. |

---

## 3. Request Models

The module defines Pydantic models to validate incoming requests.

### 3.1 ExplainRequest

**Purpose:** Represents a request for an explanation of a quantum computing concept.

| Field | Type | Required | Description |
|---|---|---|---|
| `concept` | `str` | Yes | Quantum concept to explain. |

### 3.2 CoachRequest

**Purpose:** Provides information about a quantum circuit operation requiring educational guidance.

| Field | Type | Required | Description |
|---|---|---|---|
| `latest_gate` | `str` | Yes | Most recently applied quantum gate. |
| `qubit` | `int` | Yes | Target qubit index. |
| `full_circuit_desc` | `str` | Yes | Description of the current circuit. |
| `eli5_mode` | `bool` | No | Enables simplified explanations. Defaults to `False`. |

### 3.3 EvaluateRequest

**Purpose:** Represents a learner's answer to an educational checkpoint.

| Field | Type | Required | Description |
|---|---|---|---|
| `user_answer` | `str` | Yes | Learner's submitted answer. |
| `checkpoint` | `str` | Yes | Checkpoint question being evaluated. |

### 3.4 RouteRequest

**Purpose:** Represents a user message requiring automatic agent selection.

| Field | Type | Required | Description |
|---|---|---|---|
| `user_message` | `str` | Yes | Message submitted by the user. |
| `eli5_mode` | `bool` | No | Enables simplified explanations. Defaults to `False`. |

### 3.5 TutorRequest

**Purpose:** Supplies the contextual information required by the teaching assistant.

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `str` | Yes | User's question or message. |
| `code` | `str` | No | Current code, if available. |
| `execution_error` | `str` | No | Error generated during code execution. |
| `gates` | `list[dict]` | No | Quantum gates in the current circuit. |
| `num_qubits` | `int` | No | Number of qubits. Defaults to `1`. |
| `lesson_title` | `str` | No | Current lesson title. |
| `use_model` | `bool` | No | Determines whether model-based assistance is enabled. Defaults to `True`. |

### 3.6 CodeRequest

**Purpose:** Provides information for AI-assisted code generation.

| Field | Type | Required | Description |
|---|---|---|---|
| `concept` | `str` | Yes | Quantum computing concept. |
| `analogy` | `str` | Yes | Analogy used to guide code generation. |

### 3.7 StreamRequest

**Purpose:** Defines prompts for generic AI text generation.

| Field | Type | Required | Description |
|---|---|---|---|
| `system_prompt` | `str` | Yes | Instructions defining model behaviour. |
| `user_prompt` | `str` | Yes | Prompt submitted for generation. |

---

## 4. API Endpoints

All endpoints use the HTTP `POST` method.

The paths listed below are relative to the router. Their final URLs depend on the prefix assigned when the router is registered in the FastAPI application.

| Endpoint | Handler | Response format | Description |
|---|---|---|---|
| `/explain` | `explain()` | SSE | Explains a quantum concept. |
| `/coach` | `coach()` | SSE | Provides circuit operation guidance. |
| `/evaluate` | `evaluate()` | SSE | Evaluates a learner's checkpoint answer. |
| `/route` | `route_agent()` | SSE | Classifies intent and routes requests. |
| `/tutor` | `tutor()` | JSON | Provides contextual tutoring. |
| `/code` | `generate_code_endpoint()` | SSE | Generates quantum-related code. |
| `/challenge` | `challenge()` | SSE | Generates educational problems. |
| `/stream` | `stream_generic()` | SSE | Streams responses from generic prompts. |

### 4.1 POST /explain

**Request model:** `ExplainRequest`

Delegates the supplied concept to `explain_concept()` from the Feynman agent.

The resulting explanation is streamed to the client.

### 4.2 POST /coach

**Request model:** `CoachRequest`

Delegates the latest quantum gate operation, target qubit, circuit description, and explanation mode to `explain_composer_action()`.

The endpoint provides educational guidance about the circuit operation.

### 4.3 POST /evaluate

**Request model:** `EvaluateRequest`

Constructs a prompt containing the checkpoint question and the learner's answer.

The prompt instructs the AI evaluator to assess conceptual understanding and provide encouraging, physics-focused feedback.

The requested feedback is limited to 150 words at the prompt level; this limit is not enforced programmatically.

### 4.4 POST /route

**Request model:** `RouteRequest`

Automatically selects an AI agent according to the user's message.

**Execution flow:**

1. Classifies the user message through `classify_intent()`.
2. Retrieves agent metadata from `AGENT_META`.
3. Falls back to the `general` metadata entry when necessary.
4. Sends an SSE event named `intent`, containing agent information.
5. Delegates response generation to `route_and_respond()`.
6. Streams the generated content through `chunk` events.

The metadata event includes the agent's intent, name, avatar, and description.

### 4.5 POST /tutor

**Request model:** `TutorRequest`

Creates a `TutorContext` instance containing code, execution errors, quantum gates, qubit count, and lesson information.

The context and user message are passed to `answer_tutor()`.

Unlike the other endpoints, this endpoint returns the teaching assistant's response directly, using FastAPI's default response serialisation.

### 4.6 POST /code

**Request model:** `CodeRequest`

Delegates the concept and analogy to `generate_code()` from the Qiskit engineer agent.

The generated output is returned as an SSE stream.

### 4.7 POST /challenge

**Request model:** `ExplainRequest`

Delegates the requested concept to `generate_problem()` from the Socratic tutor agent.

The generated educational challenge is streamed to the client.

### 4.8 POST /stream

**Request model:** `StreamRequest`

Passes the supplied system and user prompts directly to `generate_stream()`.

This endpoint exposes generic model generation capabilities without selecting a specialised agent.

---

## 5. Server-Sent Events

The module uses Server-Sent Events to deliver generated responses incrementally.

### 5.1 stream_sse()

**Signature:**

`stream_sse(generator)`

**Purpose:** Converts generated content into SSE-formatted messages.

**Behaviour:**

1. Iterates through the supplied generator.
2. Skips empty or otherwise falsy chunks.
3. Formats each remaining chunk using the SSE `data:` field.
4. Yields the formatted event followed by two newline characters.

**Example output:**

```text
data: A Hadamard gate creates

data: a superposition of basis states.
```

### 5.2 Route-specific streaming

The `/route` endpoint uses a separate asynchronous generator named `route_stream()`.

It emits two event types:

- `intent`: Contains agent classification metadata encoded as JSON.
- `chunk`: Contains generated response content.

### 5.3 Streaming considerations

The implementation currently inserts generated chunks directly into SSE messages.

Multiline content may require additional formatting to preserve valid SSE framing.

Additionally, errors occurring after a `StreamingResponse` has started may not be handled by the endpoint's surrounding exception handler.

---

## 6. Error Handling

Each endpoint wraps its main execution logic in a `try-except` block.

Unexpected exceptions caught during endpoint execution are converted into HTTP responses with status code `500`.

**Example response:**

```json
{
  "detail": "Error description"
}
```

FastAPI and Pydantic also provide automatic request validation. Invalid request payloads normally result in HTTP status code `422`.

### 6.1 Current Limitations

- Internal exception messages are exposed through the HTTP response.
- No endpoint-specific error categories are defined.
- Streaming errors may occur after the response has already started.
- No explicit logging mechanism is implemented in this module.
- No custom validation constraints are defined for fields such as `qubit` and `num_qubits`.

---

## 7. Security Considerations

The module accepts user-generated content and forwards it to AI agents.

The `/stream` endpoint additionally accepts both system and user prompts directly from clients.

Security considerations include:

- Restricting access to generic prompt-generation capabilities where appropriate.
- Preventing exposure of internal error details.
- Applying request-size limits and appropriate rate limiting.
- Validating numeric fields and structured quantum circuit data.
- Ensuring appropriate safeguards for model-generated content.

Authentication, authorisation, and rate limiting are not implemented directly in the supplied module.

They may be handled elsewhere in the application.

---

## 8. Module Boundaries

### Included Responsibilities

- HTTP endpoint definitions.
- Request schema validation.
- Agent invocation.
- Response streaming.
- Agent routing metadata.
- HTTP exception conversion.

### Excluded Responsibilities

- Quantum circuit execution.
- Quantum state simulation.
- Agent inference implementation.
- Model configuration and provider integration.
- Client-side rendering.
- Persistent storage.

These responsibilities are delegated to other modules or lie outside the scope of this router.

---

## 9. Testing Recommendations

The following tests are recommended to validate the module's behaviour.

| Test | Expected result |
|---|---|
| Submit a valid explanation request | Returns an SSE response. |
| Submit an invalid request payload | Returns HTTP 422. |
| Request circuit coaching | Invokes the composer agent with the supplied parameters. |
| Submit a checkpoint answer | Invokes the evaluator and streams feedback. |
| Submit a routing request | Emits agent metadata before generated chunks. |
| Request contextual tutoring | Returns a JSON-serialisable response. |
| Submit a code generation request | Streams generated content. |
| Submit an educational challenge request | Streams a generated problem. |
| Trigger an exception before streaming starts | Returns HTTP 500. |
| Trigger an exception during streaming | Verifies how the stream terminates and how the client handles the failure. |

---

## 10. Maintenance Notes

When introducing new agents or endpoints:

1. Define an appropriate Pydantic request model.
2. Import the corresponding agent or service function.
3. Register the endpoint using `APIRouter`.
4. Select the appropriate response format.
5. Implement suitable error handling.
6. Document the endpoint's input and output contract.
7. Add unit and integration tests.

Changes to the agent implementations should not require modifications to this router unless their public interfaces or response contracts change.
