import httpx
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction

from app.config import settings


class OllamaEmbeddingFunction(EmbeddingFunction[Documents]):
    """Sync Chroma embedding function backed by Ollama /api/embed.

    Synchronous because Chroma invokes it from its own threads.
    """

    def __init__(self, model: str | None = None) -> None:
        super().__init__()
        self._model = model or settings.EMBED_MODEL
        self._base_url = settings.LLM_BASE_URL

    def __call__(self, input: Documents) -> Embeddings:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": list(input)},
            )
            resp.raise_for_status()
            return resp.json()["embeddings"]


async def ollama_embed(texts: list[str], model: str | None = None) -> list[list[float]]:
    """Async variant for direct use in async code paths."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.LLM_BASE_URL}/api/embed",
            json={"model": model or settings.EMBED_MODEL, "input": texts},
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]
