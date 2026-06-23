import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualizations", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #111D26; }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }

    /* ── Metric card ── */
    .kpi {
        background: #172832;
        border-radius: 14px;
        padding: 18px 20px;
        border: 1px solid #1e3547;
        display: flex;
        justify-content: space-between;
        align-items: center;
        min-height: 90px;
    }
    .kpi-left { display: flex; flex-direction: column; gap: 4px; }
    .kpi-value { font-size: 2rem; font-weight: 800; line-height: 1; margin:0; }
    .kpi-label { font-size: 0.78rem; color: #6b8fa8; text-transform: uppercase; letter-spacing: 0.05em; margin:0; }
    .kpi-icon {
        width: 46px; height: 46px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem;
    }

    /* chart card */
    .chart-wrap {
        background: #172832;
        border-radius: 14px;
        padding: 16px 18px 10px 18px;
        border: 1px solid #1e3547;
        margin-bottom: 16px;
    }
    .chart-title { font-size: 0.95rem; font-weight: 700; color: #e5e7eb; margin:0 0 2px 0; }
    .chart-sub   { font-size: 0.75rem; color: #6b8fa8; margin:0 0 10px 0; }

    /* hide plotly modebar */
    .modebar { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
df = st.session_state.get("df", None)
if df is None:
    st.warning("⚠️ Go to **Results Table** first and apply your filters.")
    st.stop()
if df.empty:
    st.warning("⚠️ Filter returned 0 products. Adjust your filters.")
    st.stop()

plot_df = df.copy()

with st.sidebar:
    st.markdown("### 🔧 Filter by App ID")
    selected_ids = st.multiselect("", options=plot_df["ID"].tolist(), default=[], placeholder="All apps")
    if selected_ids:
        plot_df = plot_df[plot_df["ID"].isin(selected_ids)]

# ── KPI values ────────────────────────────────────────────────────────────────
total        = len(plot_df)
with_reviews = int((plot_df["Review_Count"] > 0).sum())
no_reviews   = int((plot_df["Review_Count"] == 0).sum())
max_rev      = int(plot_df["Review_Count"].max())
avg_rev      = round(plot_df["Review_Count"].mean(), 1)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<p style="font-size:1.4rem;font-weight:800;color:#ffffff;margin-bottom:2px">
  📊 ProductHunt Dashboard
</p>
<p style="font-size:0.82rem;color:#9ca3af;margin-bottom:16px">
  Mental Health AI · {total} products
</p>
""", unsafe_allow_html=True)

# ── KPI Cards row ─────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

kpis = [
    (k1, total,        "Total Products",  "#fff7ed", "#f97316", "🚀"),
    (k2, with_reviews, "Have Reviews",    "#fdf2f8", "#ec4899", "⭐"),
    (k3, no_reviews,   "No Reviews",      "#fffbeb", "#f59e0b", "🚫"),
    (k4, max_rev,      "Max Reviews",     "#fef3c7", "#d97706", "🏆"),
    (k5, avg_rev,      "Avg Reviews",     "#fff1f2", "#f43f5e", "📈"),
]

for col, val, label, bg, color, icon in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-left">
                <p class="kpi-value" style="color:{color}">{val}</p>
                <p class="kpi-label">{label}</p>
            </div>
            <div class="kpi-icon" style="background:{bg};color:{color}">{icon}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
BG   = "rgba(0,0,0,0)"
FONT = "#6b8fa8"
GRID = "#1e3547"
WARM = ["#f97316", "#ec4899", "#f59e0b", "#f43f5e", "#fb923c", "#f472b6", "#fbbf24"]

def base(h=270):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG, font_color=FONT,
        margin=dict(l=6, r=6, t=6, b=6), height=h, showlegend=False,
        xaxis=dict(gridcolor=GRID, zeroline=False, color=FONT),
        yaxis=dict(gridcolor=GRID, zeroline=False, color=FONT),
    )

def chart_card(title, sub):
    st.markdown(f"""
    <div class="chart-wrap">
        <p class="chart-title">{title}</p>
        <p class="chart-sub">{sub}</p>
    """, unsafe_allow_html=True)

def end_card():
    st.markdown("</div>", unsafe_allow_html=True)

# ── Row 1: Top 10 bar  |  Donut ───────────────────────────────────────────────
r1a, r1b = st.columns(2)

with r1a:
    chart_card("🏆 Top 10 Products by Reviews", "Most reviewed products in your filtered results")
    top10 = plot_df.nlargest(10, "Review_Count")[["Title", "Review_Count"]]
    fig1 = px.bar(top10, x="Review_Count", y="Title", orientation="h",
                  color="Review_Count",
                  color_continuous_scale=["#f59e0b", "#ec4899", "#f97316"],
                  labels={"Review_Count": "Reviews", "Title": ""})
    fig1.update_layout(**base(300))
    fig1.update_layout(coloraxis_showscale=False,
                       yaxis=dict(categoryorder="total ascending",
                                  tickfont=dict(size=10), gridcolor=GRID))
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)
    end_card()

with r1b:
    chart_card("🥧 Reviewed vs. Not Reviewed", "Share of products with at least 1 review")
    fig2 = px.pie(
        values=[with_reviews, no_reviews],
        names=["Has Reviews", "No Reviews"],
        color_discrete_sequence=["#f97316", "#1e3547"],
        hole=0.6,
    )
    fig2.update_layout(paper_bgcolor=BG, font_color=FONT, height=300,
                       margin=dict(l=6, r=6, t=6, b=6),
                       legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
    st.plotly_chart(fig2, use_container_width=True)
    end_card()

# ── Row 2: Histogram  |  Leaderboard ─────────────────────────────────────────
r2a, r2b = st.columns(2)

with r2a:
    chart_card("📈 Review Distribution", "How review counts spread across products")
    fig3 = px.histogram(plot_df, x="Review_Count", nbins=15,
                        color_discrete_sequence=["#ec4899"],
                        labels={"Review_Count": "Reviews", "count": "Products"})
    fig3.update_layout(**base(270))
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True)
    end_card()

with r2b:
    chart_card("🥇 Top 5 Leaderboard", "Products ranked by review count")
    top5   = plot_df.nlargest(5, "Review_Count")[["Title", "Review_Count"]].reset_index(drop=True)
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    colors = ["#f97316", "#ec4899", "#f59e0b", "#f43f5e", "#fb923c"]
    max_r  = plot_df["Review_Count"].max() or 1
    for i, row in top5.iterrows():
        pct = int(row["Review_Count"] / max_r * 100)
        st.markdown(f"""
        <div style="background:#111D26;border-radius:10px;padding:10px 14px;
                    margin-bottom:8px;border:1px solid #1e3547;">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="color:#e5e7eb;font-size:0.85rem">{medals[i]} {row['Title'][:30]}</span>
                <span style="color:{colors[i]};font-weight:800;font-size:0.95rem">{row['Review_Count']}</span>
            </div>
            <div style="background:#1e3547;border-radius:999px;height:5px;margin-top:6px">
                <div style="background:{colors[i]};width:{pct}%;height:5px;border-radius:999px"></div>
            </div>
        </div>""", unsafe_allow_html=True)
    end_card()

# ── Row 3: Word clouds ────────────────────────────────────────────────────────
r3a, r3b = st.columns(2)

def wc_panel(col, text, cmap, title, sub):
    with col:
        chart_card(title, sub)
        if text.strip():
            wc = WordCloud(width=600, height=260, background_color="#172832",
                           colormap=cmap, max_words=70, collocations=False).generate(text)
            fig_wc, ax = plt.subplots(figsize=(6, 2.6))
            fig_wc.patch.set_facecolor("#172832")
            ax.set_facecolor("#172832")
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig_wc)
        end_card()

wc_panel(r3a, " ".join(plot_df["Description"].dropna()),
         "YlOrRd", "☁️ Description Word Cloud", "Most frequent words in product descriptions")

wc_panel(r3b, " ".join(plot_df["Title"].dropna()),
         "autumn", "☁️ Title Word Cloud", "Most frequent words in product titles")