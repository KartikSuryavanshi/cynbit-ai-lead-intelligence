# Cynbit AI Lead Intelligence & Follow-up Assistant

Submission-ready Streamlit proof of concept for the Cynbit AI/ML Engineer Intern assessment. It turns inbound enquiries into validated requirements, transparent priority signals, and a human-reviewable follow-up draft.

## Features

- Dashboard metrics, filtering, search, service distribution, and recent leads.
- Pydantic-validated intake and structured analysis.
- Deterministic, labelled demo mode with no API key required.
- Optional LLM adapter with JSON output validation and timeout handling.
- Editable follow-up drafts with a reviewer download action; no outbound send action.
- CSV validation, duplicate reporting, batch analysis, and export.
- SQLite persistence with reset available through the data layer.
- Synthetic sample data and tests with no API calls.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL, use the CSV batch tab to load `data/sample_leads.csv`, or enter an enquiry. Demo mode is the default. Run tests with `pytest -q`.

## Configuration

Copy `.env.example` to `.env` for local reference, or export variables in the shell. `OPENAI_API_KEY` and optional `OPENAI_MODEL` enable the provider checkbox; the current app does not load `.env` automatically, so use `set -a; source .env; set +a` locally or configure deployment secrets. Never commit secrets.

## Screenshots

Run the app, load the synthetic sample CSV, and capture the Dashboard, Analyse enquiry result, and CSV export screens. Store reviewer screenshots outside the repository or add them under `docs/screenshots/` if desired.

## Architecture and reports

See `reports/ai_opportunity_report.md`, `reports/technical_approach.md`, and `reports/implementation_roadmap.md`. The app is intentionally a single Streamlit process with provider, scoring, schema, CSV, and persistence modules.

## Deployment

For Streamlit Community Cloud, select this repository, set the main file to `app.py`, and choose **Python 3.12** in **Advanced settings → Python version** before deploying. Community Cloud controls this version in the deployment settings; do not rely on `runtime.txt` or `.python-version`. For an existing app currently configured for Python 3.14, change the setting and redeploy (Community Cloud may require deleting and recreating the app to change its Python version). The pinned dependencies have been verified in a clean Python 3.12 environment using binary wheels, including pandas and Pillow. Add `OPENAI_API_KEY`/`OPENAI_MODEL` under App settings → Secrets if needed. Without secrets it runs in demo mode. SQLite storage is local/ephemeral on many hosted platforms; use a managed database before multi-user production.

To reset local demonstration data, stop the app and remove only `data/leads.db`; it is recreated automatically on the next launch.

## Security and limitations

No automatic emails are sent. Do not upload real personal or confidential data to the demo. Unknown fields are not guessed, but this is not a production privacy system. There is no authentication, CRM integration, formal accuracy/fairness evaluation, or production monitoring.

## Exact publish commands (not executed)

```bash
git add .
git commit -m "Build Cynbit AI lead intelligence proof of concept"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```
