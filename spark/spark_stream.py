from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .getOrCreate()

schema = StructType([
    StructField("timestamp", StringType()),
    StructField("source_ip", StringType()),
    StructField("destination_ip", StringType()),
    StructField("bytes", IntegerType()),
    StructField("port", IntegerType()),
    StructField("protocol", StringType())
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "network_events") \
    .load()

parsed = df.select(
    from_json(
        col("value").cast("string"),
        schema
    ).alias("data")
).select("data.*")

query = parsed.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()

query.awaitTermination(60)  # run for 60 seconds then exit
spark.stop()