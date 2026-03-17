"""
Vector Store — FAISS-based local vector store for knowledge retrieval.

Provides document ingestion, embedding generation (via Google's embedding model),
and semantic search for the RAG pipeline used by the Tutor agent.
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path


# ---------------------------------------------------------------------------
# Embedding generation (uses Google's embedding model or falls back to TF-IDF)
# ---------------------------------------------------------------------------

def _generate_embeddings_google(texts: List[str]) -> Optional[List[List[float]]]:
    """Generate embeddings using Google's text-embedding model."""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        
        embeddings = []
        # Process in batches of 20
        for i in range(0, len(texts), 20):
            batch = texts[i:i + 20]
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=batch,
            )
            embeddings.extend(result['embedding'] if isinstance(result['embedding'][0], list) else [result['embedding']])
        
        return embeddings
    except Exception as e:
        print(f"[VectorStore] Google embeddings failed: {e}")
        return None


def _generate_embeddings_tfidf(texts: List[str], dim: int = 384) -> List[List[float]]:
    """
    Fallback: generate simple TF-IDF-inspired embeddings.
    Not as good as neural embeddings but works without API keys.
    """
    import re
    import math
    
    # Build vocabulary
    vocab: Dict[str, int] = {}
    doc_freqs: Dict[str, int] = {}
    tokenized = []
    
    for text in texts:
        tokens = set(re.findall(r'\b\w+\b', text.lower()))
        tokenized.append(tokens)
        for token in tokens:
            if token not in vocab:
                vocab[token] = len(vocab)
            doc_freqs[token] = doc_freqs.get(token, 0) + 1
    
    n_docs = len(texts)
    embeddings = []
    
    for tokens in tokenized:
        vec = [0.0] * min(len(vocab), dim)
        for token in tokens:
            idx = vocab.get(token, -1)
            if idx >= 0 and idx < dim:
                idf = math.log(n_docs / (1 + doc_freqs.get(token, 0)))
                vec[idx] = idf
        
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        vec = [v / norm for v in vec]
        
        # Pad or truncate to dim
        if len(vec) < dim:
            vec.extend([0.0] * (dim - len(vec)))
        else:
            vec = vec[:dim]
        
        embeddings.append(vec)
    
    return embeddings


# ---------------------------------------------------------------------------
# FAISS Vector Store
# ---------------------------------------------------------------------------

