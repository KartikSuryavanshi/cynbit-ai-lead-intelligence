from typing import Protocol

from ..schemas import LeadAnalysis, LeadInput


class AnalysisProvider(Protocol):
    name: str

    def analyze(self, lead: LeadInput) -> LeadAnalysis: ...
