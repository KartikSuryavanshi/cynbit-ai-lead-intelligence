import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .schemas import LeadInput, LeadAnalysis


class LeadStore:
    def __init__(self, path: str = "data/leads.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init(self):
        with self._connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, customer_name TEXT, company_name TEXT, enquiry_text TEXT NOT NULL, service_category TEXT, budget TEXT, timeline TEXT, analysis_json TEXT NOT NULL, UNIQUE(enquiry_text, company_name))")

    def save(self, lead: LeadInput, analysis: LeadAnalysis) -> int:
        import json
        with self._connect() as conn:
            cursor = conn.execute("INSERT OR REPLACE INTO leads (created_at, customer_name, company_name, enquiry_text, service_category, budget, timeline, analysis_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (datetime.now(timezone.utc).isoformat(), lead.customer_name, lead.company_name, lead.enquiry_text, lead.service_category, lead.budget, lead.timeline, analysis.model_dump_json()))
            return int(cursor.lastrowid)

    def all(self):
        import json
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
        return [{**dict(row), "analysis": json.loads(row["analysis_json"])} for row in rows]

    def reset(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM leads")
