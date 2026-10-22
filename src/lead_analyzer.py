from .providers.demo_provider import DemoProvider
from .providers.llm_provider import LLMProvider, _has_explicit_budget, _has_explicit_timeline
from .prioritization import score_lead
from .schemas import LeadAnalysis, LeadInput


def analyze_lead(lead: LeadInput, use_llm: bool = False) -> tuple[LeadAnalysis, str]:
    if use_llm:
        try:
            analysis = LLMProvider().analyze(lead)
            score, priority, rationale = score_lead(lead)
            analysis.score = score
            analysis.priority = priority
            analysis.priority_rationale = rationale
            if lead.budget in {"", "Unknown", "Not specified"} and not _has_explicit_budget(lead.enquiry_text):
                analysis.budget = "Unknown"
            if lead.timeline in {"", "Unknown", "Not specified"} and not _has_explicit_timeline(lead.enquiry_text):
                analysis.timeline = "Unknown"
            return analysis, "LLM mode"
        except RuntimeError:
            pass
    return DemoProvider().analyze(lead), "Demo mode (deterministic fallback)"
