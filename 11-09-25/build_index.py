# build_index.py
import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from pathlib import Path

DATA_CSV = Path("data/valid_addresses.csv")
INDEX_FILE = Path("data/faiss_index.bin")
META_FILE = Path("data/index_meta.pkl")
EMBED_MODEL = "all-MiniLM-L6-v2"  # small & fast

def normalize_vectors(v):
    # L2 normalize rows for cosine similarity with inner product index
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    norms[norms==0] = 1
    return v / norms

def build_index():
    df = pd.read_csv(DATA_CSV)
    df['combo'] = df['postcode'].astype(str).str.strip() + " " + df['street'].astype(str).str.strip() + " " + df['town'].astype(str).str.strip() + " " + df['country'].astype(str).str.strip()
    texts = df['combo'].tolist()

    print("Loading embedding model:", EMBED_MODEL)
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True).astype("float32")

    # normalize for cosine
    embeddings = normalize_vectors(embeddings)

    dim = embeddings.shape[1]
    print(f"Embedding dim = {dim}, building FAISS IndexFlatIP (inner-product on normalized vectors)...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print("Index contains", index.ntotal, "vectors")

    # save index and metadata
    faiss.write_index(index, str(INDEX_FILE))
    with open(META_FILE, "wb") as f:
        pickle.dump(df.to_dict(orient="records"), f)

    print("Saved index ->", INDEX_FILE)
    print("Saved metadata ->", META_FILE)

if __name__ == "__main__":
    build_index()
