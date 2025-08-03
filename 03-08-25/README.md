
# 📅 README: Progress Update – 3rd August 2025

---

### ✅ Goal for the Day
Continue iterative development of the WMS Agentic AI Designer by aligning it to the real-world SDLC design flow for Blue Yonder Dispatcher WMS. Improve backend logic, frontend clarity, and AI intelligence toward automating flow extraction, design approach recommendation, and JIRA story generation.

---

### 🔨 What We Worked On Today

#### 1. 📌 Clarified Vision – Manual vs. Agentic Flow Mapping
- Thoroughly reviewed your **AS-IS vs TO-BE** workflow.
- Reconfirmed core components the AI agent must replicate:
  - Understand domain logic from `.docx`
  - Derive WMS-specific operational flow
  - Recommend design approach (context-aware)
  - Auto-generate JIRA stories
  - Draw process/flow diagrams intelligently
  - Store and reuse design knowledge

#### 2. 🧠 Refined MVP Goalpost
- You expressed dissatisfaction with **v1 MVP** (summarization-only).
- We agreed to rebuild toward a **more powerful V2**:
  - Add true reasoning over WMS logic
  - Ask clarifying questions
  - Show flowcharts (Mermaid)
  - Push stories directly to JIRA
  - Embed learnings from internal code/Confluence docs

#### 3. 📁 Folder Setup Finalized
- Project root confirmed:
  ```
  /Users/balaajiganesh/Desktop/WMS-Agent/03-08-25
  ```
- `kb/` directory selected to hold `.txt` reference knowledge for embedding-based retrieval.

#### 4. 🧱 Knowledge Base Integration
- Implemented:
  - **Embedding** of `.txt` files from `kb/` using SentenceTransformers
  - **Chunking**, **vector storage with FAISS**, and **retrieval pipeline**
  - Integrated retrieved context into prompt fed to LLM
  - Ensured kb-aware design recommendations are now possible

#### 5. 🧪 App Working Again (Fixed Errors)
- Missing `docx2txt` module installed to fix startup crash.
- Updated `app.py` to reflect new architecture with embedding context.

#### 6. 🚀 JIRA Story Auto-Creation Design (In Progress)
- Decided to push design stories directly into JIRA using JIRA Cloud REST API
- Setup steps:
  - Create API Token
  - Use HTTPBasicAuth
  - Define payload with summary + description from LLM
  - Response will contain link to created JIRA
- Final code function **`create_jira_story()`** shared (not yet integrated)

#### 7. 📎 Mermaid Diagram Rendering Prep (In Progress)
- Discussed adding Mermaid.js rendering to `index.html`
- Decided to postpone this for now

---

### 📁 Next Steps

| Priority | Task |
|---------|------|
| 🔥 | Implement JIRA auto-creation fully into backend |
| 🔄 | Resume Mermaid rendering to visualize flows |
| 📤 | Add output markdown formatting in frontend |
| 🧠 | Add clarification loop before diagram/story |
| 🎯 | Let agent ask follow-up if requirement is vague |

---

