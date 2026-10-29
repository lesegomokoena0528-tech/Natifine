# NatiFine SA — Digital Traffic Fines Management System

NatiFine SA is an **academic prototype** for managing South African traffic fines.
It consists of a **Flask REST API** (`backend/`) and a **plain HTML/CSS/JS frontend**
(`frontend/`, no build tool). Payments, SMS, WhatsApp and email are **simulated**.

- Backend: Flask 3.1 + SQLAlchemy + MySQL (PyMySQL) + Flask-Migrate, JWT auth.
- Frontend: static site (vanilla JS), currently served by Flask locally.
- Production target: **Vercel Services** (frontend + Flask API) + **Vercel
  Postgres/Neon** + **Vercel Blob**.

> This project is not connected to any real government or payment infrastructure.

---

## 1. Project structure

```
NatiFine/
├── backend/                 Flask application
│   ├── app/
│   │   ├── factory.py       create_app() factory (entry point)
│   │   ├── config/          settings.py, database.py, mail.py
│   │   ├── controllers/     request handlers
│   │   ├── services/        business logic
│   │   ├── repositories/    data access
│   │   ├── models/          SQLAlchemy models
│   │   ├── routes/          blueprints (/api/*)
│   │   ├── schemas/         marshmallow schemas
│   │   └── middleware/      auth + role guards
│   ├── migrations/          Alembic migrations
│   ├── tests/               pytest suite
│   ├── docs/                swagger config + postman collection
│   ├── gunicorn.conf.py     production server config
│   ├── requirements.txt     production deps
│   ├── requirements-dev.txt dev/test deps
│   ├── .env.example         environment template
│   └── .python-version      3.12
├── frontend/                static site
│   ├── index.html           public landing page
│   ├── pages/               citizen / officer / admin pages
│   └── assets/js/config.js  runtime API base URL config
├── render.yaml              Render blueprint
└── .gitignore
```

---

## 2. Local development (Windows PowerShell)

```powershell
# 1. Backend virtual environment
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt

# 2. Configure environment (never commit .env)
Copy-Item .env.example .env
#   edit .env -> set DB_PASSWORD, SECRET_KEY, JWT_SECRET_KEY

# 3. Create the local MySQL database (MySQL must be running)
#    In MySQL: CREATE DATABASE natifine CHARACTER SET utf8mb4;

# 4. Apply migrations (never use db.create_all() for a real database)
.\venv\Scripts\flask.exe db upgrade

# 5. (Optional) seed demonstration data
.\venv\Scripts\python.exe seed_users.py
.\venv\Scripts\python.exe seed_demo.py

# 6. Run the API + frontend (Flask serves ../frontend)
.\venv\Scripts\python.exe app.py
#   Open http://localhost:5000  (API docs at http://localhost:5000/apidocs/)

# 7. Run tests
.\venv\Scripts\python.exe -m pytest
```

Demo accounts (created by the seed scripts):

| Role    | Login                       | Password      |
|---------|-----------------------------|---------------|
| Citizen | citizen@natifine.co.za      | Citizen@123   |
| Officer | officer@natifine.gov.za     | Officer@123   |
| Admin   | admin@natifine.gov.za       | Admin@123     |

Local frontend needs no separate server: Flask serves `frontend/` and
`assets/js/config.js` stays empty (`""`) so API calls use the same origin.

---

## 3. Environment variables

See `backend/.env.example`. Key variables:

| Variable            | Purpose                                                        |
|---------------------|----------------------------------------------------------------|
| `SECRET_KEY`        | Flask signing key (generate a strong random value)             |
| `JWT_SECRET_KEY`    | JWT signing key (independent strong random value)              |
| `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` | Local MySQL connection        |
| `DATABASE_URL` / `POSTGRES_URL` | Managed Postgres URL (Vercel/Neon); `postgres://` auto-upgrades to `postgresql+psycopg2://` |
| `DATABASE_URL_UNPOOLED` / `POSTGRES_URL_NON_POOLING` | Optional unpooled Postgres URL fallback, useful for database migrations |
| `DB_SSL`            | `true` to require TLS to a managed MySQL server                |
| `CORS_ORIGINS`      | Comma-separated browser origins allowed to call the API        |
| `STORAGE_BACKEND`   | `auto` (default), `local`, or `vercel_blob`                    |
| `BLOB_ACCESS`       | `private` or `public`; must match the Blob store mode          |
| `BLOB_READ_WRITE_TOKEN` / `BLOB_STORE_ID` | Injected by the Vercel Blob integration      |
| `UPLOAD_FOLDER`     | Local fallback upload directory                                |
| `MAIL_*`            | Email config (simulated; `MAIL_SUPPRESS_SEND=true`)            |
| `LOG_LEVEL`         | Gunicorn / app log level                                       |

Generate secrets:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 4. Database & migrations

- Local development: MySQL via `mysql+pymysql`.
- Production: Postgres (Vercel/Neon) via `postgresql+psycopg2`.
- Set `DATABASE_URL` or `POSTGRES_URL` to the managed Postgres connection
  string. `postgres://` is upgraded to `postgresql+psycopg2://` automatically.
