import os
import json
import numpy as np

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), 'knowledge')
INDEX_FILE = os.path.join(KNOWLEDGE_DIR, '_index.json')
EMBEDDINGS_FILE = os.path.join(KNOWLEDGE_DIR, '_embeddings.npy')

class SearchEngine:
    def __init__(self):
        self.chunks = []
        self.embeddings = None
        self._load_index()

    def _load_index(self):
        if not os.path.exists(INDEX_FILE) or not os.path.exists(EMBEDDINGS_FILE):
            print(f"Warning: Index files not found in {KNOWLEDGE_DIR}. Please run build_index.py first.")
            return

        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
            
        self.embeddings = np.load(EMBEDDINGS_FILE)
        print(f"Loaded {len(self.chunks)} chunks into search engine.")

    def search(self, query_embedding, top_k=5):
        if self.embeddings is None or len(self.chunks) == 0:
            return []

        # Cosine similarity
        query_vec = np.array(query_embedding, dtype=np.float32)
        
        # Normalize vectors for cosine similarity
        norm_query = np.linalg.norm(query_vec)
        if norm_query > 0:
            query_vec = query_vec / norm_query
            
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1e-10
        normalized_embeddings = self.embeddings / norms
        
        similarities = np.dot(normalized_embeddings, query_vec)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            chunk = self.chunks[idx].copy()
            chunk['relevance_score'] = round(score, 4)
            results.append(chunk)
            
        return results

# Singleton instance
engine = SearchEngine()

def search_handbooks(query_embedding, top_k=5):
    return engine.search(query_embedding, top_k)
