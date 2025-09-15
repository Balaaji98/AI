# app.py
import streamlit as st
import pandas as pd
from postcode_agent import validate_orders

st.set_page_config(page_title="Postcode Validation Agent", layout="wide")
st.title("📬 Postcode Validation Agent")

st.markdown(
    """
    This dashboard fetches orders from the SQLite DB, validates them via FAISS embeddings,
    and sends low-confidence matches to LLM for top suggestions.
    """
)

st.info("Fetching and processing orders from SQLite DB... This may take a few seconds.")

results = validate_orders()

if results:
    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Format LLM suggestions as bullet points
    def format_llm_suggestions(text):
        if text:
            lines = text.split("\n")
            return "\n".join([f"• {line}" for line in lines])
        return ""
    
    df["llm_suggestions"] = df["llm_suggestions"].apply(format_llm_suggestions)

    # Highlighting function
    def highlight_row(row):
        styles = []
        if row["faiss_conf"] >= 88:
            # Subtle green
            styles = ["background-color: #d0f0c0; color: #000000"]*len(row)
        elif row["llm_suggestions"]:
            # Subtle yellow
            styles = ["background-color: #fff8b0; color: #000000"]*len(row)
        else:
            styles = ["background-color: #ffffff; color: #000000"]*len(row)
        return styles

    st.subheader("✅ Validation Results")
    st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

    # CSV download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="validated_orders.csv",
        mime="text/csv"
    )
else:
    st.warning("No orders found or processed.")
