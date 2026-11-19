#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-asia-south1}"
CONNECTION_NAME="${CLOUDSQL_CONNECTION_NAME:?Set CLOUDSQL_CONNECTION_NAME}"
IMAGE="${1:?Set container image}"

gcloud run deploy atlas \
  --image="$IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --min=0 \
  --max=2 \
  --set-cloudsql-instances="$CONNECTION_NAME" \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION" \
  --set-secrets="DATABASE_URL=atlas-database-url:latest,JWT_SECRET=atlas-jwt-secret:latest,REDIS_URL=atlas-redis-url:latest"
