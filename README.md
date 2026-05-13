# Nielsen RAG Grocery Classifier

A RAG (Retrieval-Augmented Generation) pipeline that classifies grocery
product descriptions into the Nielsen taxonomy using local SentenceTransformer
embeddings, a local SQLite vector store, and Ollama Llama2 for the final
classification step.

---

## How it works

```
Product name
    │
    ▼
[embed_product]  ──── SentenceTransformer (local) ────►  query vector
    │
    ▼
[VectorStore.search]  ──── cosine similarity vs SQLite ───►  top-3 Nielsen categories
    │
    ▼
[LLM prompt]  ── "pick one from this list" ──►  Ollama Llama2
    │
    ▼
Nielsen category path  (e.g. "Dairy > Milk & Cream > Fluid Milk")
```

### Why RAG prevents hallucination

Without RAG, an LLM might invent category names like `"Refrigerated
Beverages"` that don't exist in Nielsen. By:

1. Embedding the full Nielsen taxonomy once at build time (stored in SQLite)
2. Retrieving only the semantically closest categories at query time
3. Telling the LLM **"pick from this list only"** in the prompt

…the model's output space is constrained to valid Nielsen paths. It cannot
make up a category that isn't in the retrieved list.

### Key design decisions

| Decision | Reason |
|---|---|
| `all-MiniLM-L6-v2` for both index and query | Local embedding model; embedding model must match — mixing models produces meaningless similarity scores |
| SQLite for storage | No server needed; a full in-memory cosine scan is <1 ms for <500 categories |
| `temperature=0` for the LLM | Deterministic output — classification should be consistent across runs |
| Full path as embedded text (`"Dairy > Milk & Cream > Fluid Milk"`) | Richer context than just the leaf node gives better vector matches |
| Top-K = 3 candidates in prompt | Enough to handle ambiguous products; keeps the prompt short |

---

## What is SentenceTransformer?

SentenceTransformer is a Python library that converts text into fixed-size
numerical vectors called **embeddings**. Two pieces of text that mean similar
things will produce vectors that are close together in space; unrelated text
will produce vectors that are far apart.

This project uses the `all-MiniLM-L6-v2` model, which runs entirely on your
machine (no API calls, no cost). It is a small, fast model (22 MB) that maps
any sentence or phrase to a 384-dimensional vector.

**Why embeddings matter for classification:**
Without embeddings, matching "80/20 ground beef" to "Meat > Beef > Ground Beef"
would require exact keyword rules. With embeddings, the model understands that
"ground beef", "beef mince", and "hamburger meat" are semantically the same
thing and maps them all close to the same vector — so the similarity search
finds the right category even with varied or informal product descriptions.

The same model must be used to embed both the taxonomy at index time and the
product at query time. Mixing models produces meaningless similarity scores.

**What an embedding looks like (first 5 of 384 dimensions):**

| Dimension | "ground beef 1 lb" | "hamburger meat" | "oat milk 64 oz" |
|----------:|-------------------:|-----------------:|-----------------:|
| 1 | 0.0412 | 0.0398 | -0.2031 |
| 2 | -0.1837 | -0.1762 | 0.1454 |
| 3 | 0.2951 | 0.3014 | -0.0873 |
| 4 | 0.0129 | 0.0143 | 0.3192 |
| 5 | -0.0674 | -0.0701 | 0.0518 |
| … | … | … | … |
| 384 | -0.0623 | -0.0589 | 0.1247 |

Notice that "ground beef" and "hamburger meat" have nearly identical values
across every dimension — their vectors are close in space, so cosine similarity
returns a high score. "Oat milk" has very different values, so it scores low
against beef categories and high against dairy ones.

---

## What this repo includes

This project stores the full Nielsen taxonomy in SQLite, retrieves the
nearest category candidates via vector search, and asks a local Ollama Llama2
model to choose the best match.

## Project structure

