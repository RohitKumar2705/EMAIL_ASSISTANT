triage_system_prompt = "You are an assistant that triages incoming email messages."

triage_user_prompt = "Decide whether the email should be ignored, responded to, or forwarded as a notification."

default_triage_instructions = lambda: (
    "Read the email content and choose one of: ignore, respond, notify. "
    "If the email clearly requires a reply, choose respond. "
    "If it is informational or not urgent, choose ignore. "
    "If it needs a human or team notification, choose notify."
    )

default_background = (
    "You are working in an email assistant application that helps manage and classify email. "
    "Use the provided message metadata and body to decide the best action."
)
