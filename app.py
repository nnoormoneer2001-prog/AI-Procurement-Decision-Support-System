import os
import json
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_NAME = "openai/gpt-oss-120b:groq"

ALLOWED_ACTIONS = {
    "ask_for_info",
    "flag_policy_issue",
    "send_for_review",
    "finish"
}


# =========================================================
# 2. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Procurement Decision Support System",
    page_icon="🛒",
    layout="wide"
)


# =========================================================
# 2.1. CUSTOM UI STYLING
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f7f9fc;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    h2 {
        margin-top: 1.8rem;
        font-weight: 650;
    }

    h3 {
        margin-top: 1.4rem;
        font-weight: 600;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
        border: 1px solid #d9dee8;
    }

    .stButton > button:hover {
        border-color: #6c63ff;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    hr {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    div[data-testid="stJson"] {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 3. SESSION STATE
# =========================================================

if "request" not in st.session_state:
    st.session_state.request = None

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "human_decision" not in st.session_state:
    st.session_state.human_decision = None

if "final_status" not in st.session_state:
    st.session_state.final_status = None

if "tool_result" not in st.session_state:
    st.session_state.tool_result = {
        "status": "not_used",
        "request_id": None,
        "record": None,
        "validation_errors": []
    }


# =========================================================
# 4. AI CLIENT
# =========================================================

def get_ai_client():

    if not HF_TOKEN:
        return None

    return OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN
    )


# =========================================================
# 5. DATA TOOL
# =========================================================

def load_procurement_data():

    try:

        df = pd.read_csv(
            "data/procurement_requests.csv"
        )

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        return df

    except FileNotFoundError:

        st.error(
            "Procurement data file was not found."
        )

        return None

    except Exception as e:

        st.error(
            f"Unable to load procurement data: {e}"
        )

        return None


def get_request_by_id(request_id):

    df = load_procurement_data()

    if df is None:
        return None

    if "request_id" not in df.columns:

        st.error(
            "The CSV file does not contain the required "
            "'request_id' column."
        )

        return None

    result = df[
        df["request_id"].astype(str).str.strip()
        == str(request_id).strip()
    ]

    if result.empty:
        return None

    return result.iloc[0].to_dict()


# =========================================================
# 6. DATA VALIDATION
# =========================================================

def validate_data_record(record):

    errors = []

    required_fields = [
        "request_id",
        "employee_name",
        "department",
        "item",
        "reason",
        "cost",
        "budget",
        "manager_approval"
    ]

    for field in required_fields:

        if field not in record:

            errors.append(
                f"{field} is missing."
            )

        elif (
            pd.isna(record[field])
            or str(record[field]).strip() == ""
        ):

            errors.append(
                f"{field} is missing."
            )

    if errors:
        return errors

    try:

        cost = float(record["cost"])

        if cost < 0:

            errors.append(
                "Cost cannot be negative."
            )

    except (ValueError, TypeError):

        errors.append(
            "Cost must be a valid number."
        )

    try:

        budget = float(record["budget"])

        if budget < 0:

            errors.append(
                "Budget cannot be negative."
            )

    except (ValueError, TypeError):

        errors.append(
            "Budget must be a valid number."
        )

    if not errors:

        if cost > budget:

            errors.append(
                "Cost cannot be greater than Budget."
            )

    if record["manager_approval"] not in [
        "Yes",
        "No",
        "Pending"
    ]:

        errors.append(
            "Manager Approval has an invalid value."
        )

    elif record["manager_approval"] == "Pending":

        errors.append(
            "Manager approval is still pending."
        )

    return errors


# =========================================================
# 7. FORM VALIDATION
# =========================================================

def validate_request(request):

    errors = []

    if not request["employee_name"].strip():

        errors.append(
            "Employee Name is required."
        )

    if not request["department"].strip():

        errors.append(
            "Department is required."
        )

    if not request["item"].strip():

        errors.append(
            "Item is required."
        )

    if not request["reason"].strip():

        errors.append(
            "Reason is required."
        )

    if request["cost"] < 0:

        errors.append(
            "Cost cannot be negative."
        )

    if request["budget"] < 0:

        errors.append(
            "Budget cannot be negative."
        )

    if request["cost"] > request["budget"]:

        errors.append(
            "Cost cannot be greater than Budget."
        )

    if request["manager_approval"] != "Yes":

        errors.append(
            "Manager approval is required."
        )

    return errors


