from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import base64
import pickle
import faiss
import docx2txt
import fitz  # PyMuPDF
import markdown2

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
import tempfile


from io import BytesIO
from sentence_transformers import SentenceTransformer
from groq import Groq

from atlassian import Confluence
from dotenv import load_dotenv

import re

import graphviz
import textwrap

import xml.etree.ElementTree as ET

# === Utils for Diagram Handling ===
def extract_mermaid_code(response_text):
    """Extract Mermaid code blocks from LLM response"""
    pattern = r"```mermaid(.*?)```"
    matches = re.findall(pattern, response_text, re.DOTALL)
    return [m.strip() for m in matches]

def wrap_mermaid_for_confluence(code):
    """Wrap Mermaid diagram for Confluence Cloud macro rendering"""
    return f"""
    <ac:structured-macro ac:name="mermaid">
      <ac:plain-text-body><![CDATA[
      {code}
      ]]></ac:plain-text-body>
    </ac:structured-macro>
    """

def generate_drawio_file(prompt, output_path="diagram.drawio"):
    """
    Generate a professional Draw.io (mxGraph XML) diagram file from a prompt.
    """
    client = Groq(api_key="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")

    system_msg = (
        "You are an expert WMS solution architect. "
        "Convert the given requirement into a detailed professional Draw.io "
        "(mxGraph XML) diagram. Use clear nodes, relationships, and groupings. "
        "Output ONLY valid XML — no explanations or markdown."
    )

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Requirement:\n{prompt}"}
        ],
        temperature=0
    )

    xml_content = response.choices[0].message.content.strip()
    if not xml_content.startswith("<mxfile"):
        xml_content = f"<mxfile><diagram name='Flow'>{xml_content}</diagram></mxfile>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    return output_path


def generate_png_diagram(prompt_text, response_text, filename="wms_process_flow"):
    """
    Generate BOTH PNG + Draw.io diagrams from Mermaid/auto-generation.
    """
    os.makedirs("diagrams_output", exist_ok=True)
    base_path = os.path.join("diagrams_output", filename)

    # Extract Mermaid code
    mermaid_blocks = extract_mermaid_code(response_text)
    mermaid_code = mermaid_blocks[0] if mermaid_blocks else auto_generate_mermaid(prompt_text)

    # Parse nodes & edges
    nodes, edges = [], []
    for line in mermaid_code.splitlines():
        line = line.strip()
        if "-->" in line:
            parts = [p.strip() for p in line.split("-->")]
            if len(parts) == 2:
                edges.append((parts[0], parts[1]))
                if parts[0] not in nodes: nodes.append(parts[0])
                if parts[1] not in nodes: nodes.append(parts[1])
        elif line and not line.startswith("graph") and line not in nodes:
            nodes.append(line)

    # --- PNG (Graphviz) ---
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR", splines="spline", fontsize="11", fontname="Helvetica")

    # Global node + edge theme
    dot.attr("node", shape="box", style="rounded,filled", fillcolor="lightblue", color="black", fontcolor="black")
    dot.attr("edge", color="gray30", arrowsize="0.7", fontname="Helvetica", fontsize="9")

    for n in nodes:
        dot.node(n)
    for src, dst in edges:
        dot.edge(src, dst)

    png_path = dot.render(base_path, cleanup=True)    

    # --- Draw.io ---
    drawio_path = generate_drawio_file(prompt_text, f"{base_path}.drawio")

    return {"png": png_path, "drawio": drawio_path}


def upload_diagram_to_confluence(page_id, diagram_path):
    """Upload PNG diagram to Confluence and return HTML image embed."""
    try:
        confluence.attach_file(
            filename=diagram_path,
            name=os.path.basename(diagram_path),
            #drawio_file = generate_drawio_file(requirement_text),
            page_id=page_id
        )
        return f'<ac:image><ri:attachment ri:filename="{os.path.basename(diagram_path)}" /></ac:image>'
    except Exception as e:
        return f"<p>❌ Diagram upload failed: {e}</p>"

def convert_markdown_to_html(markdown_text):
    return markdown2.markdown(markdown_text)


def generate_title_from_text(text):
    prompt = f"""You are a Confluence documentation assistant. Read the requirement or document below and generate a clear, crisp, and short Confluence page title (max 10 words) that summarizes it well.

Text:
{text[:1500]}

Respond ONLY with the title, nothing else."""
    
    title_response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    return title_response.choices[0].message.content.strip()


