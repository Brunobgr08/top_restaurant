FROM python:3.10-slim

WORKDIR /app

# Instala dependências do Kafka
RUN apt-get update && apt-get install -y \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primeiro para aproveitar cache
COPY services/order-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do serviço e shared
COPY shared /app/shared
COPY services/order-service/ .

# Configura PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]