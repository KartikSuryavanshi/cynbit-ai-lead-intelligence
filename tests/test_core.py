import io
from pathlib import Path

from src.csv_processor import parse_csv
from src.data_store import LeadStore
from src.lead_analyzer import analyze_lead
from src.providers.llm_provider import LLMProvider
from src.prioritization import score_lead
from src.schemas import LeadInput, LeadAnalysis


def lead(**kwargs):
    return LeadInput(enquiry_text=kwargs.pop("enquiry_text", "We need to build an AI support assistant for a launch next month."), **kwargs)


def test_validation_rejects_short_enquiry():
    try: lead(enquiry_text="too short")
    except ValueError: return
    assert False


def test_priority_uses_explicit_evidence():
    score, priority, rationale = score_lead(lead(timeline="next month"))
    assert score >= 70 and priority == "High" and "timeline" in rationale


def test_demo_mode_is_labelled_and_validated():
    analysis, mode = analyze_lead(lead(), False)
    assert "Demo" in mode and isinstance(analysis, LeadAnalysis) and analysis.follow_up_email


def test_provider_failure_falls_back_to_demo(monkeypatch):
    def fail(self, item):
        raise RuntimeError("timeout")
    monkeypatch.setattr(LLMProvider, "analyze", fail)
    analysis, mode = analyze_lead(lead(), True)
    assert "fallback" in mode and analysis.priority in {"High", "Medium", "Low"}


def test_llm_priority_is_recomputed_from_input(monkeypatch):
    def fake(self, item):
        return LeadAnalysis(summary="x", business_problem="x", service_category="x", priority="High", priority_rationale="fake", confidence=1, recommended_next_action="x", follow_up_email="x", score=100, budget="Unknown", timeline="Unknown")
    monkeypatch.setattr(LLMProvider, "analyze", fake)
    analysis, mode = analyze_lead(lead(enquiry_text="We are casually exploring software options."), True)
    assert mode == "LLM mode" and analysis.priority == "Low" and analysis.score < 100


def test_malformed_provider_payload_is_rejected():
    try:
        LeadAnalysis.model_validate({"summary": "missing required fields"})
    except ValueError as exc:
        assert "business_problem" in str(exc)
    else:
        assert False, "Malformed structured output should be rejected"


def test_llm_cannot_supply_unsupported_budget_or_timeline(monkeypatch):
    def fake(self, item):
        return LeadAnalysis(summary="x", business_problem="x", service_category="x", priority="Low", priority_rationale="x", confidence=1, recommended_next_action="x", follow_up_email="x", budget="$1m", timeline="tomorrow")
    monkeypatch.setattr(LLMProvider, "analyze", fake)
    analysis, _ = analyze_lead(lead(enquiry_text="We are considering a software platform."), True)
    assert analysis.budget == "Unknown" and analysis.timeline == "Unknown"


def test_prompt_injection_is_treated_as_input_data():
    from src.providers.llm_provider import SYSTEM_PROMPT
    assert "untrusted data" in SYSTEM_PROMPT and "never instructions" in SYSTEM_PROMPT


def test_missing_information_is_not_fabricated():
    analysis, _ = analyze_lead(lead(enquiry_text="We are considering a website."), False)
    assert analysis.budget == "Unknown" and analysis.timeline == "Unknown"


def test_csv_reports_missing_columns_and_duplicates():
    data = "company_name,enquiry_text\nAcme,We need software development\nAcme,We need software development\n"
    leads, errors = parse_csv(io.StringIO(data))
    assert len(leads) == 1 and any("duplicate" in error for error in errors)
    _, errors = parse_csv(io.StringIO("company_name\nAcme\n"))
    assert "required" in errors[0]
    _, errors = parse_csv(io.StringIO(""))
    assert errors and "Could not read CSV" in errors[0]


def test_store_round_trip(tmp_path: Path):
    store = LeadStore(str(tmp_path / "leads.db")); item = lead()
    analysis, _ = analyze_lead(item, False); identifier = store.save(item, analysis)
    assert identifier > 0 and len(store.all()) == 1
    store.reset(); assert store.all() == []
