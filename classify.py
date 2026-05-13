# classify.py
#
# PURPOSE:
#   Classify grocery product descriptions into Nielsen taxonomy categories
#   using a Retrieval-Augmented Generation (RAG) pipeline.
#
# PIPELINE OVERVIEW:
#   1. Embed the product description  →  query vector
#   2. Search SQLite vector store     →  top-k nearest Nielsen categories
#   3. Inject those categories into an LLM prompt  →  the LLM picks one
#
# WHY RAG PREVENTS HALLUCINATION:
#   Without RAG the LLM might invent category names like "Refrigerated
#   Beverages" that don't exist in Nielsen.  By providing ONLY the retrieved
#   candidates in the prompt and instructing the model to pick from that list,
#   the output is always a valid Nielsen path.

import csv
import json
import os
import requests

from sentence_transformers import SentenceTransformer

from vector_store import VectorStore

# ── Configuration ─────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "all-MiniLM-L6-v2"        # same model used when building index
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama's default API endpoint
CHAT_MODEL = "llama2"                      # Ollama model name
TOP_K = 3          # number of candidate categories retrieved per product
TEMPERATURE = 0.0  # 0 = fully deterministic; we want consistent classification

# ── Models (shared across calls) ─────────────────────────────────────────────

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Load the vector store once at module import time.
# The constructor reads all rows from SQLite into memory (fast for <500 cats).
store = VectorStore()


# ── Core functions ────────────────────────────────────────────────────────────

def embed_product(product_name: str) -> list[float]:
    """
    Embed a single product description using the same model that was used to
    embed the Nielsen categories.  Using mismatched models would give garbage
    similarity scores.
    """
    embedding = embedding_model.encode([product_name], convert_to_numpy=False)[0]
    return embedding.tolist()


def build_prompt(product_name: str, candidates: list[dict]) -> str:
    """
    Construct the classification prompt.

    The candidates list (from the vector store) is formatted as a numbered
    list so the LLM can reference them unambiguously.  The instruction
    explicitly prohibits inventing new category names — this is the
    anti-hallucination constraint.
    """
    candidate_lines = "\n".join(
        f"  {i + 1}. {c['text']}  (similarity: {c['score']:.3f})"
        for i, c in enumerate(candidates)
    )

    return f"""You are a grocery product data specialist trained on the Nielsen taxonomy.

Your task is to classify the product below into EXACTLY ONE category from the
retrieved list.  These candidates were selected by semantic similarity search,
so the correct answer is almost certainly in the list.

Retrieved Nielsen categories (most relevant first):
{candidate_lines}

Product to classify: "{product_name}"

Rules:
  - Return ONLY the full category path (e.g. "Dairy > Milk & Cream > Fluid Milk")
  - Do NOT add any explanation, commentary, or introductory text
  - Do NOT modify, abbreviate, or combine category names
  - Do NOT invent a category that is not in the list above
  - If the product is ambiguous, choose the closest match

Category:"""


def classify_product(product_name: str) -> dict:
    """
    Full RAG pipeline for a single product.

    Returns a dict with:
      product    - the input string
      category   - the Nielsen path chosen by the LLM
      candidates - the top-k categories retrieved from the vector store
    """
    # ── Step 1: Embed the incoming product description ──────────────────────
    query_vector = embed_product(product_name)

    # ── Step 2: Retrieve the top-k most similar Nielsen categories (RAG) ────
    # This is the "retrieval" part of RAG.  The vector store returns the
    # Nielsen paths whose embeddings are closest in semantic space to the
    # product description.
    candidates = store.search(query_vector, top_k=TOP_K)

    # ── Step 3: Ask the LLM to pick one category from the retrieved list ────
    # Injecting the candidates into the prompt constrains the model's output
    # space — it cannot hallucinate categories that aren't in our taxonomy.
    prompt = build_prompt(product_name, candidates)

    # Call Ollama API
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": CHAT_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": TEMPERATURE}
        }
    )
    response.raise_for_status()
    result = response.json()
    chosen_category = result["response"].strip()

    chosen_category = extract_category_from_response(result["response"], candidates)

    return {
        "product": product_name,
        "category": chosen_category,
        "candidates": candidates,
    }


