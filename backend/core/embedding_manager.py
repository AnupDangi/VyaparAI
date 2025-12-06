"""
Embedding Manager - Serverless Version
Uses Jina AI Embeddings API (Free Tier Compatible) for embeddings
Uses Qdrant Cloud for storage
"""
import os
import time
import requests
from typing import List, Dict, Any, Tuple
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

class EmbeddingManager:
    """Manages embeddings using Jina AI API"""
    
    def __init__(self):
        # Qdrant Configuration
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_key = os.getenv("QDRANT_API_KEY")
        
        # Initialize Qdrant
        if not self.qdrant_url:
            print("WARNING: QDRANT_URL not set. Using local in-memory/disk mode.")
            self.client = QdrantClient(path="./vector_store")
        else:
            try:
                self.client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_key)
                print(f"Connected to Qdrant Cloud")
            except Exception as e:
                print(f"Failed to connect to Qdrant Cloud: {e}")
                self.client = None

        self.collection_name = "products_schema"
        
        # Jina AI Configuration
        self.jina_api_key = os.getenv("JINA_API_KEY", "") 
        self.api_url = "https://api.jina.ai/v1/embeddings"
        self.model_name = "jina-embeddings-v2-base-en"
        self.embedding_dim = 768 

        if not self.jina_api_key:
             print("\n⚠️  WARNING: JINA_API_KEY not found. Using anonymous/limited access (might fail).")
             print("   Get a free key from https://jina.ai/embeddings/\n")
            
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings using Jina AI API
        """
        if not texts:
            return np.array([])
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jina_api_key}"
        }
        
        data = {
            "input": texts,
            "model": self.model_name
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            
            if response.status_code != 200:
                print(f"Jina API Error {response.status_code}: {response.text}")
                # Fallback to zeros if API fails to prevent hard crash during dev
                print("   -> Returning zero vectors as fallback.")
                return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)
                
            result = response.json()
            embeddings = [item['embedding'] for item in result['data']]
            return np.array(embeddings, dtype=np.float32)
            
        except Exception as e:
            print(f"Error calling Jina API: {e}")
            return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)

    def create_index(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """Create Qdrant collection"""
        if not self.client: return
        
        if len(embeddings) == 0:
            print("Skipping index creation (no embeddings)")
            return
            
        # Recreate collection
        try:
            self.client.delete_collection(collection_name=self.collection_name)
        except:
            pass
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
        )
        
        # Upsert
        points = []
        for idx, (embedding, meta) in enumerate(zip(embeddings, metadata)):
            point = PointStruct(id=idx, vector=embedding.tolist(), payload=meta, score=1.0) # score added for type safety if needed?
            points.append(point)
            
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"Indexed {len(points)} items in Qdrant")

    def search(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search Qdrant"""
        if not self.client: return []
        
        query_vec = self.generate_embeddings([query_text])[0]
        
        # If fallback zeros, don't search
        if np.all(query_vec == 0):
             return []

        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vec.tolist(),
            limit=top_k
        ).points
        
        return [{"score": r.score, "metadata": r.payload} for r in search_result]

    def embed_schema(self, schema: Dict[str, Any]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Convert schema to text and embed"""
        texts = []
        metadata = []
        
        for table, info in schema['tables'].items():
            for col in info['columns']:
                text = f"Table: {table} | Column: {col['name']} | Type: {col['type']} | Desc: {col['description']}"
                texts.append(text)
                metadata.append({
                    "table": table, 
                    "column": col['name'], 
                    "type": "column",
                    "description": col['description']
                })
                
        if not texts:
            return np.array([]), []
            
        print(f"Generating embeddings for {len(texts)} schema elements via Jina API...")
        embeddings = self.generate_embeddings(texts)
        return embeddings, metadata

# Global
_embedding_manager = None
def get_embedding_manager():
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager
