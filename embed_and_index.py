# embed_and_index.py
#
# PURPOSE:
#   Build the RAG knowledge base by embedding every Nielsen category and
#   storing the resulting vectors in a local SQLite database.
#   Run this ONCE before you run classify.py.
#
# HOW IT WORKS:
#   1. Read the list of Nielsen categories from nielsen_categories.py
#   2. Send all category text strings to the OpenAI embedding API in one batch
#   3. Persist each (id, text, embedding) row in SQLite as a JSON-encoded blob
#
# WHY SQLITE?
#   For a catalogue of ~50-500 categories, SQLite is perfectly adequate.
#   We do a full-table scan at query time and rank by cosine similarity in
#   Python — no vector DB required.  For 100k+ categories, swap in pgvector
#   or Chroma.

import json
import sqlite3

import os
os.environ["HF_HUB_VERBOSITY"] = "error"

from sentence_transformers import SentenceTransformer

from nielsen_categories import NIELSEN_CATEGORIES

# ── Configuration ─────────────────────────────────────────────────────────────

DB_PATH = "nielsen_embeddings.db"           # SQLite file created in current dir
EMBEDDING_MODEL = "all-MiniLM-L6-v2"        # local embedding model, 384 dimensions
BATCH_SIZE = 100  # Process in batches to avoid memory issues

# ── SentenceTransformer model ─────────────────────────────────────────────────

# Load the model once at module import time.
model = SentenceTransformer(EMBEDDING_MODEL)


def create_table(conn: sqlite3.Connection) -> None:
    """
    Create the embeddings table if it doesn't already exist.

    Schema:
      id        TEXT PRIMARY KEY  — matches the id field in NIELSEN_CATEGORIES
      text      TEXT              — the full "Dept > Cat > Subcat" path we embedded
      embedding TEXT              — JSON array of floats (the vector)
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS category_embeddings (
            id        TEXT PRIMARY KEY,
            text      TEXT NOT NULL,
            embedding TEXT NOT NULL   -- stored as JSON array, e.g. [0.12, -0.34, ...]
        )
        """
    )
    conn.commit()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using the local SentenceTransformer model.

    The model returns embeddings in the same order as the input texts, so we can
    zip them safely with our category list.
    """
    embeddings = model.encode(texts, convert_to_numpy=False)
    return [embedding.tolist() for embedding in embeddings]


def build_index() -> None:
    """
    Main entry point.  Embeds all Nielsen categories and upserts them into
    the SQLite database.  Safe to re-run — existing rows are replaced.
    """
    print(f"Connecting to SQLite database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    # Check how many categories are already indexed so we can skip if up to date
    already_indexed = conn.execute(
        "SELECT COUNT(*) FROM category_embeddings"
    ).fetchone()[0]

    if already_indexed == len(NIELSEN_CATEGORIES):
        print(
            f"Index is already up to date ({already_indexed} categories). "
            "Delete the .db file and re-run to force a rebuild."
        )
        conn.close()
        return

    print(f"Embedding {len(NIELSEN_CATEGORIES)} Nielsen categories …")

    # Process in batches to stay well under the API payload limit
    for batch_start in range(0, len(NIELSEN_CATEGORIES), BATCH_SIZE):
        batch = NIELSEN_CATEGORIES[batch_start : batch_start + BATCH_SIZE]
        texts = [cat["text"] for cat in batch]

        print(
            f"  Calling API for rows {batch_start + 1}–"
            f"{batch_start + len(batch)} …"
        )
        vectors = get_embeddings(texts)

        # Upsert each row: INSERT OR REPLACE handles re-runs cleanly
        rows = [
            (cat["id"], cat["text"], json.dumps(vector))
            for cat, vector in zip(batch, vectors)
        ]
        conn.executemany(
            "INSERT OR REPLACE INTO category_embeddings (id, text, embedding) "
            "VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()

    total = conn.execute(
        "SELECT COUNT(*) FROM category_embeddings"
    ).fetchone()[0]
    print(f"\nDone — {total} category embeddings stored in '{DB_PATH}'.")
    conn.close()


if __name__ == "__main__":
    build_index()
