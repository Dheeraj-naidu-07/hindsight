---
name: rag-engineering
description: Use this skill when building Retrieval-Augmented Generation (RAG) pipelines, integrating vector databases, or improving retrieval relevance.
---

# RAG Engineering

## When to Use

Use this skill when:
- Ingesting, chunking, and embedding documents.
- Querying a vector database for semantic search.
- Designing reranking pipelines.
- Assembling retrieved context into an LLM prompt.

## Workflow

1. **Ingestion & Chunking**: Clean source documents and chunk them semantically (e.g., by header or paragraph) rather than arbitrarily.
2. **Embedding**: Generate dense embeddings (and optionally sparse vectors for hybrid search). Store in a vector store.
3. **Retrieval**: Query the vector store using the user's embedded query.
4. **Reranking**: (Optional) Use a cross-encoder to rerank the top-k results for higher precision.
5. **Generation**: Inject the most relevant chunks into the LLM prompt and instruct the model to ground its answers using only the provided context.

## Best Practices

- Embed document metadata (dates, authors) to enable pre-filtering during retrieval.
- Hybrid search (keyword + semantic) almost always beats pure semantic search.

## Common Failure Modes

- "Lost in the middle": Injecting too much context so the LLM ignores chunks in the middle.
- Embedding drift: Updating the embedding model but failing to re-index the historical documents.

## Verification

- Inspect the retrieved chunks before they are sent to the LLM to ensure they actually contain the answer to the user's query.