# =========================================================
# 8. POLICY CHECKER
# =========================================================

def check_policy(request):

    policy_results = {}

    policy_results["Department"] = (
        "PASS"
        if request["department"].strip()
        else "FAIL"
    )

    policy_results["Item"] = (
        "PASS"
        if request["item"].strip()
        else "FAIL"
    )

    policy_results["Reason"] = (
        "PASS"
        if request["reason"].strip()
        else "FAIL"
    )

    policy_results["Budget"] = (
        "PASS"
        if request["cost"] <= request["budget"]
        else "FAIL"
    )

    policy_results["Manager Approval"] = (
        "PASS"
        if request["manager_approval"] == "Yes"
        else "FAIL"
    )

    return policy_results


# =========================================================
# 9. DETERMINISTIC AGENT DECISION
# =========================================================

def agent_decision(
    request,
    validation_errors,
    policy_results
):

    if validation_errors:

        return {
            "action": "ask_for_info",
            "reason": (
                "The request contains missing "
                "or invalid information."
            )
        }

    failed_policies = [
        rule
        for rule, result in policy_results.items()
        if result == "FAIL"
    ]

    if failed_policies:

        return {
            "action": "flag_policy_issue",
            "reason": (
                "The request violates one or more "
                "procurement policies."
            ),
            "failed_policies": failed_policies
        }

    if request["manager_approval"] == "Yes":

        return {
            "action": "send_for_review",
            "reason": (
                "The request passed validation and "
                "policy checks but requires human review."
            )
        }

    return {
        "action": "finish",
        "reason": (
            "The request has completed the decision process."
        )
    }


# =========================================================
# 10. SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are an AI Procurement Decision Support Agent.

Your role is to analyze procurement requests and determine
the appropriate next action based ONLY on the information
provided in the current state.

You are NOT an approval authority.

You must NEVER approve, reject, or authorize a purchase.

Final procurement approval must always be performed by
a human reviewer.

==================================================
CORE RULES
==================================================

1. Use ONLY the information provided in the current state.

2. NEVER invent, assume, fabricate, or guess:
   - missing information
   - prices
   - budgets
   - approvals
   - employee information
   - procurement rules
   - tool results

3. If required information is missing or invalid:
   use "ask_for_info".

4. Deterministic validation results have priority.
   Do not override or contradict them.

5. Deterministic policy-check results have priority.
   Do not invent additional policies.

6. Cost and budget calculations are performed by the system.

7. Tool results are authoritative for information retrieved
   from the procurement dataset.

8. If an explicit policy violation exists:
   use "flag_policy_issue".

9. If the request is valid and policy-compliant but requires
   human approval or review:
   use "send_for_review".

10. Use "finish" only when no further action is required.

==================================================
ALLOWED ACTIONS
==================================================

You may return ONLY:

- ask_for_info
- flag_policy_issue
- send_for_review
- finish

Never create another action.

==================================================
DECISION PRIORITY
==================================================

1. Missing or invalid information
   -> ask_for_info

2. Explicit policy violation
   -> flag_policy_issue

3. Valid and policy-compliant request requiring
   human review
   -> send_for_review

4. No further processing required
   -> finish

==================================================
UNCERTAINTY RULE
==================================================

If information is insufficient, DO NOT GUESS.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

{
  "action": "<one allowed action>",
  "reason": "<short factual explanation>",
  "missing_information": [],
  "policy_issues": []
}

==================================================
FINAL SAFETY RULE
==================================================

Never make a procurement approval decision.

The final decision must always be made by a human reviewer.
"""


# =========================================================
# 11. USER PROMPT
# =========================================================

def build_user_prompt(state):

    return f"""
Analyze the following procurement request state.

Use the system instructions as the highest-priority rules.

CURRENT STATE:

REQUEST:
{json.dumps(
    state["request"],
    indent=2,
    default=str
)}

