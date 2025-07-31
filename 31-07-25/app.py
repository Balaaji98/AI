from flask import Flask, request, render_template, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import base64
import subprocess
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from groq import Groq

app = Flask(__name__)
client = Groq(api_key="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")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

index = faiss.read_index("faiss_index.idx")

def search_similar_chunks(query, top_k=5):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]

def query_llm(prompt):
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You're a BY Dispatcher WMS 2019 expert. If the user query is vague, ask a clarifying question. If the query is about a process or flow, generate Mermaid diagram syntax."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return chat_completion.choices[0].message.content

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    if user_input.strip().lower() in ["hi", "hello", "hey"]:
        return jsonify({"response": "👋 Hello! I'm your WMS Design Assistant for BY Dispatcher WMS 2019. How can I assist you today?"})

    similar_chunks = search_similar_chunks(user_input)
    context = "\n".join(similar_chunks)

    final_prompt = f"""Context:\n{context}\n\nUser Query: {user_input}\n\nRespond in clean bullet points. If the question is vague, ask a clarifying question."""
    response = query_llm(final_prompt)
    return jsonify({"response": response})

# =================== Diagram Generation ===================== #

def is_diagram_needed(user_input: str) -> bool:
    keywords = ["flow", "process", "architecture", "diagram", "steps", "workflow"]
    return any(kw in user_input.lower() for kw in keywords)

def generate_mermaid_from_llm(user_input, context):
    prompt = f"""
Context:\n{context}

Generate a detailed Mermaid flowchart for the following WMS requirement:

"{user_input}"

Use professional Mermaid syntax. Only output code block with mermaid content.
"""
    return query_llm(prompt)

def render_mermaid_to_base64(mermaid_code: str) -> str:
    try:
        with open("temp.mmd", "w") as f:
            f.write(mermaid_code)

        subprocess.run(["mmdc", "-i", "temp.mmd", "-o", "diagram.png"], check=True)

        with open("diagram.png", "rb") as img:
            encoded = base64.b64encode(img.read()).decode("utf-8")

        os.remove("temp.mmd")
        os.remove("diagram.png")

        return encoded
    except Exception as e:
        print(f"Diagram generation failed: {e}")
        return None

@app.route("/generate-diagram", methods=["POST"])
def generate_diagram():
    user_input = request.json.get("message", "")

    if not is_diagram_needed(user_input):
        return jsonify({"error": "Diagram not applicable for this query."})

    similar_chunks = search_similar_chunks(user_input)
    context = "\n".join(similar_chunks)

    mermaid_code = generate_mermaid_from_llm(user_input, context)

    if not mermaid_code.strip().startswith("```mermaid"):
        mermaid_code = f"```mermaid\n{mermaid_code.strip()}\n```"

    # Extract code inside ```mermaid
    clean_code = mermaid_code.strip().split("```mermaid")[-1].split("```")[0].strip()

    diagram_base64 = render_mermaid_to_base64(clean_code)

    if diagram_base64:
        return jsonify({
            "diagram_text": mermaid_code,
            "diagram_base64": diagram_base64
        })
    else:
        return jsonify({"diagram_text": mermaid_code, "diagram_base64": None})
    
# =================== Run App ===================== #
if __name__ == "__main__":
    app.run(debug=True)
