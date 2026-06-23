import streamlit as st

st.set_page_config(
    page_title="ProductHunt Explorer",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 ProductHunt App Explorer")
st.markdown("---")

st.markdown("""
Welcome to the **ProductHunt Explorer** — a data visualization application built on top of
scraped ProductHunt search results.

Use the **sidebar** to navigate between pages:

- 📋 **Results Table** — Browse and filter all scraped products
- 📊 **Visualizations** — Explore charts and insights from the data
- 🧠 **Sentiment Analysis** — Analyze application descriptions using a Hugging Face model and explore sentiment scores, confidence levels, and overall application sentiment
---

### ℹ️ How it works
The data was scraped from ProductHunt using Selenium and saved locally.
Use the **keyword filter** on the Results Table page to search within the dataset.
""")

st.caption("Data sourced from ProductHunt via Selenium scraping · Built with Streamlit")