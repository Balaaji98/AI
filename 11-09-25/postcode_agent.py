# postcode_agent.py
import sqlite3
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DB_FILE = "mvp_db.sqlite"
INDEX_FILE = "data/faiss_index.bin"
META_FILE = "data/index_meta.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
HIGH_CONF_THRESHOLD = 0.88  # cosine (inner product) threshold; tune this

# Initialize Groq client
groq_client = Groq(api_key="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")

def normalize(v):
    v = v.astype("float32")
    n = np.linalg.norm(v)
    return v / (n if n != 0 else 1.0)

def score_to_confidence(score):
    s = max(min(score, 1.0), -1.0)
    return int(((s + 1) / 2) * 100)

def load_index_meta():
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        meta = pickle.load(f)
    return index, meta

def embed_text(model, text):
    v = model.encode([text], convert_to_numpy=True).astype("float32")
    v = v / np.linalg.norm(v, axis=1, keepdims=True)
    return v

def llm_guess_address(postcode, street, town, country, suggestions):
    """
    Calls Groq Mixtral to generate better guesses for low-confidence cases.
    """
    prompt = f"""
You are a postcode correction assistant.
User entered: {postcode} {street} {town} {country}

Here are FAISS top suggestions:
{suggestions}

Return ONLY 3 likely corrected postcode suggestions with street + town.
Format each suggestion as: POSTCODE | Street, Town (confidence: high/medium/low)
No explanation text, just bullet points.
"""
    try:
        response = groq_client.chat.completions.create(
           # model="mixtral-8x7b-32768",  # fast + cheap model
            model="llama-3.1-8b-instant",  # ✅ latest Groq recommended model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM error: {e}"

def fetch_orders():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT order_id, postcode, street, town, country FROM mvp_orders;")
    rows = cur.fetchall()
    conn.close()
    return rows

def validate_orders():
    model = SentenceTransformer(EMBED_MODEL)
    index, meta = load_index_meta()
    orders = fetch_orders()

    results = []
    for row in orders:
        order_id, postcode, street, town, country = row
        combo = f"{postcode} {street} {town} {country}".strip()
        vec = embed_text(model, combo)

        D, I = index.search(vec, TOP_K)
        top_scores = D[0]
        top_idxs = I[0]

        best_score = top_scores[0]
        confidence = score_to_confidence(best_score)

        faiss_top = meta[top_idxs[0]]
        faiss_match = f"{faiss_top['postcode']} | {faiss_top['street']}, {faiss_top['town']}"

        llm_suggestions = ""
        if best_score < HIGH_CONF_THRESHOLD:
            top_suggestions = "\n".join(
                [f"{meta[idx]['postcode']} | {meta[idx]['street']}, {meta[idx]['town']}" for idx in top_idxs]
            )
            llm_suggestions = llm_guess_address(postcode, street, town, country, top_suggestions)

        results.append({
            "order_id": order_id,
            "input_postcode": postcode,
            "input_street": street,
            "faiss_top_match": faiss_match,
            "faiss_conf": confidence,
            "llm_suggestions": llm_suggestions
        })

    return results
