import pytest

from chromadb.api.types import Documents, Embeddings, EmbeddingFunction

from app.agents.skill_agent import compute_skill_gap
from app.rag.store import chunk_text, index_resume, query_resume_chunks


class FakeEF(EmbeddingFunction[Documents]):
    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return "fake-test-ef"

    def __call__(self, input: Documents) -> Embeddings:
        vecs = []
        for doc in input:
            v = [0.0] * 16
            for w in doc.lower().split():
                v[hash(w) % 16] += 1.0
            vecs.append(v)
        return vecs


def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   \n  ") == []


def test_chunk_text_short_single():
    assert chunk_text("hello world") == ["hello world"]


def test_chunk_text_long_overlaps():
    text = "word " * 500  # 2500 chars
    chunks = chunk_text(text, size=800, overlap=150)
    assert len(chunks) > 1
    assert all(len(c) <= 800 for c in chunks)
    # overlap continuity: end of one chunk appears in the next
    assert chunks[0][-150:] in chunks[1]


@pytest.mark.asyncio
async def test_index_and_query_roundtrip(tmp_path):
    path = str(tmp_path / "chroma")
    n = await index_resume("u1", "r1", "Python developer with Docker and Kubernetes experience", FakeEF(), path)
    assert n >= 1
    hits = await query_resume_chunks("u1", "r1", "Python Docker", k=2, embedding_fn=FakeEF(), path=path)
    assert hits
    assert any("Python" in h for h in hits)


@pytest.mark.asyncio
async def test_query_isolates_user_and_resume(tmp_path):
    path = str(tmp_path / "chroma")
    await index_resume("u1", "r1", "Python developer with Docker experience", FakeEF(), path)
    await index_resume("u2", "r2", "Python developer with Docker experience", FakeEF(), path)

    # Other user's data is invisible.
    assert await query_resume_chunks("u1", "r2", "Python", embedding_fn=FakeEF(), path=path) == []
    assert await query_resume_chunks("u2", "r1", "Python", embedding_fn=FakeEF(), path=path) == []
    # Own data is visible.
    own = await query_resume_chunks("u1", "r1", "Python", embedding_fn=FakeEF(), path=path)
    assert own


@pytest.mark.asyncio
async def test_skill_gap_default_path_uses_static_templates():
    parsed = {"skills": ["Python"]}
    result = await compute_skill_gap(parsed, "AI Engineer", context=None)
    assert "TensorFlow" in result["missing"]
    rec = next(r for r in result["recommendations"] if r["skill"] == "TensorFlow")
    assert "roadmap.sh" in rec["resource"]
