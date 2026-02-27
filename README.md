# Spark + Kafka Streaming Demo (Docker Compose)

## Architecture Diagram

```
                    REAL-TIME NETWORK ANALYTICS PIPELINE
                    ────────────────────────────────────

                    Docker Compose Environment


    DATA INGESTION
    ┌────────────────────────────┐
    │ Producer Container         │
    │ producer.py                │
    │                            │
    │ Generates network traffic  │
    │ events                     │
    └──────────────┬─────────────┘
                   │ JSON events
                   ▼
    STREAMING PLATFORM
    ┌────────────────────────────┐
    │ Kafka Broker               │
    │                            │
    │ Topic: network_events      │
    │ Event Streaming Platform   │
    └──────────────┬─────────────┘
                   │ continuous stream
                   ▼
    STREAM PROCESSING ENGINE
    ┌────────────────────────────┐
    │ Spark Container            │
    │ spark_stream.py            │
    │                            │
    │ Structured Streaming       │
    │ Processing Engine          │
    └──────────────┬─────────────┘
                   ▼


    TRANSFORMATION LAYER
    ┌────────────────────────────┐
    │ JSON Parsing & Validation  │
    │                            │
    │ • Schema enforcement       │
    │ • Timestamp conversion     │
    │ • Structured event model   │
    └──────────────┬─────────────┘
                   ▼

    ┌────────────────────────────┐
    │ Window Aggregation Engine  │
    │                            │
    │ • 30-second windows        │
    │ • Group by destination IP  │
    │ • Traffic volume counting  │
    └──────────────┬─────────────┘
                   ▼
    STORAGE LAYER
    ┌────────────────────────────┐
    │ Parquet Data Lake          │
    │                            │
    │ /tmp/network_agg_parquet   │
    │                            │
    │ Optimized analytical       │
    │ storage format             │
    └────────────────────────────┘
    STATE MANAGEMENT
    ┌────────────────────────────┐
    │ Checkpoint Storage         │
    │                            │
    │ /tmp/checkpoints/          │
    │ network_agg                │
    │                            │
    │ • Fault tolerance          │
    │ • Offset tracking          │ 
    │ • Crash recovery           │
    └────────────────────────────┘
```

This project demonstrates a real-time streaming pipeline using:
- Apache Kafka (message broker)
- A Python producer that generates synthetic network events
- Spark Structured Streaming (PySpark) that consumes Kafka messages, parses JSON, and prints events to the console

The goal is to show a production-style streaming flow: producer -> broker -> streaming processor.


# Running the Streaming Pipeline

This section explains how to build, start, and monitor the real-time network analytics pipeline using Docker Compose.

The system includes the following services:

- Producer container – generates network traffic events  
- Kafka broker – handles event streaming  
- Spark container – processes events and writes aggregated results  

---

## Step 1 — Stop existing containers

Stop all running services to ensure a clean restart:

```cmd
docker compose down
```

This command:

- Stops all containers  
- Removes containers and networks  
- Prevents conflicts with previous runs  

---

## Step 2 — Rebuild the Spark container

Rebuild the Spark container without using cached layers:

```cmd
docker compose build --no-cache spark
```

This ensures:

- Latest code changes are included  
- The streaming application is rebuilt  
- No outdated cached layers are used  

This step is required after modifying:

```text
spark/spark_stream.py
```

---

## Step 3 — Start the entire pipeline

Start all services:

```cmd
docker compose up
```

This will start:

- Kafka broker  
- Producer container  
- Spark streaming container  

Once running, the system will automatically:

- Generate network events  
- Stream events through Kafka  
- Process events using Spark  
- Store aggregated results in Parquet format  

Output directory:

```text
output/
```

Checkpoint directory:

```text
checkpoints/
```

---

## Monitoring the system

You can monitor each component using logs.

---

### View Spark streaming logs

```cmd
docker compose logs -f spark
```

Shows:

- Streaming query execution  
- Batch processing  
- Aggregation progress  
- Errors (if any)  

---

### View Producer logs

```cmd
docker compose logs -f producer
```

Shows generated network events being sent to Kafka.

Example output:

```text
Sent event: {"timestamp":"...","source_ip":"..."}
```

This confirms that data ingestion is working correctly.

---

## Stopping the system

To stop all services:

```cmd
docker compose down
```

---

## Successful execution

The pipeline is running correctly when:

- Producer logs show events being generated  
- Spark logs show streaming batches  
- Parquet files are created in the output directory  



## Stopping the Stack

Stop and remove containers:

```bash
docker compose down
```

Remove containers and volumes (clean state):

```bash
docker compose down -v
```

## Kafka Topic

Topic name used by this demo:

* `network_events`

List topics:

```bash
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list
```

Consume a few messages directly from Kafka:

```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic network_events \
  --from-beginning \
  --max-messages 5
```

## Project Structure

```text
SPARK-STREAMING/                # Root project directory containing the entire streaming pipeline

├── checkpoints/                # Spark checkpoint directory used for fault tolerance and recovery
│                               # Stores Kafka offsets and aggregation state

├── output/                     # Output directory where Spark writes aggregated Parquet files
│                               # Contains analytical results generated by the streaming job

├── producer/                   # Data ingestion component (network event generator)
│
│   ├── Dockerfile             # Defines the Docker image for the Producer container
│   │                          # Specifies base image, dependencies, and execution command
│
│   └── producer.py            # Python script that generates simulated network events
│                              # Sends JSON messages to Kafka topic "network_events"

├── spark/                     # Stream processing component (real-time analytics engine)
│
│   ├── Dockerfile             # Defines the Docker image for the Spark container
│   │                          # Installs Spark and configures the streaming environment
│
│   └── spark_stream.py       # Main Spark Structured Streaming application
│                              # Reads events from Kafka, processes them, and writes Parquet output

├── .gitignore                 # Specifies files and folders excluded from Git version control
│                              # Prevents committing checkpoints, output, and temporary files

├── Commands.txt               # Contains useful Docker and debugging commands
│                              # Used to build, run, and monitor the pipeline

├── docker                     # Optional Docker helper files or configuration (if present)

└── docker-compose.yml        # Main orchestration file that starts all services
                               # Defines Producer, Kafka, and Spark containers and networking
```

## Spark Streaming Details

### Schema (StructType)

Kafka message values arrive as bytes. Spark converts them to string and parses JSON into columns using an explicit schema:

* timestamp: string
* source_ip: string
* destination_ip: string
* bytes: int
* port: int
* protocol: string

