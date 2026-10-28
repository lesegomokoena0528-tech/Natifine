# NatiFine SA — Digital Traffic Fines Management System

NatiFine SA is an **academic prototype** for managing South African traffic fines.
It consists of a **Flask REST API** (`backend/`) and a **plain HTML/CSS/JS frontend**
(`frontend/`, no build tool). Payments, SMS, WhatsApp and email are **simulated**.

- Backend: Flask 3.1 + SQLAlchemy + MySQL (PyMySQL) + Flask-Migrate, JWT auth.
- Frontend: static site (vanilla JS), currently served by Flask locally.
- Production target: **Render** (API) + **Vercel** (static frontend) + **managed MySQL**.

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
│   └── .python-version      3.13.0
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
| `DATABASE_URL`      | Production override; `mysql://` auto-upgrades to `mysql+pymysql://` |
| `DB_SSL`            | `true` to require TLS to a managed MySQL server                |
| `CORS_ORIGINS`      | Comma-separated browser origins allowed to call the API        |
| `UPLOAD_FOLDER`     | Upload directory                                               |
| `MAIL_*`            | Email config (simulated; `MAIL_SUPPRESS_SEND=true`)            |
| `LOG_LEVEL`         | Gunicorn / app log level                                       |

Generate secrets:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 4. Database & migrations

- Engine: MySQL via `mysql+pymysql`.
- Migrations live in `backend/migrations/` (Alembic). Head revision:
  `fd274eb3c917` (initial schema — creates all 11 tables in dependency order).
  It was regenerated from the models because the earlier chain was incomplete
  (it referenced `traffic_fines` before that table existed).
- Apply migrations: `flask db upgrade`. Create one: `flask db migrate -m "message"`.
- **Do not** use `db.create_all()` against the production database.
- Back up the database before applying migrations.

If the data currently exists only in a local MySQL instance, export it and import
it into the managed database before pointing Render at it:

```powershell
# export (structure + data)
mysqldump -u root -p --databases natifine > natifine_backup.sql
# import into the managed database (provider host/credentials)
mysql -h <host> -P <port> -u <user> -p < natifine_backup.sql
```

---

## 5. Backend deployment — Render

1. Push the repository to GitHub (see section 7).
2. Render Dashboard → **New → Blueprint** (uses `render.yaml`) **or** **New → Web Service**.
   - Root Directory: `backend`
   - Runtime: Python 3.13 (`PYTHON_VERSION=3.13.0`)
   - Build command: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start command: `gunicorn -c gunicorn.conf.py "app.factory:create_app()"`
   - Health check path: `/healthz`
3. Set environment variables in the Render dashboard (do **not** commit them):
   `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL` (or `DB_*`), `DB_SSL`,
   `CORS_ORIGINS` (add the Vercel URL after step 6), `FLASK_ENV=production`.
4. Deploy. Confirm logs show a clean start and no credentials printed.
5. Verify: `GET https://<your-service>.onrender.com/healthz` → `{"status":"ok",...}`.
6. Swagger UI: `https://<your-service>.onrender.com/apidocs/`.

The start command uses the Flask **application factory** `app.factory:create_app()`
(the same entry point as `flask --app app.factory run`). Gunicorn binds
`0.0.0.0:$PORT` and is never run in Flask debug mode.

---

## 6. Frontend deployment — Vercel

The frontend is **static** (no Vite/React/Next). There is no build step.

1. Vercel Dashboard → **Add New → Project** → import the same GitHub repo.
2. **Root Directory**: `frontend`.
3. Framework Preset: **Other**. Build Command: *(leave empty)*. Output Directory: `frontend` (`.`).
4. Set the API base URL **before deploying** by editing
   `frontend/assets/js/config.js`:

   ```js
   window.NF_API_BASE = "https://<your-render-service>.onrender.com";
   ```

   - No trailing slash. Do **not** include `/api` — API paths already contain it.
   - Leave empty (`""`) for local development (same-origin).
   - This value is public (it is the API origin); never put secrets here.
5. Deploy and open the Vercel URL.

> Static hosting cannot inject build-time env vars without a build step, so the
> API base lives in `config.js`. If you prefer env-driven configuration, add a
> small Node build step or use a Vercel rewrite proxy (`/api/*` → Render) instead;
> both are documented alternatives.

