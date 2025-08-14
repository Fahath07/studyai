"""
Embedding and Retrieval Module for StudyMate
Handles text embedding generation and FAISS-based semantic search
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingRetriever:
    """
    Handles embedding generation and semantic retrieval using SentenceTransformers and FAISS.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding retriever.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.index = None
        self.chunks = []
        self.embeddings = None
        
        logger.info(f"Initializing EmbeddingRetriever with model: {model_name}")
        self._load_model()
    
    def _load_model(self):
        """Load the SentenceTransformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            raise
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> np.ndarray:
        """
        Create embeddings for all text chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            
        Returns:
            np.ndarray: Array of embeddings
        """
        if not chunks:
            logger.warning("No chunks provided for embedding creation")
            return np.array([])
        
        self.chunks = chunks
        texts = [chunk["text"] for chunk in chunks]
        
        logger.info(f"Creating embeddings for {len(texts)} chunks...")
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            self.embeddings = embeddings
            logger.info(f"Successfully created embeddings with shape: {embeddings.shape}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def build_faiss_index(self, embeddings: np.ndarray = None):
        """
        Build FAISS index for fast similarity search.
        
        Args:
            embeddings: Optional embeddings array. Uses self.embeddings if not provided.
        """
        if embeddings is None:
            embeddings = self.embeddings
        
        if embeddings is None or len(embeddings) == 0:
            logger.error("No embeddings available for index building")
            return
        
        try:
            # Get embedding dimension
            dimension = embeddings.shape[1]
            
            # Create FAISS index (L2 distance)
            self.index = faiss.IndexFlatL2(dimension)
            
            # Add embeddings to index
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors, dimension {dimension}")
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {str(e)}")
            raise
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a given query.
        
        Args:
            query: User's question/query
            top_k: Number of top chunks to retrieve
            
        Returns:
            List[Dict]: List of relevant chunks with similarity scores
        """
        if not query.strip():
            logger.warning("Empty query provided")
            return []
        
        if self.index is None or len(self.chunks) == 0:
            logger.warning("No index or chunks available for retrieval")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            
            # Search in FAISS index
            distances, indices = self.index.search(
                query_embedding.astype('float32'), 
                min(top_k, len(self.chunks))
            )
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.chunks):  # Valid index
                    chunk = self.chunks[idx].copy()
                    chunk["similarity_score"] = float(distance)
                    chunk["rank"] = i + 1
                    results.append(chunk)
            
            logger.info(f"Retrieved {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return []
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current retrieval system.
        
        Returns:
            Dict: Statistics about embeddings and index
        """
        stats = {
            "model_name": self.model_name,
            "total_chunks": len(self.chunks),
            "index_built": self.index is not None,
            "embedding_dimension": None,
            "index_size": 0
        }
        
        if self.embeddings is not None:
            stats["embedding_dimension"] = self.embeddings.shape[1]
        
        if self.index is not None:
            stats["index_size"] = self.index.ntotal
        
        return stats


def initialize_retrieval_system(chunks: List[Dict[str, Any]], 
                              model_name: str = "all-MiniLM-L6-v2") -> EmbeddingRetriever:
    """
    Initialize the complete retrieval system with chunks.
    
    Args:
        chunks: List of text chunks with metadata
        model_name: SentenceTransformer model name
        
    Returns:
        EmbeddingRetriever: Initialized retriever ready for queries
    """
    logger.info("Initializing retrieval system...")
    
    # Create retriever
    retriever = EmbeddingRetriever(model_name=model_name)
    
    if not chunks:
        logger.warning("No chunks provided - retrieval system will be empty")
        return retriever
    
    # Create embeddings
    embeddings = retriever.create_embeddings(chunks)
    
    # Build FAISS index
    retriever.build_faiss_index(embeddings)
    
    logger.info("Retrieval system initialization complete")
    return retriever


def format_retrieved_chunks(chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks for display or LLM input.
    
    Args:
        chunks: List of retrieved chunks with metadata
        
    Returns:
        str: Formatted text combining all chunks
    """
    if not chunks:
        return ""
    
    formatted_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        source_info = f"[Source: {chunk['filename']}, Section {chunk['chunk_index'] + 1}]"
        chunk_text = chunk['text']
        
        formatted_part = f"Context {i}:\n{source_info}\n{chunk_text}\n"
        formatted_parts.append(formatted_part)
    
    return "\n".join(formatted_parts)


def get_chunk_sources(chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract source information from retrieved chunks.
    
    Args:
        chunks: List of retrieved chunks
        
    Returns:
        List[Dict]: List of source information dictionaries
    """
    sources = []
    
    for chunk in chunks:
        source = {
            "filename": chunk.get("filename", "Unknown"),
            "section": f"Section {chunk.get('chunk_index', 0) + 1}",
            "preview": chunk.get("text", "")[:200] + "..." if len(chunk.get("text", "")) > 200 else chunk.get("text", "")
        }
        sources.append(source)
    
    return sources
