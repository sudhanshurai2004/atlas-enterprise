from typing import Any

from app.api.state import client
from app.ingestion.embedder import embed_query


def _cosine(left: list[float], right: list[float]) -> float:
    if not left or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def get_cached_answer(question: str) -> dict[str, Any] | None:
    query_embedding = embed_query(question)
    entries = client.zrange("atlas:semantic-cache", 0, -1)

    for entry_key in entries:
        raw = client.get(entry_key)
        embedding_raw = client.get(f"{entry_key}:embedding")
        if not raw or not embedding_raw:
            continue
        embedding = [float(value) for value in embedding_raw.split(",")]
        if _cosine(query_embedding, embedding) >= 0.98:
            import json

            return json.loads(raw)

    return None


def set_cached_answer(question: str, response: dict[str, Any]) -> None:
    import json
    import uuid

    embedding = embed_query(question)
    cache_key = f"atlas:cache:{uuid.uuid4().hex}"
    client.set(cache_key, json.dumps(response), ex=3600)
    client.set(
        f"{cache_key}:embedding",
        ",".join(str(value) for value in embedding),
        ex=3600,
    )
    client.zadd("atlas:semantic-cache", {cache_key: 1})