Direct-refresh works on all pages because every route maps to a real `.html`
file (e.g. `/pages/login.html`); no SPA rewrites or `vercel.json` are required.

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

- Backend CORS is restricted to `CORS_ORIGINS` (comma-separated). Set it to the
  exact Vercel origin, e.g. `https://natifine.vercel.app`.
- `Authorization` header is allowed; credentials (cookies) are **not** used, so
  wildcard-with-credentials is avoided.
- Preflight `OPTIONS` is handled by Flask-CORS.
- After deploying the frontend, update `CORS_ORIGINS` on Render and redeploy.
- In the browser Network tab, API calls should target the **Render** URL, never
  `localhost`.

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

- [ ] `flask db upgrade` runs cleanly on the production database (after backup).
- [ ] `GET /healthz` returns 200 with `{"status":"ok"}`.
- [ ] Backend tests pass (`python -m pytest`).
- [ ] Register + login work against the deployed API.
- [ ] Protected routes reject requests without a valid token (401/403).
- [ ] Citizen cannot open another citizen's records.
- [ ] CORS: browser calls from the Vercel origin succeed; other origins blocked.
- [ ] Fines, disputes, notifications, dashboards render with live API data.
- [ ] Database writes persist after a backend restart.
- [ ] No secrets appear in the Git repo or the frontend bundle.
- [ ] Direct refresh on `/pages/...` URLs does not 404.
- [ ] Browser console has no errors; Network tab shows Render calls only.

---

## 11. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| Render build fails parsing `requirements.txt` | File was UTF-16; it is now UTF-8. Re-commit. |
| `Access denied` / DB errors on Render | Wrong `DATABASE_URL`/`DB_*`; check provider host/port and `DB_SSL`. |
| CORS error in browser | `CORS_ORIGINS` does not include the exact Vercel origin (scheme + host, no trailing slash). |
| Frontend calls `localhost` / its own host | `window.NF_API_BASE` not set in `frontend/assets/js/config.js`. |
| Slow first response | Render free instances sleep and cold-start (~30–60s). Upgrade to avoid. |
| `flask db upgrade` makes no changes | Migrations not applied to the right DB; verify `DATABASE_URL`. |
| Login works but other calls 401 | Access token expired; refresh token flow or re-login. |

---

## 12. Files created / modified for deployment

**Created**
- `backend/requirements-dev.txt` — split dev/test dependencies.
- `backend/gunicorn.conf.py` — production WSGI config (PORT, workers, timeouts).
- `backend/.env.example` — safe environment template.
- `backend/.python-version` — pins Python 3.13.0 for Render.
- `.gitignore` — excludes venv, caches, secrets, generated files.
- `render.yaml` — Render blueprint (rootDir, build/start, health check).
- `frontend/assets/js/config.js` — runtime API base URL for Vercel.
- `README.md` — this document.

**Modified**
- `backend/requirements.txt` — re-encoded UTF-16 → UTF-8, removed duplicates and
  dev-only packages (moved to `requirements-dev.txt`).
- `backend/app/config/settings.py` — `DATABASE_URL`/`DB_SSL`/`CORS_ORIGINS`
  support, MySQL URL normalization, connection pool settings.
- `backend/app/factory.py` — origin-restricted CORS + `/healthz` endpoint.
- `frontend/assets/js/api.js` — API base resolved from `window.NF_API_BASE`.
- `frontend/**/*.html` (29 files) — load `config.js` before `api.js`.
- `backend/migrations/versions/` — old broken chain replaced with
  `fd274eb3c917_initial_schema.py` (all tables, correct FK order).

---

## 13. Known limitations

- **Database**: currently local MySQL only. Cloud hosting is not yet provisioned;
  the backend is deploy-ready but needs a `DATABASE_URL` (managed MySQL).
- **Render free tier**: web service sleeps when idle (cold starts).
- **Simulated services**: payments, SMS, WhatsApp and email are mocked; no real
  gateway/provider credentials are used.
- **Swagger** server list still contains placeholder domains (`api.natifine.co.za`);
  cosmetic only.
- **No SPA routing**: pages are static files, so keep `.html` links intact.
