# WMS AI Design Assistant 🤖📦

An intelligent AI-powered assistant designed to **automate Warehouse Management System (WMS) design workflows** — mirroring the expertise of human solution architects.

---

## 🚀 Project Vision

This project aims to **transform how WMS functional and technical designs are created** by leveraging AI to:

- Understand requirement documents (chat or uploaded files).
- Ask clarifying questions like a real WMS solution architect.
- Automatically generate high-quality design documents, diagrams, PL/SQL logic guidance, and JIRA-ready stories.
- Seamlessly push the design to Confluence with smart page titles and rich formatting.
- Become context-aware of existing warehouse logic — just like a seasoned designer.

---

## 🎯 Ultimate Goal

> To build an agent that **fully understands end-to-end WMS functionality**, including warehouse operations, PL/SQL packages, HHT screens, and RDT rules, and is capable of:
>
> - Interpreting new enhancement requests.
> - Generating expert-level technical/functional designs.
> - Mapping enhancements to relevant WMS components accurately.
> - Acting as a virtual WMS design architect — consistently and at scale.

---

## 🧪 Current MVP (Minimal Viable Product)

We're starting with a focused MVP:
- ✅ Use **embedded `.txt` files** for KB (knowledge base) containing one specific WMS functionality — `Stock Adjustment`.
- ✅ Support RAG (Retrieval-Augmented Generation) using **FAISS** and **Sentence Transformers** to enable context-aware responses.
- ✅ Design assistant responds to natural prompts and suggests suitable designs for enhancements.
- ✅ Automatically generates and uploads Confluence pages using smart titles and rich Markdown-to-HTML formatting.

---

## 🧠 How It Works (MVP Flow)

1. `.txt` files about a selected WMS feature (e.g. `Stock Adjustment`) are stored under `/kb/`.
2. A script processes and embeds this content using:
   - `sentence-transformers` for embeddings.
   - `faiss` for fast similarity search.
3. User interacts via chat or provides a new requirement/enhancement.
4. The assistant:
   - Retrieves relevant knowledge from the index.
   - Generates a design response with `Summary`, `Design`, `Flow`, `Assumptions`.
   - Auto-publishes the design to **Confluence** with:
     - Smart title extraction.
     - Clean HTML formatting.
     - Rich preview support in UI.

---

## ⚙️ Tech Stack

- 🧠 **AI / NLP**: OpenAI GPT-4, Sentence Transformers (MiniLM)
- 📦 **Vector Store**: FAISS
- 🗃️ **Knowledge Base**: `.txt` files (sample design logic, PL/SQL, flow notes)
- 🌐 **Backend**: Python (Flask single-file app)
- 🖼️ **Frontend**: Simple HTML/CSS/JS chat UI with full-screen support
- 📚 **Documentation + Storage**: Confluence Cloud (Atlassian API)
- 🧪 **Design Test Case**: Stock Adjustment functionality (Warehouse)

---

## 📌 Features Implemented So Far

- [x] Chat UI with full-screen experience.
- [x] Smart Confluence link previews.
- [x] Embedded `.txt` knowledge base + chunking + indexing.
- [x] Markdown-to-HTML formatting for clean documentation.
- [x] Smart Confluence page titles using summarization.
- [x] Auto-publishing to Confluence using REST API.
- [x] Accurate design suggestions for a chosen WMS flow (`Stock Adjustment`).
- [x] Readable and structured AI design responses (`Summary`, `Design`, etc.).

---

## 🛣️ What's Next

- 🔜 Expand to multiple WMS flows (e.g., `Putaway`, `Picking`, `Returns`).
- 🔜 Parse `.docx`, `.pdf`, `.pptx` requirement files for richer input.
- 🔜 Implement live clarification loop: agent asks back if requirement is vague.
- 🔜 Version-controlled design archive with smart labels in Confluence.
- 🔜 More advanced flowchart and diagram generation (Mermaid/Draw.io).
- 🔜 Enable PL/SQL snippet generation mapped to design stories.

---

## 🧪 Try These Prompts (MVP Scope)

1. `Design an enhancement to allow two-step stock adjustment approval.`
2. `What changes are needed in the HHT screen for stock discrepancy?`
3. `Suggest design for auto-posting stock adjustments after manager approval.`

---

