# European Railway Station Index 2026

Interactive Consumer Choice Center dashboard for comparing passenger convenience across 60 major European railway stations.

## Features

- Full 2026 station rankings
- Accent-insensitive city, country, and station search
- Individual station metrics and score breakdowns
- Two-station comparison with chart and accessible table
- Punctuality, waiting-time, country, and personalized-priority analysis
- Standalone finder embed mode: `?view=station-finder&embed=true`
- Responsive CCC 2026 design

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_2026_data.py
streamlit run app.py
```

The processed CSV is already included, so rebuilding it is only necessary after changing the source workbook.

## Data

- Source workbook: `data/raw/2026 European Railway Stations Index.xlsx`
- Processed dashboard data: `data/processed/stations_2026.csv`
- Data preparation: `scripts/build_2026_data.py`

The raw workbook is intentionally included and versioned in this public repository. The data preparation script applies the confirmed Frankfurt Main Hbf 2025 passenger-volume correction of `164.25 million`.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests cover city/station matching, accent normalization, score breakdowns, comparisons, and finder-only embed mode.

## Docker

Build the image from the repository root:

```bash
docker build -t ccc-european-railway-index-2026 .
```

The included `docker-compose.yml` follows the hardened production deployment and expects the external Docker network `archivebox_default`.

## Branding

The interface follows the CCC 2026 brand system, including Autumn Orange `#E95C1F`, Leila/Navy `#22264E`, Warm White `#FFF7EF`, Cool Mist `#E7ECF4`, and Montserrat/Hind typography. See `BRAND_IMPLEMENTATION.md` for details.
