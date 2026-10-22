from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Priority = Literal["High", "Medium", "Low", "Unknown"]


class LeadInput(BaseModel):
    customer_name: str = Field(default="", max_length=120)
    company_name: str = Field(default="", max_length=160)
    enquiry_text: str = Field(min_length=10, max_length=8000)
    service_category: str = Field(default="Not specified", max_length=100)
    budget: str = Field(default="Unknown", max_length=120)
    timeline: str = Field(default="Unknown", max_length=120)

    @field_validator("customer_name", "company_name", "service_category", "budget", "timeline", mode="before")
    @classmethod
    def clean_optional_text(cls, value):
        return str(value or "").strip()

    @field_validator("enquiry_text")
    @classmethod
    def clean_enquiry(cls, value):
        value = str(value).strip()
        if len(value) < 10:
            raise ValueError("Enquiry must contain at least 10 characters.")
        return value


class LeadAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    business_problem: str
    service_category: str
    requirements: list[str] = Field(default_factory=list)
    budget: str = "Unknown"
    timeline: str = "Unknown"
    priority: Priority = "Unknown"
    priority_rationale: str
    confidence: float = Field(ge=0, le=1)
    missing_information: list[str] = Field(default_factory=list)
    recommended_next_action: str
    follow_up_email: str
    score: int = Field(default=0, ge=0, le=100)
    follow_up_status: Literal["Needs review", "Contacted", "Qualified", "Closed"] = "Needs review"


class StoredLead(LeadInput):
    id: int | None = None
    created_at: str | None = None
    analysis: LeadAnalysis
