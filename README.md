# Enterprise Knowledge Intelligence Platform (EKIP)

A production-oriented RAG platform built with Next.js, FastAPI, PostgreSQL/pgvector and Docker. This repository starts with a fully runnable local MVP and is designed to evolve into the enterprise Azure/Kubernetes architecture described in `docs/architecture.md`.

## Current MVP

- PDF/DOCX/TXT/Markdown ingestion
- Document chunking
- Deterministic local embeddings for development
- PostgreSQL + pgvector semantic retrieval
- RAG-style answer generation with citations
- Next.js UI
- Docker Compose
- Health endpoint

> The local embedding and answer generator are intentionally deterministic so the repository runs without an external AI API. The next release replaces these adapters with Azure OpenAI/OpenAI/Gemini providers.

## Run

```bash
docker compose up --build
```

Open http://localhost:3000 and upload a document.

API: http://localhost:8000/docs

## Roadmap

1. LLM/embedding provider abstraction and Azure OpenAI
2. JWT + RBAC + document permissions
3. Conversation persistence
4. Hybrid retrieval and reranking
5. Evaluation with Ragas/DeepEval
6. OpenTelemetry and metrics
7. Production Docker/Kubernetes
8. Azure + Terraform + GitHub Actions

## License

MIT
