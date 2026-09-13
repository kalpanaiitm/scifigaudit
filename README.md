# SciFigAudit

SciFigAudit is a free, open-source, privacy-conscious preflight checker for scientific figures. It provides explainable technical and accessibility signals plus a human-review checklist before journal, thesis, poster, or conference submission.

## What it checks

- pixel dimensions and available DPI metadata
- luminance range and dominant-colour separation
- possible edge-clipping signals
- presence of a user-written figure description
- essential items that still require human inspection

Every automated result includes evidence. The score is a heuristic preparation indicator—not journal approval or a rating of scientific quality.

## Privacy by design

- image bytes are processed in the active application session
- the app creates no upload directory or database
- filenames and image contents are not intentionally logged
- uploads are limited to 10 MB and supported image signatures are validated
- a fictional downloadable sample allows testing without real research data

Hosting infrastructure may create operational metadata outside the application's control. Do not upload confidential, unpublished, personal, export-controlled, legally privileged, or commercially sensitive figures to the public demonstration.

## Important limitations

SciFigAudit does not read axis text, detect fabrication or manipulation, validate scientific conclusions, guarantee accessibility, or predict journal acceptance. Requirements vary between journals and can change. Always inspect the figure at final size and consult the selected journal's current instructions.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Test

```bash
pytest -q
```

## Licence

MIT. Third-party trademarks and journal guidance remain the property of their respective owners.

