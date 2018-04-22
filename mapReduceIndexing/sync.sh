#!/usr/bin/env bash
git reset --hard
git pull origin master
sbt clean assembly
spark-submit --verbose \
        --class ir.IndexCreation \
        --master "local[*]" \
        --driver-memory=14G \
        --executor-memory=14G \
        --conf spark.default.parallelism=12 \
        --conf "spark.executor.extraJavaOptions=-XX:+UseG1GC -XX:+PrintGCDetails" \
	target/scala-2.11/mapReduceIndexing-assembly-0.0.1.SNAPSHOT.jar
