# Todo API (FastAPI + SQLite)

Minimal task service for a take-home:

-   Auth: Signup + OAuth2 Password login → JWT (`/token`)
-   Protected routes require **Authorization: Bearer <token>** + **X-API-Key: 123456**
-   DB: SQLite (file `app.db`)
-   Tests: `pytest`

## Project layout

```
├─ app/
│  ├─ main.py            # app factory + router includes
│  ├─ models.py          # SQLAlchemy ORM models
│  ├─ database.py        # engine/session & get_db
│  ├─ schemas.py         # Pydantic models
│  ├─ security.py        # hashing + JWT helpers
│  ├─ deps.py            # common FastAPI dependencies (auth, API key)
│  └─ routers/
│     ├─ auth.py         # /signup, /token
│     └─ tasks.py        # /tasks endpoints
└─ tests/                # pytest suite
```

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

## Deployment (Render)

Live URL: https://taskmanagementsystem-v2bw.onrender.com/

This app is deploy-ready on Render's Free plan.

**Service settings**

-   Build command: `pip install --upgrade pip && pip install -r requirements.txt`
-   Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
-   Health check path: `/health`
-   Environment variables:
    -   `SECRET_KEY`
    -   `API_KEY`
    -   (`PORT` is provided by Render automatically)

**Notes**

-   Free instances sleep after inactivity → first request may be slow ("cold start").
-   SQLite is ephemeral on Free plan → the database can reset on redeploy/restart/sleep.
-   Docs are at `/docs`. Auth uses OAuth2 Password (get a JWT from `/token`) and
    all task routes also require `X-API-Key: 123456`.

**Basic smoke test**

```bash
# health
curl https://taskmanagementsystem-v2bw.onrender.com/health

# signup
curl -X POST https://taskmanagementsystem-v2bw.onrender.com/signup \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"mya\",\"password\":\"s3cret\"}"

# token
curl -X POST https://taskmanagementsystem-v2bw.onrender.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=mya&password=s3cret"
# => {"access_token":"<JWT>","token_type":"bearer"}

# create task (JWT + API key)
TOKEN="<JWT_FROM_ABOVE>"
curl -X POST https://taskmanagementsystem-v2bw.onrender.com/tasks \
  -H "Authorization: Bearer $TOKEN" -H "X-API-Key: 123456" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Buy milk\",\"description\":\"2%\"}"
```
