from typing import Any

from psycopg_pool import ConnectionPool

from app.config import settings
from app.ingestion.embedder import embed_query


HYBRID_SQL = """
WITH vec AS (
  SELECT id, content, 1 - (embedding <=> %s::vector) AS v_score
  FROM chunks
  WHERE embedding IS NOT NULL
  ORDER BY embedding <=> %s::vector
  LIMIT 20
),
kw AS (
  SELECT id, ts_rank(
    tsv,
    websearch_to_tsquery('english', %s)
  ) AS tsq_rank
  FROM chunks
  WHERE tsv @@ websearch_to_tsquery('english', %s)
  ORDER BY tsq_rank DESC
  LIMIT 20
)
SELECT c.id, c.content, d.title, d.gcs_uri,
       0.7 * COALESCE(v.v_score, 0) AS v_score,
       COALESCE(k.tsq_rank, 0) AS keyword_score
FROM chunks c
LEFT JOIN vec v ON v.id = c.id
LEFT JOIN kw k ON k.id = c.id
LEFT JOIN documents d ON d.id = c.document_id
WHERE v.id IS NOT NULL OR k.id IS NOT NULL
LIMIT 40;
"""


pool = ConnectionPool(
    conninfo=settings.database_url,
    min_size=1,
    max_size=5,
    open=True,
)


def _min_max(values: list[float]) -> list[float]:
    if not values:
        return []
    low = min(values)
    high = max(values)
    if high == low:
        return [1.0 if value > 0 else 0.0 for value in values]
    return [(value - low) / (high - low) for value in values]


def retrieve(query: str, k: int = 5) -> list[dict[str, Any]]:
    query_embedding = embed_query(query)
    embedding_text = str(query_embedding)

    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                HYBRID_SQL,
                (
                    embedding_text,
                    embedding_text,
                    query,
                    query,
                ),
            )
            rows = cursor.fetchall()

    keyword_scores = _min_max([float(row[5]) for row in rows])
    results: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        vector_score = max(0.0, float(row[4]))
        score = 0.7 * vector_score + 0.3 * keyword_scores[index]
        score = max(0.0, min(1.0, score))
        results.append(
            {
                "chunk_id": str(row[0]),
                "content": row[1],
                "title": row[2],
                "source_uri": row[3],
                "score": round(score, 6),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:k]
