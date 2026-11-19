import json

import redis

from app.config import settings


client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get_history(session_id: str) -> list[dict[str, object]]:
    raw = client.get(f"session:{session_id}")
    if not raw:
        return []
    history = json.loads(raw)
    if not isinstance(history, list):
        raise ValueError("Invalid conversation history stored in Redis")
    return history


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


def record_query(cache_hit: bool) -> tuple[int, int]:
    total = client.incr("atlas:metrics:queries")
    hits = client.incr("atlas:metrics:cache_hits") if cache_hit else int(
        client.get("atlas:metrics:cache_hits") or 0
    )
    client.expire("atlas:metrics:queries", 86400)
    if cache_hit:
        client.expire("atlas:metrics:cache_hits", 86400)
    return int(total), int(hits)
