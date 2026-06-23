import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils import load_data, compute_sentiment_scores, compute_sentiment

st.set_page_config(page_title="Sentiment Analysis", page_icon="🧠", layout="wide")

st.title("🧠 Sentiment Analysis")
st.markdown("---")

st.markdown("""
This page uses the **Hugging Face** model `nlptown/bert-base-multilingual-uncased-sentiment`
to perform sentiment analysis on the applications retrieved from ProductHunt.

⚠️ **Important:** Since `results.json` only stores the number of reviews and not the review content,
the sentiment analysis is based on the application's **description**. The predicted sentiment is expressed
as a rating from 1 to 5 stars.
""")

# --- Load data ---
df = load_data()

if df.empty:
    st.warning("No data available. Run a search from the home page first.")
    st.stop()

with st.spinner("Computing sentiment analysis... (first load only)"):
    df_sentiment = compute_sentiment_scores(df)

# ============================================================
# 1. Overview: sentiment chart for all applications
# ============================================================
st.subheader("📊 Overall Sentiment by Application")

sort_option = st.radio(
    "Sort by:",
    ["Sentiment Score", "Review Count", "Title"],
    horizontal=True
)

if sort_option == "Sentiment Score":
    df_sorted = df_sentiment.sort_values("Sentiment_Score", ascending=False)
elif sort_option == "Review Count":
    df_sorted = df_sentiment.sort_values("Review_Count", ascending=False)
else:
    df_sorted = df_sentiment.sort_values("Title")

colors = df_sorted["Sentiment_Category"].map({
    "Positive": "#2ecc71",
    "Neutral": "#f1c40f",
    "Negative": "#e74c3c"
})

fig, ax = plt.subplots(figsize=(10, max(4, len(df_sorted) * 0.35)))

ax.barh(
    df_sorted["Title"],
    df_sorted["Sentiment_Score"],
    color=colors
)

ax.set_xlabel("Sentiment Score (-1 = Negative, +1 = Positive)")
ax.set_xlim(-1, 1)
ax.axvline(0, color="gray", linewidth=0.8)
ax.invert_yaxis()

st.pyplot(fig)

# Legend
st.markdown("""
🟢 Positive &nbsp;&nbsp; 🟡 Neutral &nbsp;&nbsp; 🔴 Negative
""")

st.markdown("---")

# ============================================================
# 2. Summary KPIs
# ============================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Positive Apps 🟢",
        int((df_sentiment["Sentiment_Category"] == "Positive").sum())
    )

with col2:
    st.metric(
        "Neutral Apps 🟡",
        int((df_sentiment["Sentiment_Category"] == "Neutral").sum())
    )

with col3:
    st.metric(
        "Negative Apps 🔴",
        int((df_sentiment["Sentiment_Category"] == "Negative").sum())
    )

st.markdown("---")

# ============================================================
# 3. Details for a selected application
# ============================================================
st.subheader("🔍 Application Details")

selected_title = st.selectbox(
    "Choose an application:",
    df_sentiment["Title"].tolist()
)

selected_row = df_sentiment[
    df_sentiment["Title"] == selected_title
].iloc[0]

c1, c2 = st.columns([2, 1])

with c1:
    st.markdown(f"### {selected_row['Title']}")
    st.write(selected_row["Description"])
    st.caption(
        f"ID: {selected_row['ID']} • {selected_row['Reviews']}"
    )

with c2:
    category = selected_row["Sentiment_Category"]

    emoji = {
        "Positive": "🟢",
        "Neutral": "🟡",
        "Negative": "🔴"
    }.get(category, "⚪")

    st.metric("Sentiment", f"{emoji} {category}")
    st.metric("Model Label", selected_row["Sentiment_Label"])
    st.metric(
        "Confidence",
        f"{selected_row['Sentiment_Confidence']*100:.1f}%"
    )

st.markdown("---")

# ============================================================
# 4. Test the model on custom text
# ============================================================
with st.expander("✍️ Test the model on custom text"):

    custom_text = st.text_area(
        "Enter some text (e.g., a sample review):",
        "This application is amazing"
    )

    if st.button("Analyze"):

        result = compute_sentiment(custom_text)

        emoji = {
            "Positive": "🟢",
            "Neutral": "🟡",
            "Negative": "🔴"
        }.get(result["category"], "⚪")

        st.write(
            f"**Result:** {emoji} {result['category']} — "
            f"{result['label']} "
            f"(confidence: {result['confidence']*100:.1f}%)"
        )