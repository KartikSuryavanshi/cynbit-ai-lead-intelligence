import io
import pandas as pd

from .schemas import LeadInput

REQUIRED = {"enquiry_text"}


def parse_csv(uploaded_file) -> tuple[list[LeadInput], list[str]]:
    try:
        df = pd.read_csv(uploaded_file if hasattr(uploaded_file, "read") else io.StringIO(uploaded_file))
    except Exception as exc:
        return [], [f"Could not read CSV: {exc}"]
    df.columns = [str(column).strip().lower() for column in df.columns]
    missing = REQUIRED - set(df.columns)
    if missing:
        return [], [f"Missing required column(s): {', '.join(sorted(missing))}"]
    leads, errors = [], []
    seen = set()
    for index, row in df.fillna("").iterrows():
        values = {key: str(row.get(key, "")).strip() for key in ["customer_name", "company_name", "enquiry_text", "service_category", "budget", "timeline"]}
        key = (values["company_name"].lower(), values["enquiry_text"].lower())
        if key in seen:
            errors.append(f"Row {index + 2}: duplicate skipped")
            continue
        try:
            leads.append(LeadInput(**values)); seen.add(key)
        except Exception as exc:
            errors.append(f"Row {index + 2}: {exc}")
    return leads, errors
