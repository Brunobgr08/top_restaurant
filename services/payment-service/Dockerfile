FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema para confluent-kafka
RUN apt-get update && apt-get install -y \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Primeiro copia apenas requirements.txt para aproveitar cache do Docker
COPY services/payment-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Depois copia o resto do código
COPY shared /app/shared
COPY services/payment-service/ .

# Configura o PYTHONPATH para incluir a pasta shared
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5002"]