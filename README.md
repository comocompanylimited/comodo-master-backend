# COMODO MASTER BACKEND

Production-ready FastAPI ecommerce backend.

## Stack
- FastAPI + Uvicorn
- PostgreSQL + SQLAlchemy 2.0
- Alembic migrations
- JWT authentication
- Pydantic v2

## Setup

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY

pip install -r requirements.txt

alembic upgrade head
python seed.py

uvicorn main:app --host 0.0.0.0 --port 8000
```

## Zeabur Deployment

1. Push to GitHub
2. Create Zeabur project → New Service → GitHub repo
3. Add environment variables from `.env.example`
4. Add PostgreSQL service in Zeabur — copy `DATABASE_URL` to env vars
5. Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

After first deploy, run migrations:
```
alembic upgrade head
python seed.py
```

## API Docs
`/api/docs` — Swagger UI  
`/api/redoc` — ReDoc  
`/health` — Health check

## Auth
`POST /api/v1/auth/login` — returns JWT bearer token  
`POST /api/v1/auth/register` — create user  
`GET /api/v1/auth/me` — current user

Seed admin: `admin@covora.com` / `Admin1234!`

## Roles
`super_admin` → `admin` → `manager` → `staff` → `read_only`
