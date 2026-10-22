from .schemas import LeadAnalysis, LeadInput


def draft_email(lead: LeadInput, analysis: LeadAnalysis) -> str:
    recipient = lead.customer_name or "there"
    company = f" from {lead.company_name}" if lead.company_name else ""
    questions = "\n".join(f"- {item}" for item in analysis.missing_information[:3])
    questions = questions or "- Are there any technical constraints or success criteria we should understand?"
    return f"""Subject: Re: Your {analysis.service_category} enquiry

Hi {recipient},

Thank you for reaching out to Cynbit{company}. From your note, it sounds like you are exploring {analysis.service_category.lower()} to address {analysis.business_problem.lower()}.

We would be happy to understand the context and suggest a sensible next step. To help us prepare, could you share:
{questions}

We have not assumed a budget or delivery commitment from the information provided. Once we have the details above, our team can review the opportunity and arrange a conversation.

Best regards,
Cynbit Technologies
"""
