name := "mapReduceIndexing"
organization := "ir"

scalaVersion := "2.11.8"

scalacOptions ++= Seq(
  "-target:jvm-1.8",
  "-encoding", "UTF-8",
  "-unchecked",
  "-deprecation",
  "-feature",
  "-Xfuture",
  "-Xlint:missing-interpolator",
  "-Yno-adapted-args",
  "-Ywarn-dead-code",
  "-Ywarn-numeric-widen",
  "-Ywarn-value-discard",
  "-Ywarn-dead-code",
  "-Ywarn-unused"
)

//The default SBT testing java options are too small to support running many of the tests
// due to the need to launch Spark in local mode.
javaOptions ++= Seq("-Xms512M", "-Xmx2048M", "-XX:MaxPermSize=2048M", "-XX:+CMSClassUnloadingEnabled")
parallelExecution in Test := false

lazy val spark = "2.1.0"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % spark % "provided",
  "org.apache.spark" %% "spark-sql" % spark % "provided",
  "databricks" %% "spark-corenlp" % "0.3.0-SNAPSHOT",
  "edu.stanford.nlp" % "stanford-corenlp" % "3.7.0" classifier "models",
  "com.typesafe" % "config" % "1.3.1",
  "net.ruippeixotog" %% "scala-scraper" % "1.2.0"
)

run in Compile := Defaults.runTask(fullClasspath in Compile, mainClass.in(Compile, run), runner.in(Compile, run)).evaluated


assemblyMergeStrategy in assembly := {
  case PathList("com", "esotericsoftware", xs@_*) => MergeStrategy.last
  case PathList("META-INF", "MANIFEST.MF") => MergeStrategy.discard
  case _ => MergeStrategy.first
}

test in assembly := {}

initialCommands in console :=
  """
    |import org.apache.spark.SparkConf
    |import org.apache.spark.sql.{ DataFrame, SparkSession }
    |import org.apache.spark.sql.functions._
    |import com.databricks.spark.corenlp.functions._
    |import java.io.File
    |
    |val conf: SparkConf = new SparkConf()
    |    .setAppName("invertedIndex")
    |    .setMaster("local[*]")
    |    .set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    |    .set("spark.executor.memory", "11G")
    |    .set("spark.default.parallelism", "12")
    |
    |val spark: SparkSession = SparkSession
    |    .builder()
    |    .config(conf)
    |    .getOrCreate()
    |
    |import spark.implicits._
  """.stripMargin

mainClass := Some("ir.IndexCreation")
