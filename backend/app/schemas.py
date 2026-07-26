"""Pydantic models for the API contract.

Source of truth: specs/2_spec.md §9 (contrato de salida), pinned for the API
by specs/5_backend_contract.md. Do not change field names or drop fields here
without updating §9 first.
"""

from pydantic import BaseModel, ConfigDict


class Label(BaseModel):
    id: str
    score: float


class Fragment(BaseModel):
    id: int
    text: str
    start: int
    end: int
    labels: list[Label]


class Category(BaseModel):
    id: str
    present: bool
    confidence: float
    fragment_count: int
    gdpr_reference: str


class Exposure(BaseModel):
    level: str
    score: float
    disclaimer: str


class Document(BaseModel):
    source_language: str
    translated: bool
    translation_available: bool
    exposure: Exposure
    categories: list[Category]
    fragment_count: int


class AnalyzeResponse(BaseModel):
    # protected_namespaces=() lets us keep the contract's `model_version` field
    # name as-is instead of renaming it away from pydantic's reserved `model_*`.
    model_config = ConfigDict(protected_namespaces=())

    model_version: str
    stub: bool
    document: Document
    fragments: list[Fragment]


class AnalyzeRequest(BaseModel):
    text: str | None = None
    url: str | None = None


class HealthResponse(BaseModel):
    status: str