```
nielsen_rag/
├── nielsen_categories.py   # Full Nielsen taxonomy (60 categories across 9 departments)
├── embed_and_index.py      # One-time build step: embeds taxonomy → SQLite
├── vector_store.py         # Loads SQLite into memory, exposes cosine similarity search
├── classify.py             # Main RAG pipeline + demo batch classifier
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Vector search explained

### Step 1 — Build time (`embed_and_index.py`)

Every Nielsen category path is converted to a vector once and stored in SQLite:

```
"Meat > Beef > Ground Beef"              → [0.041, -0.184, 0.295, ..., -0.062]
"Dairy > Milk & Cream > Fluid Milk"      → [0.203,  0.145, -0.087, ...,  0.124]
"Snacks > Crackers > ..."                → [...]
... 58 more rows
```

This only runs once. After that, the vectors sit in `nielsen_embeddings.db`
and are loaded into memory at query time.

### Step 2 — Query time (`classify.py`)

When you run `make query PRODUCT="ground beef 1 lb"`, the same model converts
your product into a vector:

```
"ground beef 1 lb" → [0.039, -0.178, 0.301, ..., -0.058]
```

### Step 3 — Cosine similarity (`vector_store.py`)

That query vector is compared against every stored category vector using
cosine similarity — measuring the angle between two vectors. An angle near 0°
means the two texts are semantically close; near 90° means unrelated.

**How the score is calculated (3-dimension example):**

```
"ground beef 1 lb"          A = [0.04, -0.18, 0.30]
"Meat > Beef > Ground Beef" B = [0.04, -0.18, 0.30]
```

**Step 1 — Dot product: multiply each pair of dimensions, then sum**

A dot product multiplies each pair of matching numbers from two vectors, then
adds all the results together. If two vectors have large positive numbers in
the same positions, those pairs multiply to large numbers and the sum gets
big — high score. If one is positive where the other is negative, they cancel
out — low score. This naturally rewards alignment between two vectors.

```
(0.04 × 0.04) + (-0.18 × -0.18) + (0.30 × 0.30)
= 0.0016 + 0.0324 + 0.0900
= 0.124
```

**Step 2 — Divide by the length of each vector**

This normalizes the result so the score is always between 0 and 1, regardless
of how large or small the numbers are:
```
cosine similarity = dot product / (length of A × length of B)
                  = 0.124 / (0.354 × 0.354)
                  = 0.91
```

**What the score means:**

| Score | Meaning |
|---|---|
| 1.0 | Vectors point in exactly the same direction (identical meaning) |
| 0.5 | Loosely related |
| 0.0 | Completely unrelated |

This is done for all 60 category vectors. The top 3 scores are returned and
sent to the LLM to pick the best match:

| Category | Similarity score |
|---|---|
| Meat > Beef > Ground Beef | 0.91 ✓ |
| Meat > Poultry > Fresh Chicken | 0.61 |
| Dairy > Milk & Cream > Fluid Milk | 0.22 |

### Why it works without keyword matching

The query `"hamburger meat"` never contains the word "beef" — but both phrases
were learned to mean similar things during training, so their vectors point in
nearly the same direction and cosine similarity catches that. A keyword search
would miss it entirely.

This project only searches the Nielsen taxonomy (60 categories), not your full
product catalogue. It embeds only the input product string at classification
time.

## Setup & usage

### Fresh setup (Make)

Run these commands in order for a clean first-time setup:

```bash
make install       # create .venv and install Python dependencies
make serve         # start Ollama server (keep this terminal open)
```

In a second terminal:

```bash
make download      # pull the llama2 model (one-time, ~3.8 GB)
make build-index   # embed Nielsen taxonomy into nielsen_embeddings.db (one-time)
make classify      # run the demo classifier and write output.csv
make query PRODUCT="oat milk 64 oz"  # classify a single product
make query PRODUCT="land o lakes butter"  # classify a single product
```

To shut down the Ollama server when you're done:

```bash
make stop          # kill the Ollama server process
```

---

### Manual setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
.venv/bin/pip install -r requirements.txt
```

### Makefile shortcuts

Once your repo is set up, you can use these common commands instead of
calling Python directly:

```bash
make install       # create venv and install dependencies
make build-index   # embed Nielsen categories into nielsen_embeddings.db
make classify      # run the classification demo and write output.csv
make query PRODUCT="oat milk 64 oz"  # classify a single product
make serve         # start the Ollama server
make stop          # stop the Ollama server
make download      # download the Llama2 model via Ollama
make list-models   # list installed Ollama models
make clean         # delete generated nielsen_embeddings.db
```

### 3. Install and start Ollama

Install Ollama on macOS with Homebrew:

```bash
brew install ollama
```

Start the Ollama server in the background:

```bash
ollama serve
```

Then, in a new terminal, download the Llama2 model:

```bash
ollama run llama2
```

(The first run will download the model; subsequent runs will use the cached version.)

### 4. Build the vector index (run once)

This embeds all 60 Nielsen categories and saves them to `nielsen_embeddings.db`.

```bash
.venv/bin/python embed_and_index.py
```

Expected output:
```
Connecting to SQLite database: nielsen_embeddings.db
Embedding 60 Nielsen categories …
  Calling API for rows 1–60 …
Done — 60 category embeddings stored in 'nielsen_embeddings.db'.
```

### 5. Run the classifier

```bash
.venv/bin/python classify.py
```