class VectorStore:
    """Simple FAISS-based vector store for educational content retrieval."""
    
    def __init__(self, store_path: str = "knowledge_store"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        self.documents: List[Dict[str, Any]] = []
        self.index = None
        self.dimension = 768  # Default embedding dimension
        self._faiss_available = False
        
        try:
            import faiss
            self._faiss_available = True
        except ImportError:
            print("[VectorStore] FAISS not installed. Using cosine similarity fallback.")
        
        # Load existing store if available
        self._load_store()
    
    def _load_store(self):
        """Load persisted documents and index."""
        docs_path = self.store_path / "documents.json"
        if docs_path.exists():
            try:
                with open(docs_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            except Exception:
                self.documents = []
        
        if self._faiss_available:
            index_path = self.store_path / "faiss.index"
            if index_path.exists():
                try:
                    import faiss
                    self.index = faiss.read_index(str(index_path))
                    self.dimension = self.index.d
                except Exception:
                    self.index = None
    
    def _save_store(self):
        """Persist documents and index to disk."""
        docs_path = self.store_path / "documents.json"
        with open(docs_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2)
        
        if self._faiss_available and self.index is not None:
            import faiss
            faiss.write_index(self.index, str(self.store_path / "faiss.index"))
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the vector store.
        
        Each document should have 'content' and optionally 'title', 'topic', 'source'.
        """
        if not documents:
            return
        
        texts = [doc.get("content", "") for doc in documents]
        
        # Generate embeddings
        embeddings = _generate_embeddings_google(texts)
        if embeddings is None:
            embeddings = _generate_embeddings_tfidf(texts)
        
        if not embeddings:
            return
        
        self.dimension = len(embeddings[0])
        
        import numpy as np
        embedding_array = np.array(embeddings, dtype=np.float32)
        
        if self._faiss_available:
            import faiss
            if self.index is None:
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine after normalize)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embedding_array)
            self.index.add(embedding_array)
        
        # Store documents with their embeddings
        for i, doc in enumerate(documents):
            doc_id = hashlib.md5(doc.get("content", "").encode()).hexdigest()[:12]
            self.documents.append({
                "id": doc_id,
                "content": doc.get("content", ""),
                "title": doc.get("title", ""),
                "topic": doc.get("topic", ""),
                "source": doc.get("source", ""),
                "embedding": embeddings[i] if not self._faiss_available else None,
            })
        
        self._save_store()
        print(f"[VectorStore] Added {len(documents)} documents. Total: {len(self.documents)}")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: Search query text.
            top_k: Number of results to return.
        
        Returns:
            List of dicts with 'content', 'title', 'topic', 'score'.
        """
        if not self.documents:
            return []
        
        # Generate query embedding
        query_embeddings = _generate_embeddings_google([query])
        if query_embeddings is None:
            query_embeddings = _generate_embeddings_tfidf([query], dim=self.dimension)
        
        if not query_embeddings:
            return []
        
        import numpy as np
        query_vec = np.array([query_embeddings[0]], dtype=np.float32)
        
        if self._faiss_available and self.index is not None:
            import faiss
            faiss.normalize_L2(query_vec)
            scores, indices = self.index.search(query_vec, min(top_k, len(self.documents)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    doc = self.documents[idx]
                    results.append({
                        "content": doc["content"],
                        "title": doc.get("title", ""),
                        "topic": doc.get("topic", ""),
                        "score": float(score),
                    })
            return results
        else:
            # Fallback: brute-force cosine similarity
            results = []
            for doc in self.documents:
                if doc.get("embedding"):
                    doc_vec = np.array(doc["embedding"], dtype=np.float32)
                    q = query_vec.flatten()
                    d = doc_vec.flatten()
                    
                    # Ensure same dimension
                    min_dim = min(len(q), len(d))
                    q = q[:min_dim]
                    d = d[:min_dim]
                    
                    norm_q = np.linalg.norm(q) or 1.0
                    norm_d = np.linalg.norm(d) or 1.0
                    similarity = float(np.dot(q, d) / (norm_q * norm_d))
                    
                    results.append({
                        "content": doc["content"],
                        "title": doc.get("title", ""),
                        "topic": doc.get("topic", ""),
                        "score": similarity,
                    })
            
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
    
    def ingest_text_file(self, filepath: str, topic: str = "", chunk_size: int = 500):
        """Ingest a text file by chunking it into documents."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[VectorStore] Could not read {filepath}: {e}")
            return
        
        # Split into chunks
        words = content.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append({
                "content": chunk,
                "title": os.path.basename(filepath),
                "topic": topic,
                "source": filepath,
            })
        
        if chunks:
            self.add_documents(chunks)
    
    @property
    def size(self) -> int:
        return len(self.documents)


# Singleton
_store_instance: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get the singleton vector store instance."""
    global _store_instance
    if _store_instance is None:
        store_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_store")
        _store_instance = VectorStore(store_path=store_dir)
        
        # Seed with some built-in educational content if empty
        if _store_instance.size == 0:
            _seed_default_content(_store_instance)
    
    return _store_instance


def _seed_default_content(store: VectorStore):
    """Seed the vector store with foundational CS/Science knowledge."""
    documents = [
        {
            "content": "A linked list is a linear data structure where elements are stored in nodes. Each node contains data and a pointer to the next node. Types include singly linked list, doubly linked list, and circular linked list. Time complexity for insertion at head is O(1), at tail is O(n) for singly linked list. Searching is O(n) since no random access.",
            "title": "Linked Lists",
            "topic": "DSA",
        },
        {
            "content": "A binary search tree (BST) is a binary tree where the left subtree contains nodes with keys less than the root, and the right subtree contains keys greater than the root. Search, insert, delete are O(h) where h is tree height. Balanced BSTs like AVL trees and Red-Black trees ensure O(log n) operations.",
            "title": "Binary Search Trees",
            "topic": "DSA",
        },
        {
            "content": "Sorting algorithms: Bubble Sort O(n²), Selection Sort O(n²), Insertion Sort O(n²), Merge Sort O(n log n), Quick Sort O(n log n) average, Heap Sort O(n log n). Merge Sort is stable and uses O(n) extra space. Quick Sort is in-place but not stable. For nearly sorted data, Insertion Sort performs best.",
            "title": "Sorting Algorithms",
            "topic": "DSA",
        },
        {
            "content": "Object-Oriented Programming has four pillars: Encapsulation (bundling data and methods), Abstraction (hiding complexity), Inheritance (child classes inherit from parent), and Polymorphism (one interface, multiple implementations). Runtime polymorphism uses virtual functions and dynamic dispatch.",
            "title": "OOP Pillars",
            "topic": "OOP",
        },
        {
            "content": "The OSI model has 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application. TCP/IP model simplifies to 4 layers: Network Access, Internet, Transport, Application. TCP provides reliable ordered delivery; UDP provides best-effort unreliable delivery.",
            "title": "OSI and TCP/IP Models",
            "topic": "Computer Networks",
        },
        {
            "content": "SQL normalization reduces redundancy. 1NF: atomic values, unique rows. 2NF: 1NF + no partial dependencies. 3NF: 2NF + no transitive dependencies. BCNF: every determinant is a candidate key. ACID properties: Atomicity, Consistency, Isolation, Durability ensure reliable transactions.",
            "title": "Database Normalization",
            "topic": "DBMS",
        },
        {
            "content": "Newton's laws of motion: First law (inertia) - an object stays at rest or in uniform motion unless acted upon by a force. Second law F=ma - force equals mass times acceleration. Third law - every action has an equal and opposite reaction. These form the foundation of classical mechanics.",
            "title": "Newton's Laws",
            "topic": "Physics",
        },
        {
            "content": "Calculus fundamentals: Derivatives measure the rate of change. The derivative of x^n is n*x^(n-1). The chain rule: d/dx[f(g(x))] = f'(g(x)) * g'(x). Integration is the reverse of differentiation. The fundamental theorem of calculus connects derivatives and integrals.",
            "title": "Calculus Basics",
            "topic": "Mathematics",
        },
        {
            "content": "Graph algorithms: BFS (Breadth-First Search) uses a queue and explores level by level, O(V+E). DFS (Depth-First Search) uses a stack/recursion, O(V+E). Dijkstra's algorithm finds shortest paths from a source in weighted graphs with non-negative edges, O((V+E)log V) with a priority queue.",
            "title": "Graph Algorithms",
            "topic": "DSA",
        },
        {
            "content": "Dynamic Programming solves problems by breaking them into overlapping subproblems and storing results (memoization or tabulation). Classic problems: Fibonacci, knapsack, longest common subsequence, edit distance, coin change. Key: identify optimal substructure and overlapping subproblems.",
            "title": "Dynamic Programming",
            "topic": "DSA",
        },
    ]
    
    store.add_documents(documents)
    print(f"[VectorStore] Seeded with {len(documents)} default educational documents.")
