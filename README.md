# OSS Lakehouse in Docker — Scala + Python

A minimal, reproducible **lakehouse** stack you can run locally with Docker:

* **Apache Spark 3.5** (master + worker) with **Delta Lake**
* **MinIO** (S3-compatible) for Bronze/Silver/Gold object storage
* **MLflow** server with artifacts stored in MinIO
* **JupyterLab** (PySpark + delta-spark + Great Expectations)

> **Data** in `data/raw` is **synthetic** and for demo only.

---

## Architecture

```
+-------------------+         +-----------------+         +-----------------+
|   Raw CSV (demo)  |  --->   |  Scala Ingest   |  --->   |  Delta Bronze    |
|  data/raw/*.csv   |         |  (sbt / Spark)  |         |  s3a://bronze/...|
+-------------------+         +-----------------+         +------------------+
                                                           |
                                                           v
                                                   +-----------------+
                                                   | PySpark Curate  |
                                                   |  (delta-spark   |
                                                   |  + GE checks)   |
                                                   +-----------------+
                                                     |          |
                                                     v          v
                                         s3a://silver/...   s3a://gold/...
```

**Observability**

* **Jupyter** for notebooks & ad-hoc work
* **MLflow** for experiment tracking (backed by SQLite) and **artifacts in MinIO**
* **Spark UI** for job/cluster status

---

## Prerequisites

* Docker Desktop (or Docker Engine) + Compose v2
* Open ports: **8888** (Jupyter), **5000** (MLflow), **9000/9001** (MinIO), **8080/8081** (Spark UIs)

---

## Environment

Copy this to `.env` (keep your real `.env` **out of git**) and adjust as needed:

```env
# MinIO console/admin (demo defaults)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# S3-style access used by Jupyter & MLflow
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
MLFLOW_S3_ENDPOINT_URL=http://minio:9000

# Optional region flags used in compose
AWS_REGION=us-east-1
AWS_EC2_METADATA_DISABLED=true
AWS_S3_FORCE_PATH_STYLE=true
```

Also add a committed **`.env.example`** with the same values for others to copy.

---

## Quick Start

Bring the stack up:

```bash
docker compose up -d
```

Generate demo raw data, ingest to **Bronze**, then curate to **Silver/Gold**:

```bash
# 1) Generate raw CSVs (inside Jupyter container)
docker compose exec -T jupyter python /work/scripts/generate_raw_csv.py

# 2) Build Scala job
./scripts/build_scala.sh

# 3) Submit Scala Spark job (writes Delta Bronze to MinIO)
./scripts/submit_scala_ingest.sh

# 4) Curate with PySpark (Delta -> Silver/Gold + simple quality checks)
docker compose exec -T jupyter python /work/py/silver_gold.py
```

**UIs**

* Spark Master UI: [http://localhost:8080](http://localhost:8080)
* MinIO Console: [http://localhost:9001](http://localhost:9001)  (login: `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`)
* MLflow UI: [http://localhost:5000](http://localhost:5000)
* JupyterLab: [http://127.0.0.1:8888/lab](http://127.0.0.1:8888/lab)

**Paths**

* Bronze: `s3a://bronze/trips`
* Silver: `s3a://silver/trips`
* Gold: `s3a://gold/kpis`

> Buckets `bronze/silver/gold/mlflow` are created automatically by the `minio-setup` service.

---

## Smoke Tests

**Verify MLflow <-> MinIO artifacts work:**

```bash
docker compose exec -T jupyter python - <<'PY'
import os, boto3, mlflow
mlflow.set_tracking_uri("http://mlflow:5000")
with mlflow.start_run(run_name="smoke"):
    mlflow.log_param("alpha", 0.1)
    mlflow.log_metric("rmse", 1.23)
    mlflow.log_text("hello", "notes.txt")

s3 = boto3.client("s3", endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"])
print("Buckets:", [b["Name"] for b in s3.list_buckets()["Buckets"]])
PY
```

You should see `Buckets: ['bronze', 'gold', 'mlflow', 'silver']` and a new run in the MLflow UI.

**List run artifacts via S3:**

```bash
docker compose exec -T jupyter python - <<'PY'
import os, boto3
from mlflow.tracking import MlflowClient
c = MlflowClient("http://mlflow:5000")
exp = c.get_experiment_by_name("Default")
run = c.search_runs([exp.experiment_id], order_by=["attributes.start_time DESC"], max_results=1)[0]
print("Run:", run.info.run_id)
s3 = boto3.client("s3", endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"])
prefix = f"0/{run.info.run_id}/artifacts/"
resp = s3.list_objects_v2(Bucket="mlflow", Prefix=prefix)
print("Keys:", [o["Key"] for o in resp.get("Contents", [])])
PY
```

---

## Project Layout

```
OSS-Lakehouse/
├─ data/
│  └─ raw/                # Demo CSV inputs (committed)
├─ mlflow/                # MLflow backend (DB/logs) - ignored by git
├─ minio/                 # MinIO persisted data - ignored by git
├─ py/                    # PySpark curation (Silver/Gold, GE checks)
├─ scala/                 # Scala sbt project for ingest (Bronze)
├─ scripts/
│  ├─ generate_raw_csv.py
│  ├─ build_scala.sh
│  └─ submit_scala_ingest.sh
├─ docker-compose.yml
├─ .env                   # not committed (use .env.example)
└─ README.md
```

---

## Windows Tips

* If you run heredoc commands in **Git Bash**, prefix with:

  ```bash
  MSYS_NO_PATHCONV=1 docker compose exec -T jupyter python - <<'PY'
  # ...
  PY
  ```

  This prevents MSYS from rewriting paths in your heredoc.

* If the Jupyter tab doesn’t load on `localhost`, use `http://127.0.0.1:8888/lab`.

---

## Troubleshooting

* **Jupyter not reachable**

  * `docker compose ps jupyter`
  * `docker compose port jupyter 8888` should show `0.0.0.0:8888`
  * `docker compose logs -n 200 jupyter`

* **MLflow shows endless logs / 404 on `experiments/list`**

  * UI/API is up when you see `Uvicorn running on 0.0.0.0:5000`.
  * Use `/api/2.0/mlflow/experiments/get-by-name` or the UI; the “search” endpoint is `/ajax-api/2.0/...` (as used by UI).

* **Artifacts not appearing in MinIO**

  * Ensure Jupyter has `boto3` + `mlflow` installed (the image does this at startup).
  * Check env in both **mlflow** and **jupyter** containers:

    ```bash
    docker compose exec -T mlflow env | egrep 'AWS_|MLFLOW_S3'
    docker compose exec -T jupyter env | egrep 'AWS_|MLFLOW_S3'
    ```

* **Clean reset**

  ```bash
  docker compose down -v
  rm -rf minio mlflow data/bronze data/silver data/gold
  docker compose up -d
  ```

---

## .gitignore

Keep raw demo inputs, ignore generated data & local state:

```
# OS / editors
.DS_Store
Thumbs.db
.vscode/
.idea/

# Python / Jupyter
__pycache__/
*.py[cod]
.venv/
.ipynb_checkpoints/
.jupyter/lab/workspaces/

# Scala / sbt / Metals
scala/target/
scala/project/target/
scala/project/project/
.metals/
.bsp/

# Spark local
spark-warehouse/
metastore_db/
derby.log
**/.sparkStaging/

# Lake outputs & state
data/bronze/
data/silver/
data/gold/
minio/data/
mlflow/mlruns/
mlflow/*.db*
mlflow/*-journal
mlflow/*.log

# Env
.env
.env.*
```

---

## License

MIT