def extract_title(text, fallback="WMS Design"):
    lines = text.strip().split("\n")
    for line in lines:
        clean_line = line.strip()
        if clean_line and len(clean_line.split()) >= 3:  # At least 3 words
            return clean_line[:80]  # Limit title length for Confluence
    return fallback

def generate_summary(requirement_text):
    summary_prompt = f" Understand the business context to the fullest of clarity and Summarize the following requirement in 3-5 concise lines:\n\n{requirement_text}"
    return query_llm(summary_prompt)  # Using your existing LLM call
    return {"summary": summary, "link": confluence_url}

# Load credentials from confluence.env
load_dotenv("confluence.env")

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_EMAIL,
    password=CONFLUENCE_API_TOKEN
)

def create_confluence_page(title, content, with_diagram=False, prompt_text=None, response_text=None):
    try:
        page = confluence.create_page(
            space=CONFLUENCE_SPACE_KEY,
            title=title,
            body=content,
            representation="storage"
        )
        page_id = page["id"]

        if with_diagram and prompt_text and response_text:
            paths = generate_png_diagram(prompt_text, response_text)
            diagram_html = upload_diagram_to_confluence(page_id, paths["png"])
            updated_body = content + "<p><strong>Process Flow Diagram:</strong></p>" + diagram_html
            confluence.update_page(
                parent_id=None,
                page_id=page_id,
                title=title,
                body=updated_body,
                type="page",
                representation="storage"
            )

        return f"{CONFLUENCE_URL}{page['_links']['webui']}"
    except Exception as e:
        return f"❌ Failed to create Confluence page: {e}"




app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = Groq(api_key="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")  # Replace with your real key
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load knowledge base chunks and FAISS index
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)
index = faiss.read_index("faiss_index.idx")


# === Utility Functions ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

def search_similar_chunks(query, top_k=5):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]

def query_llm(prompt):
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a senior WMS solution architect assistant. If input is vague, ask clarifying questions. Otherwise, suggest the best BY Dispatcher WMS 2019 design approach. Format response with: Summary, Assumptions, Recommended Design, Flowchart if applicable."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return chat_completion.choices[0].message.content

# === Quick Auto-decide Mermaid Generator ===
def auto_generate_mermaid(text):
    """
    Generate Mermaid flowchart from requirement text.
    Uses keyword matching + simple sequence detection.
    """
    keywords = ["Receiving", "Putaway", "Replenishment", "Picking", "Shipping", "Crossdock"]
    nodes = [kw for kw in keywords if kw.lower() in text.lower()]
    
    edges = []
    sentences = re.split(r'[.\n]', text)
    for sentence in sentences:
        for i, kw1 in enumerate(keywords):
            for kw2 in keywords[i+1:]:
                pattern = rf"{kw1}.*(then|->|followed by|after).*{kw2}"
                if re.search(pattern, sentence, re.IGNORECASE):
                    edges.append((kw1, kw2))
    
    mermaid = "graph TD\n"
    for node in nodes:
        mermaid += f"    {node}\n"
    for src, dst in edges:
        mermaid += f"    {src} --> {dst}\n"
    return mermaid


