import os
from pyspark.sql import SparkSession, functions as F

S3_ENDPOINT = "http://minio:9000"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")

packages = ",".join([
    "io.delta:delta-spark_2.12:3.1.0",
    "org.apache.hadoop:hadoop-aws:3.3.4",
    "com.amazonaws:aws-java-sdk-bundle:1.12.691",
])

builder = (
    SparkSession.builder.appName("SilverGold")
    .config("spark.jars.packages", packages)
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    # S3A / MinIO settings
    .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT)
    .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY_ID)
    .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
)

spark = builder.getOrCreate()

bronze = "s3a://bronze/trips"
silver = "s3a://silver/trips_clean"
gold   = "s3a://gold/trip_kpis"

df_bronze = spark.read.format("delta").load(bronze)

df_silver = (
    df_bronze
    .filter(F.col("pickup_ts").isNotNull() & F.col("dropoff_ts").isNotNull())
    .filter((F.col("trip_km") >= 0) & (F.col("trip_km") <= 200))
    .filter((F.col("fare") >= 0) & (F.col("fare") <= 1000))
    .withColumn("pickup_date", F.to_date("pickup_ts"))
)
df_silver.write.mode("overwrite").format("delta").partitionBy("pickup_date").save(silver)

df_gold = (
    spark.read.format("delta").load(silver)
    .groupBy("pickup_date")
    .agg(
        F.count(F.lit(1)).alias("trips"),
        F.avg("fare").alias("avg_fare"),
        F.expr("percentile_approx(trip_km, 0.95)").alias("p95_km"),
    )
    .orderBy("pickup_date")
)
df_gold.write.mode("overwrite").format("delta").save(gold)

print("Gold rows:", df_gold.count())
spark.stop()
