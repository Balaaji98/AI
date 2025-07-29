import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from typing import List

# ===✅ PATHS ===
TEXT_FILE = "/Users/balaajiganesh/Desktop/WMS-Agent/by_dispatcher_wms_knowledge.txt"
CHUNKS_FILE = "/Users/balaajiganesh/Desktop/WMS-Agent/chunks.pkl"
FAISS_INDEX_FILE = "/Users/balaajiganesh/Desktop/WMS-Agent/faiss_index.idx"

# ===✅ Helper Function to Chunk Text ===
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# ===✅ Main Function ===
def main():
    print("[INFO] Chunking text...")

    if not os.path.exists(TEXT_FILE):
        raise FileNotFoundError(f"❌ File not found: {TEXT_FILE}")

    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)

    print("[INFO] Loading embedding model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    print(f"[INFO] Encoding {len(chunks)} chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)

    print("[INFO] Creating FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(CHUNKS_FILE), exist_ok=True)

    # Save chunks and index
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)

    faiss.write_index(index, FAISS_INDEX_FILE)

    print("[✅ DONE] FAISS index and chunks saved.")

# ===✅ Run the Script ===
if __name__ == "__main__":
    main()
