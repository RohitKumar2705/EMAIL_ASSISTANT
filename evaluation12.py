"""
evaluation_fixed.py
===================
Full evaluation script — all dependencies defined inline.
No missing module errors.

Run: python evaluation_fixed.py

BEFORE RUNNING:
- .env file must exist in the SAME directory as this script (or one level above)
- It must contain:
      LANGSMITH_API_KEY=ls__xxxxxxxxxxxxxxxx
      OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx  (required only for LLM-as-judge)
"""

import os
import sys

# ─────────────────────────────────────────────
# SECTION 1: Load Environment Variables
# ─────────────────────────────────────────────
from dotenv import load_dotenv

# Try current dir first, then one level up
loaded = load_dotenv(".env") or load_dotenv("../.env")
print("✅ .env loaded:", loaded)

for key in ["LANGSMITH_API_KEY"]:
    val = os.getenv(key)
    if not val:
        print(f"❌ ERROR: '{key}' not found in .env file. Please add it and retry.")
        sys.exit(1)
    else:
        print(f"✅ {key} found: {val[:8]}...")


# ─────────────────────────────────────────────
# SECTION 2: Inline Prompt — replaces missing
#            email_assistant.eval.prompts
# ─────────────────────────────────────────────

RESPONSE_CRITERIA_SYSTEM_PROMPT = """You are an expert evaluator assessing the quality of an AI email assistant's responses.

Your task is to evaluate whether the assistant's response meets the provided success criteria.

Guidelines:
- Be objective and focus on whether the specific criteria are satisfied.
- Look for concrete evidence in the response that supports or contradicts the criteria.
- Provide a clear justification citing specific parts of the response.
- Grade True only if the response clearly meets ALL aspects of the criteria.
- Grade False if the response is missing key elements, is unclear, or fails the criteria.
"""


# ─────────────────────────────────────────────
# SECTION 3: Inline Dataset — replaces missing
#            email_assistant.eval.email_dataset
# ─────────────────────────────────────────────

email_inputs = [
    "Subject: Invoice payment\n\nHi team, I have a question about my latest invoice.",
    "Subject: Meeting request\n\nCan we schedule a meeting for next week to discuss the project?",
    "Subject: Urgent bug report\n\nOur production system is down! Getting 500 errors on all endpoints.",
    "Subject: Newsletter unsubscribe\n\nPlease remove me from your mailing list.",
]

triage_outputs_list = [
    "This looks like a billing inquiry that should be routed to Finance.",
    "This is a scheduling request that needs a calendar response.",
    "This is an urgent technical issue requiring immediate escalation.",
    "This is an unsubscribe request that should be handled automatically.",
]

expected_tool_calls = [
    ["open_invoice", "check_payment_status"],
    ["create_calendar_event", "send_email"],
    ["create_ticket", "escalate_issue"],
    ["unsubscribe_email"],
]

response_criteria_list = [
    "Provide a clear statement of the issue and next steps for the user.",
    "Confirm the meeting request and suggest available time slots.",
    "Acknowledge the urgency and provide a ticket number or escalation confirmation.",
    "Confirm the unsubscription and provide a timeline for removal.",
]

examples_triage = [
    {
        "inputs": {"email_input": email_inputs[i]},
        "outputs": {
            "classification": "respond",
            "expected_tool_calls": expected_tool_calls[i],
            "triage_output": triage_outputs_list[i],
            "response_criteria": response_criteria_list[i],
        },
    }
    for i in range(len(email_inputs))
]


# ─────────────────────────────────────────────
# SECTION 4: Inline Utilities — replaces missing
#            email_assistant.utils
# ─────────────────────────────────────────────

def format_messages_string(messages: list) -> str:
    """Convert a list of message dicts into a readable string."""
    parts = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        if isinstance(content, list):
            # Handle structured content blocks
            content = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        parts.append(f"[{role}]: {content}")
    return "\n".join(parts)


def extract_tool_calls(messages: list) -> list:
    """Extract tool call names from a list of messages (lowercased)."""
    tool_calls = []
    for msg in messages:
        # Standard tool_calls field
        for tc in msg.get("tool_calls", []):
            name = None
            if isinstance(tc, dict):
                name = tc.get("function", {}).get("name") or tc.get("name")
            elif hasattr(tc, "function"):
                name = tc.function.name
            elif hasattr(tc, "name"):
                name = tc.name
            if name:
                tool_calls.append(name.lower())

        # Content blocks (e.g. Anthropic-style)
        content = msg.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_calls.append(block.get("name", "").lower())
    return tool_calls


