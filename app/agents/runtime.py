import asyncio
import json
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.supervisor import supervisor


APP_NAME = "atlas"
session_service = InMemorySessionService()
runner = Runner(
    app_name=APP_NAME,
    agent=supervisor,
    session_service=session_service,
    auto_create_session=True,
)


async def _run(question: str, user_id: str, session_id: str) -> dict[str, Any]:
    events = runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=question)],
        ),
    )
    final_text = ""
    async for event in events:
        if event.is_final_response() and event.content:
            final_text = "".join(
                part.text or "" for part in event.content.parts
            )

    if not final_text:
        raise RuntimeError("The Atlas supervisor returned no final response")

    try:
        result = json.loads(final_text)
    except json.JSONDecodeError:
        result = {
            "answer": final_text,
            "citations": [],
            "confidence": 0.5,
        }

    if not isinstance(result, dict) or not isinstance(result.get("answer"), str):
        return {
            "answer": final_text,
            "citations": [],
            "confidence": 0.5,
        }

    result.setdefault("citations", [])
    result.setdefault("confidence", 0.5)
    return result


def run_supervisor(
    question: str,
    user_id: str,
    session_id: str,
) -> dict[str, Any]:
    return asyncio.run(_run(question, user_id, session_id))
