from __future__ import print_function

import sys
import socket
from operator import add
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf

sock = socket.gethostname().split('.', 1)[0]
slave="spark://"+sock+":7077"
conf = SparkConf().setAppName('sparktest').setMaster(slave)
sc = SparkContext(conf=conf)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: wordcount <file>", file=sys.stderr)
        sys.exit(-1)

    spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

    lines = spark.read.text(sys.argv[1]).rdd.map(lambda r: r[0])
    counts = lines.flatMap(lambda x: x.split(' ')) \
                  .map(lambda x: (x, 1)) \
                  .reduceByKey(add)
    output = counts.collect()
    for (word, count) in output:
        print("%s: %i" % (word, count))

    spark.stop()

