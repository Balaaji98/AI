# 🧠 Demand-Seasonality-Aware Slotting Optimizer (MVP)

An interactive **Streamlit-based GenAI-enabled MVP** that demonstrates how intelligent slotting optimization can dramatically reduce picker travel time and improve warehouse efficiency.

This prototype simulates **SKU movement optimization** in a warehouse layout, showcasing **before vs. after slotting efficiency**, **distance/time savings**, and **AI-generated actionable insights** — all through a sleek, professional UI.

---

## 🚀 Overview

This MVP demonstrates how a **Warehouse Management System (WMS)** can use **AI-driven slotting optimization** to:
- Analyze SKU demand velocity.
- Recommend optimal slotting locations.
- Visually simulate picker travel before and after re-slotting.
- Quantify performance gains in distance and time.
- Present **human-readable GenAI recommendations** for planners.

---

## 🎯 Key Features

✅ **Interactive Simulation**
- Simulates SKU movements before and after slotting optimization.  
- Displays real-time **distance** and **time savings** metrics per SKU.  

✅ **Distance Savings KPI**
- Compares pre-optimization vs. optimized routes.
- Shows KPI metrics like: `31% picker travel reduction`.

✅ **Animated Visualization**
- Dynamic arrows and color-coded routes for easy comparison.
- Supports switching between *Simulation View* and *Insights View*.

✅ **GenAI Recommendation Layer**
- Generates contextual suggestions such as:  
  > “Move SKU123 (high-demand beverage) closer to dispatch zone — reduces picker travel by ~15%.”

✅ **Minimal Realistic Data**
- 5 SKUs  
- 10 warehouse locations  
- 1000 synthetic orders for velocity simulation  

✅ **Business Impact Dashboard**
- Summarized metrics for savings in **distance**, **time**, and **efficiency gain**.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-------------|
| UI | [Streamlit](https://streamlit.io/) |
| Core Logic | Python (NumPy, Pandas, Math, Datetime) |
| Visualization | Plotly |
| GenAI Layer | OpenAI GPT (future integration) |
| Simulation | Synthetic SKU & order data modeling |

---

## ⚙️ How It Works

1. **Input Data Generation**  
   - Generates 5 sample SKUs, 10 locations, and 1000 synthetic orders.  
   - Computes weekly SKU velocities.  

2. **Optimization Engine**  
   - Sorts SKUs by velocity and reassigns them to closer (more efficient) pick zones.  
   - Calculates distance and time savings per SKU.  

3. **Simulation Module**  
   - Visualizes SKU movement from current → optimized locations.  
   - Computes KPI metrics dynamically.  

4. **GenAI Layer (next phase)**  
   - Uses LLM reasoning to explain re-slotting logic.  
   - Produces narrative recommendations for warehouse planners.  

---

## 📊 Example Output

**Sample Recommendation:**  
> “Move SKU004 (fast-moving snack) from L09 to L02 near the dispatch zone. This improves picker efficiency by 27% and saves ~6.5 seconds per order.”

**Sample Metrics:**  
| SKU | Current Dist (steps) | Optimized Dist | Savings (%) | Time Saved (s) |
|------|---------------------|----------------|--------------|----------------|
| SKU001 | 22.0 | 15.0 | 31.8% | 6.3 |
| SKU002 | 18.0 | 12.0 | 33.3% | 5.0 |

---

## 💰 Business Value

| Benefit | Description |
|----------|-------------|
| 🔹 **Reduced Picker Travel** | Up to 30–40% reduction in walking distance. |
| 🔹 **Higher Throughput** | Faster order completion and reduced fatigue. |
| 🔹 **Data-Driven Decisions** | Uses actual SKU demand velocity for slotting. |
| 🔹 **Faster ROI** | Quick win with minimal integration complexity. |

---

## 🧩 Next Steps

1. 🔜 **Integrate LLM for AI Insights**
   - Explain slotting logic with natural language.
   - Generate JIRA-ready optimization recommendations.

2. 🗺️ **Warehouse Map Enhancements**
   - Show location IDs and golden zones visually.

3. 📥 **CSV Upload**
   - Allow customers to upload SKU-location mapping.

4. ⚙️ **Confluence/JIRA Integration**
   - Auto-publish simulation results to documentation tools.

---

## 🧑‍💻 Run Locally

```bash
# Clone the repository
git clone https://github.com/<your-repo>/wms-slotting-optimizer.git
cd wms-slotting-optimizer

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
