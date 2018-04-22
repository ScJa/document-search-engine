# map reduce indexing
Demonstration of map reduce pattern to create an inverted index in spark.

use `sbt console`to interactively run queries or `sbt run` but make sure to set `$SBT_OPTS -Xmx8G -XX:+UseConcMarkSweepGC -XX:+CMSClassUnloadingEnabled -Xss2M`
as spark will be launched inside sbt. But `sbt assembly and then spark-submit` works fine as well.

**requirements**
- jdk8
- sbt
- git
- spark-corenlp
    ```
    git clone https://github.com/geoHeil/spark-corenlp.git
    cd spark-corenlp
    git checkout updateDependencies
    sbt +publishLocal
    ```
- then you can run `sbt run` to run this project

**running it**
simply execute

```
sbt run
```
if you have a fully fledged spark cluster executing `sbt assembly` and submitting the fat jar via `spark-submit` is also a possibility.

We used

```
sbt assembly
spark-submit --verbose \
        --class "ir.IndexCreation" \
        --master "local[*]" \
        --driver-memory=13G \
        --conf spark.default.parallelism=12 \
        --conf "spark.executor.extraJavaOptions=-XX:+UseG1GC -XX:+PrintGCDetails" \
	target/scala-2.11/mapReduceIndexing-assembly-0.0.1.SNAPSHOT.jar
```

As we assume you have a spark cluster (maybe local one) at your disposal the jar which is uploaded will exclude hadoop and spark dependencies to limit its size to a reasonable amount.

**inspiration**
- https://github.com/stdatalabs/inverted-index/blob/master/SparkInvertedIndex/src/main/scala/com/stdatalabs/SparkInvertedIndex/Driver.scala
- https://github.com/deanwampler/spark-scala-tutorial/blob/master/src/main/scala/sparktutorial/InvertedIndex5b.scala
- http://stackoverflow.com/questions/31051107/read-multiple-files-from-a-directory-using-spark
- to parse the id numbers https://github.com/ruippeixotog/scala-scraper
