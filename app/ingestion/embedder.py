import time
from typing import Sequence

from google import genai
from google.genai import types

from app.config import settings


MODEL_NAME = settings.google_embedding_model
BATCH_SIZE = 5
EMBEDDING_DIMENSIONS = 3072


def _client() -> genai.Client:
    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is required for Google AI Studio")
    return genai.Client(api_key=settings.google_api_key)


def embed_texts(
    texts: Sequence[str],
    task_type: str,
) -> list[list[float]]:
    client = _client()
    embeddings: list[list[float]] = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = list(texts[start : start + BATCH_SIZE])
        response = client.models.embed_content(
            model=MODEL_NAME,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )
        if response.embeddings is None:
            raise RuntimeError("Embedding API returned no embeddings")
        embeddings.extend(
            [list(item.values or []) for item in response.embeddings]
        )
        if start + BATCH_SIZE < len(texts):
            time.sleep(0.2)

    if any(len(embedding) != EMBEDDING_DIMENSIONS for embedding in embeddings):
        raise ValueError(
            f"Embedding model must return {EMBEDDING_DIMENSIONS} dimensions"
        )
    return embeddings


def embed_query(text: str) -> list[float]:
    return embed_texts([text], "RETRIEVAL_QUERY")[0]
