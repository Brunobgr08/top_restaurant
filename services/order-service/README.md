# Order Service

O **Order Service** é responsável pelo gerenciamento dos pedidos realizados pelos clientes. Ele se comunica com os serviços de cardápio (menu-service), pagamento (payment-service) e utiliza eventos Kafka para manter a integridade e a sincronização do sistema.

## 🚀 Funcionalidades

- ✅ Recebe pedidos via API REST
- ✅ Valida itens do pedido com base no cardápio (menu-service)
- ✅ Armazena pedidos com status inicial `pending`
- ✅ Publica eventos `order_created` e `order_updated` no Kafka
- ✅ Atualiza status do pedido baseado em eventos `payment_updated`
- ✅ Cache Redis para minimizar chamadas ao menu-service
- ✅ Sincronização automática via evento `menu_updated`
- ✅ Cobertura de testes 98%+

## 📋 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/orders` | Cria um novo pedido |
| `GET` | `/api/v1/orders` | Lista todos os pedidos |
| `PUT` | `/api/v1/payments/confirm/{order_id}` | Proxy para confirmação de pagamento |

## 🏗️ Estrutura de Diretórios

```
services/order-service/
├── main.py              # Entry point da aplicação
├── cache.py            # Gerenciamento do cache Redis
├── controllers.py      # Lógica de negócio
├── proxy_routes.py     # Rotas proxy para outros serviços
├── routes.py          # Rotas principais
├── models.py          # Modelos SQLAlchemy
├── schemas.py         # Schemas Pydantic
├── database.py        # Configuração do banco
├── kafka_producer.py  # Publicação de eventos
├── kafka_consumer.py  # Consumo de eventos
├── init.sql          # Script de inicialização do DB
├── tests/            # Testes unitários
├── Dockerfile        # Container Docker
├── requirements.txt  # Dependências Python
└── README.md        # Esta documentação
```

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Redis** - Cache em memória
- **Kafka** - Mensageria assíncrona (via confluent-kafka)
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI
- **Requests** - Cliente HTTP
- **Pytest** - Framework de testes

## 🚀 Executando Localmente

### Via Docker Compose (Recomendado)
```bash
# Na raiz do projeto
docker compose up --build order-service
```

### Desenvolvimento Local
```bash
cd services/order-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5001 --reload
```

### Acesso à Documentação
- **Swagger UI:** http://localhost:5001/docs
- **ReDoc:** http://localhost:5001/redoc

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DB_HOST` | Host do banco PostgreSQL | `order-db` |
| `DB_PORT` | Porta do banco | `5432` |
| `DB_NAME` | Nome do banco | `orderdb` |
| `DB_USER` | Usuário do banco | `user` |
| `DB_PASS` | Senha do banco | `pass` |
| `KAFKA_BROKERS` | Lista de brokers Kafka | `kafka-controller:9092` |
| `REDIS_HOST` | Host do Redis | `redis` |
| `REDIS_PORT` | Porta do Redis | `6379` |

## 📬 Eventos Kafka

### Eventos Publicados
- **`order_created`**: Novo pedido criado
  ```json
  {
    "event_type": "order_created",
    "order_id": "uuid",
    "total_price": 25.50,
    "payment_type": "manual|online",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```

- **`order_updated`**: Status do pedido alterado
  ```json
  {
    "event_type": "order_updated",
    "order_id": "uuid",
    "status": "pending|paid|failed",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```

### Eventos Consumidos
- **`menu_updated`**: Atualiza cache local do cardápio
- **`payment_updated`**: Altera status do pedido baseado no pagamento

## 🔄 Integrações

### Dependências Diretas
- **Menu Service**: Validação de itens e preços
- **Payment Service**: Confirmação de pagamentos (via proxy)
- **Redis**: Cache do cardápio
- **Kafka**: Comunicação assíncrona

### Fluxo de Pedido
1. Cliente submete pedido via POST `/api/v1/orders`
2. Validação dos itens contra cache/menu-service
3. Criação do pedido com status `pending`
4. Publicação do evento `order_created`
5. Payment-service processa pagamento
6. Recebimento do evento `payment_updated`
7. Atualização do status e publicação `order_updated`

## 🐳 Docker

### Build da Imagem
```bash
# Na raiz do projeto
docker build -f services/order-service/Dockerfile -t order-service .
```

### Execução Standalone
```bash
docker run -d \
  -p 5001:5001 \
  -e DB_HOST=localhost \
  -e REDIS_HOST=localhost \
  -e KAFKA_BROKERS=localhost:9092 \
  order-service
```

## 🧪 Executando os Testes

### Testes Básicos
```bash
docker exec -it top-restaurant_order-service_1 pytest -v
```

### Testes com Cobertura
```bash
docker exec -it top-restaurant_order-service_1 pytest --cov=. --cov-report=term --cov-report=html
```

## 📊 Métricas de Qualidade

- **Cobertura de Testes:** 98%+
- **Cache Hit Rate:** Monitorado via Redis
- **Latência Média:** < 100ms para criação de pedidos
- **Throughput:** Suporta 1000+ pedidos/min

## 🚧 Roadmap

- [ ] Histórico de status dos pedidos
- [ ] Cancelamento de pedidos
- [ ] Estimativa de tempo de preparo
- [ ] Notificações em tempo real (WebSocket)
- [ ] Métricas de performance (Prometheus)

