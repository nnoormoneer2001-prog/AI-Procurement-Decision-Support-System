# AI Procurement Decision Support System

## 1. Project Name & Problem

### Project Name

**AI Procurement Decision Support System**

### Problem

Manually checking procurement requests against company policy can be repetitive and time-consuming, especially when requests contain missing information or violate one or more policy rules.

The system will provide decision support by validating procurement requests, checking them against a written company policy, identifying missing information or policy issues, and selecting the appropriate next action.

The system will not automatically approve purchases or execute any purchase or payment.

---

## 2. Target User & Goal

### Target User

Employees or staff members who need to submit procurement requests.

### Goal

The user wants to submit a procurement request, check whether the request meets the written procurement policy requirements, and understand the next action needed.

The possible next actions are:

* Ask for missing information.
* Flag a policy issue.
* Send the request for human review.
* Finish the process when appropriate.

The final procurement approval must always remain with a human reviewer.

---

## 3. Scope

### In Scope

The system will:

* Collect procurement requests through a structured Streamlit form.
* Validate required fields and input values.
* Distinguish missing information from invalid input.
* Extract validated request information into a structured object.
* Check the request against the written company procurement policy.
* Evaluate each policy rule separately.
* Use an AI Agent to select an allowed next action based on validated data and policy-check results.
* Display the request details and policy-check results.
* Explain missing information and policy issues.
* Allow users to correct missing information and resubmit the request.
* Route completed requests to human review.
* Maintain request history during the application.
* Provide a human-review status without treating it as automatic approval.

### Out of Scope

The system will not:

* Automatically approve procurement requests.
* Automatically authorize company spending.
* Execute purchases.
* Execute payments.
* Modify the company policy.
* Invent missing information.
* Execute unrestricted AI-generated Python code.
* Send private or sensitive real-world employee records to third-party AI services.

### Example of an Out-of-Scope Request

> "Please purchase a laptop and pay for it using the company's account."

The system may analyze the request and provide decision support, but it will not perform the purchase or payment.

---

## 4. Input Contract

The procurement request will contain the following fields:

| Field            | Required | Type             | Example              |
| ---------------- | -------- | ---------------- | -------------------- |
| Request ID       | Yes      | Text             | REQ-001              |
| Employee Name    | Yes      | Text             | Noor Moneer          |
| Department       | Yes      | Text / Selection | IT                   |
| Item             | Yes      | Text             | Laptop               |
| Reason           | Yes      | Text             | Software development |
| Cost             | Yes      | Number           | 800                  |
| Budget           | Yes      | Number           | 1000                 |
| Manager Approval | Yes      | Yes/No           | Yes                  |

### Input Rules

* Required text fields cannot be empty.
* Cost must be numeric.
* Budget must be numeric.
* Cost must be non-negative.
* Budget must be non-negative.
* Manager Approval must contain an allowed value: `Yes` or `No`.
* The system must distinguish missing information from invalid input.

### Missing Information

Examples:

* Missing Department.
* Missing Item.
* Missing Reason.
* Missing Budget.
* Missing Manager Approval.

A missing field should cause the system to request that specific information rather than guess it.

### Invalid Input

Examples:

* Cost is text instead of a number.
* Budget is text instead of a number.
* Cost is negative.
* Budget is negative.
* Manager Approval contains an unsupported value such as `Pending`.

Invalid input must be rejected during validation before policy checking.

---

## 5. Output Contract

After processing a valid request, the system will display:

1. Submitted request details.
2. Validation status.
3. Individual policy-check results.
4. Missing information, if any.
5. Policy issues, if any.
6. AI Agent decision.
7. Recommended next action.
8. Human-review status where applicable.

### Example: Policy-Compliant Request

The output may show:

* Department: Passed
* Item and Reason: Passed
* Cost: Passed
* Cost within Budget: Passed
* Manager Approval: Passed

### Agent Decision

`send_for_review`

### Next Action

> Send the request for Human Review.

The interface will clearly state:

