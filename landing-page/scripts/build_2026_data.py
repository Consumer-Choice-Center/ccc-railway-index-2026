from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "2026 European Railway Stations Index.xlsx"
OUT = ROOT / "data" / "processed" / "stations_2026.csv"

def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Raw workbook not found: {RAW}")

    # The source-data page in Emil's workbook.
    df = pd.read_excel(RAW, sheet_name="Research", engine="openpyxl")

    # Keep only actual station rows.
    # The first three fields in the research sheet are Country, City, Railway Station.
    df = df[df.iloc[:, 2].notna()].copy()

    # Build a clean public-facing extract by source-column position.
    # These correspond to the 2026 Research tab structure.
    source_positions = {
        "country": 0,
        "city": 1,
        "station": 2,
        "passenger_volume_latest": 3,
        "passenger_volume_2025": 4,
        "passenger_volume_2024": 5,
        "operating_hours_score": 7,
        "ticket_score": 9,
        "wait_minutes_2026": 10,
        "wait_score": 11,
        "delay_percent_2026": 12,
        "delay_score": 13,
        "information_score": 15,
        "elevators_score": 17,
        "accessibility_score": 20,
        "shops_count": 21,
        "shops_score": 22,
        "restaurants_count": 23,
        "restaurants_score": 24,
        "lounge_score": 26,
        "application_score": 28,
        "wifi_score": 30,
        "connections_score": 32,
        "competition_score": 34,
        "ride_hailing_score": 36,
        "total_score": 37,
    }

    clean = pd.DataFrame({
        new_name: df.iloc[:, pos]
        for new_name, pos in source_positions.items()
    })

    # Remove invisible leading/trailing whitespace so locations group correctly.
    for col in {"country", "city", "station"}:
        clean[col] = (
            clean[col]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Confirmed normalization from Emil:
    # Frankfurt Main Hbf's 2025 value is 164.25 million, not 164,250 million.
    frankfurt = clean["station"].astype(str).eq("Frankfurt Main Hbf")
    clean.loc[frankfurt, "passenger_volume_2025"] = 164.25

    # Numeric conversion where appropriate.
    for col in clean.columns:
        if col not in {"country", "city", "station"}:
            clean[col] = pd.to_numeric(clean[col], errors="coerce")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(OUT, index=False, encoding="utf-8")
    print(f"Wrote {len(clean)} station rows to {OUT}")

if __name__ == "__main__":
    main()
