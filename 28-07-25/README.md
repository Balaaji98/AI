# WMS AI Design Agent – MVP (28-07-2025)

## 📌 Overview
Today, we built the **first version (MVP)** of an AI-powered web application that:
- Extracts text from WMS requirement documents (`.docx` files)
- Sends the text to **Groq's LLM** for AI-driven analysis
- Generates **structured JSON** containing:
  - Key Requirements
  - Affected Components (PL/SQL packages, RDT rules, DB tables)
  - Development Recommendations
- Produces a **professional Word report** and allows it to be downloaded
- Provides a **Flask-based UI** for easy interaction

---

## ✅ **Key Features Implemented**
1. **Requirement Parsing**
   - Reads `.docx` files using `python-docx`
   - Extracts and cleans text for AI analysis

2. **AI Integration (Groq API)**
   - Uses **`llama3-70b-8192`** model for analysis
   - Strict JSON response format for consistency
   - Handles JSON parsing and error cases

3. **Document Generation**
   - Creates a **Word report** with:
     - Title & structured sections
     - Key Requirements (bullet list)
     - Affected Components (table)
     - Detailed Recommendations
   - Adds professional formatting (headings, bullets, table styles)

4. **Web Application (Flask)**
   - Built a **UI with Bootstrap**
   - Users can **upload a `.docx` file**
   - AI processes and returns a **downloadable Word report**
   - Handles invalid model responses gracefully with debug logs

---

## ✅ **Tech Stack**
- **Python 3.x**
- **Flask** (Web Framework)
- **Groq SDK** (AI Model API)
- **python-docx** (Word document handling)
- **Bootstrap 5** (Frontend styling)

---
