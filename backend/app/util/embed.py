"""
Embedding utilities for vector search in CampusMind
"""
import numpy as np
from typing import List, Dict, Any
import httpx
import os

class EmbeddingService:
    """Service for generating embeddings for vector search"""
    
    def __init__(self):
        self.embedding_model = "text-embedding-ada-002"  # OpenAI model
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_dimension = 1536  # OpenAI ada-002 dimension
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API"""
        try:
            if not self.openai_api_key:
                # Return dummy embedding for development
                return [0.0] * self.embedding_dimension
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.embedding_model,
                        "input": text
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["data"][0]["embedding"]
                else:
                    print(f"OpenAI API error: {response.status_code}")
                    return [0.0] * self.embedding_dimension
                    
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * self.embedding_dimension
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            embeddings = []
            for text in texts:
                embedding = await self.generate_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            return [[0.0] * self.embedding_dimension] * len(texts)
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def prepare_vector_document(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare document for vector storage"""
        try:
            embedding = await self.generate_embedding(content)
            
            return {
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
                "vector_dimension": self.embedding_dimension
            }
        except Exception as e:
            print(f"Error preparing vector document: {e}")
            return {
                "content": content,
                "embedding": [0.0] * self.embedding_dimension,
                "metadata": metadata,
                "vector_dimension": self.embedding_dimension
            }
