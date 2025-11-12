# OSS Lakehouse in Docker — Scala + Python

**Stack**
- Spark 3.5 (bitnami) + Delta
- MinIO (S3-compatible) for Bronze/Silver/Gold
- MLflow server + artifacts in MinIO
- Jupyter (PySpark + delta-spark + Great Expectations)

**Skills shown**
- Scala batch ingest → **Delta Bronze** on S3A (MinIO), **schema evolution**
- PySpark curation → **Silver/Gold**, simple data-quality
- MLflow-ready env; one-command Docker bring-up

## Quick start
```bash
docker compose up -d
docker compose exec lakehouse-jupyter python /work/scripts/generate_raw_csv.py
./scripts/build_scala.sh
./scripts/submit_scala_ingest.sh
docker compose exec lakehouse-jupyter python /work/py/silver_gold.py
```

**UIs**
- Spark Master UI: http://localhost:8080
- MinIO Console:    http://localhost:9001  (minioadmin/minioadmin)
- MLflow UI:        http://localhost:5000

**Paths**
- Bronze: `s3a://bronze/trips`
- Silver: `s3a://silver/trips`
- Gold:   `s3a://gold/kpis`

**Reset**
```bash
docker compose down -v
rm -rf minio mlflow data/raw/*
docker compose up -d
```
