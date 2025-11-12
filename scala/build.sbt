ThisBuild / scalaVersion := "2.12.18"

lazy val sparkVersion = "3.5.1"
lazy val deltaVersion = "3.1.0"

lazy val root = (project in file("."))
  .settings(
    name := "transforms-core",
    version := "0.1.0",

    // Spark is provided by the cluster
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-sql" % sparkVersion % "provided",
      // ✅ Delta Lake for Spark (correct artifact)
      "io.delta"        %% "delta-spark" % deltaVersion,
      // S3/MinIO support
      "org.apache.hadoop" % "hadoop-aws" % "3.3.4",
      "com.amazonaws"     % "aws-java-sdk-bundle" % "1.12.691",
      // tests (optional)
      "org.scalatest" %% "scalatest" % "3.2.18" % Test
    ),

    // Make sure Maven Central is used (it is by default, but no harm being explicit)
    ThisBuild / resolvers ++= Seq(
      Resolver.mavenCentral
    )
  )
