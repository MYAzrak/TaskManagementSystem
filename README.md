# Todo API (FastAPI + SQLite)

Minimal task service for a take-home:

-   Auth: Signup + OAuth2 Password login → JWT (`/token`)
-   Protected routes require **Authorization: Bearer <token>** + **X-API-Key: 123456**
-   DB: SQLite (file `app.db`)
-   Tests: `pytest`

## Quickstart (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: <http://127.0.0.1:8000/docs>

## Auth flow

1. Signup

```bash
curl -X POST http://127.0.0.1:8000/signup \
 -H "Content-Type: application/json" \
 -d "{\"username\":\"mya\",\"password\":\"s3cret\"}"
```

2. Token

```bash
curl -X POST http://127.0.0.1:8000/token \
 -H "Content-Type: application/x-www-form-urlencoded" \
 -d "username=mya&password=s3cret"
```

Response: `{ "access_token": "<JWT>", "token_type": "bearer" }`

## Tasks (JWT + API Key)

```bash
TOKEN="<JWT_FROM_PREV_STEP>"

# create
curl -X POST http://127.0.0.1:8000/tasks \
 -H "Authorization: Bearer $TOKEN" -H "X-API-Key: 123456" \
 -H "Content-Type: application/json" \
 -d "{\"title\":\"Buy milk\",\"description\":\"2%\"}"

# list
curl -H "Authorization: Bearer $TOKEN" -H "X-API-Key: 123456" \
 http://127.0.0.1:8000/tasks

# update
curl -X PUT http://127.0.0.1:8000/tasks/1 \
 -H "Authorization: Bearer $TOKEN" -H "X-API-Key: 123456" \
 -H "Content-Type: application/json" \
 -d "{\"status\":\"completed\"}"

# delete
curl -X DELETE http://127.0.0.1:8000/tasks/1 \
 -H "Authorization: Bearer $TOKEN" -H "X-API-Key: 123456"
```

## Tests

```bash
pytest -q
```
