import numpy as np


class VectorStore:
    def __init__(self, documents: list[str], embeddings: np.ndarray):
        self.documents = documents
        self.embeddings = embeddings

    def search(self, query_embedding: np.ndarray, top_k: int = 3):
        query_norm = np.linalg.norm(query_embedding)
        document_norm = np.linalg.norm(self.embeddings, axis=1)

        dot_products = self.embeddings @ query_embedding

        similarities = dot_products / (document_norm * query_norm)

        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [
            {"text": self.documents[i], "score": similarities[i]} for i in top_indices
        ]