Expected output (abbreviated):
```
======================================================================
Nielsen RAG Grocery Classifier
======================================================================
Model : llama2 (via Ollama)
Top-K : 3 candidates retrieved per product
======================================================================

  Organic 2% reduced fat milk, 1 gallon           →  Dairy > Milk & Cream > Fluid Milk
  Land O'Lakes unsalted butter sticks              →  Dairy > Butter & Margarine > Butter
  80/20 ground beef 1 lb                           →  Meat > Beef > Ground Beef
  Prego traditional pasta sauce, 24 oz             →  Condiments & Sauces > Pasta Sauce > Tomato & Marinara Sauce
  ...
```

### Output file

Running `classify.py` also saves the full batch results to `output.csv` in the repository root.

The file contains these columns:
- `product` — input product description
- `category` — the chosen Nielsen category path
- `candidates` — the retrieved top-K candidate paths and similarity scores as JSON text

Example `output.csv` rows:

| product | category | candidates |
|---|---|---|
| Organic 2% reduced fat milk, 1 gallon | Dairy > Milk & Cream > Fluid Milk | `[{"id":"dairy_milk","text":"Dairy > Milk & Cream > Fluid Milk","score":0.912}, ...]` |
| Land O'Lakes unsalted butter sticks | Dairy > Butter & Margarine > Butter | `[{"id":"dairy_butter","text":"Dairy > Butter & Margarine > Butter","score":0.887}, ...]` |
| Nabisco Ritz crackers, original | Snacks > Crackers > Crackers & Crispbreads | `[{"id":"snacks_crackers","text":"Snacks > Crackers > Crackers & Crispbreads","score":0.879}, ...]` |

Open `output.csv` in Excel, Numbers, VS Code, or any CSV viewer.

### 5. Use in your own code

```python
from classify import classify_product

result = classify_product("Oat milk, original, 64 oz")
print(result["category"])
# → Dairy > Refrigerated Alternative Milk > Almond, Oat & Soy Milk

# Full result dict
# {
#   "product": "Oat milk, original, 64 oz",
#   "category": "Dairy > Refrigerated Alternative Milk > Almond, Oat & Soy Milk",
#   "candidates": [
#     {"id": "dairy_alt_milk", "text": "...", "score": 0.891},
#     {"id": "dairy_fluid_milk", ...},
#     {"id": "bev_juice", ...}
#   ]
# }
```

---

## Verbose mode (see retrieved candidates)

Set `verbose=True` in `classify_batch()` to inspect what the vector search
retrieved before the LLM made its decision:

```python
classify_batch(["Oat milk, 64 oz"], verbose=True)
```

```
  Oat milk, 64 oz                                  →  Dairy > Refrigerated Alternative Milk > Almond, Oat & Soy Milk
      candidate: Dairy > Refrigerated Alternative Milk > Almond, Oat & Soy Milk  (score=0.891)
      candidate: Dairy > Milk & Cream > Fluid Milk  (score=0.801)
      candidate: Beverages > Juice > Refrigerated Juice  (score=0.723)
```

---

## Extending the taxonomy

Add more categories to `NIELSEN_CATEGORIES` in `nielsen_categories.py`, then
delete `nielsen_embeddings.db` and re-run `embed_and_index.py`.

```bash
rm nielsen_embeddings.db
python embed_and_index.py
```

---

## Exploring the database visually

The easiest way to inspect `nielsen_embeddings.db` without leaving VS Code is
the **SQLite Viewer** extension by Florian Klampfer.

### Install

1. Open Extensions (`Cmd+Shift+X`)
2. Search `SQLite Viewer`
3. Click **Install**

### Open the database

1. In the VS Code file explorer, click `nielsen_embeddings.db`
2. It opens as a spreadsheet tab showing all rows in the `category_embeddings` table

If it opens as garbled text instead, right-click the file → **Open With** → **SQLite Viewer**.

### What you'll see

| Column | Contents |
|---|---|
| `id` | Short identifier for the category (e.g. `beef_ground`) |
| `text` | Full Nielsen path (e.g. `Meat > Beef > Ground Beef`) |
| `embedding` | The 384-number vector stored as a JSON array |

---

## Scaling beyond SQLite

For >10,000 categories, replace `vector_store.py` with:

- **Chroma** (`pip install chromadb`) — local, no server
- **pgvector** — if you already run Postgres
- **Pinecone / Weaviate** — if you need cloud-scale search

The `classify.py` interface (`store.search(vector, top_k)`) stays the same.

---

## Cost estimate

Since this now uses local models, there are no API costs!

| Operation | Cost (approx) |
|---|---|
| Build index (60 categories) | Free (local embeddings) |
| Classify one product | Free (local embeddings + Ollama) |
| Classify 10,000 products | Free |
