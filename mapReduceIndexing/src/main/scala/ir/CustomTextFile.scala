// Copyright (C) 2017 Georg Heiler
package org.apache.spark

// deliberately in spark namespace

import java.nio.charset.Charset

import org.apache.hadoop.io.{ LongWritable, Text }
import org.apache.hadoop.mapred.TextInputFormat
import org.apache.hadoop.mapreduce.lib.input.{ FileInputFormat => NewFileInputFormat }
import org.apache.hadoop.mapreduce.{ InputFormat => NewInputFormat, Job => NewHadoopJob }
import org.apache.spark.input.WholeTextFileInputFormat
import org.apache.spark.rdd._
import org.apache.spark.sql.SparkSession

import scala.language.implicitConversions

// http://stackoverflow.com/questions/43200978/spark-read-wholetextfiles-with-non-utf-8-encoding
object CustomTextFile {
  val DEFAULT_CHARSET = Charset.forName("iso-8859-1")

  def withCharset(context: SparkContext, location: String, charset: String): RDD[String] = {
    if (Charset.forName(charset) == DEFAULT_CHARSET) {
      context.textFile(location)
    } else {
      // can't pass a Charset object here cause its not serializable
      // TODO: maybe use mapPartitions instead?
      context.hadoopFile[LongWritable, Text, TextInputFormat](location).map(
        pair => new String(pair._2.getBytes, 0, pair._2.getLength, charset)
      )
    }
  }

  def wholeTextFiles(spark: SparkSession, path: String,
    minPartitions: Int = 12): RDD[(String, String)] = {

    val job = NewHadoopJob.getInstance(spark.sparkContext.hadoopConfiguration)
    // Use setInputPaths so that wholeTextFiles aligns with hadoopFile/textFile in taking
    // comma separated files as input. (see SPARK-7155)
    NewFileInputFormat.setInputPaths(job, path)
    val updateConf = job.getConfiguration
    new WholeTextFileRDD(
      spark.sparkContext,
      classOf[WholeTextFileInputFormat],
      classOf[Text],
      classOf[Text],
      updateConf,
      minPartitions
    )
      .map(record => (record._1.toString, new String(record._2.getBytes, 0, record._2.getLength, "iso-8859-1")))
      .setName(path)
  }
}