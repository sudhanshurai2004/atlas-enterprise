from types import SimpleNamespace

import pytest

from app.ingestion import embedder


def test_embed_texts_uses_google_ai_studio(monkeypatch) -> None:
    calls = []

    class FakeModels:
        def embed_content(self, *, model, contents, config):
            calls.append((model, contents, config.task_type))
            return SimpleNamespace(
                embeddings=[
                    SimpleNamespace(values=[0.25] * 3072)
                    for _ in contents
                ]
            )

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(embedder.settings, "google_api_key", "test-key")
    monkeypatch.setattr(
        embedder.genai,
        "Client",
        lambda *, api_key: FakeClient(),
    )

    vectors = embedder.embed_texts(
        ["doc one", "doc two"],
        "RETRIEVAL_DOCUMENT",
    )

    assert len(vectors) == 2
    assert all(len(vector) == 3072 for vector in vectors)
    assert calls == [
        ("gemini-embedding-001", ["doc one", "doc two"], "RETRIEVAL_DOCUMENT")
    ]


def test_embed_texts_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr(embedder.settings, "google_api_key", None)

    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        embedder.embed_texts(["query"], "RETRIEVAL_QUERY")
