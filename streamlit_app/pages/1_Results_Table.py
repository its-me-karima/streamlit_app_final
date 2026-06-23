import streamlit as st
from utils import load_data, filter_data

st.set_page_config(page_title="Results Table", page_icon="📋", layout="wide")

st.title("📋 Results Table")
st.markdown("---")

# ── Load data once ────────────────────────────────────────────────────────────
df = load_data("results.json")

if df.empty:
    st.stop()

# ── Info banner ───────────────────────────────────────────────────────────────
st.info(
    f"📦 Dataset contains **{len(df)} products** scraped from ProductHunt "
    f"for the query **'mental health ai'**. Use the filters below to search within this data."
)

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    keyword = st.text_input(
        "🔍 Filter by keyword",
        placeholder="e.g. therapy, meditation, journal…",
        help="Searches within product titles and descriptions"
    )

with col2:
    min_reviews = st.number_input("Minimum reviews", min_value=0, value=0, step=1)

# Apply filters
filtered = filter_data(df, keyword=keyword, min_reviews=min_reviews)
filtered = filtered.sort_values("Review_Count", ascending=False)

# ── Save filtered data for Visualizations page ───────────────────────────────
st.session_state["df"] = filtered

# ── Result count feedback ─────────────────────────────────────────────────────
if keyword or min_reviews > 0:
    if filtered.empty:
        st.warning(f"No products match your filters. Try a different keyword.")
        st.stop()
    else:
        st.success(f"✅ **{len(filtered)}** products match your filters.")
else:
    st.markdown(f"Showing all **{len(filtered)}** products")

# ── Table ─────────────────────────────────────────────────────────────────────
st.dataframe(
    filtered[["Title", "Description", "Reviews"]].reset_index(drop=True),
    use_container_width=True,
    height=500,
)

# ── Download ──────────────────────────────────────────────────────────────────
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download as CSV", csv, "producthunt_results.csv", "text/csv")