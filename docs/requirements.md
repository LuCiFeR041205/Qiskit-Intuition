# WELCOME TO REQUIREMENTS!
We divide the program into two different requirements:
- Functional
- Non-Functional

Each requirements has:
- ID
- Name
- Description
- Preconditions
- Success Criteria / Expected Outcome
- Failure Handling

## Functional Requirements
### FR-01: User registration and login

**Description:**
The system shall allow the user to register through authentication and authorization using their google account.

**Preconditions:***
The user must have an existing google account.

**Success criteria:** 
- The is successfully registered.
- A valid token is created.
- The user is redirected to the dashboard.

**Failure Handling:**
Advice the user to create a google account.

### FR-02: Complete a lesson
**Description:**
An authenticated user must be able to open a lesson and complete it from start to finish.

**Preconditions:**
The user must be logged in and a lesson must exist.

**Success criteria:**
If the user is able to go from:
- Intuition
- Prediction
- Experimentation
- Formalization
- Coding
- Reflection
And the lesson turns from incomplete to completed after `Reflection`, then the lesson is completed.

**Failure Handling:**
If the authenticated user fails to provide a reflection, then the lesson won't be able to be completed.

### FR-03: Complete a subsection of a lesson
**Description:**
If the lesson is only a reading lesson, the system will show a button that says "Mark as compled". Otherwise, the user should complete at least 80% of the activities within the subsection of the lesson to have said subsection completed.

**Preconditions:***
The user must be authenticated.

**Success criteria:**
The lesson marks as completed if it's only reading material and marks as completed in interactive exercises only when 80% of the activities within the subsection of the lesson are completed.

**Failure Handling:**
- Failure of user authorization: user must log in again.

