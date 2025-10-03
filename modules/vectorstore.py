import faiss
import numpy as np
import os
import pickle
import json
from typing import List, Dict, Any, Tuple

class VectorStore:
    def __init__(self, dim: int = 1536, persist_path: str = "vectorstore"):
        self.dim = dim
        self.persist_path = persist_path
        self.ids: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []

        os.makedirs(self.persist_path, exist_ok=True)
        self.index_file = os.path.join(self.persist_path, "faiss.index")
        self.meta_file = os.path.join(self.persist_path, "meta.pkl")

        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            if os.path.exists(self.meta_file):
                with open(self.meta_file, "rb") as f:
                    self.ids, self.metadatas = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dim)

    def add(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Adding embeddings + metadata to FAISS index.
        """
        if len(embeddings) != len(ids) or len(embeddings) != len(metadatas):
            raise ValueError("Length of embeddings, ids, and metadatas must match")

        embs = np.array(embeddings, dtype="float32")
        self.index.add(embs)
        self.ids.extend(ids)
        self.metadatas.extend(metadatas)
        self._save()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        if self.index.ntotal == 0:
            return []
        q_emb = np.array([query_embedding], dtype="float32")
        distances, indices = self.index.search(q_emb, top_k)
        results: List[Tuple[str, float, Dict[str, Any]]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.ids):
                meta = self.metadatas[idx] if idx < len(self.metadatas) else {}
                results.append((self.ids[idx], float(dist), meta))
        return results


    def _save(self):
        # Persist FAISS index and metadata to disk
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "wb") as f:
            pickle.dump((self.ids, self.metadatas), f)

    def reset(self):
        # Clear the vectorstore completely.
        self.index = faiss.IndexFlatL2(self.dim)
        self.ids = []
        self.metadatas = []
        self._save()


# singleton instance for easy reuse
vector_store_instance: VectorStore = None

def init_vectorstore(dim: int = 1536, persist_path: str = "vectorstore") -> VectorStore:
    global vector_store_instance
    vector_store_instance = VectorStore(dim=dim, persist_path=persist_path)
    return vector_store_instance
