"""
Embedding Manager - Generates and manages embeddings for schema elements using Qdrant
"""
import os
import uuid
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()


class EmbeddingManager:
    """Manages embeddings and vector similarity search using Qdrant"""
    
    def __init__(self):
        self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Determine vector DB path - prefer backend/vector_store
        env_path = os.getenv("VECTOR_DB_PATH", "./vector_store")
        
        # Check standard locations
        possible_paths = [
            "backend/vector_store",
            "vector_store",
            env_path
        ]
        
        self.vector_db_path = env_path # Default fallback
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                self.vector_db_path = path
                break
                
        self.collection_name = "schema_embeddings"
        
        # Load embedding model
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize Qdrant client (in-memory mode with persistence)
        os.makedirs(self.vector_db_path, exist_ok=True)
        self.client = QdrantClient(path=self.vector_db_path)
        
        print(f"Qdrant client initialized with local storage at: {self.vector_db_path}")
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings (shape: [len(texts), embedding_dim])
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return np.array(embeddings, dtype=np.float32)
    
    def create_index(
        self, 
        embeddings: np.ndarray, 
        metadata: List[Dict[str, Any]]
    ):
        """
        Create a Qdrant collection from embeddings
        
        Args:
            embeddings: Numpy array of embeddings
            metadata: List of metadata dictionaries (one per embedding)
        """
        if len(embeddings) == 0:
            raise ValueError("Cannot create index with empty embeddings")
        
        # Recreate collection (delete if exists)
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Deleted existing collection: {self.collection_name}")
        except Exception:
            pass  # Collection doesn't exist
        
        # Create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedding_dim,
                distance=Distance.COSINE
            )
        )
        
        # Prepare points for insertion
        points = []
        for idx, (embedding, meta) in enumerate(zip(embeddings, metadata)):
            point = PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload=meta
            )
            points.append(point)
        
        # Insert points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        print(f"Created Qdrant collection '{self.collection_name}' with {len(points)} vectors")
    
    def search(
        self, 
        query_text: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar items using vector similarity
        
        Args:
            query_text: Query string
            top_k: Number of results to return
            
        Returns:
            List of results with metadata and similarity scores
        """
        # Check if collection exists
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == self.collection_name for c in collections):
                raise ValueError(f"Collection '{self.collection_name}' not found. Run initialization first.")
        except Exception as e:
            raise ValueError(f"Error accessing Qdrant: {e}")
        
        # Generate query embedding
        query_embedding = self.model.encode([query_text])[0]
        
        # Search in Qdrant using query_points (new API)
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),
            limit=top_k
        ).points
        
        # Prepare results
        results = []
        for i, result in enumerate(search_results):
            results.append({
                "rank": i + 1,
                "score": result.score,
                "similarity": result.score,  # Cosine similarity is already 0-1
                "metadata": result.payload
            })
        
        return results
    
    def save_index(self, index_name: str = "schema_index"):
        """
        Save method for compatibility (Qdrant auto-persists)
        
        Args:
            index_name: Name for the saved index files (not used, for compatibility)
        """
        # Qdrant with path parameter automatically persists data
        print(f"Qdrant collection persisted automatically to {self.vector_db_path}")
    
    def load_index(self, index_name: str = "schema_index") -> bool:
        """
        Load Qdrant collection (check if it exists)
        
        Args:
            index_name: Name of the saved index files (not used, for compatibility)
            
        Returns:
            True if collection exists and is loaded, False otherwise
        """
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if collection_exists:
                # Get collection info
                collection_info = self.client.get_collection(self.collection_name)
                print(f"Loaded Qdrant collection '{self.collection_name}' with {collection_info.points_count} vectors")
                return True
            else:
                print(f"Collection '{self.collection_name}' not found")
                return False
        
        except Exception as e:
            print(f"Error loading Qdrant collection: {e}")
            return False
    
    def embed_schema(self, schema: Dict[str, Any]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Generate embeddings for all schema elements
        
        Args:
            schema: Schema dictionary from SchemaIntrospector
            
        Returns:
            Tuple of (embeddings array, metadata list)
        """
        texts = []
        metadata = []
        
        # Embed each column
        for table_name, table_info in schema['tables'].items():
            for column in table_info['columns']:
                # Create rich text representation
                text = self._create_column_text(
                    table_name, 
                    column['name'], 
                    column['description'],
                    column['type']
                )
                
                texts.append(text)
                metadata.append({
                    "type": "column",
                    "table": table_name,
                    "column": column['name'],
                    "data_type": column['type'],
                    "description": column['description'],
                    "table_description": table_info['description']
                })
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        return embeddings, metadata
    
    def _create_column_text(
        self, 
        table_name: str, 
        column_name: str, 
        description: str,
        data_type: str
    ) -> str:
        """Create rich text representation for a column"""
        parts = [
            f"Table: {table_name}",
            f"Column: {column_name}",
            f"Type: {data_type}",
            f"Description: {description}"
        ]
        return " | ".join(parts)


# Global instance
_embedding_manager = None


def get_embedding_manager() -> EmbeddingManager:
    """Get or create global embedding manager instance"""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager
