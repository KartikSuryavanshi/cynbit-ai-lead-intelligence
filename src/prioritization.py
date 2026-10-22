import re

from .schemas import LeadInput


URGENCY = ("urgent", "asap", "immediately", "this week", "deadline", "launch")
CONCRETE = ("need", "build", "migrate", "automate", "develop", "integrate", "audit", "deploy")
RELEVANT = ("ai", "software", "web", "mobile", "cloud", "seo", "automation", "saas", "agent")


def score_lead(lead: LeadInput) -> tuple[int, str, str]:
    text = lead.enquiry_text.lower()
    score = 0
    evidence: list[str] = []
    urgency = [term for term in URGENCY if term in text or term in lead.timeline.lower()]
    if urgency:
        score += 30
        evidence.append(f"explicit urgency ({', '.join(urgency[:2])})")
    if lead.timeline.lower() not in {"", "unknown", "not specified"}:
        score += 15
        evidence.append("a timeline was provided")
    concrete = [term for term in CONCRETE if re.search(rf"\b{re.escape(term)}\w*\b", text)]
    if concrete:
        score += 25
        evidence.append("a concrete project action is described")
    relevant = [term for term in RELEVANT if term in text or term in lead.service_category.lower()]
    if relevant:
        score += 15
        evidence.append("the request maps to Cynbit's published service areas")
    if len(text.split()) >= 35:
        score += 15
        evidence.append("requirements contain useful detail")
    score = min(score, 100)
    priority = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    rationale = "; ".join(evidence) if evidence else "The enquiry does not contain enough evidence for a stronger priority."
    return score, priority, rationale
