// Copyright (C) 2017 Georg Heiler
package ir

import net.ruippeixotog.scalascraper.browser.JsoupBrowser
import net.ruippeixotog.scalascraper.dsl.DSL._
import net.ruippeixotog.scalascraper.scraper.ContentExtractors.{ elementList, text }

case class TopicContent(topic: String, content: Option[String], filepath: String)

object ExtractDocuments {

  @transient lazy val browser = JsoupBrowser()

  def mapToTopics(iterator: Iterator[RawRecords]): Iterator[TopicContent] = {
    iterator.flatMap(k => {
      val documents = browser.parseString(k.content) >> elementList("doc")
      documents.map(d => {
        val documentID = d >> text("docno")
        val textDoc = d >?> text("text")
        TopicContent(documentID, textDoc, k.path)
      })
    })
  }
}