# ─────────────────────────────────────────────
# SECTION 5: Preview Test Case
# ─────────────────────────────────────────────

test_case_ix = 0

print("\n--- Test Case Preview ---")
print("Email Input:           ", email_inputs[test_case_ix])
print("Expected Triage Output:", triage_outputs_list[test_case_ix])
print("Expected Tool Calls:   ", expected_tool_calls[test_case_ix])
print("Response Criteria:     ", response_criteria_list[test_case_ix])

print("\n--- examples_triage Structure Debug ---")
print("Total examples:", len(examples_triage))
first = examples_triage[0]
print("Keys in first example:", list(first.keys()))
print("Dataset Example Input  (inputs):", first["inputs"])
print("Dataset Example Output (outputs):", first["outputs"])


# ─────────────────────────────────────────────
# SECTION 6: LangSmith Client + Dataset Setup
# ─────────────────────────────────────────────
from langsmith import Client

api_key = os.getenv("LANGSMITH_API_KEY")
client = Client(api_key=api_key)

dataset_name = "E-mail Triage Evaluation"

try:
    if not client.has_dataset(dataset_name=dataset_name):
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="A dataset of e-mails and their triage decisions."
        )
        client.create_examples(dataset_id=dataset.id, examples=examples_triage)
        print(f"\n✅ Dataset '{dataset_name}' created with {len(examples_triage)} examples.")
    else:
        print(f"\n✅ Dataset '{dataset_name}' already exists. Skipping creation.")
except Exception as e:
    print(f"\n❌ LangSmith dataset error: {e}")
    sys.exit(1)


# ─────────────────────────────────────────────
# SECTION 7: Email Assistant — import or stub
#
# If your real email_assistant package is available,
# it will be imported. Otherwise a stub is used so
# the rest of the script runs without errors.
# ─────────────────────────────────────────────

try:
    from email_assistant.email_assistant import email_assistant
    ASSISTANT_AVAILABLE = True
    print("\n✅ email_assistant imported successfully.")
except ImportError as e:
    ASSISTANT_AVAILABLE = False
    print(f"\n⚠️  email_assistant not found ({e}). Using stub for structure tests.")

    class _StubAssistant:
        """Minimal stub so evaluation scaffolding runs without the real assistant."""

        class _Nodes:
            def __getitem__(self, key):
                return self

            def invoke(self, inputs):
                class _R:
                    update = {"classification_decision": "respond"}
                return _R()

        nodes = _Nodes()

        def invoke(self, inputs):
            return {
                "messages": [
                    {"role": "assistant", "content": "Stub response: no real assistant loaded."}
                ]
            }

    email_assistant = _StubAssistant()


# ─────────────────────────────────────────────
# SECTION 8: Pytest Tool-Call Tests
# Run: pytest evaluation_fixed.py -k test_email_dataset_tool_calls
# ─────────────────────────────────────────────
import pytest
try:
    from langsmith import testing as t
    LANGSMITH_TESTING = True
except ImportError:
    LANGSMITH_TESTING = False


@pytest.mark.langsmith
@pytest.mark.parametrize(
    "email_input, expected_calls",
    [
        (email_inputs[0], expected_tool_calls[0]),
        (email_inputs[3], expected_tool_calls[3]),
    ],
)
def test_email_dataset_tool_calls(email_input, expected_calls):
    """Test if email processing contains all expected tool calls."""
    messages = [{"role": "user", "content": str(email_input)}]
    result = email_assistant.invoke({"messages": messages})

    extracted = extract_tool_calls(result["messages"])
    missing_calls = [c for c in expected_calls if c.lower() not in extracted]

    if LANGSMITH_TESTING:
        t.log_outputs({
            "missing_calls": missing_calls,
            "extracted_tool_calls": extracted,
            "response": format_messages_string(result["messages"]),
        })

    assert len(missing_calls) == 0, f"Missing tool calls: {missing_calls}"


# ─────────────────────────────────────────────
# SECTION 9: Target + Evaluator Functions
# ─────────────────────────────────────────────

def target_email_assistant(inputs: dict) -> dict:
    """Pass dataset email input through the triage router and return classification."""
    response = email_assistant.nodes["triage_router"].invoke(
        {"email_input": inputs["email_input"]}
    )
    return {"classification_decision": response.update["classification_decision"]}


