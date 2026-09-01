# European Railway Station Index 2026 — Complete Local Starter

This package now contains:

- the **actual 2026 Excel research workbook** in `data/raw/`;
- a real `scripts/build_2026_data.py` data-cleaning script;
- non-empty Streamlit component modules;
- `app.py`;
- styles and configuration;
- a processed-data workflow.

## First run

From the project folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/build_2026_data.py
streamlit run app.py
```

## Important

The raw workbook is included in this ZIP so you can work locally, but `.gitignore`
is configured so `data/raw/` is **not uploaded to GitHub by accident**.

### Confirmed data correction
Frankfurt Main Hbf 2025 passenger volume:
`164.25 million`.

## CCC 2026 branding
The UI is now aligned to the 2026 CCC brand guide:
- Autumn Orange `#E95C1F`
- Leila/Navy `#22264E`
- Warm White `#FFF7EF`
- Cool Mist `#E7ECF4`
- approved tertiary chart palette
- Montserrat/Hind typography

See `BRAND_IMPLEMENTATION.md` for details.

## Editorial interface update
See `WHAT_CHANGED.md` for the exact files to replace in the previous version.
