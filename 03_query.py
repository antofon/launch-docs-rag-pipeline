# 03_query.py
import faiss, json, re
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

ART = Path("artifacts")
IDX = Path("index/faiss.index")

# Load index + corpus
index = faiss.read_index(str(IDX))
corpus = (ART/"corpus.txt").read_text().split("\n\n")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, k=3):
    q_emb = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, k)
    return [corpus[i] for i in I[0]]

def ask(query):
    context = "\n\n".join(search(query))
    messages = [
        {"role": "system", "content": "You are a safe, helpful support assistant. Cite sources. Avoid unsafe content for kids."},
        {"role": "user", "content": f"Question: {query}\n\nContext:\n{context}"}
    ]
    resp = ollama.chat(model="mistral", messages=messages)
    return resp["message"]["content"]

while True:
    q = input("Ask a question (or 'quit'): ")
    if q.lower() == "quit": break
    print(ask(q))
