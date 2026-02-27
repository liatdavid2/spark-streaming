from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, to_timestamp
from pyspark.sql.types import *

# ------------------------------------------------------------
# Spark Session
# ------------------------------------------------------------

spark = SparkSession.builder \
    .appName("NetworkStreaming") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ------------------------------------------------------------
# Schema definition for incoming Kafka JSON
# ------------------------------------------------------------

schema = StructType([
    StructField("timestamp", StringType()),
    StructField("source_ip", StringType()),
    StructField("destination_ip", StringType()),
    StructField("bytes", IntegerType()),
    StructField("port", IntegerType()),
    StructField("protocol", StringType())
])

# ------------------------------------------------------------
# Read from Kafka stream
# ------------------------------------------------------------

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "network_events") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# ------------------------------------------------------------
# Parse JSON from Kafka value
# ------------------------------------------------------------

parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# ------------------------------------------------------------
# Convert timestamp column to real Spark timestamp
# ------------------------------------------------------------

parsed = parsed.withColumn(
    "timestamp",
    to_timestamp("timestamp")
)

# ------------------------------------------------------------
# DEBUG STREAM (optional, safe)
# ------------------------------------------------------------

debug_query = parsed.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", "false") \
    .option("checkpointLocation", "/tmp/checkpoints/debug") \
    .trigger(processingTime="5 seconds") \
    .start()

# ------------------------------------------------------------
# Add watermark (REQUIRED for append mode with window)
# ------------------------------------------------------------

watermarked = parsed.withWatermark(
    "timestamp",
    "2 minutes"
)

# ------------------------------------------------------------
# Window aggregation
# ------------------------------------------------------------

windowed = watermarked.groupBy(
    window(col("timestamp"), "30 seconds"),
    col("destination_ip")
).count()

# ------------------------------------------------------------
# Write aggregated results to parquet (FIXED)
# ------------------------------------------------------------

query = windowed.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", "/tmp/network_agg_parquet") \
    .option("checkpointLocation", "/tmp/checkpoints/network_agg") \
    .trigger(processingTime="30 seconds") \
    .start()

# ------------------------------------------------------------
# Await termination
# ------------------------------------------------------------

query.awaitTermination()