# Local setup

## Python backend (Windows)

1. Create virtual environment:

```powershell
python -m venv .venv
```

2. Activate it:

```powershell
.\.venv\Scripts\activate
```

3. Install dependencies for local development:

```powershell
pip install -r requirements.dev.txt
```

4. Create env file for backend:

```powershell
copy backend\.env.example backend\.env
```

5. Run migrations and start server:

```powershell
cd backend
python manage.py migrate
python manage.py runserver
```

## Frontend

1. Install dependencies:

```powershell
cd frontend
npm install
```

2. Create env file for frontend:

```powershell
copy .env.example .env
```

3. Run Vite dev server:

```powershell
npm run dev
```

## Notes

- `requirements.txt` keeps production-style dependency `psycopg2`.
- `requirements.dev.txt` uses `psycopg2-binary` to avoid `pg_config` build issues on Windows.
- Backend settings read from environment variables (see `backend/.env.example`).
- Frontend API base URL is configured via `VITE_API_URL` (see `frontend/.env.example`).