# === Routes ===
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "❌ Please enter a valid requirement or question."})

    if user_input.lower() in ["hi", "hello", "hey"]:
        return jsonify({"response": "👋 Hello! I'm your WMS Design Assistant. Ask me about an existing process or request a design recommendation!"})

    similar_chunks = search_similar_chunks(user_input)
    context = "\n".join(similar_chunks)

    # Intent detection keywords
    explanation_keywords = ["explain", "how does", "what is", "current flow", "existing process", "functionality", "flow of", "meaning of"]
    design_keywords = ["design", "recommendation", "solution", "approach", "change request", "enhancement", "new process"]

    # Detect mode
    mode = "design"
    if any(k in user_input.lower() for k in explanation_keywords):
        mode = "explanation"
    elif any(k in user_input.lower() for k in design_keywords):
        mode = "design"

    if mode == "explanation":
        final_prompt = f"""You are a WMS knowledge base assistant. 
User Question: {user_input}

Context from KB:
{context}

Task:
Explain the process or feature clearly and concisely based ONLY on the context. 
Do NOT provide any design recommendations, assumptions, PL/SQL mappings, JIRA stories, or diagrams.
There should not be any technical information in your response like any database table, any code, any technology.
Your response must be a detailed step by step explanation that is well aligned towards the functionality more on an operational aspect.
"""
    else:
        final_prompt = f"""Requirement: {user_input}

Context:\n{context}

Your Tasks:
1. Understand the business context to the fullest of clarity
2. Generate the most ideal design recommendation (mention impacted PL/SQL packages)
3. Create a suitable, valid, clean looking Mermaid process flow diagram with a clear explanation including Process, Sequence, or Context
4. Draft a JIRA-ready technical story containing all key details
5. Ask clarifying questions if anything is unclear
6. Generate a clean- professional looking response with neat indentations, numberings, bullet points (if required), clean spacing

Respond in a structured format with headings:
- Requirement Summary
- Design Recommendation
- PL/SQL Mapping
- Mermaid Flow Diagram
- JIRA Story Content
- Clarification Questions (if needed)

Instructions:
- If the requirement is vague, ask a clarifying question first.
- Else, generate a clean design recommendation in this format:

Summary:
...

Assumptions:
...

Recommended Design Approach:
...

Flowchart (if applicable):
...
"""

        # Get full response
    full_response = query_llm(final_prompt)

        # Extract Mermaid if exists
    #mermaid_blocks = extract_mermaid_code(full_response)
    #if mermaid_blocks:
     #   for code in mermaid_blocks:
      #      full_response = full_response.replace(
       #         f"```mermaid\n{code}\n```", wrap_mermaid_for_confluence(code)
        #    )

    # === Auto-generate diagram based on prompt ===
    auto_mermaid = auto_generate_mermaid(user_input)
    full_response += f"\n\nFlowchart (auto-generated):\n```mermaid\n{auto_mermaid}\n```"

# Wrap Mermaid for Confluence
  #  for code in extract_mermaid_code(full_response):
   #     full_response = full_response.replace(
    #        f"```mermaid\n{code}\n```", wrap_mermaid_for_confluence(code)
     #   )

    # Generate title & Confluence page
    title = generate_title_from_text(user_input)
    html_response = convert_markdown_to_html(full_response)

    page_link = create_confluence_page(title=title, content=html_response, with_diagram=True, prompt_text=user_input, response_text=full_response)


    # Generate short summary for chat
    summary_text = generate_summary(user_input)

    # Chat output: ONLY summary + link
    chat_message = f" {summary_text}\n\n📄 **View full details here:** {page_link}"

    return jsonify({"response": chat_message})



@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        if filename.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(filepath)
        else:
            extracted_text = extract_text_from_docx(filepath)

        top_chunks = search_similar_chunks(extracted_text)
        context = "\n".join(top_chunks)
        summary_prompt = f"""A new requirement document has been uploaded.

Extract the key points from this and suggest a WMS design if possible.

Context:\n{context}

Document Text:\n{extracted_text[:3000]}  # Truncate for safety

Respond in this format:
Summary:
...

Assumptions:
...

Recommended Design Approach:
...

Flowchart (if applicable):
...
"""


        response = query_llm(summary_prompt)


        # Handle Mermaid
       # mermaid_blocks = extract_mermaid_code(response)
        #if mermaid_blocks:
         #   for code in mermaid_blocks:
          #      response = response.replace(
           #         f"```mermaid\n{code}\n```", wrap_mermaid_for_confluence(code)
            #    )

        # Create Confluence page with full design
        title = generate_title_from_text(extracted_text)
        html_response = convert_markdown_to_html(response)
        page_link = create_confluence_page(title=title, content=html_response,with_diagram=True, prompt_text=extracted_text, response_text=response)

        # Prompt for summary only
        summary_prompt = f"""Summarize the key points from this WMS requirement document in a short, crisp way suitable for chat display. Understand the business context to the fullest of clarity and Summarize the following requirement in 3-5 concise lines

Document Text:
{extracted_text[:3000]}
"""
        summary_response = query_llm(summary_prompt)

        # Chat gets summary + Confluence link
        chat_output = f"{summary_response}\n\n🔗 View Full Design in Confluence: {page_link}"

        return jsonify({"response": chat_output})

    return jsonify({"error": "Only .docx and .pdf files are allowed"})




if __name__ == "__main__":
    app.run(debug=True)
