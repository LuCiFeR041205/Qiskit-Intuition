# Execute API Router — Technical Documentation

## 1. Module Overview

**Module:** `backend/routers/execute.py`
**Project:** Qiskit Intuition
**Architectural Layer:** API / Presentation Layer
**Framework:** FastAPI
**Communication Protocol:** HTTP
**Response Format:** JSON

### 1.1 Purpose

The `execute.py` module provides an HTTP endpoint for executing Python code within Qiskit Intuition's notebook execution environment.

It acts as an interface between client applications and the notebook execution engine, allowing users to submit code and retrieve its execution results, including standard output, error information, and generated figures.

### 1.2 Responsibilities

The module is responsible for:

- Exposing an HTTP endpoint for code execution.
- Validating incoming requests using Pydantic.
- Delegating code execution to the notebook engine.
- Encoding generated PNG figures into Base64 strings.
- Returning structured execution results as JSON.
- Handling unexpected exceptions during request processing.

The module does not directly implement the code execution environment or manage the underlying execution process.

---

## 2. Architectural Integration

The module belongs to the API layer of Qiskit Intuition's modular architecture.

It delegates execution responsibilities to the `notebook_engine` module, maintaining separation between HTTP request handling and execution logic.

### 2.1 Internal Dependencies

| Dependency                     | Responsibility                                                                                                            |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| `backend.core.notebook_engine` | Provides the `execute_notebook_code()` function responsible for executing submitted code and returning execution results. |

### 2.2 External Dependencies

| Library                 | Purpose                                            |
| ----------------------- | -------------------------------------------------- |
| `fastapi.APIRouter`     | Defines and registers the execution endpoint.      |
| `fastapi.HTTPException` | Represents HTTP errors.                            |
| `pydantic.BaseModel`    | Validates incoming request payloads.               |
| `base64`                | Encodes generated PNG figures into Base64 strings. |

---

## 3. Request Models

### 3.1 ExecuteRequest

**Purpose:** Represents a request containing Python code to be executed by the notebook engine.

| Field  | Type  | Required | Description                                 |
| ------ | ----- | -------- | ------------------------------------------- |
| `code` | `str` | Yes      | Python source code submitted for execution. |

**Example request:**

```json
{
  "code": "print('Hello, Qiskit Intuition!')"
}
```

Pydantic validates that the incoming request contains the required `code` field with a string value.

No additional constraints, such as maximum code length or non-empty content, are defined in this model.

---

## 4. API Endpoint

### 4.1 POST /execute

**Handler:** `execute()`
**Request Model:** `ExecuteRequest`
**Response Format:** JSON

#### Description

Executes the submitted Python code using the notebook engine and returns the corresponding execution results.

#### Execution Flow

1. Receives an HTTP POST request containing Python code.
2. Validates the request against the `ExecuteRequest` model.
3. Passes the submitted code to `execute_notebook_code()`.
4. Retrieves the execution results returned by the notebook engine.
5. Extracts generated figures from the `figures` collection.
6. Encodes each PNG figure into a Base64 ASCII string.
7. Constructs a structured JSON response containing the execution results.
8. Returns the response to the client.

#### Example Request

```http
POST /execute
Content-Type: application/json
```

```json
{
  "code": "print(2 + 2)"
}
```

#### Example Successful Response

```json
{
  "success": true,
  "stdout": "4\n",
  "stderr": "",
  "error": null,
  "figures": []
}
```

This example assumes that the notebook engine successfully executes the supplied code and captures its standard output.

---

## 5. Response Structure

The endpoint returns a JSON object containing five fields.

| Field     | Type          | Description                                                            |
| --------- | ------------- | ---------------------------------------------------------------------- |
| `success` | `bool`        | Indicates whether execution succeeded. Defaults to `false` if missing. |
| `stdout`  | `str`         | Captured standard output. Defaults to an empty string.                 |
| `stderr`  | `str`         | Captured standard error output. Defaults to an empty string.           |
| `error`   | `str \| null` | Execution error information, if available.                             |
| `figures` | `list[str]`   | Base64-encoded PNG figures generated during execution.                 |

The values are retrieved from the dictionary returned by `execute_notebook_code()`.

The router supplies fallback values when the corresponding keys are absent.

### 5.1 Figure Encoding

Generated figures are processed using the following expression:

