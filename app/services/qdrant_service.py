import hashlib

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.core.config import settings


class QdrantService:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url)

    @staticmethod
    def fake_embed(text: str, dim: int = 8) -> list[float]:
        digest = hashlib.sha256(text.encode('utf-8')).digest()
        return [int(digest[i]) / 255 for i in range(dim)]

    def ensure_collection(self, name: str) -> None:
        collections = [c.name for c in self.client.get_collections().collections]
        if name not in collections:
            self.client.create_collection(collection_name=name, vectors_config=VectorParams(size=8, distance=Distance.COSINE))

    def upsert_learning_item(self, item_id: int, text: str, payload: dict) -> None:
        self.ensure_collection(settings.qdrant_collection_learning)
        self.client.upsert(
            collection_name=settings.qdrant_collection_learning,
            points=[PointStruct(id=item_id, vector=self.fake_embed(text), payload=payload)],
        )

    def search_learning(self, query: str, limit: int = 5):
        self.ensure_collection(settings.qdrant_collection_learning)
        return self.client.search(
            collection_name=settings.qdrant_collection_learning,
            query_vector=self.fake_embed(query),
            limit=limit,
        )
