# README.md

## 🍽️ Sistema de Pedidos - Microserviços com Kafka e Docker

### Descrição

Aplicação backend distribuída simulando um sistema de pedidos para restaurante. Os serviços se comunicam via Apache Kafka. Estruturado em microserviços com Python (Flask ou FastAPI), usando Docker para conteinerização.

### 🔧 Serviços

- **menu-service**: fornece e gerencia o cardápio.
- **order-service**: recebe pedidos, publica em `order_created`.
- **payment-service**: processa pagamentos, publica em `payment_processed`.
- **notification-service**: envia mensagens baseadas nos eventos.
- **frontend**: interface simples (HTML/JS) para interação com o sistema.

### 📬 Kafka - Tópicos

- `order_created`: gerado pelo `order-service`
- `payment_processed`: resposta do `payment-service`
- `order_ready`: sinaliza que o pedido está pronto (gerado pelo `order-service`)

### 🐳 Docker Compose

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - '9092:9092'
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  order-db:
    image: postgres:13
    environment:
      POSTGRES_DB: orderdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - '5433:5432'

  payment-db:
    image: postgres:13
    environment:
      POSTGRES_DB: paymentdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - '5434:5432'

  notification-db:
    image: postgres:13
    environment:
      POSTGRES_DB: notificationdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - '5435:5432'

  menu-db:
    image: postgres:13
    environment:
      POSTGRES_DB: menudb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - '5436:5432'

  order-service:
    build: ./services/order-service
    depends_on:
      - kafka
      - order-db
    environment:
      DB_HOST: order-db
      DB_PORT: 5432
      DB_NAME: orderdb
      DB_USER: user
      DB_PASS: pass

  payment-service:
    build: ./services/payment-service
    depends_on:
      - kafka
      - payment-db
    environment:
      DB_HOST: payment-db
      DB_PORT: 5432
      DB_NAME: paymentdb
      DB_USER: user
      DB_PASS: pass

  notification-service:
    build: ./services/notification-service
    depends_on:
      - kafka
      - notification-db
    environment:
      DB_HOST: notification-db
      DB_PORT: 5432
      DB_NAME: notificationdb
      DB_USER: user
      DB_PASS: pass

  menu-service:
    build: ./services/menu-service
    depends_on:
      - menu-db
    environment:
      DB_HOST: menu-db
      DB_PORT: 5432
      DB_NAME: menudb
      DB_USER: user
      DB_PASS: pass

  frontend:
    image: nginx:alpine
    volumes:
      - ./frontend:/usr/share/nginx/html
    ports:
      - '8080:80'
```

### ▶️ Executando o Projeto

```bash
docker-compose up --build
```

### 📂 Exemplos de Código (order-service/app.py)

```python
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json
import psycopg2

app = Flask(__name__)
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

db = psycopg2.connect(
    dbname='orderdb',
    user='user',
    password='pass',
    host='order-db',
    port='5432'
)

@app.route('/order', methods=['POST'])
def create_order():
    order = request.json
    cursor = db.cursor()
    cursor.execute("INSERT INTO orders (data) VALUES (%s)", (json.dumps(order),))
    db.commit()
    producer.send('order_created', order)
    return jsonify({'message': 'Order created'}), 201
```

<!-- ## Tópicos Kafka
- `order_created`: produzido pelo order-service, consumido pelo payment-service
- `payment_processed`: produzido pelo payment-service, consumido pelo notification-service

Configurar execução automática dos consumidores via entrypoint.sh

Adicionar logs de rastreio para eventos Kafka

Implementar testes de integração para os serviços Kafka -->

<!-- Implementar a API REST para CRUD no menu-service

Criar testes de integração entre order-service e menu-service

Simular chamadas do order-service para buscar dados do menu -->

<!-- COMANDOS

Listar tópicos
kafka-topics --bootstrap-server kafka:9092 --list -->



<!-- Exemplos de JSONs para teste dos Endpoints


📦 POST /orders (Criar pedido)

{
  "customer_name": "João Silva",
  "item_name": "Pizza Calabresa",
  "quantity": 2,
  "total_price": 50.00
}
✅ Esperado: 201 Created

❌ Erro (campo ausente):

{
  "item_name": "Pizza Calabresa",
  "quantity": 2,
  "total_price": 50.00
}
🔁 Retorno esperado: 400 Bad Request, informando customer_name ausente

💳 POST /payments (Registrar pagamento manual direto)

{
  "order_id": 1,
  "amount": 50.00,
  "payment_type": "manual",
  "status": "paid"
}
✅ Esperado: 201 Created

❌ Erro 1: payment_type inválido

{
  "order_id": 1,
  "amount": 50.00,
  "payment_type": "online",
  "status": "paid"
}
🔁 Retorno esperado: 400 Bad Request com mensagem sobre tipo de pagamento

❌ Erro 2: status incorreto

{
  "order_id": 1,
  "amount": 50.00,
  "payment_type": "manual",
  "status": "pending"
}
🔁 Retorno esperado: 400 Bad Request com mensagem sobre o status exigido ser "paid"


🧾 POST /confirm-payment/{order_id} (Confirmar pagamento manual pendente)
POST /confirm-payment/2
✅ Esperado: 200 OK com mensagem de confirmação

❌ Erro: order_id não encontrado → 404 Not Found

❌ Erro: status já é "paid" → 400 Bad Request

❌ Erro: payment_type não é "manual" → 400 Bad Request


📋 GET /orders (Listar pedidos)
✅ Resposta esperada:

[
  {
    "id": 1,
    "customer_name": "João Silva",
    "item_name": "Pizza Calabresa",
    "quantity": 2,
    "total_price": 50.0,
    "status": "pending"
  }
]


💰 GET /payments (Listar pagamentos)
✅ Resposta esperada:

[
  {
    "id": 1,
    "order_id": 1,
    "amount": 50.0,
    "status": "paid",
    "payment_type": "manual",
    "created_at": "2025-06-09T12:34:56.789Z"
  }
] -->
