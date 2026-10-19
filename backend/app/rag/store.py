import asyncio

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction

from app.config import settings
from app.rag.embeddings import OllamaEmbeddingFunction

RESUMES_COLLECTION = "resumes"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

_client = None


def get_client(path: str | None = None):
    global _client
    if path is not None:
        return chromadb.PersistentClient(path=path)
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_collection(
    name: str,
    embedding_fn: EmbeddingFunction[Documents] | None = None,
    path: str | None = None,
):
    client = get_client(path)
    return client.get_or_create_collection(
        name,
        embedding_function=embedding_fn or OllamaEmbeddingFunction(),
    )


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Deterministic sliding-window chunker over characters."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    if len(cleaned) <= size:
        return [cleaned]
    chunks = []
    step = size - overlap
    for start in range(0, len(cleaned), step):
        chunk = cleaned[start:start + size]
        if chunk.strip():
            chunks.append(chunk)
        if start + size >= len(cleaned):
            break
    return chunks


def _index_resume_sync(
    user_id: str,
    resume_id: str,
    raw_text: str,
    embedding_fn: EmbeddingFunction[Documents] | None = None,
    path: str | None = None,
) -> int:
    chunks = chunk_text(raw_text)
    if not chunks:
        return 0
    collection = get_collection(RESUMES_COLLECTION, embedding_fn, path)
    collection.upsert(
        ids=[f"{resume_id}:{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"user_id": user_id, "resume_id": resume_id} for _ in chunks],
    )
    return len(chunks)


async def index_resume(
    user_id: str,
    resume_id: str,
    raw_text: str,
    embedding_fn: EmbeddingFunction[Documents] | None = None,
    path: str | None = None,
) -> int:
    """Index a resume's chunks. Raises on failure -- callers decide fallback."""
    return await asyncio.to_thread(
        _index_resume_sync, user_id, resume_id, raw_text, embedding_fn, path
    )


def _query_resume_sync(
    user_id: str,
    resume_id: str,
    query: str,
    k: int,
    embedding_fn: EmbeddingFunction[Documents] | None = None,
    path: str | None = None,
) -> list[str]:
    collection = get_collection(RESUMES_COLLECTION, embedding_fn, path)
    result = collection.query(
        query_texts=[query],
        n_results=k,
        where={"$and": [{"user_id": {"$eq": user_id}}, {"resume_id": {"$eq": resume_id}}]},
    )
    docs = result.get("documents") or []
    return list(docs[0]) if docs else []


async def query_resume_chunks(
    user_id: str,
    resume_id: str,
    query: str,
    k: int | None = None,
    embedding_fn: EmbeddingFunction[Documents] | None = None,
    path: str | None = None,
) -> list[str]:
    """Retrieve top-k resume chunks scoped to this user+resume. Raises on failure."""
    return await asyncio.to_thread(
        _query_resume_sync,
        user_id,
        resume_id,
        query,
        k or settings.RAG_TOP_K,
        embedding_fn,
        path,
    )