```python
figures_b64 = [
    base64.b64encode(png).decode("ascii")
    for png in result.get("figures", [])
]
```

Each figure is expected to be represented as PNG binary data.

The encoding process converts the binary content into an ASCII-compatible Base64 string suitable for inclusion in JSON responses.

This operation does not generate figures or modify their visual content.

### 5.2 Execution Failure Response

If the notebook engine returns a result indicating unsuccessful execution, the endpoint can return a response such as:

```json
{
  "success": false,
  "stdout": "",
  "stderr": "NameError: name 'x' is not defined",
  "error": "NameError",
  "figures": []
}
```

This example is illustrative. The actual error fields depend on the structure returned by the notebook engine.

An unsuccessful code execution does not automatically produce an HTTP error response. If the notebook engine returns normally, the router returns its structured result.

---

## 6. Error Handling

The endpoint wraps its execution and response-processing logic in a `try-except` block.

Unexpected exceptions are converted into HTTP responses with status code `500`.

**Example HTTP error response:**

```json
{
  "detail": "Internal execution error"
}
```

FastAPI and Pydantic also handle request validation errors automatically.

### 6.1 Error Scenarios

| Scenario                             | Expected behaviour                                                         |
| ------------------------------------ | -------------------------------------------------------------------------- |
| Missing `code` field                 | HTTP 422 validation error.                                                 |
| Invalid request field type           | HTTP 422 when Pydantic rejects the value.                                  |
| Code execution reports failure       | JSON response with `success: false`, provided the engine returns normally. |
| Unexpected notebook engine exception | HTTP 500.                                                                  |
| Unexpected figure encoding exception | HTTP 500.                                                                  |

### 6.2 Current Limitations

- Internal exception messages are exposed to clients.
- No explicit logging mechanism is implemented in the router.
- No custom validation constraints are defined for the submitted code.
- The response structure is not enforced through a dedicated Pydantic response model.

---

## 7. Security Considerations

The endpoint accepts executable Python code from clients and forwards it to the notebook engine.

This introduces security considerations beyond ordinary data-processing endpoints.

Important safeguards include:

- Executing untrusted code within an appropriately isolated environment.
- Enforcing execution time and resource limits.
- Restricting filesystem and network access where appropriate.
- Preventing access to sensitive application resources.
- Applying authentication, authorisation, and rate limiting as required.

The supplied router does not implement these safeguards directly.

Their implementation must be verified within the notebook execution engine or the surrounding application infrastructure.

---

## 8. Module Boundaries

### Included Responsibilities

- HTTP endpoint registration.
- Request payload validation.
- Invocation of the notebook execution engine.
- Base64 encoding of PNG figures.
- JSON response construction.
- HTTP exception conversion.

### Excluded Responsibilities

- Python code interpretation and execution.
- Execution environment isolation.
- Quantum circuit simulation.
- Figure generation.
- Execution resource management.
- Client-side result rendering.

These responsibilities belong to the notebook engine or other application components.

---

## 9. Testing Recommendations

| Test                                             | Expected Result                                        |
| ------------------------------------------------ | ------------------------------------------------------ |
| Submit valid Python code                         | Returns execution results in JSON.                     |
| Submit code producing standard output            | Populates the `stdout` field.                          |
| Submit code producing an execution error         | Returns the engine's failure information.              |
| Submit code generating PNG figures               | Returns Base64-encoded figure strings.                 |
| Submit a request without `code`                  | Returns HTTP 422.                                      |
| Trigger an unexpected execution engine exception | Returns HTTP 500.                                      |
| Return a result with missing optional keys       | Applies the defined fallback values.                   |
| Return malformed figure data                     | Verifies that the router handles the encoding failure. |

Tests should mock `execute_notebook_code()` when validating router-specific behaviour independently of the execution engine.

---

## 10. Maintenance Notes

When modifying the execution endpoint:

1. Preserve the separation between API handling and notebook execution logic.
2. Update the request model when introducing new input parameters.
3. Maintain compatibility with the notebook engine's return structure.
4. Ensure generated figures remain compatible with the expected response format.
5. Review error handling when changing execution behaviour.
6. Update API tests and documentation whenever the request or response contract changes.

Changes to the internal execution engine should not require modifications to this router unless its public interface or return structure changes.
