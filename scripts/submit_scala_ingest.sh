#!/usr/bin/env bash
set -euo pipefail

# Load .env so we reuse the same creds everywhere
set -a
source ./.env
set +a

JAR_PATH=/work/scala/target/scala-2.12/transforms-core_2.12-0.1.0.jar
CLASS=com.example.lakehouse.Ingest

MSYS_NO_PATHCONV=1 docker exec -it spark-master bash -lc "
  mkdir -p /opt/spark/.ivy2 &&
  /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --class ${CLASS} \
    --conf spark.jars.ivy=/opt/spark/.ivy2 \
    --packages io.delta:delta-spark_2.12:3.1.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.691 \
    --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
    --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
    --conf spark.delta.logStore.class=org.apache.spark.sql.delta.storage.S3SingleDriverLogStore \
    --conf spark.hadoop.fs.s3a.access.key=${MINIO_ROOT_USER} \
    --conf spark.hadoop.fs.s3a.secret.key=${MINIO_ROOT_PASSWORD} \
    --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
    ${JAR_PATH} s3a://bronze /work/data/raw
"
