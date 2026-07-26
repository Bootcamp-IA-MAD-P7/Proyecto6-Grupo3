"""Error format for the API: every deliberate error is {"error": "<message>"},
never a bare 500 (specs/5_backend_contract.md, FORMATO DE ERROR)."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class BackendError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BackendError)
    async def handle_backend_error(request: Request, exc: BackendError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"error": "Internal server error."})
