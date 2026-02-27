FROM apache/spark:3.5.1

USER root
RUN mkdir -p /home/spark/.ivy2/cache && chown -R spark:spark /home/spark/.ivy2
USER spark

WORKDIR /app
COPY spark_stream.py .

CMD ["/opt/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", "/app/spark_stream.py"]