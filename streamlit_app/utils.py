import json
import pandas as pd
import streamlit as st
from transformers import pipeline


@st.cache_data
def load_data(json_path: str = "results.json") -> pd.DataFrame:
    """
    Load scraped ProductHunt data from results.json.
    Cached so the file is only read once per session.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        df = pd.DataFrame(raw)

        # Parse "42 reviews" → integer for sorting/charting
        if "Reviews" in df.columns:
            df["Review_Count"] = (
                df["Reviews"]
                .str.extract(r"(\d+)")
                .astype(float)
                .fillna(0)
                .astype(int)
            )

        return df

    except FileNotFoundError:
        st.error("❌ results.json not found. Make sure it's in the same folder as Home.py.")
        return pd.DataFrame()

    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse results.json: {e}")
        return pd.DataFrame()


def filter_data(df: pd.DataFrame, keyword: str = "", min_reviews: int = 0) -> pd.DataFrame:
    """Filter the DataFrame by keyword and minimum review count."""
    if df.empty:
        return df

    if keyword:
        mask = (
            df["Title"].str.contains(keyword, case=False, na=False)
            | df["Description"].str.contains(keyword, case=False, na=False)
        )
        df = df[mask]

    if min_reviews > 0:
        df = df[df["Review_Count"] >= min_reviews]

    return df


# ============================================================
# Partie D : Sentiment Analysis
# ============================================================
# results.json ne contient pas le texte des reviews (juste un
# compte, ex: "15 reviews"), donc l'analyse de sentiment est
# faite sur la Description de chaque app.

@st.cache_resource
def load_sentiment_model():
    """
    Charge le pipeline de sentiment analysis HuggingFace.
    Modèle: nlptown/bert-base-multilingual-uncased-sentiment
    -> renvoie un label "1 star" à "5 stars" + un score de confiance.
    Mis en cache avec @st.cache_resource pour ne charger le modèle
    qu'une seule fois par session (pas à chaque rerun Streamlit).
    """
    classifier = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment"
    )
    return classifier


def get_app_text(df: pd.DataFrame, app_id: str) -> str:
    """
    Récupère le texte (Description) d'une app à partir de son ID.
    """
    row = df[df["ID"] == str(app_id)]
    if row.empty:
        return ""
    return str(row.iloc[0]["Description"])


def compute_sentiment(text: str) -> dict:
    """
    Calcule le sentiment d'un texte avec le modèle HuggingFace.
    Retourne un dict avec:
      - label brut du modèle ("1 star" ... "5 stars")
      - score de confiance (0-1)
      - catégorie simplifiée (Negative / Neutral / Positive)
      - score numérique normalisé entre -1 et 1
    """
    if not text or not text.strip():
        return {
            "label": "N/A",
            "confidence": 0.0,
            "category": "Neutral",
            "score": 0.0
        }

    classifier = load_sentiment_model()
    result = classifier(text[:512])[0]  # tronque à 512 tokens max
    label = result["label"]          # ex: "4 stars"
    confidence = result["score"]

    # Le modèle renvoie 1 à 5 étoiles -> on simplifie en 3 catégories
    stars = int(label[0])
    if stars <= 2:
        category = "Negative"
    elif stars == 3:
        category = "Neutral"
    else:
        category = "Positive"

    # Score normalisé : 1 star -> -1.0 ... 5 stars -> +1.0
    normalized_score = (stars - 3) / 2

    return {
        "label": label,
        "confidence": confidence,
        "category": category,
        "score": normalized_score
    }


@st.cache_data
def compute_sentiment_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule le sentiment pour chaque app du DataFrame (basé sur sa
    Description) et retourne un nouveau DataFrame avec les colonnes
    ajoutées: Sentiment_Label, Sentiment_Category, Sentiment_Score.
    Mis en cache car l'inférence du modèle est coûteuse.
    """
    if df.empty:
        return df

    results = df["Description"].fillna("").apply(compute_sentiment)

    df = df.copy()
    df["Sentiment_Label"] = results.apply(lambda r: r["label"])
    df["Sentiment_Category"] = results.apply(lambda r: r["category"])
    df["Sentiment_Score"] = results.apply(lambda r: r["score"])
    df["Sentiment_Confidence"] = results.apply(lambda r: r["confidence"])

    return df