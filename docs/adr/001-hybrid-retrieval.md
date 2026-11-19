# ADR 001: Hybrid Retrieval

Use a weighted combination of pgvector cosine similarity and PostgreSQL full-text rank.

Vector search finds semantic matches; keyword search finds exact enterprise terms.
