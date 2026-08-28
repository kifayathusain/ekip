# Architecture

```text
React + TypeScript
       |
       v
     FastAPI
       |
  +----+----------------+
  |                     |
  v                     v
PostgreSQL + pgvector  Document Processing
  |                     |
  +---------+-----------+
            |
            v
       RAG Retrieval
            |
            v
       LLM Provider
```

Production target:

```text
Users -> App Gateway/Ingress -> AKS
                           |-> FastAPI API
                           |-> Document Worker
                           |-> Evaluation Worker
                           |
                           +-> Azure PostgreSQL + pgvector
                           +-> Blob Storage
                           +-> Service Bus
                           +-> Azure OpenAI
                           +-> Key Vault
                           +-> Application Insights
```
