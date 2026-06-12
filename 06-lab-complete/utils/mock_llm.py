"""Offline mock LLM used by the deployment lab."""
import random
import re
import time


DEFAULT_RESPONSES = [
    "The production agent received your question successfully.",
    "The agent is healthy and ready to serve requests.",
    "This is an offline mock response. Replace it with a real LLM in production.",
]


def ask(question: str, history: list[dict[str, str]] | None = None) -> str:
    time.sleep(0.02)
    question_lower = question.lower()

    if "what is my name" in question_lower or "what's my name" in question_lower:
        for message in reversed(history or []):
            if message.get("role") != "user":
                continue
            match = re.search(r"\bmy name is\s+([A-Za-z][A-Za-z '-]{0,50})", message["content"], re.I)
            if match:
                return f"Your name is {match.group(1).strip()}."

    if "docker" in question_lower:
        return "Docker packages an application and its dependencies into a portable container."
    if "deploy" in question_lower:
        return "Deployment makes an application available in a target environment such as the cloud."
    return random.choice(DEFAULT_RESPONSES)
