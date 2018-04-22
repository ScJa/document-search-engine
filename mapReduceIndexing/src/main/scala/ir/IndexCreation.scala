// Copyright (C) 2017 Georg Heiler

package ir

import java.io.File

import com.databricks.spark.corenlp.functions._
import com.typesafe.config.ConfigFactory
import net.ruippeixotog.scalascraper.browser.JsoupBrowser
import org.apache.spark.sql.functions._
import org.apache.spark.sql.{ SaveMode, SparkSession }
import org.apache.spark.{ CustomTextFile, SparkConf }
import scala.language.postfixOps

import scala.collection.JavaConverters._

case class RawRecords(path: String, content: String)

case class TokenOccurence(documentID: String, count: Int)

case class InvertedIndex(word: String, documents: Seq[TokenOccurence])

case class DocumentTokenized(topic: String, lemma: String)

object IndexCreation extends App {

  val confIndex = ConfigFactory.load()
  val stopWords = confIndex.getStringList("indexCreation.stopwords").asScala

  val browser = JsoupBrowser()

  val conf: SparkConf = new SparkConf()
    .setAppName("invertedIndex")
    .setMaster("local[*]")
    .set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .set("spark.executor.memory", "11G")
    .set("spark.default.parallelism", "12")
    .set("spark.speculation", "true")

  val spark: SparkSession = SparkSession
    .builder()
    .config(conf)
    .getOrCreate()

  import spark.implicits._

  val broadcastStopWords = spark.sparkContext.broadcast(stopWords)
  val dataPath = ".." + File.separator + "data" + File.separator
  //  val path = dataPath + "small" // only minimal sample with 3 files
  val path = dataPath + "TREC8all" + File.separator + "Adhoc" + File.separator + "*"

  val minimalPartitions = spark.conf.getOption("spark.default.parallelism").map(_.toInt).getOrElse(12)

  val df = CustomTextFile.wholeTextFiles(spark, path, minimalPartitions).toDF
    .withColumnRenamed("_1", "path")
    .withColumnRenamed("_2", "content")
    .as[RawRecords]
  println(s"number of files ${df.select("path").distinct.count}")

  val distinctWords = udf((xs: Seq[String]) => xs.distinct)
  val topics = df
    .mapPartitions(ExtractDocuments.mapToTopics)
    .filter('content isNotNull)
    .filter(length('content) > 5) // remove documents with *empty* content
  val wordcountPerTopic = topics
    .select(
      'topic,
      split('content, " ").alias("words")
    )
    .withColumn("uniqueWordCount", size(distinctWords('words)))
    .withColumn("allWordCount", size(distinctWords('words)))
    .drop("words")
  topics.cache

  println("#########################")
  //  topics.show
  println(s"count number of ALL topics: ${topics.count}")
  println(s"count ALL words ofALL documents: ${wordcountPerTopic.select(sum('allWordCount).cast("int")).as[Int].first}")
  println(s"average word count forALL documents: ${wordcountPerTopic.select(avg('uniqueWordCount).cast("int")).as[Int].first}")
  println("counting all words per topic")
  wordcountPerTopic.show
  println("#########################")

  // as a single word
  // perform proper stopwords removal http://stackoverflow.com/questions/30019054/text-tokenization-with-stanford-nlp-filter-unrequired-words-and-characters
  // todo find a better/nicer way to write it
  val tokens = topics
    //    .withColumn("lemma", explode(lemma('content))) // TODO some token are [] which crash lemmatizer
    .withColumn("lemma", explode(tokenize('content)))
    .filter(length($"lemma") > 1)
    .withColumn("isStopword", when('lemma isin (broadcastStopWords.value: _*), 1).otherwise(0))
    .filter($"isStopword" =!= 1)
    .drop("content", "isStopword", "filepath")

  val indexedTokens = tokens.as[DocumentTokenized].flatMap {
    case d: DocumentTokenized => d.lemma.trim.split("""[^\p{IsAlphabetic}]+""").map(word => (word, d.topic))
  }.map {
    case (lemma, topic) => ((lemma, topic), 1)
  }.rdd
    .reduceByKey {
      (count1, count2) => count1 + count2
    }.map {
      case ((word, path), n) => (word, (path, n))
    }.toDF

  val groupedStuff = indexedTokens.groupBy($"_1".alias("word"))
    .agg(collect_list($"_2").alias("documents")).as[InvertedIndex]
  groupedStuff.cache
  groupedStuff.show

  groupedStuff.repartition(1).write.mode(SaveMode.Overwrite).json(".." + File.separator + "mapReduceIndex.json")
  wordcountPerTopic.repartition(1).write.mode(SaveMode.Overwrite).json(".." + File.separator + "wordCountPerTopic.json")

  println("#########################")
  println(s"elements in index: ${groupedStuff.count}")
  println("#########################")

  spark.stop
}
