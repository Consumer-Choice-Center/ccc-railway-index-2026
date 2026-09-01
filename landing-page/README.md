# European Railway Stations Index 2026

Landing page portion of the dashboard for exploring the 2026 European Railway Stations Index.

This section of the dashboard compares major European railway stations across passenger-facing measures, including overall station score, passenger volume, delayed trains, and average waiting time.

## Features

- Searchable European station rankings
- Station and country-level comparisons
- Punctuality and waiting-time analysis
- Interactive charts and data tooltips
- Transparent scoring and methodology notes
- Responsive Consumer Choice Center interface

## Data

The dashboard uses the processed research dataset located at:

`data/processed/stations_2026.csv`

The underlying research workbook is excluded from the public repository.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
