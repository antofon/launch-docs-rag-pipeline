# 02_build_index.py
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DATA = Path("artifacts")
INDEX = Path("index"); INDEX.mkdir(exist_ok=True)

# Load docs from step 1
doc_json = json.loads((DATA/"doc.json").read_text())

# Grab text chunks to embed (overview, key changes, FAQs, etc.)
texts = []
for k, v in doc_json.items():
    if isinstance(v, str) and v:
        texts.append(v)
    elif isinstance(v, list):
        texts.extend([x for x in v if isinstance(x, str)])

# Embed using a free SentenceTransformer
embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedder.encode(texts, convert_to_numpy=True)

# Create FAISS index
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# Save artifacts
faiss.write_index(index, str(INDEX/"faiss.index"))
(DATA/"corpus.txt").write_text("\n\n".join(texts))

print(f"Indexed {len(texts)} chunks into FAISS")
