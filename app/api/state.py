import json

import redis

from app.config import settings


client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get_history(session_id: str) -> list[dict[str, object]]:
    raw = client.get(f"session:{session_id}")
    if not raw:
        return []
    return json.loads(raw)


def append_turn(session_id: str, question: str, answer: str) -> list[dict[str, object]]:
    history = get_history(session_id)
    history.append({"question": question, "answer": answer})
    history = history[-10:]
    client.setex(
        f"session:{session_id}",
        3600,
        json.dumps(history),
    )
    return history
