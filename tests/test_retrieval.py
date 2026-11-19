import pytest

from app.retrieval.hybrid_retriever import _min_max, retrieve


def test_min_max_normalization() -> None:
    assert _min_max([1.0, 2.0, 3.0]) == [0.0, 0.5, 1.0]
    assert _min_max([]) == []


@pytest.mark.integration
def test_hybrid_retrieval_returns_citations() -> None:
    results = retrieve("how to rotate database credentials", k=5)

    assert len(results) <= 5
    for result in results:
        assert 0.0 <= result["score"] <= 1.0
        assert result["chunk_id"]
        assert result["content"]
        assert result["title"]
        assert result["source_uri"]
