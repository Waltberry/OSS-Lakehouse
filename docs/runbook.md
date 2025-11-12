# Runbook

## Bring up
docker compose up -d

## Generate raw
docker compose exec lakehouse-jupyter python /work/scripts/generate_raw_csv.py

## Build scala
./scripts/build_scala.sh

## Ingest -> Bronze
./scripts/submit_scala_ingest.sh

## Curate -> Silver/Gold
docker compose exec lakehouse-jupyter python /work/py/silver_gold.py

## Reset
docker compose down -v
rm -rf minio mlflow data/raw/*
docker compose up -d
