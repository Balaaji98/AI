import os
import pickle
import faiss
import numpy as np
from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
from groq import Groq

# === Set Absolute Base Path ===
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "faiss_index.idx")
CHUNKS_FILE = os.path.join(BASE_DIR, "chunks.pkl")
GROQ_API_KEY = "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"  # replace with your actual key

# === Load Embedding Model and Index ===
print("[INFO] Loading embedding model and FAISS index...")
model = SentenceTransformer("all-MiniLM-L6-v2")

try:
    with open(CHUNKS_FILE, "rb") as f:
        chunks = pickle.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ chunks.pkl not found at: {CHUNKS_FILE}")

try:
    index = faiss.read_index(INDEX_FILE)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load FAISS index: {INDEX_FILE}\n{str(e)}")

# === Initialize Groq Client ===
client = Groq(api_key=GROQ_API_KEY)

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def index_html():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please enter a valid message."})

    # Encode user query and search
    query_embedding = model.encode([user_message]).astype("float32")
    D, I = index.search(query_embedding, k=3)
    retrieved_chunks = "\n".join([chunks[i] for i in I[0] if i < len(chunks)])

    prompt = f"""You are a helpful AI Design Architect for Blue Yonder Dispatcher WMS 2019.
Use the following context to answer the question:
\n---\n{retrieved_chunks}\n---\n
Question: {user_message}
Answer:"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful WMS architect."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content.strip()
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
