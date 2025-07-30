import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ===== Paths =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_FOLDER = os.path.join(BASE_DIR, "kb")
INDEX_FILE = os.path.join(BASE_DIR, "faiss_index.idx")
CHUNK_FILE = os.path.join(BASE_DIR, "chunks.pkl")

# ===== Chunking Config =====
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

# ===== Step 1: Load and combine all KB text =====
def load_kb_text():
    combined_text = ""
    for file in os.listdir(KB_FOLDER):
        if file.endswith(".txt"):
            path = os.path.join(KB_FOLDER, file)
            with open(path, "r", encoding="utf-8") as f:
                combined_text += f"\n\n# {file.replace('_', ' ').replace('.txt','').title()}\n"
                combined_text += f.read()
    return combined_text

# ===== Step 2: Chunk the text =====
def chunk_text(text):
    print("[INFO] Chunking text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)

# ===== Step 3: Create embeddings and build FAISS index =====
def embed_chunks(chunks):
    print("[INFO] Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("[INFO] Generating embeddings...")
    embeddings = model.encode(chunks)
    
    print("[INFO] Building FAISS index...")
    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    return index, embeddings

# ===== Step 4: Save index and chunks =====
def save_data(index, chunks):
    print("[INFO] Saving FAISS index and chunks...")
    faiss.write_index(index, INDEX_FILE)
    with open(CHUNK_FILE, "wb") as f:
        pickle.dump(chunks, f)
    print("✅ Indexing complete.")

# ===== Main =====
def main():
    print("[INFO] Loading KB from ./kb/")
    full_text = load_kb_text()
    if not full_text.strip():
        raise RuntimeError("❌ KB text is empty. Please check ./kb/")
    
    chunks = chunk_text(full_text)
    index, _ = embed_chunks(chunks)
    save_data(index, chunks)

if __name__ == "__main__":
    main()