VALIDATION RESULTS:
{json.dumps(
    state["validation_errors"],
    indent=2,
    default=str
)}

POLICY CHECK RESULTS:
{json.dumps(
    state["policy_results"],
    indent=2,
    default=str
)}

PROCUREMENT DATA TOOL RESULT:
{json.dumps(
    state["tool_result"],
    indent=2,
    default=str
)}

DETERMINISTIC DECISION:
{json.dumps(
    state["deterministic_decision"],
    indent=2,
    default=str
)}

Determine the single appropriate next action.

Do not invent missing information.
Do not override validation results.
Do not override policy results.
Do not approve or reject the purchase.

Return ONLY valid JSON.
"""


# =========================================================
# 12. AI OUTPUT VALIDATION
# =========================================================

def validate_ai_response(result):

    required_fields = [
        "action",
        "reason",
        "missing_information",
        "policy_issues"
    ]

    for field in required_fields:

        if field not in result:

            return {
                "valid": False,
                "error": (
                    f"AI response is missing "
                    f"the '{field}' field."
                )
            }

    if result["action"] not in ALLOWED_ACTIONS:

        return {
            "valid": False,
            "error": (
                "AI returned an unsupported action."
            )
        }

    if not isinstance(
        result["missing_information"],
        list
    ):

        return {
            "valid": False,
            "error": (
                "'missing_information' must be a list."
            )
        }

    if not isinstance(
        result["policy_issues"],
        list
    ):

        return {
            "valid": False,
            "error": (
                "'policy_issues' must be a list."
            )
        }

    return {
        "valid": True,
        "error": None
    }


# =========================================================
# 13. AI AGENT
# =========================================================

def run_ai_agent(state):

    client = get_ai_client()

    if client is None:

        return {
            "action": "send_for_review",
            "reason": (
                "AI configuration is unavailable. "
                "Human review is required."
            ),
            "missing_information": [],
            "policy_issues": [],
            "source": "fallback"
        }

    user_prompt = build_user_prompt(state)

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0,
            max_tokens=500
        )

        content = response.choices[0].message.content

        if not content:

            return {
                "action": "send_for_review",
                "reason": (
                    "The AI returned an empty response. "
                    "Human review is required."
                ),
                "missing_information": [],
                "policy_issues": [],
                "source": "fallback"
            }

        content = content.strip()

        if content.startswith("```"):

            content = content.replace(
                "```json",
                "",
                1
            )

            content = content.replace(
                "```",
                "",
                1
            )

            content = content.strip()

        result = json.loads(content)

        validation = validate_ai_response(
            result
        )

        if not validation["valid"]:

            return {
                "action": "send_for_review",
                "reason": (
                    "The AI response failed output "
                    "validation. Human review is required."
                ),
                "missing_information": [],
                "policy_issues": [],
                "source": "fallback",
                "validation_error": validation["error"]
            }

        result["source"] = "ai"

        return result

    except json.JSONDecodeError:

        return {
            "action": "send_for_review",
            "reason": (
                "The AI returned invalid JSON. "
                "Human review is required."
            ),
            "missing_information": [],
            "policy_issues": [],
            "source": "fallback"
        }

    except Exception as e:

        return {
            "action": "send_for_review",
            "reason": (
                "The AI service could not complete the analysis. "
                "Human review is required."
            ),
            "missing_information": [],
            "policy_issues": [],
            "source": "fallback",
            "error": str(e)
        }


# =========================================================
# 14. PAGE HEADER
# =========================================================

st.title(
    "🛒 AI Procurement Decision Support System"
)

st.write(
    "This system analyzes procurement requests against "
    "a written company policy and provides AI-assisted "
    "decision support."
)

st.info(
    "The system does not automatically approve purchases. "
    "Final approval must be completed by a human reviewer."
)


# =========================================================
# 15. COMPANY POLICY
# =========================================================

st.subheader(
    "📋 Procurement Policy"
)

st.write(
    "The system checks the following procurement rules:"
)

st.markdown(
    """
    - Department must be provided.
    - Item and reason must be provided.
    - Cost must be a valid non-negative value.
    - Cost must be within the available budget.
    - Manager approval is required.
    """
)


# =========================================================
# 16. PROCUREMENT REQUEST FORM
# =========================================================

st.subheader(
    "📝 Procurement Request"
)

with st.form("procurement_form"):

    employee_name = st.text_input(
        "Employee Name"
    )

    department = st.text_input(
        "Department"
    )

    item = st.text_input(
        "Item"
    )

    reason = st.text_area(
        "Reason"
    )

    cost = st.number_input(
        "Cost",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

    budget = st.number_input(
        "Budget",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

    manager_approval = st.selectbox(
        "Manager Approval",
        ["Yes", "No"]
    )

    submitted = st.form_submit_button(
        "Submit Request"
    )


# =========================================================
# 17. SAVE REQUEST
# =========================================================

if submitted:

    st.session_state.request = {
        "employee_name": employee_name,
        "department": department,
        "item": item,
        "reason": reason,
        "cost": cost,
        "budget": budget,
        "manager_approval": manager_approval
    }

    # Reset previous AI and human decisions
    st.session_state.ai_result = None
    st.session_state.human_decision = None
    st.session_state.final_status = None

    # Reset Data Tool state for the new request
    st.session_state.tool_result = {
        "status": "not_used",
        "request_id": None,
        "record": None,
        "validation_errors": []
    }

    st.success(
        "Request submitted successfully."
    )


# =========================================================
# 18. PROCESS CURRENT REQUEST
# =========================================================

if st.session_state.request is not None:

    request = st.session_state.request

    st.subheader(
        "🔍 Request Processing"
    )


    # -----------------------------------------------------
    # 18.1 FORM VALIDATION
    # -----------------------------------------------------

    validation_errors = validate_request(
        request
    )

    if validation_errors:

        st.error(
            "❌ Request validation failed."
        )

        for error in validation_errors:

            st.write(
                f"- {error}"
            )

    else:

        st.success(
            "✅ Request passed validation."
        )


    # -----------------------------------------------------
    # 18.2 POLICY CHECK
    # -----------------------------------------------------

    policy_results = check_policy(
        request
    )

    st.subheader(
        "📋 Policy Check Results"
    )

    for rule, result in policy_results.items():

        if result == "PASS":

            st.success(
                f"✅ {rule}: PASS"
            )

        else:

            st.error(
                f"❌ {rule}: FAIL"
            )


    # -----------------------------------------------------
    # 18.3 DETERMINISTIC DECISION
    # -----------------------------------------------------

    deterministic_decision = agent_decision(
        request,
        validation_errors,
        policy_results
    )


    # -----------------------------------------------------
    # 18.4 CURRENT REQUEST
    # -----------------------------------------------------

    st.subheader(
        "📄 Current Request"
    )

    st.json(
        request
    )


    # -----------------------------------------------------
    # 18.5 PROCUREMENT DATA TOOL
    # -----------------------------------------------------

    st.subheader(
        "🛠️ Procurement Data Tool"
    )

    request_id = st.text_input(
        "Search Request ID",
        placeholder="Example: REQ-001"
    )

    if st.button(
        "Search Request"
    ):

        found_request = get_request_by_id(
            request_id
        )

        if found_request is None:

            st.session_state.tool_result = {
                "status": "not_found",
                "request_id": request_id,
                "record": None,
                "validation_errors": []
            }

            st.warning(
                "No procurement request was found "
                "with this Request ID."
            )

        else:

            data_errors = validate_data_record(
                found_request
            )

            st.session_state.tool_result = {
                "status": "found",
                "request_id": request_id,
                "record": found_request,
                "validation_errors": data_errors
            }

            st.success(
                "Procurement request found."
            )

            st.json(
                found_request
            )

            if data_errors:

                st.warning(
                    "⚠️ Data validation found issues."
                )

                for error in data_errors:

                    st.write(
                        f"- {error}"
                    )

            else:

                st.success(
                    "✅ The procurement data is valid."
                )


    # -----------------------------------------------------
    # 18.6 BUILD AGENT STATE
    # -----------------------------------------------------

    state = {
        "request": request,
        "validation_errors": validation_errors,
        "policy_results": policy_results,
        "tool_result": st.session_state.tool_result,
        "deterministic_decision": deterministic_decision
    }


    # -----------------------------------------------------
    # 18.7 AI AGENT
    # -----------------------------------------------------

    st.subheader(
        "🤖 AI Agent"
    )

    if st.button(
        "Run AI Analysis"
    ):

        with st.spinner(
            "AI Agent is analyzing the request..."
        ):

            ai_result = run_ai_agent(
                state
            )

        st.session_state.ai_result = ai_result
        st.session_state.human_decision = None
        st.session_state.final_status = None

        if ai_result["source"] == "ai":

            st.success(
                "AI analysis completed successfully."
            )

        else:

            st.warning(
                "AI analysis could not be completed. "
                "The system safely routed the request "
                "to human review."
            )


    # -----------------------------------------------------
    # 18.8 DISPLAY AI RESULT
    # -----------------------------------------------------

    if st.session_state.ai_result is not None:

        ai_result = st.session_state.ai_result

        st.write(
            f"**AI Action:** `{ai_result['action']}`"
        )

        st.write(
            f"**AI Reason:** {ai_result['reason']}"
        )

        if ai_result["missing_information"]:

            st.write(
                "**Missing Information:**"
            )

            for item in ai_result[
                "missing_information"
            ]:

                st.write(
                    f"- {item}"
                )

        if ai_result["policy_issues"]:

            st.write(
                "**Policy Issues:**"
            )

            for issue in ai_result[
                "policy_issues"
            ]:

                st.write(
                    f"- {issue}"
                )


        # -------------------------------------------------
        # 18.9 HUMAN REVIEW
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "👤 Human Review"
        )

        st.info(
            "The AI provides decision support only. "
            "The final procurement decision must be "
            "made by a human reviewer."
        )

        if ai_result["action"] == "send_for_review":

            st.write(
                "**Human reviewer decision:**"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                if st.button(
                    "✅ Approve",
                    key="approve_request"
                ):

                    st.session_state.human_decision = (
                        "Approved by Human"
                    )

                    st.session_state.final_status = (
                        "Approved"
                    )

            with col2:

                if st.button(
                    "❌ Reject",
                    key="reject_request"
                ):

                    st.session_state.human_decision = (
                        "Rejected by Human"
                    )

                    st.session_state.final_status = (
                        "Rejected"
                    )

            with col3:

                if st.button(
                    "🔄 Request Re-review",
                    key="rereview_request"
                ):

                    st.session_state.human_decision = (
                        "Human requested re-review"
                    )

                    st.session_state.final_status = (
                        "Re-review Required"
                    )


        elif ai_result["action"] == "ask_for_info":

            st.warning(
                "Additional information is required "
                "before human review can be completed."
            )

        elif ai_result["action"] == "flag_policy_issue":

            st.warning(
                "A policy issue was identified. "
                "The request requires policy review."
            )

            if st.button(
                "🔄 Send for Human Review",
                key="policy_human_review"
            ):

                st.session_state.human_decision = (
                    "Sent to Human Review"
                )

                st.session_state.final_status = (
                    "Human Review Required"
                )

        elif ai_result["action"] == "finish":

            st.info(
                "The AI completed the processing stage. "
                "No automatic procurement approval was made."
            )

            if st.button(
                "👤 Send to Human for Final Decision",
                key="finish_human_review"
            ):

                st.session_state.human_decision = (
                    "Sent to Human Review"
                )

                st.session_state.final_status = (
                    "Human Review Required"
                )


        # -------------------------------------------------
        # 18.10 FINAL STATUS
        # -------------------------------------------------

        if st.session_state.final_status is not None:

            st.divider()

            st.subheader(
                "📌 Final Status"
            )

            st.write(
                f"**Human Decision:** "
                f"{st.session_state.human_decision}"
            )

            st.write(
                f"**Final Status:** "
                f"{st.session_state.final_status}"
            )

            if st.session_state.final_status == "Approved":

                st.success(
                    "The request was approved by a human reviewer."
                )

            elif st.session_state.final_status == "Rejected":

                st.error(
                    "The request was rejected by a human reviewer."
                )

            else:

                st.warning(
                    "The request requires additional review."
                )