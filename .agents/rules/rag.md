---
trigger: model_decision
name: rag-engineering-rules
description: Apply when designing, implementing, evaluating, or debugging retrieval-augmented generation systems, including ingestion, chunking, embeddings, retrieval, reranking, and grounding.
---

# Retrieval-Augmented Generation (RAG) Rules

- **Retrieval Quality**: Focus on retrieval quality before generation quality. The LLM cannot generate accurate answers without relevant context.
- **Appropriate Chunking**: Chunk documents logically (e.g., by paragraph or section) rather than indiscriminately by character count. Keep semantic units intact.
- **Metadata Preservation**: Preserve source metadata (e.g., document title, author, URL, page number) alongside text chunks for filtering and citation.
- **Embedding Consistency**: Ensure that queries and documents are embedded using the exact same model and version.
- **Retrieval Evaluation**: Evaluate the retrieval system independently of the generation step using metrics like NDCG or MRR.
- **Grounding**: Instruct the LLM to only use the provided context to answer the user's query.
- **Citation/Source Tracking**: Require the model to cite its sources from the retrieved chunks.
- **Unsupported Claims**: Instruct the model to explicitly state when the provided context does not contain the answer, preventing unsupported claims or hallucinations.