> **This is an AI-assisted decision-support recommendation. Final approval must be completed by a human reviewer.**

### Example: Missing Information

If Budget is missing:

> **Missing Information:** Budget is required.
> **Agent Action:** `ask_for_info`

The user can provide the missing information and resubmit the request.

### Example: Policy Issue

If Cost is greater than Budget:

> **Policy Issue:** The requested cost exceeds the available budget.
> **Agent Action:** `flag_policy_issue`

---

## 6. Workflow

The complete workflow will be:

```text
User Input
    ↓
Validation
    ↓
Extract Fields
    ↓
Policy Check
    ↓
Agent Decision
    ↓
Decision Support Output
    ↓
Human Review
    ↓
Save / History
```

### Alternative Paths

#### Missing Information

```text
User Input
    ↓
Validation
    ↓
Missing Information
    ↓
Ask for Information
    ↓
User Corrects Request
    ↓
Resubmit
```

#### Invalid Input

```text
User Input
    ↓
Validation
    ↓
Validation Error
    ↓
User Corrects Input
```

The request does not proceed to policy checking until validation succeeds.

#### Policy Violation

```text
Validation
    ↓
Policy Check
    ↓
Policy Rule Fails
    ↓
flag_policy_issue
```

#### Complete and Compliant Request

```text
Validation
    ↓
All Policy Checks Pass
    ↓
Agent Decision
    ↓
send_for_review
    ↓
Human Review
```

### Component Responsibilities

**Validation** checks whether the submitted data is complete and valid.

**Policy Checker** checks whether the validated request follows the written company policy.

**AI Agent** chooses the appropriate next action based on the validation and policy-check results.

---

## 7. Agent Specification

### Agent Goal

> Determine the appropriate next action for a procurement request based on validated input and policy-check results.

### Allowed Actions

The Agent may select only one of the following actions:

```text
ask_for_info
flag_policy_issue
send_for_review
finish
```

### Agent Decision Rules

#### Missing Required Information

If required information is genuinely missing:

```text
ask_for_info
```

The Agent must ask only for the missing information and must not invent values.

#### Invalid Input

If validation fails:

* The request stops before Agent decision-making.
* The user receives a validation error.
* The user must correct the input.

#### Policy Violation

If one or more policy rules fail:

```text
flag_policy_issue
```

The Agent must identify and explain the relevant policy issue.

#### Complete and Policy-Compliant Request

If all required information is present and all policy checks pass:

```text
send_for_review
```

The system must never treat this as automatic approval.

#### Process Completed

When the supported workflow has been completed:

```text
finish
```

### Agent State Variables

The system will maintain structured state information such as:

* `request_id`
* `request_data`
* `validation_status`
* `policy_results`
* `agent_action`
* `status`
* `review_status`

### Agent Permissions

The Agent may:

* Access validated request information.
* Access policy-check results.
* Select one allowed action.
* Generate a decision-support explanation.
* Identify missing information already detected by the system.

The Agent may not:

* Approve purchases.
* Authorize spending.
* Execute purchases.
* Execute payments.
* Modify policy rules.
* Invent missing information.
* Execute unrestricted generated code.

### System Prompt

The AI Agent will receive a System Prompt defining its role, allowed actions, safety rules, and decision constraints.

The System Prompt will instruct the Agent to:

* Act as a procurement decision-support agent.
* Use only the supplied request data and policy-check results.
* Select only an allowed action.
* Never approve purchases.
* Never invent missing information.
* Ask only for genuinely missing information.
* Explain policy issues using the supplied policy-check results.

### User Prompt

The User Prompt will provide the Agent with:

* Structured procurement request data.
* Validation status.
* Individual policy-check results.
* Relevant missing information or policy issues.

The Agent will then select the appropriate allowed action and provide a concise explanation.

### AI Decision Safety

The application will validate the Agent's returned action against the allowed action list.

If the AI response is invalid or unavailable, the application will not invent a new action or silently approve the request. The system will use safe handling and keep human review as the final authority.

