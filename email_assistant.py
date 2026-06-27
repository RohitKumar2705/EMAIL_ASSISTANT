from __future__ import annotations

from typing import Any, Dict


class EmailAssistant:
    """A simple placeholder email assistant for local testing."""

    def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        messages = request.get("messages", [])
        return {"messages": messages}


email_assistant = EmailAssistant()
