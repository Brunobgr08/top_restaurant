FROM python:3.10-slim

WORKDIR /app

# Evita problemas de DNS e SSL em ambientes Docker minimalistas
RUN apt-get update && \
    apt-get install -y netcat-openbsd iputils-ping ca-certificates wget && \
    rm -rf /var/lib/apt/lists/*

COPY create_topics.py .

RUN pip install --no-cache-dir kafka-python

CMD ["python", "create_topics.py"]