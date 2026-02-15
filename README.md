# Career Growth MVP Backend

FastAPI backend that ingests resumes, extracts/normalizes skills, computes skill gaps for a target role, generates roadmap plans, and serves RAG learning recommendations.

## Stack
- Python 3.11, FastAPI, Pydantic v2
- Postgres + SQLAlchemy 2.0 + Alembic
- Redis + RQ async jobs
- Qdrant vector search

## Run
```bash
docker compose up --build
```

Backend: `http://localhost:8000` (OpenAPI at `/docs`)

API key header for all endpoints:
```text
X-API-Key: dev-api-key
```

## Seed data
On startup the API/worker run:
- `alembic upgrade head`
- `python scripts/load_seed.py`

This loads:
- skills
- roles + role requirements
- 20 learning items indexed in Qdrant

## Example API flow
```bash
curl -X POST http://localhost:8000/v1/users -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{}'

curl -X POST http://localhost:8000/v1/profiles -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{"user_id":"<USER_ID>"}'

curl -X POST http://localhost:8000/v1/profiles/<PROFILE_ID>/resume -H 'X-API-Key: dev-api-key' -F 'text=Python ML engineer with SQL and Docker experience'

curl -X POST http://localhost:8000/v1/profiles/<PROFILE_ID>/intake-check -H 'X-API-Key: dev-api-key'

curl -X POST http://localhost:8000/v1/profiles/<PROFILE_ID>/skills -H 'X-API-Key: dev-api-key'

curl http://localhost:8000/v1/jobs/<JOB_ID> -H 'X-API-Key: dev-api-key'

curl -X POST http://localhost:8000/v1/plans -H 'X-API-Key: dev-api-key' -H 'Content-Type: application/json' -d '{"user_id":"<USER_ID>","profile_id":"<PROFILE_ID>","target_role_id":1}'

curl -X POST http://localhost:8000/v1/plans/<PLAN_ID>/recommendations -H 'X-API-Key: dev-api-key'
```

## Job polling
`GET /v1/jobs/{job_id}` returns:
- `status`: queued | running | done | failed
- `progress`: 0..1
- `error`: error text if failed
- `result_ref`: plan/profile id

## Testing
```bash
pytest
```
