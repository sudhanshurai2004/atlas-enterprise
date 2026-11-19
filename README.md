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

1. Render: create Blueprint from this repository and use `render.yaml`.
2. Add Render environment secrets: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`,
   `GCP_PROJECT_ID`, `GCP_REGION`, `CORS_ORIGINS`.
3. Deploy the backend and copy its HTTPS URL.
4. Set `atlas-backend.onrender.com` in `frontend/vercel.json` to that URL.
5. Vercel: import this repository, set root directory to `frontend`,
   framework preset to Vite, and deploy.
6. Set `CORS_ORIGINS` to the exact Vercel HTTPS URL.

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
