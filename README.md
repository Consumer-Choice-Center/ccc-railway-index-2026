# CCC European Railway Station Index 2026

**Interactive application and publication:** [consumerchoicecenter.org/european-railway-station-index-2026](https://consumerchoicecenter.org/european-railway-station-index-2026/)

This repository contains the source code, methodology workflow, and published research data supporting the Consumer Choice Center's **European Railway Station Index 2026**. The index compares passenger convenience across 60 major European railway stations using measures including delays, waiting times, ticket options, accessibility, station services, connectivity, competition, Wi-Fi, and ride-hailing availability.

Use the CCC publication page for the full interactive experience, report, and project context. This repository provides the technical and research record behind the application and published results.

## Explore the application

The dashboard includes:

- Complete 2026 station rankings
- Accent-insensitive search by station, city, or country
- Individual station metrics and score breakdowns
- Side-by-side station comparison
- Punctuality, waiting-time, country, and personalized-priority analysis
- Accessible data tables and a standalone station-finder embed mode

The application source is in [`railway-final/`](railway-final/).

## Run locally

```bash
cd railway-final
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/build_2026_data.py
python3 -m streamlit run app.py
```

The processed CSV is included, so rebuilding it is only necessary after changing the source workbook.

## Index interpretation

The overall score combines measures of passenger convenience and station performance. Higher scores indicate stronger performance under the published framework. Rankings are comparative and quantitative; they are not a judgment of a station's broader social value or every passenger's individual experience.

The station finder presents each station's headline result, its component-level score breakdown, and comparisons with another European rail hub. Personalized results are exploratory and do not alter the official index rankings.

## Data files

- `railway-final/data/raw/2026 European Railway Stations Index.xlsx`: source research workbook
- `railway-final/data/processed/stations_2026.csv`: processed 60-station dashboard dataset
- `railway-final/scripts/build_2026_data.py`: reproducible data-preparation workflow

Rebuild the processed dataset with:

```bash
cd railway-final
python3 scripts/build_2026_data.py
```

## Tests

```bash
cd railway-final
python3 -m unittest discover -s tests -v
```

The tests cover station matching, accent normalization, score breakdowns, comparisons, and finder-only embed mode.

## Docker

```bash
cd railway-final
docker build -t ccc-european-railway-index-2026 .
```

The included `docker-compose.yml` reflects the production deployment and expects the external Docker network `archivebox_default`.

## Research caution

The index relies on heterogeneous data that may be outdated, contradictory, or measured differently across countries. Network coverage estimates are also imperfect. Results should therefore be read as quantitative, non-normative assessments based on the best information available at the time of publication in August 2026.

Please report sourced research or data corrections through this repository's issue tracker. General enquiries about the project should be directed to the [Consumer Choice Center](https://consumerchoicecenter.org/european-railway-station-index-2026/).

