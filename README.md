# 📬 AI-Powered Postcode Validation Agent

## 📝 Overview
The **Postcode Validation Agent** is an AI-powered solution that automatically validates customer order addresses against a list of legitimate addresses.  
It uses **FAISS embeddings** for fast similarity search and falls back to an **LLM** (Groq LLaMA-3) when the confidence score is low — ensuring more accurate suggestions.

---

## 🎯 Goal
Reduce time and effort spent manually verifying and correcting invalid or incomplete postcodes by automatically:
- Finding the **closest valid match**
- Generating **3 AI-powered suggestions** for low-confidence cases
- Presenting results in a **visual dashboard** for easy review

---

## 🔄 End-to-End Flow

1. **📥 New Order in DB**  
   The system fetches order details (postcode, street, town, country) from the SQLite database.

2. **🔍 Validation with FAISS**  
   - Address is converted to an **embedding**.
   - FAISS index searches for the **nearest valid match**.
   - A confidence score (0-100%) is assigned.

3. **🤖 AI Fallback (if confidence is low)**  
   - Top FAISS matches are passed to the LLM.
   - LLM returns 3 best human-like suggestions with confidence labels (high/medium/low).

4. **📊 Dashboard Output**  
   - Results are displayed with:
     - Order ID & Entered Address
     - Best FAISS Match & Confidence
     - AI Suggestions (if available)
   - Users can **download results as CSV** or review low-confidence cases manually.

---

## 🆚 AS-IS vs TO-BE (Impact)

| Aspect | Current Manual Process | AI-Powered Agent (To-Be) |
|-------|---------------------|----------------------|
| Effort per validation | 3-5 minutes per order | < 2 seconds per order |
| Accuracy | Prone to manual errors | Consistent, ML-based validation |
| Scalability | Limited by human availability | Processes 1000+ orders in minutes |
| Speed | Slow, repetitive work | Real-time validation |
| Monthly workload | High (manual checks needed for every order) | 80-90% orders auto-validated, humans only handle exceptions |

---

## 📊 Example Output

| Order ID | Entered Address | FAISS Top Match | Confidence (%) | AI Suggestions |
|--------|----------------|---------------|---------------|---------------|
| 28 | M3 1VE St | M1 1AE \| Market Street, Manchester | 83 | • M3 1AA \| Princess Street (high)<br>• M3 1AB \| Portland Street (medium)<br>• M3 1AC \| King Street (medium) |

---

## 🚀 Key Benefits
✅ **Faster** – Validates thousands of orders instantly  
✅ **Smarter** – AI-powered suggestions reduce manual guesswork  
✅ **Scalable** – Works with growing order volumes  
✅ **Actionable** – Easy dashboard + CSV export for reporting  

---
