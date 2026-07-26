# backend — API that serves the model

FastAPI service for PrivacyLens. Serves the response contract in
`specs/2_spec.md` §9 from a seeded stub, until the real model is wired in
(see `specs/5_backend_contract.md` for the full contract and rationale).

## Setup

1. Copy `backend/.env.example` to `backend/.env` and adjust
   `CORS_ALLOWED_ORIGINS` if needed (defaults to the Vite dev server,
   `http://localhost:5173`).
2. From the repository root: `uv sync`.

## Run

From the repository root:

```
uv run uvicorn backend.app.main:app --reload --port 8000
```

Port 8000 is required — the frontend's Vite dev proxy (`frontend/vite.config.js`)
forwards `/api/*` to `http://localhost:8000`.

## Try it

```
curl http://localhost:8000/api/health

curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"First paragraph about data collection.\n\nSecond paragraph about sharing with third parties.\"}"
```

Calling `/api/analyze` twice with the same text returns byte-identical
category/fragment scores (seeded stub).

## What's stubbed vs. real

| Piece | Status |
|---|---|
| `document`/`fragments` shape (§9 contract) | Real — frozen, won't change when the model lands |
| Category & fragment probabilities | **Stub**: seeded-random, not a trained model (`app/stub.py`) |
| `exposure` (the "semaforo") | **Placeholder**: fixed `medium`/`0.5`; weights aren't decided yet (2_spec §7) |
| `gdpr_reference` | **Placeholder**: always `"TODO"`; mapping not applied yet (2_spec §8) |
| Translation (`app/translation.py`) | **Wired, no-op**: language is detected, but nothing is actually translated yet |
| `{"url": ...}` requests | Returns `501` — footer scraping is a separate, not-yet-built layer (SSRF risk, 2_spec §11.1) |

## Errors

- Missing/empty `text` or text over 100,000 characters → `400` with
  `{"error": "<message>"}`.
- `url` without `text` → `501` (not implemented yet).
- Anything unexpected → `500` with `{"error": "Internal server error."}`,
  never a bare unhandled exception.
