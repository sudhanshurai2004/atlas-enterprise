import os
import time
from typing import Sequence

import vertexai
from vertexai.language_models import TextEmbeddingModel


MODEL_NAME = "gemini-embedding-2"
BATCH_SIZE = 5


def _model() -> TextEmbeddingModel:
    vertexai.init(
        project=os.getenv("GCP_PROJECT_ID", "atlas-demo"),
        location=os.getenv("GCP_REGION", "asia-south1"),
    )
    return TextEmbeddingModel.from_pretrained(MODEL_NAME)


def embed_texts(
    texts: Sequence[str],
    task_type: str,
) -> list[list[float]]:
    model = _model()
    embeddings: list[list[float]] = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = list(texts[start : start + BATCH_SIZE])
        response = model.get_embeddings(
            batch,
            task_type=task_type,
        )
        embeddings.extend([item.values for item in response])
        if start + BATCH_SIZE < len(texts):
            time.sleep(0.2)

    return embeddings


def embed_query(text: str) -> list[float]:
    return embed_texts([text], "RETRIEVAL_QUERY")[0]
