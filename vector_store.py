# vector_store.py
#
# PURPOSE:
#   Lightweight vector store backed by SQLite.
#   Loads all embeddings from disk into memory once, then answers nearest-
#   neighbour queries via cosine similarity computed in NumPy.
#
# DESIGN NOTE:
#   For ~50–500 categories a full in-memory scan is instant (<1 ms).
#   If your catalogue grows to tens of thousands of categories you would
#   replace this module with pgvector, Chroma, or Pinecone — the
#   classify.py interface stays the same.

import json
import sqlite3

import numpy as np

DB_PATH = "nielsen_embeddings.db"


class VectorStore:
    """
    Loads all category embeddings from SQLite on initialisation and exposes
    a `search` method that returns the top-k most similar categories for any
    query vector.
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        """
        Load every row from the database into three parallel NumPy arrays so
        that cosine similarity can be vectorised across the whole catalogue in
        one matrix multiplication.
        """
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT id, text, embedding FROM category_embeddings"
        ).fetchall()
        conn.close()

        if not rows:
            raise RuntimeError(
                f"No embeddings found in '{db_path}'. "
                "Run embed_and_index.py first."
            )

        self.ids: list[str] = []
        self.texts: list[str] = []
        raw_vectors: list[list[float]] = []

        for row_id, text, embedding_json in rows:
            self.ids.append(row_id)
            self.texts.append(text)
            raw_vectors.append(json.loads(embedding_json))

        # Stack into a 2-D matrix: shape (n_categories, embedding_dim)
        # Then L2-normalise each row so dot product == cosine similarity
        self.matrix = np.array(raw_vectors, dtype=np.float32)
        norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
        self.matrix = self.matrix / norms  # unit vectors

        print(f"VectorStore: loaded {len(self.ids)} categories from '{db_path}'.")

    def search(
        self, query_vector: list[float], top_k: int = 3
    ) -> list[dict]:
        """
        Return the top_k most similar categories to `query_vector`.

        Parameters
        ----------
        query_vector : list[float]
            The embedding of the product description being classified.
        top_k : int
            Number of candidate categories to return (default 3).

        Returns
        -------
        list of dicts with keys: id, text, score
            Sorted descending by cosine similarity score.
        """
        # Normalise the query vector to a unit vector
        q = np.array(query_vector, dtype=np.float32)
        q = q / np.linalg.norm(q)

        # Cosine similarity = dot product when both vectors are unit length.
        # Shape: (n_categories,)
        scores = self.matrix @ q

        # argsort ascending, then flip to get top scores first
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            {
                "id": self.ids[i],
                "text": self.texts[i],
                "score": float(scores[i]),  # convert np.float32 → Python float
            }
            for i in top_indices
        ]
