package com.example.lakehouse

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._

object Ingest {
  def main(args: Array[String]): Unit = {
    if (args.length < 2) {
      System.err.println("Usage: Ingest <bronze-s3a-path> <raw-folder>")
      System.exit(1)
    }
    val bronzePath = args(0)   // e.g., s3a://bronze/trips
    val rawFolder  = args(1)   // e.g., /work/data/raw

    val spark = SparkSession.builder()
      .appName("OSS Lakehouse - Bronze Ingest")
      .config("spark.sql.extensions","io.delta.sql.DeltaSparkSessionExtension")
      .config("spark.sql.catalog.spark_catalog","org.apache.spark.sql.delta.catalog.DeltaCatalog")
      .getOrCreate()

    val df = spark.read
      .option("header","true")
      .option("inferSchema","true")
      .csv(rawFolder)

    val cleaned = df
      .withColumn("pickup_ts", to_timestamp(col("pickup_ts")))
      .withColumn("dropoff_ts", to_timestamp(col("dropoff_ts")))
      .withColumn("trip_km", col("trip_km").cast("double"))
      .withColumn("fare", col("fare").cast("double"))
      .withColumn("ingest_ts", current_timestamp())

    // Write once
    cleaned.write
      .format("delta")
      .mode("append")
      .save(s"${bronzePath}/trips")

    // Schema evolution demo: add a new column and merge schema
    val evolved = cleaned.withColumn("tip", lit(0.0).cast("double"))
    evolved.write
      .format("delta")
      .option("mergeSchema","true")
      .mode("append")
      .save(s"${bronzePath}/trips")

    spark.stop()
  }
}
