FROM python:3.10-slim

WORKDIR /app

# Primeiro copia apenas requirements.txt para aproveitar cache do Docker
COPY services/notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Depois copia o resto do código
COPY services/notification-service/ .

# Configura o PYTHONPATH para incluir a pasta shared
ENV PYTHONPATH="${PYTHONPATH}:/app/shared"

CMD ["python", "app.py"]