from ..email_generator import draft_email
from ..prioritization import score_lead
from ..schemas import LeadAnalysis, LeadInput


def _service(lead: LeadInput) -> str:
    if lead.service_category and lead.service_category != "Not specified":
        return lead.service_category
    text = lead.enquiry_text.lower()
    matches = [("AI automation", ("ai", "agent", "llm", "automation")), ("Software development", ("app", "software", "platform", "website")), ("Cloud infrastructure", ("cloud", "aws", "azure", "migration")), ("Digital marketing & SEO", ("seo", "search", "leads"))]
    for name, words in matches:
        if any(word in text for word in words):
            return name
    return "Needs discovery"


class DemoProvider:
    name = "Deterministic demo mode"

    def analyze(self, lead: LeadInput) -> LeadAnalysis:
        score, priority, rationale = score_lead(lead)
        service = _service(lead)
        text = lead.enquiry_text.strip()
        requirements = [sentence.strip() for sentence in text.replace("!", ".").split(".") if len(sentence.strip()) > 12][:4]
        missing = []
        if lead.budget in {"", "Unknown", "Not specified"}: missing.append("Budget range or procurement constraints")
        if lead.timeline in {"", "Unknown", "Not specified"}: missing.append("Desired timeline or milestone")
        if not lead.company_name: missing.append("Company and project context")
        analysis = LeadAnalysis(summary=text[:240], business_problem="The enquiry describes a need that requires further discovery.", service_category=service, requirements=requirements, budget=lead.budget or "Unknown", timeline=lead.timeline or "Unknown", priority=priority, priority_rationale=rationale, confidence=round(min(0.92, 0.45 + score / 180), 2), missing_information=missing, recommended_next_action="Human review, then ask the missing discovery questions before proposing scope.", follow_up_email="")
        analysis.follow_up_email = draft_email(lead, analysis)
        return analysis
