from flask import Flask, request, render_template, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import base64
from groq import Groq

# === Existing Setup ===
app = Flask(__name__)
client = Groq(api_key="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")  # Replace with your actual key

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
            {"role": "system", "content": "You are a helpful AI assistant for BY Dispatcher WMS 2019. Provide answers in bullet points, cleanly formatted, and ask clarifying questions when needed."},
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

    final_prompt = f"""Context:\n{context}\n\nUser Query: {user_input}\n\nAnswer in clean bullet points with indentation."""
    response = query_llm(final_prompt)
    return jsonify({"response": response})


# === Diagram/Image Generation Logic (Appended) ===
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def text_to_diagram(text):
    lines = text.split("\n")
    width, height = 800, 40 + 40 * len(lines)
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    y = 20
    for line in lines:
        draw.text((20, y), line.strip(), fill=(0, 0, 0), font=font)
        y += 40

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.route("/generate-diagram", methods=["POST"])
def generate_diagram():
    user_input = request.json.get("message", "")
    similar_chunks = search_similar_chunks(user_input)
    context = "\n".join(similar_chunks)

    diagram_prompt = f"""Create a clean bullet-point process diagram or flow for the following concept:\n\n{user_input}\n\nUse step-by-step format."""
    diagram_text = query_llm(diagram_prompt)

    base64_img = text_to_diagram(diagram_text)
    return jsonify({
        "diagram_text": diagram_text,
        "diagram_base64": base64_img
    })

# === Run the Flask app ===
if __name__ == "__main__":
    app.run(debug=True)
