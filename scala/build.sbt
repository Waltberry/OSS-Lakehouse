ThisBuild / scalaVersion := "2.12.18"
name := "transforms-core"
version := "0.1.0"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.5.1" % "provided",
  "io.delta" %% "delta-core" % "3.1.0",
  "org.apache.hadoop" % "hadoop-aws" % "3.3.4",
  "com.amazonaws" % "aws-java-sdk-bundle" % "1.12.691",
  "org.scalatest" %% "scalatest" % "3.2.18" % Test
)
