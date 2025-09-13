FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y netcat-openbsd iputils-ping ca-certificates wget && \
    rm -rf /var/lib/apt/lists/*

COPY create_topics.py wait_for_kafka.py ./

RUN pip install --no-cache-dir kafka-python python-dotenv

CMD ["sh", "-c", "python wait_for_kafka.py && python create_topics.py"]