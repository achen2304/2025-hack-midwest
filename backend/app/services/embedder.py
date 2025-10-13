# app/services/embedder.py
from sentence_transformers import SentenceTransformer
from functools import lru_cache
from typing import List

@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 384 dims

def embed_text(text: str) -> List[float]:
    v = _model().encode([text], normalize_embeddings=True)  # cosine-friendly
    return v[0].tolist()