def classification_evaluator(outputs: dict, reference_outputs: dict) -> bool:
    """Return True if agent classification matches ground truth (case-insensitive)."""
    return (
        outputs["classification_decision"].lower()
        == reference_outputs["classification"].lower()
    )


# ─────────────────────────────────────────────
# SECTION 10: Run LangSmith Dataset Evaluation
# ─────────────────────────────────────────────

def run_triage_evaluation():
    """Run the triage evaluation experiment against the LangSmith dataset."""
    if not ASSISTANT_AVAILABLE:
        print("\n⚠️  Skipping triage evaluation — email_assistant not available.")
        return None

    print("\n--- Running Triage Evaluation ---")
    experiment_results = client.evaluate(
        target_email_assistant,
        data=dataset_name,
        evaluators=[classification_evaluator],
        experiment_prefix="E-mail assistant workflow",
        max_concurrency=2,
    )
    print("✅ Evaluation complete. Check LangSmith UI for results.")
    return experiment_results


# ─────────────────────────────────────────────
# SECTION 11: LLM-as-Judge Evaluation
# ─────────────────────────────────────────────
from pydantic import BaseModel, Field


class CriteriaGrade(BaseModel):
    """Score the response against specific criteria."""
    justification: str = Field(
        description="Justification for the grade, with specific examples from the response."
    )
    grade: bool = Field(description="Does the response meet the provided criteria?")


def run_llm_judge_evaluation(email_input_idx: int = 0):
    """Run a single LLM-as-judge evaluation on one email example."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("\n⚠️  OPENAI_API_KEY not set — skipping LLM-as-judge evaluation.")
        return None

    try:
        from langchain.chat_models import init_chat_model
    except ImportError:
        try:
            from langchain_community.chat_models import init_chat_model
        except ImportError:
            print("\n⚠️  langchain not installed — skipping LLM-as-judge evaluation.")
            print("    Install with: pip install langchain langchain-openai")
            return None

    criteria_eval_llm = init_chat_model("openai:gpt-4o")
    criteria_eval_structured_llm = criteria_eval_llm.with_structured_output(CriteriaGrade)

    email_input      = email_inputs[email_input_idx]
    success_criteria = response_criteria_list[email_input_idx]

    print(f"\nEmail Input:      {email_input}")
    print(f"Success Criteria: {success_criteria}")

    if not ASSISTANT_AVAILABLE:
        print("⚠️  Skipping LLM judge — email_assistant not available.")
        return None

    response = email_assistant.invoke({"email_input": email_input})
    all_messages_str = format_messages_string(response["messages"])

    eval_result = criteria_eval_structured_llm.invoke([
        {"role": "system", "content": RESPONSE_CRITERIA_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"\n\nResponse criteria: {success_criteria}"
                f"\n\nAssistant's response:\n\n{all_messages_str}"
                f"\n\nEvaluate whether the assistant's response meets the criteria "
                f"and provide justification for your evaluation."
            ),
        },
    ])

    print(f"\n✅ LLM Judge Result:")
    print(f"   Grade:         {eval_result.grade}")
    print(f"   Justification: {eval_result.justification}")
    return eval_result


# ─────────────────────────────────────────────
# SECTION 12: Read Experiment Results (optional)
# ─────────────────────────────────────────────

def load_experiment_results(experiment_name: str):
    """Load and print stats for a completed experiment by name."""
    results = client.read_project(project_name=experiment_name, include_stats=True)
    print(f"\n--- Experiment Results: {experiment_name} ---")
    print("Latency p50:    ", results.latency_p50)
    print("Latency p99:    ", results.latency_p99)
    print("Token Usage:    ", results.total_tokens)
    print("Feedback Stats: ", results.feedback_stats)
    return results


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":

    # --- Toggle these flags to control what runs ---
    RUN_TRIAGE_EVAL = True    # Runs dataset evaluation via LangSmith
    RUN_LLM_JUDGE   = True    # Runs LLM-as-judge on example 0
    LOAD_EXPERIMENT = False   # Set True + fill name below to load past results
    EXPERIMENT_NAME = "email_assistant:8286b3b8"

    if RUN_TRIAGE_EVAL:
        run_triage_evaluation()

    if RUN_LLM_JUDGE:
        run_llm_judge_evaluation(email_input_idx=0)

    if LOAD_EXPERIMENT:
        load_experiment_results(EXPERIMENT_NAME)