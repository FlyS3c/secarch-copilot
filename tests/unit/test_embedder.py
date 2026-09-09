import pytest

from app.ingestion.embedder import OllamaEmbedder


class FakeOllamaClient:
    def embed(self, *, model: str, input: list[str], truncate: bool) -> dict:
        assert model == "embeddinggemma"
        assert truncate is False
        return {"embeddings": [[float(len(text)), 1.0] for text in input]}


class WrongCountClient:
    def embed(self, **kwargs) -> dict:
        return {"embeddings": []}


def test_vector_count_equals_text_count() -> None:
    embedder = OllamaEmbedder(client=FakeOllamaClient(), batch_size=2)
    vectors = embedder.embed_texts(["one", "two", "three"])
    assert len(vectors) == 3
    assert all(len(vector) == 2 for vector in vectors)


def test_wrong_vector_count_is_rejected() -> None:
    embedder = OllamaEmbedder(client=WrongCountClient())
    with pytest.raises(RuntimeError, match="different number"):
        embedder.embed_texts(["one"])
