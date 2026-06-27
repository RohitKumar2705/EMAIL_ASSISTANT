from typing import Any, Dict, List
import re


def parse_email(raw_email: str) -> Dict[str, str]:
    """Parse a raw email string into a structured dictionary."""
    # This is a simple placeholder parser. Replace with your real logic.
    return {
        "subject": "",
        "sender": "",
        "body": raw_email,
    }


def format_email_markdown(email_data: Dict[str, str]) -> str:
    """Format parsed email data as markdown."""
    subject = email_data.get("subject", "")
    sender = email_data.get("sender", "")
    body = email_data.get("body", "")
    return f"**From:** {sender}\n\n**Subject:** {subject}\n\n{body}"


def format_messages_string(messages: List[Dict[str, Any]]) -> str:
    """Convert a list of assistant messages into a readable string."""
    if not isinstance(messages, list):
        return str(messages)

    formatted = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role", "unknown")
        content = message.get("content", "")
        formatted.append(f"{role}: {content}")
    return "\n\n".join(formatted)


def extract_tool_calls(messages: List[Dict[str, Any]]) -> List[str]:
    """Extract normalized tool-call names from assistant messages."""
    calls = []
    if not isinstance(messages, list):
        return calls

    for message in messages:
        if not isinstance(message, dict):
            continue

        tool_call = message.get("tool_call")
        if isinstance(tool_call, dict):
            name = tool_call.get("name")
            if isinstance(name, str):
                calls.append(name.lower())

        content = message.get("content")
        if isinstance(content, str):
            calls += [match.lower() for match in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", content)]

    return list(dict.fromkeys(calls))


extract_toll_calls = extract_tool_calls