---

## 8. Data Preparation

The system will use a small set of non-sensitive sample procurement records for testing and demonstration.

Each record will contain:

* Request ID
* Employee Name
* Department
* Item
* Reason
* Cost
* Budget
* Manager Approval

The sample data will include different cases:

1. Complete and policy-compliant request.
2. Another complete valid request.
3. Request with missing Budget.
4. Request with missing Manager Approval.
5. Request that violates the budget policy.
6. Boundary-value request where Cost equals Budget.
7. Request with an invalid negative Cost.
8. Request with an invalid Manager Approval value.

### Sample Data Safety

All sample records will use fictional, non-sensitive information.

The sample CSV is used for testing and demonstration. It is not a user-upload mechanism for the application.

### Data Checking

The application will check:

* Required fields.
* Data types.
* Numeric values.
* Non-negative Cost and Budget.
* Allowed Manager Approval values.
* Missing information.

The application will then separately perform policy checking.

This separation ensures that:

```text
Validation Error ≠ Policy Issue
```

---

## 9. Interface Sketch

The application will use a Streamlit interface.

### Main Page

The page will contain:

#### Project Title

**AI Procurement Decision Support System**

#### Project Description

A short explanation that the application analyzes procurement requests against a written policy and provides decision support.

### Procurement Request Form

The form will contain:

* Employee Name
* Department
* Item
* Reason
* Cost
* Budget
* Manager Approval

A:

**Submit Request**

button will process the request.

### Company Policy Summary

The interface will display a brief summary of the written procurement policy so the user understands the rules being checked.

### Decision Support Result

After submission, the interface will show:

* Request Details
* Validation Result
* Policy Checks
* Missing Information
* Policy Issues
* Agent Decision
* Next Action
* Human Review Status

### Resubmission

If information is missing, the user can correct the request and resubmit it without losing the rest of the request information.

### Request History

The application will provide a history of requests processed during the application.

### Optional UI Enhancement

The interface may use clean cards, status indicators, success/warning/error messages, and organized sections to create a professional user experience.

These visual enhancements are optional and do not replace any required project functionality.

---

## 10. Success Tests

The system will be tested using at least five realistic cases.

### Test 1 — Complete Policy-Compliant Request

**Input:** Complete request with all policy rules satisfied.

**Expected Result:**

```text
send_for_review
```

The request must not be automatically approved.

---

### Test 2 — Missing Information

**Input:** Request with a missing Budget.

**Expected Result:**

```text
ask_for_info
```

The system should ask only for the missing Budget.

---

### Test 3 — Policy Violation

**Input:**

```text
Cost = 1500
Budget = 1000
```

**Expected Result:**

```text
flag_policy_issue
```

The system should identify that the cost exceeds the available budget.

---

### Test 4 — Boundary Value

**Input:**

```text
Cost = 1000
Budget = 1000
```

**Expected Result:**

The result must follow the defined policy decision table for the boundary condition.

---

### Test 5 — Invalid Input

**Input:**

```text
Cost = -200
```

**Expected Result:**

Validation error.

The request must not proceed to policy checking or Agent decision-making.

---

### Additional Test

The system will verify that a human reviewer can inspect the request history.

Each test will record:

* Test Case
* Input
* Expected Result
* Actual Result
* Pass/Fail

The final results will be recorded in `TEST_RESULTS.md`.

---

## 11. Technology Plan

### Core Technologies

**Python**

Used for the application logic, validation, policy checking, Agent workflow, and data processing.

**Streamlit**

Used to build the interactive web application and procurement form.

**Pandas**

Used for handling the sample procurement records and structured data where needed.

**Session State**

Used to preserve relevant request information, resubmission data, Agent results, and temporary request history during the current application session.

**Rule-Based Policy Checker**

Used to evaluate the written procurement rules separately and transparently.

**Hugging Face**

Used as the AI model provider for the Agent decision layer.

The AI model will receive the validated request and policy-check results through controlled prompts.

