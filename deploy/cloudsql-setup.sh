#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-asia-south1}"
INSTANCE_NAME="${CLOUDSQL_INSTANCE:-atlas-postgres}"

gcloud config set project "$PROJECT_ID"
gcloud services enable sqladmin.googleapis.com aiplatform.googleapis.com storage.googleapis.com

gcloud sql instances describe "$INSTANCE_NAME" >/dev/null 2>&1 ||
  gcloud sql instances create "$INSTANCE_NAME" \
    --database-version=POSTGRES_16 \
    --tier=db-f1-micro \
    --region="$REGION"

gcloud sql databases create atlas --instance="$INSTANCE_NAME" || true

gcloud sql connect "$INSTANCE_NAME" --database=atlas --user=postgres <<'SQL'
CREATE EXTENSION IF NOT EXISTS vector;
\i db/init/001_schema.sql
SQL
