# Atlas

Atlas is a multi-agent enterprise knowledge and data operations platform.

## Local setup

```powershell
Copy-Item .env.example .env
python -m pip install -r requirements.txt
make test
make lint
make run
```

The health endpoint is available at `http://localhost:8080/health`.

## Architecture

See [docs/architecture.md](docs/architecture.md). Architecture decisions are in
[docs/adr](docs/adr).

## Local run

```powershell
docker compose up -d db redis
python db/seed/seed_docs.py
python db/seed/seed_billing.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Render + Vercel deployment

1. In Google AI Studio, create an API key. Do not send it in chat or commit it.
2. In Render, create a Blueprint from this repository and use `render.yaml`.
3. Add Render environment secrets: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`,
   `GOOGLE_API_KEY`, `API_USERNAME`, `API_PASSWORD`, and `CORS_ORIGINS`.
4. Deploy the backend and copy its HTTPS URL.
5. Vercel: import this repository, set root directory to `frontend`,
   framework preset to Vite, set `VITE_API_URL` to the Render HTTPS URL, and deploy.
6. Set Render `CORS_ORIGINS` to the exact Vercel HTTPS URL.

The AI path uses Google AI Studio's `GOOGLE_API_KEY` and Gemini API rather than
Vertex AI. Free quota and model availability are controlled by Google and can
change. Document ingestion from GCS still requires Google Cloud Storage access;
local files can be used without GCS.

For Supabase, use its PostgreSQL connection string as `DATABASE_URL` and include
`?sslmode=require`. In the Supabase SQL editor run
`CREATE EXTENSION IF NOT EXISTS vector;`, then apply `db/init/001_schema.sql`.
Do not configure the Supabase service-role API key; Atlas connects via PostgreSQL.

Render's free web service may sleep when idle. Supabase, Upstash, Vercel, Render,
and Google AI Studio free quotas and limits vary; verify their current terms and
quotas before using the demo.

## GCP deployment

```powershell
$env:GCP_PROJECT_ID="your-project"
$env:GCP_REGION="asia-south1"
bash deploy/cloudsql-setup.sh
bash deploy/cloudrun-deploy.sh us-docker.pkg.dev/your-project/atlas/atlas:latest
```

Create required Secret Manager values:

- `atlas-database-url`
- `atlas-jwt-secret`
- `atlas-redis-url`

## Verification

```powershell
pytest -q
ruff check .
python -m app.evals.run_evals
npm --prefix frontend run build
docker compose config
```
