# Example evaluation dataset for email_assistant.eval.email_dataset
# Replace these sample values with your real test cases.

email_inputs = [
    "Subject: Invoice payment\n\nHi team, I have a question about my latest invoice.",
    "Subject: Account access issue\n\nI cannot log in to my account after resetting the password.",
    "Subject: Meeting reschedule\n\nCan we move our meeting from 3pm to 4pm tomorrow?",
    "Subject: Product feedback\n\nThe new feature is helpful but I found a bug in the dashboard.",
]

expected_tool_calls = [
    ["open_invoice", "check_payment_status"],
    ["verify_account", "reset_password"],
    ["check_calendar", "reschedule_meeting"],
    ["log_bug", "send_feedback"],
]

triage_outputs_list = [
    "This looks like a billing inquiry that should be routed to Finance.",
    "This is an account access issue that should be handled by Support.",
    "This is a scheduling request that should be assigned to the calendar team.",
    "This is product feedback that should be forwarded to the product team.",
]

response_criteria_list = [
    "Provide a clear statement of the issue and next steps for the user.",
    "Provide account recovery instructions and confirm the next security step.",
    "Confirm the requested time change and if any additional steps are needed.",
    "Acknowledge the feedback and explain how the bug report will be handled.",
]

examples_triage = [
    {
        "inputs": {"email_input": email_inputs[0]},
        "outputs": {
            "classification": "respond",
            "expected_tool_calls": expected_tool_calls[0],
            "triage_output": triage_outputs_list[0],
            "response_criteria": response_criteria_list[0],
        },
    },
    {
        "inputs": {"email_input": email_inputs[1]},
        "outputs": {
            "classification": "respond",
            "expected_tool_calls": expected_tool_calls[1],
            "triage_output": triage_outputs_list[1],
            "response_criteria": response_criteria_list[1],
        },
    },
    {
        "inputs": {"email_input": email_inputs[2]},
        "outputs": {
            "classification": "respond",
            "expected_tool_calls": expected_tool_calls[2],
            "triage_output": triage_outputs_list[2],
            "response_criteria": response_criteria_list[2],
        },
    },
    {
        "inputs": {"email_input": email_inputs[3]},
        "outputs": {
            "classification": "notify",
            "expected_tool_calls": expected_tool_calls[3],
            "triage_output": triage_outputs_list[3],
            "response_criteria": response_criteria_list[3],
        },
    },
]
