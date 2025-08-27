FROM python:3.10-slim

WORKDIR /app

# Instale apenas dependências necessárias
RUN apt-get update && apt-get install -y librdkafka-dev && rm -rf /var/lib/apt/lists/*

COPY shared /app/shared
COPY services/order-service/ /app/

# Instale dependências
RUN pip install --no-cache-dir -r requirements.txt

USER 1000

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]