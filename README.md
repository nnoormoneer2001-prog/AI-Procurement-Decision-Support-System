# 🛒 AI Procurement Decision Support System

## 📌 Project Overview

The **AI Procurement Decision Support System** is a Streamlit-based application designed to support procurement teams in analyzing purchase requests.

The system validates procurement data, checks procurement policies, retrieves request information from a CSV data source, and uses an AI Agent to recommend the appropriate next action.

The system is designed as a **Decision Support System**, not an automatic approval system. The final procurement decision is always made by a human reviewer.

---

## 🎯 Project Objective

The main objective is to demonstrate how an AI Agent can be integrated into a real-world procurement workflow while maintaining:

* Data validation
* Policy checking
* Tool usage
* State management
* AI-based decision support
* Human-in-the-loop review
* Safe handling of missing or invalid information

---

## ⚙️ How the System Works

The system follows this workflow:

```text
Procurement Request
        ↓
Data Validation
        ↓
Policy Check
        ↓
Procurement Data Tool
        ↓
Agent State
        ↓
AI Agent
        ↓
Recommended Action
        ↓
Human Review
        ↓
Final Human Decision
```

The AI Agent does not directly approve or reject purchases.

---

## 🤖 AI Agent

The AI Agent analyzes the current procurement state and determines the appropriate next action.

The Agent can only return one of four allowed actions:

| Action              | Purpose                                    |
| ------------------- | ------------------------------------------ |
| `ask_for_info`      | Required information is missing or invalid |
| `flag_policy_issue` | A policy issue has been identified         |
| `send_for_review`   | The request requires human review          |
| `finish`            | No further processing is required          |

The Agent is instructed to:

* Use only the provided state.
* Never invent missing information.
* Never guess prices, budgets, approvals, or policies.
* Respect deterministic validation and policy results.
* Never approve or reject a procurement request.
* Return structured JSON only.

---

## 🧠 State Management

The application uses **Streamlit Session State** to preserve important information between interactions.

The state includes:

* Current procurement request
* Validation results
* Policy results
* Procurement Data Tool result
* Deterministic decision
* AI result
* Human decision
* Final status

This allows multiple UI actions, such as searching the data tool and then running the AI Agent, without losing the previous results.

---

## 🛠️ Procurement Data Tool

The system includes a simple data tool based on a CSV file:

```text
data/procurement_requests.csv
```

The tool can search for a procurement request using its Request ID.

Example:

```text
REQ-001
```

The tool returns the corresponding procurement record and validates the retrieved data.

It can detect issues such as:

* Missing budget
* Negative cost
* Invalid values
* Missing manager approval

---

## ✅ Validation

Before making a decision, the system validates the procurement request.

The validation checks:

* Employee name
* Department
* Item
* Reason
* Cost
* Budget
* Manager approval
* Negative values
* Cost exceeding budget

Invalid or incomplete requests are not treated as valid procurement requests.

---

## 📋 Policy Checking

The system checks the procurement request against defined procurement rules.

Current rules include:

* Department must be provided.
* Item and reason must be provided.
* Cost must be a valid non-negative value.
* Cost must not exceed the available budget.
* Manager approval is required.

The policy results are passed to the Agent as part of the current state.

---

## 👤 Human-in-the-Loop

Human review is a core part of the system.

When the AI recommends:

```text
send_for_review
```

a human reviewer can:

* Approve
* Reject
* Request re-review

The system never treats the AI recommendation as the final procurement approval.

This ensures that the AI acts as a **decision-support assistant**, while the final decision remains under human control.

---

## 🧪 Testing

The system was tested using different scenarios:

### 1. Normal Case

A valid procurement request with sufficient budget and manager approval.

**Expected:** `send_for_review`

### 2. Error Case

A request where the cost exceeds the available budget.

**Expected:** Validation failure and `ask_for_info`

### 3. Ambiguous Case

A request with missing required information.

**Expected:** Validation failure and `ask_for_info`

### 4. Boundary Case

A request where:

```text
Cost = Budget
```

**Expected:** Validation passes and the request proceeds to human review.

### 5. Data Tool Cases

The CSV tool was also tested with valid and invalid records, including:

* Valid procurement request
* Missing budget
* Negative cost
* Pending manager approval

---

## 🔐 Safety Principles

The system follows several safety principles:

* No automatic procurement approval
* Human review for final decisions
* No guessing missing information
* Deterministic validation before AI reasoning
* Restricted AI action set
* Structured AI output validation
* Safe fallback when the AI service fails

If the AI cannot provide a valid response, the system safely routes the request toward human review instead of making an unsafe automatic decision.

---

## 🖥️ User Interface

The application is built with **Streamlit** and includes:

* Procurement request form
* Validation results
* Policy results
* Current request display
* Procurement Data Tool
* AI Agent analysis
* Human Review section
* Final Status

The interface was also styled to provide a clean and professional user experience.

---

## 🧰 Technologies Used

* **Python**
* **Streamlit**
* **Pandas**
* **OpenAI Python SDK**
* **Hugging Face Inference Providers**
* **Groq**
* **python-dotenv**
* **CSV**
* **JSON**

### AI Model

```text
openai/gpt-oss-120b:groq
```

The model is accessed through the Hugging Face Router using the OpenAI-compatible API.

---

## 📁 Project Structure

```text
AI-Procurement-Decision-Support-System/
│
├── app.py
├── requirements.txt
├── .env
│
└── data/
    └── procurement_requests.csv
```

> The `.env` file contains the API token and should not be uploaded to GitHub.

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the environment variable

Create a `.env` file:

```text
HF_TOKEN=your_huggingface_token
```

### 3. Run the application

```bash
streamlit run app.py
```

The application will open in the browser.

---

## 🔑 Environment Variable

The project uses:

```text
HF_TOKEN
```

for authentication with the Hugging Face API.

The actual token must remain private and should never be committed to GitHub.

---

## 📌 Key Features

* ✅ Procurement request management
* ✅ Input validation
* ✅ Policy checking
* ✅ CSV data tool
* ✅ Session State management
* ✅ AI Agent
* ✅ System Prompt
* ✅ User Prompt
* ✅ Structured JSON output
* ✅ AI output validation
* ✅ Missing/invalid data handling
* ✅ Human-in-the-loop review
* ✅ Safe AI fallback
* ✅ Multiple test scenarios
* ✅ Professional Streamlit interface

---

## 🎓 Project Purpose

This project demonstrates the practical implementation of an AI Agent within a controlled business workflow.

It combines traditional deterministic programming with AI reasoning:

```text
Deterministic Logic
+
Data Tool
+
State Management
+
AI Agent
+
Human Review
=
AI Procurement Decision Support System
```

The project focuses on using AI responsibly to **support human decisions rather than replace them**.

---

## 👩‍💻 Author

**Noor Moneer Jameel Aldramly**

Industrial Engineer | AI & Data Projects

## 🎥 Video Demo

A short demonstration of the AI Procurement Decision Support System:

**[Watch the Project Demo](https://drive.google.com/file/d/1SfDmbeyPjz5cBefR3m0tmRwj3WdBvRtX/view?usp=drive_link)**
