from fastapi import APIRouter

from ..analyze import analyze_text
from ..config import MAX_TEXT_LENGTH
from ..errors import BackendError
from ..schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    text = request.text

    if not text or not text.strip():
        if request.url:
            raise BackendError(
                501,
                "Analyzing a policy by URL is not implemented yet (footer "
                "scraping is a separate, not-yet-built layer — SSRF risk, "
                "see 2_spec.md section 11.1). Provide 'text' instead.",
            )
        raise BackendError(400, "The 'text' field is required and cannot be empty.")

    if len(text) > MAX_TEXT_LENGTH:
        raise BackendError(400, f"Text exceeds the {MAX_TEXT_LENGTH} character limit.")

    return analyze_text(text)
