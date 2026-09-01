from pathlib import Path
import pandas as pd
import streamlit as st

PROCESSED_DATA = Path(__file__).resolve().parents[1] / "data" / "processed" / "stations_2026.csv"

@st.cache_data
def load_stations():
    if not PROCESSED_DATA.exists():
        raise FileNotFoundError(
            "Processed data is missing. Run: python scripts/build_2026_data.py"
        )

    df = pd.read_csv(PROCESSED_DATA)
    for c in {"country", "city", "station"}:
        df[c] = (
            df[c]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    numeric_cols = [c for c in df.columns if c not in {"country", "city", "station"}]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["rank_2026"] = (
        df["total_score"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    return df