### Prompt Architecture

The application will use:

* **System Prompt** — defines the Agent role, allowed actions, safety rules, and constraints.
* **User Prompt** — supplies the current request and policy-check results.

### Structured Agent Output

The Agent response will be handled as structured data where possible and validated by the application.

The application will verify that the returned action belongs to:

```text
ask_for_info
flag_policy_issue
send_for_review
finish
```

### Secrets

The Hugging Face API key will not be hardcoded.

It will be stored securely through environment configuration such as:

```text
HUGGINGFACE_API_KEY
```

The key must not appear in source code, screenshots, sample data, or documentation.

### Request History

Request history will be maintained using Streamlit session state during the current application session.

If persistent storage is not implemented, the README will clearly state that history is temporary and disappears when the application restarts.

### Security

The application will not:

* Execute unrestricted AI-generated Python code.
* Expose API keys.
* Send private real-world employee records to third-party AI services without permission.
* Allow the AI Agent to approve spending or execute purchases.

---

## 12. Build Order

The project will be implemented in the following order:

### Step 1 — Project Setup

Create the project folder and required files:

```text
AI-Procurement-Decision-Support-System/
│
├── app.py
├── PROJECT_PLAN.md
├── README.md
├── requirements.txt
├── TEST_RESULTS.md
│
└── sample_data/
    └── procurement_requests.csv
```

### Step 2 — Streamlit Interface

Build:

* Page configuration.
* Project title.
* Project description.
* Company policy summary.
* Procurement request form.

### Step 3 — Session State

Set up the required session-state variables for:

* Current request.
* Request history.
* Processing results.
* Review status.

### Step 4 — Validation

Implement validation for:

* Required fields.
* Data types.
* Numeric ranges.
* Cost and Budget.
* Manager Approval.

### Step 5 — Structured Data Extraction

Convert validated form input into a structured request object.

### Step 6 — Policy Checker

Implement a separate policy-checking function.

The function must evaluate every written policy rule and record an individual result for each rule.

### Step 7 — AI Agent

Implement:

* System Prompt.
* User Prompt.
* Hugging Face connection.
* Structured Agent response.
* Allowed-action validation.

### Step 8 — Agent Decision

The Agent will select:

```text
ask_for_info
flag_policy_issue
send_for_review
finish
```

based on the validated information and policy-check results.

### Step 9 — Decision Support Output

Display:

* Submitted details.
* Validation status.
* Policy-check results.
* Missing information.
* Policy issues.
* Agent decision.
* Next action.
* Human-review status.

### Step 10 — Correction and Resubmission

Allow users to correct missing information and submit the request again without losing the remaining request data.

### Step 11 — Human Review and History

Display requests that require human review and maintain request history during the current session.

Final approval remains outside the AI system and must be completed by a human reviewer.

### Step 12 — Testing

Run the required realistic test cases:

1. Complete compliant request.
2. Missing information.
3. Policy violation.
4. Boundary value.
5. Invalid input.

Record Expected Result, Actual Result, and Pass/Fail.

### Step 13 — Documentation

Complete:

* `README.md`
* `requirements.txt`
* `PROJECT_PLAN.md`
* `TEST_RESULTS.md`

The README will include:

* Project purpose.
* Setup instructions.
* Run instructions.
* Example usage.
* Architecture/workflow.
* Limitations.
* Human-review limitation.
* Temporary-history limitation if applicable.

### Step 14 — Final End-to-End Test

Verify the complete workflow:

```text
Input
 ↓
Validation
 ↓
Extraction
 ↓
Policy Check
 ↓
AI Agent
 ↓
Decision Validation
 ↓
Decision Support Output
 ↓
Human Review
 ↓
History
```

### Step 15 — Final Demonstration and Submission

Prepare:

* Working application.
* Project files.
* Sample data.
* Test results.
* Screenshots.
* Final demonstration.

The final project must satisfy the trainer's acceptance requirements and be explainable by the student from input through output and Agent decision.