def extract_category_from_response(response_text: str, candidates: list[dict]) -> str:
    """Parse the LLM response and return the exact Nielsen category path."""
    cleaned = response_text.strip()

    # Prefer an exact match against the retrieved candidate paths.
    for candidate in candidates:
        if candidate["text"] in cleaned:
            return candidate["text"]

    # Fallback: return the last non-empty line, stripped of quotes.
    lines = [line.strip(' "\'') for line in cleaned.splitlines() if line.strip()]
    if lines:
        return lines[-1]

    return cleaned


def classify_batch(products: list[str], verbose: bool = False) -> list[dict]:
    """
    Classify a list of products, printing progress as we go.

    Parameters
    ----------
    products : list of product description strings
    verbose  : if True, also print the retrieved candidates for each product
    """
    results = []
    for product in products:
        result = classify_product(product)
        results.append(result)

        # Always print the final classification
        print(f"  {result['product']:<45} →  {result['category']}")

        # Optionally show what the vector search retrieved
        if verbose:
            for c in result["candidates"]:
                print(f"      candidate: {c['text']}  (score={c['score']:.3f})")

    return results

def save_results_csv(results: list[dict], path: str = "output.csv") -> None:
    """Write classification results to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["product", "category", "candidates"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "product": result["product"],
                    "category": result["category"],
                    "candidates": json.dumps(result["candidates"], ensure_ascii=False),
                }
            )

# ── Demo ──────────────────────────────────────────────────────────────────────

# A diverse set of products that tests category boundaries
TEST_PRODUCTS = [
    # Dairy
    "Organic 2% reduced fat milk, 1 gallon",
    "Land O'Lakes unsalted butter sticks",
    "Chobani plain Greek yogurt",
    "Tillamook sharp cheddar cheese block",
    "Large brown eggs, 12 count",
    # Meat
    "80/20 ground beef 1 lb",
    "Boneless skinless chicken breasts",
    "Oscar Mayer applewood smoked bacon",
    "Johnsonville original bratwurst",
    # Bakery
    "Nature's Own honey wheat sandwich bread",
    "Flour tortillas, burrito size 10 count",
    # Produce
    "Ripe bananas, bunch",
    "Fresh strawberries, 1 lb container",
    "Baby spinach leaves, 5 oz bag",
    # Canned & Packaged
    "Hunt's crushed tomatoes 28 oz can",
    "Bush's Best original baked beans",
    "Campbell's tomato soup, condensed",
    "Barilla spaghetti, 1 lb box",
    # Sauces
    "Prego traditional pasta sauce, 24 oz",
    "Heinz tomato ketchup, 32 oz",
    "Frank's RedHot original hot sauce",
    # Frozen
    "Bird's Eye steamfresh broccoli florets",
    "DiGiorno rising crust pepperoni pizza",
    # Beverages
    "Tropicana Pure Premium orange juice, 52 oz",
    "Folgers Classic Roast ground coffee, 30.5 oz",
    # Snacks
    "Lay's classic potato chips, 8 oz bag",
    "Nabisco Ritz crackers, original",
]

if __name__ == "__main__":
    print("=" * 70)
    print("Nielsen RAG Grocery Classifier")
    print("=" * 70)
    print(f"Model : {CHAT_MODEL} (via Ollama)")
    print(f"Top-K : {TOP_K} candidates retrieved per product")
    print("=" * 70)
    print()

    # Set verbose=True to see which candidates the vector search retrieved
    results = classify_batch(TEST_PRODUCTS, verbose=False)

    print()
    save_results_csv(results, path="output.csv")
    print("Classification complete.")
    print("Saved results to output.csv")
