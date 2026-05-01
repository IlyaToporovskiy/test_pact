# Contract Testing Demo (FastAPI + Pact)

Small demo project for contract testing:
- Provider API: FastAPI (`/health`, `GET /users/{id}`, `POST /users`)
- Consumer contract generation: Pactman mock server
- Provider verification: Pactman verifier against generated pact files

## 1) Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Run contract tests locally

Consumer tests (generate pact files in `pacts/`):

```powershell
pytest -q tests/consumer
```

Provider verification (auto-starts local provider unless `PROVIDER_BASE_URL` is set):

```powershell
pytest -q tests/provider
```

Run all:

```powershell
pytest -q
```

## 3) Run with Docker Compose

```powershell
docker compose up --build tests
```

This will:
1. build the image,
2. start provider API service,
3. wait for `/health`,
4. run consumer + provider contract tests in the `tests` container.

## Notes

- Pact files are stored in `pacts/`.
- In CI, run `pytest -q tests/consumer tests/provider` and keep `pacts/` as test artifacts if needed.
