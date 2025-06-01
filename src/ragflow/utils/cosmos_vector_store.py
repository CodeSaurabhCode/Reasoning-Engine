from typing import List, Dict, Optional, Tuple
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
import numpy as np

class CosmosVectorStore(VectorStore):
    def __init__(self, container, embedding_function):
        self.container = container
        self.embedding_function = embedding_function

    def similarity_search_with_relevance_scores(
        self, query: str, k: int = 4, score_threshold: float = 0.5
    ) -> List[Tuple[Document, float]]:
        query_embedding = self.embedding_function.embed_query(query)

        # Fetch all docs & embeddings from Cosmos (you could optimize with filtering/indexing)
        items = list(self.container.read_all_items())

        scored = []
        for item in items:
            emb = np.array(item['embedding'])
            score = self._cosine_similarity(query_embedding, emb)
            if score >= score_threshold:
                doc = Document(page_content=item['page_content'], metadata=item.get('metadata', {}))
                scored.append((doc, score))

        # Sort by relevance
        scored = sorted(scored, key=lambda x: x[1], reverse=True)
        return scored[:k]

    def add_documents(self, documents: List[Document], ids: Optional[List[str]] = None):
        for i, doc in enumerate(documents):
            emb = self.embedding_function.embed_documents([doc.page_content])[0]
            self.container.upsert_item({
                'id': ids[i] if ids else str(i),
                'content': doc.page_content,
                'metadata': doc.metadata,
                'embedding': emb,
            })

    def get(self, ids: Optional[List[str]] = None, where: Optional[dict] = None) -> Dict:
        if ids:
            return {'documents': [self.container.read_item(item_id=id, partition_key=id) for id in ids]}
        # Optional: support filtering on metadata
        return {'documents': list(self.container.read_all_items())}

    def delete_collection(self):
        # Optional: Clear all items (dev only)
        for item in self.container.read_all_items():
            self.container.delete_item(item['id'], partition_key=item['id'])

    def _cosine_similarity(self, a, b):
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def from_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None) -> "CosmosVectorStore":
        documents = [Document(page_content=text, metadata=metadata) for text, metadata in zip(texts, metadatas or [{}])]
        self.add_documents(documents, ids)
        return self
    
    def similarity_search(self, query, k = 4, **kwargs):
        return super().similarity_search(query, k, **kwargs)