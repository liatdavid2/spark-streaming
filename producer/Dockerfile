FROM python:3.10

WORKDIR /app

RUN pip install kafka-python

COPY producer.py .

CMD ["python", "/app/producer.py"]