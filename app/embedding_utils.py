"""
Embedding Utilities for Government AI API
This module provides functions for creating embeddings using OpenAI.
"""

import os
from typing import List, Union
import openai
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EmbeddingService:
    """Service for creating and managing embeddings"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding service
        
        Args:
            model: OpenAI embedding model to use
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            # Clean and prepare text
            text = text.strip()
            if not text:
                raise ValueError("Empty text cannot be embedded")
            
            # Create embedding
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Created embedding for text of length {len(text)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Clean texts
            cleaned_texts = [text.strip() for text in texts if text.strip()]
            
            if not cleaned_texts:
                return []
            
            # OpenAI can handle up to 2048 embeddings per request
            batch_size = 2048
            all_embeddings = []
            
            for i in range(0, len(cleaned_texts), batch_size):
                batch = cleaned_texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Created embeddings for batch {i//batch_size + 1}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {str(e)}")
            raise
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def find_similar_texts(
        self,
        query_embedding: List[float],
        text_embeddings: List[List[float]],
        texts: List[str],
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[tuple]:
        """
        Find texts most similar to a query based on embeddings
        
        Args:
            query_embedding: Embedding of the query text
            text_embeddings: List of embeddings to search through
            texts: Original texts corresponding to embeddings
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of tuples (text, similarity_score) sorted by similarity
        """
        similarities = []
        
        for i, text_embedding in enumerate(text_embeddings):
            similarity = self.cosine_similarity(query_embedding, text_embedding)
            
            if similarity >= threshold:
                similarities.append((texts[i], similarity))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        return similarities[:top_k]

# Utility functions for direct use
def create_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Convenience function to create a single embedding
    
    Args:
        text: Text to embed
        model: OpenAI embedding model to use
        
    Returns:
        Embedding vector
    """
    service = EmbeddingService(model=model)
    return service.create_embedding(text)

def create_embeddings_batch(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """
    Convenience function to create multiple embeddings
    
    Args:
        texts: List of texts to embed
        model: OpenAI embedding model to use
        
    Returns:
        List of embedding vectors
    """
    service = EmbeddingService(model=model)
    return service.create_embeddings_batch(texts)

def semantic_search(
    query: str,
    documents: List[str],
    top_k: int = 5,
    threshold: float = 0.7,
    model: str = "text-embedding-3-small"
) -> List[tuple]:
    """
    Perform semantic search on a list of documents
    
    Args:
        query: Search query
        documents: List of documents to search through
        top_k: Number of top results to return
        threshold: Minimum similarity threshold
        model: OpenAI embedding model to use
        
    Returns:
        List of tuples (document, similarity_score) sorted by relevance
    """
    service = EmbeddingService(model=model)
    
    # Create embeddings for query and documents
    query_embedding = service.create_embedding(query)
    doc_embeddings = service.create_embeddings_batch(documents)
    
    # Find similar documents
    results = service.find_similar_texts(
        query_embedding,
        doc_embeddings,
        documents,
        top_k=top_k,
        threshold=threshold
    )
    
    return results