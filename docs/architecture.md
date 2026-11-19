# Atlas Architecture

```text
React/Vite
  -> FastAPI / Cloud Run
  -> ADK Supervisor
       -> RAG Agent -> pgvector + PostgreSQL
       -> SQL Agent -> Read-only billing table
       -> Summarizer Agent
       -> Critic Agent
  -> Redis cache/state
  -> GCS ingestion
  -> Vertex AI / Gemini
```

## Components

| Component | Responsibility |
|---|---|
| React/Vite | Login, chat, citations, metrics |
| FastAPI | JWT, SSE, history, metrics, query logging |
| ADK | Multi-agent orchestration |
| pgvector | Semantic chunk retrieval |
| PostgreSQL | Structured billing data |
| Redis | Conversation state and semantic cache |
| GCS | Source document storage |
| Vertex AI | Embeddings and Gemini models |
