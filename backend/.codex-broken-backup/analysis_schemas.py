from typing import Any

from core.schemas import StrictModel


# --------------- SECTION STATE ---------------

class AnalysisSectionState(StrictModel):
    status: str = "pending"
    result: dict[str, Any] | None = None
    error: str | None = None
    elapsed_seconds: float | None = None


# --------------- ANALYSIS STATE ---------------

class AnalysisSnapshot(StrictModel):
    analysis_id: str
    status: str
    filename: str
    finished_sections: int
    total_sections: int
    sections: dict[str, AnalysisSectionState]


class AnalysisStartResponse(StrictModel):
    analysis_id: str
    status: str