- Migrations live in `backend/migrations/` (Alembic). The initial migration is
  portable: it creates native Postgres enum types once and uses regular
  `sa.Enum` columns on MySQL.
- Apply migrations against the managed database:
  `flask db upgrade`. Create one: `flask db migrate -m "message"`.
- **Do not** use `db.create_all()` against the production database.
- Back up the database before applying migrations.

If data currently exists only in local MySQL, migrate it explicitly (for example
with `pgloader`) before pointing the deployed app at Postgres. Uploaded files and
receipts are not part of the SQL dump.

---

## 5. Deployment �?" Vercel Services (frontend + backend)

The repository root contains `vercel.json`, which deploys both apps as one
Vercel project:

- `frontend/` — static site (`framework: null`, no build step).
- `backend/` — Flask WSGI app exposed by `backend/index.py` as `app`.
- Requests to `/api/*` and `/healthz` go to the backend; everything else goes to
  the frontend. Both share one origin, so no CORS setup is required.

Steps:

1. Push the repository to GitHub and import it at
   [vercel.com/new](https://vercel.com/new). Vercel reads `vercel.json`.
2. Add a Postgres integration (Neon or another Marketplace provider) and a Blob
   store to the project. Connect both to Production/Preview/Development.
3. Confirm these environment variables are present in Vercel:
   - `DATABASE_URL` or `POSTGRES_URL` (provided by the Postgres integration;
     it must be a PostgreSQL connection URL)
   - `BLOB_READ_WRITE_TOKEN` or `BLOB_STORE_ID` (provided by the Blob store)
   - `STORAGE_BACKEND=auto` (uses Blob when credentials are available)
   - `SECRET_KEY`, `JWT_SECRET_KEY` (generate strong random values)
   - `BLOB_ACCESS=private` (or `public`, matching the store)
4. Run the migrations once against the managed database from your machine.
   The command requires the production Postgres URL:
   ```powershell
   cd backend
   $env:DATABASE_URL="postgresql://<user>:<password>@<host>/<database>?sslmode=require"
   .\venv\Scripts\python.exe -m flask --app app.factory db upgrade
   ```
5. Deploy. Verify `GET https://<project>.vercel.app/healthz` returns
   `{"status":"ok",...}` and `https://<project>.vercel.app/apidocs/` loads.

> Vercel Postgres is now delivered through Marketplace integrations (Neon). The
> `POSTGRES_URL`/`DATABASE_URL` naming is unchanged.

On Vercel, the app fails at startup if the Postgres URL is missing. It never
falls back to MySQL defaults. Blob credentials can be connected after the first
project deployment; until then, upload/export operations fail with an explicit
configuration error instead of writing to ephemeral local storage. Locally,
storage continues to use the filesystem unless Blob credentials are provided.

---

## 6. Alternative: separate frontend and backend projects

If you prefer independent deployments:

1. Deploy `backend/` as its own Vercel project (Root Directory: `backend`).
2. Deploy `frontend/` as another Vercel project (Root Directory: `frontend`,
   Framework: Other, no build command).
3. Edit `frontend/assets/js/config.js` and set `window.NF_API_BASE` to the
   backend origin (no trailing slash, no `/api`). Add the frontend origin to
   `CORS_ORIGINS` on the backend.

The single-project `vercel.json` setup above is recommended because it avoids
cross-origin configuration entirely.

Direct-refresh works because every page maps to a real `.html` file (e.g.
`/pages/login.html`); no SPA fallback is required.

---

## 7. Git & GitHub

A Git repository is **not yet initialised**. To create one and push:

```powershell
cd <project root>          # the folder containing backend/ and frontend/
git init
git add .
git commit -m "NatiFine SA: production deployment prep"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

`.gitignore` already excludes `venv/`, `__pycache__/`, `.env`, `node_modules/`,
generated receipts/uploads/exports, and caches. **Never commit `.env`.**

---

## 8. Connecting frontend, backend & CORS

- With `vercel.json` Services the browser calls `/api/*` on the same origin, so
  CORS is not involved.
- `CORS_ORIGINS` only matters for the separate-project alternative. Set it to
  the exact frontend origin, e.g. `https://natifine.vercel.app`.
- `Authorization` header is allowed; credentials (cookies) are **not** used, so
  wildcard-with-credentials is avoided.
- Preflight `OPTIONS` is handled by Flask-CORS.

---

## 9. Security notes

- JWT access/refresh tokens are held in `sessionStorage` and sent via the
  `Authorization` header (not cookies) — CSRF surface is low.
- Passwords are hashed with bcrypt.
- Secrets only live in Render/Vercel dashboards and local `.env` (git-ignored).
- Always use HTTPS in production (Render and Vercel provide it by default).
- Rotate `SECRET_KEY` / `JWT_SECRET_KEY` if they were ever exposed.
- Health endpoint returns static status only (no credentials or PII).

---

## 10. Verification checklist

- [ ] `flask db upgrade` runs cleanly on the Postgres database (after backup).
- [ ] `GET /healthz` returns 200 with `{"status":"ok"}`.
- [ ] Backend tests pass (`python -m pytest`).
- [ ] Register + login work against the deployed API.
- [ ] Protected routes reject requests without a valid token (401/403).
- [ ] Citizen cannot open another citizen's records.
- [ ] Fines, disputes, notifications, dashboards render with live API data.
- [ ] Database writes persist across cold starts.
- [ ] Dispute uploads and receipt downloads still work after a cold start
      (proves files are in Vercel Blob, not local disk).
- [ ] No secrets appear in the Git repo or the frontend bundle.
- [ ] Direct refresh on `/pages/...` URLs does not 404.
- [ ] Browser console has no errors; API calls go to `/api/*` on the same origin.

---

## 11. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| Vercel build cannot find the Flask app | Ensure `vercel.json` points at `backend/` with entrypoint `index:app`. |
| `Access denied` / DB errors | Wrong `DATABASE_URL`/`POSTGRES_URL`; check host, password and `sslmode=require`. |
| `NoSuchModuleError: postgres` | The URL used `postgres://`; this project rewrites it to `postgresql+psycopg2://`. |
| Vercel reports `pg_config executable not found` while installing psycopg2 | Ensure the deployment uses the current `psycopg2-binary` pin in `backend/requirements.txt` and rebuild from the latest commit; older pins may lack a wheel for Vercel's Python/Linux target. |
| Upload/export returns a Blob configuration error | Connect a Blob store to the project and confirm `BLOB_READ_WRITE_TOKEN` or `BLOB_STORE_ID` is available to the deployment. |
| Uploads/receipts disappear | Confirm Blob credentials are configured and `BLOB_ACCESS` matches the store. Older deployments may have written files to ephemeral local storage. |
| `BlobCredentialsError` | The Blob store is not connected to the Vercel project (or `BLOB_ACCESS` does not match the store). |
| Large upload returns 413 | Vercel Functions cap request bodies at 4.5 MB; use a smaller file or client uploads. |
| CORS error in browser (separate projects) | `CORS_ORIGINS` does not include the exact frontend origin. |
| `flask db upgrade` makes no changes | Migrations not applied to the right DB; verify `DATABASE_URL`. |
| Login works but other calls 401 | Access token expired; refresh token flow or re-login. |

---

## 12. Files created / modified for deployment

**Created**
- `vercel.json` — Vercel Services config (frontend + Flask backend).
- `backend/index.py` — Vercel WSGI entrypoint.
- `backend/app/services/storage_service.py` — local/Vercel Blob abstraction.
- `backend/requirements-dev.txt` — split dev/test dependencies.
- `backend/gunicorn.conf.py` — production WSGI config (PORT, workers, timeouts).
- `backend/.env.example` — safe environment template.
- `backend/.python-version` — selects Vercel's default supported Python 3.12
  runtime. The Docker/Render configuration can use its own Python version.
- `.gitignore` — excludes venv, caches, secrets, generated files.
- `render.yaml` — optional Render blueprint (alternative host).
- `README.md` — this document.

**Modified**
- `backend/requirements.txt` — added `psycopg2-binary`, `vercel-blob`, `openpyxl`.
- `backend/app/config/settings.py` — Postgres URL detection/normalization,
  serverless pool settings, Blob settings, 4 MB upload limit.
- `backend/app/services/upload_service.py` — stores dispute documents in Blob.
- `backend/app/services/receipt_service.py` — generates PDFs in memory and stores
  them in Blob.
- `backend/app/services/export_service.py` — exports through Blob/local storage.
- `backend/app/services/email_service.py` — reads receipt attachments from storage.
- `backend/migrations/versions/fd274eb3c917_initial_schema.py` — portable enums
  for Postgres (created once, no duplicate-type errors).
- `frontend/assets/js/config.js` — same-origin API base by default.
- `backend/app/factory.py` — origin-restricted CORS + `/healthz` endpoint.
- `frontend/assets/js/api.js` — API base resolved from `window.NF_API_BASE`.
- `frontend/**/*.html` (29 files) — load `config.js` before `api.js`.

---

## 13. Known limitations

- **Database**: local MySQL for development, managed Postgres for deployment.
  A `DATABASE_URL`/`POSTGRES_URL` is required on Vercel.
- **Vercel Functions**: request bodies are capped at 4.5 MB; keep dispute
  attachments smaller (the app defaults to 4 MB).
- **Blob access mode**: receipts and dispute documents are private by default.
  Set `BLOB_ACCESS=public` only if the store was created as public.
- **Simulated services**: payments, SMS, WhatsApp and email are mocked; no real
  gateway/provider credentials are used.
- **Swagger** server list still contains placeholder domains (`api.natifine.co.za`);
  cosmetic only.
- **No SPA routing**: pages are static files, so keep `.html` links intact.
