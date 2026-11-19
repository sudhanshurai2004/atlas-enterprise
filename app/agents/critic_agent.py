from typing import Any

from google.adk.agents import Agent


critic_agent = Agent(
    name="critic_agent",
    model="gemini-2.5-flash",
    instruction=(
        "Critique an answer for citation coverage and confidence. "
        "If confidence is below 0.7 or citations are missing, request "
        "re-retrieval and provide concise feedback."
    ),
)


def critique_answer(
    candidate: dict[str, Any],
    max_rounds: int = 2,
) -> dict[str, Any]:
    confidence = float(candidate.get("confidence", 0.0))
    citations = candidate.get("citations", [])
    feedback: list[str] = []

    if confidence < 0.7:
        feedback.append("Low confidence; retrieve stronger evidence")
    if not citations:
        feedback.append("Citation missing")

    return {
        "approved": not feedback,
        "feedback": feedback,
        "rounds_remaining": max(0, max_rounds - 1),
    }
