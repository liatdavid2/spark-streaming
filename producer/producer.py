import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

def random_ip():
    return f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"

producer = None

for i in range(60):  # up to 60 seconds
    try:
        producer = KafkaProducer(
        bootstrap_servers="kafka:9092",
        value_serializer=lambda v: json.dumps(v).encode(),
        retries=5,
        acks="all",
        linger_ms=10,
    )
        print("Connected to Kafka")
        break
    except NoBrokersAvailable:
        print(f"Kafka not ready yet... retry {i+1}/60")
        time.sleep(1)

if producer is None:
    raise RuntimeError("Kafka not available after 60 seconds")

while True:
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": random_ip(),
        "destination_ip": random_ip(),
        "bytes": random.randint(100, 10000),
        "port": random.choice([80, 443, 22]),
        "protocol": random.choice(["TCP", "UDP"])
    }

    producer.send("network_events", event)
    producer.flush()
    print("Sent:", event)
    time.sleep(0.1)