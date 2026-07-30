from fastapi import APIRouter

from ..analyze import analyze_text
from ..config import MAX_TEXT_LENGTH
from ..errors import BackendError
from ..fetcher import fetch_policy_text
from ..schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    text = request.text

    # No text but a URL: fetch the page and extract its text. The fetcher is a
    # separate layer with its own SSRF guards (2_spec.md section 11.1) and raises
    # readable BackendErrors of its own when the page cannot be read.
    if (not text or not text.strip()) and request.url:
        text = fetch_policy_text(request.url.strip())

    if not text or not text.strip():
        raise BackendError(400, "Provide either 'text' or 'url'.")

    if len(text) > MAX_TEXT_LENGTH:
        raise BackendError(400, f"Text exceeds the {MAX_TEXT_LENGTH} character limit.")

    return analyze_text(text)