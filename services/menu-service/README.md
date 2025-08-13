# Menu Service

O **Menu Service** é responsável por gerenciar o cardápio da aplicação, incluindo operações de cadastro, atualização, listagem e exclusão de itens do menu. Ele também emite eventos Kafka para manter outros microserviços sincronizados com o estado atual do cardápio.

## 🚀 Funcionalidades

- ✅ CRUD completo de itens de menu (nome, descrição, preço)
- ✅ Validação de integridade dos dados com Pydantic
- ✅ Emissão de eventos Kafka `menu_updated` a cada alteração
- ✅ Integração com o `order-service` via cache e eventos Kafka
- ✅ Documentação automática com FastAPI/Swagger
- ✅ Cobertura de testes 98%+

## 📋 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/menu` | Cria um novo item no menu |
| `GET` | `/api/v1/menu` | Lista todos os itens do menu |
| `GET` | `/api/v1/menu/{item_id}` | Obtém um item específico por ID |
| `PUT` | `/api/v1/menu/{item_id}` | Atualiza um item do menu |
| `DELETE` | `/api/v1/menu/{item_id}` | Remove um item do menu |

## 🏗️ Estrutura de Diretórios

```
services/menu-service/
├── main.py              # Entry point da aplicação
├── controllers.py       # Lógica de negócio
├── routes.py           # Definição das rotas
├── models.py           # Modelos SQLAlchemy
├── schemas.py          # Schemas Pydantic
├── database.py         # Configuração do banco
├── kafka_producer.py   # Publicação de eventos
├── init.sql           # Script de inicialização do DB
├── tests/             # Testes unitários
├── Dockerfile         # Container Docker
├── requirements.txt   # Dependências Python
└── README.md         # Esta documentação
```

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Kafka** - Mensageria assíncrona (via confluent-kafka)
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI
- **Pytest** - Framework de testes

## 🚀 Executando Localmente

### Via Docker Compose (Recomendado)
```bash
# Na raiz do projeto
docker compose up --build menu-service
```

### Desenvolvimento Local
```bash
cd services/menu-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5003 --reload
```

### Acesso à Documentação
- **Swagger UI:** http://localhost:5003/docs
- **ReDoc:** http://localhost:5003/redoc

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DB_HOST` | Host do banco PostgreSQL | `menu-db` |
| `DB_PORT` | Porta do banco | `5432` |
| `DB_NAME` | Nome do banco | `menudb` |
| `DB_USER` | Usuário do banco | `user` |
| `DB_PASS` | Senha do banco | `pass` |
| `KAFKA_BROKERS` | Lista de brokers Kafka | `kafka-controller:9092` |

## 📬 Eventos Kafka

### Eventos Publicados
- **`menu_updated`**: Emitido quando um item é criado, atualizado ou removido
  ```json
  {
    "event_type": "menu_updated",
    "item_id": "uuid",
    "action": "created|updated|deleted",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```

## 🐳 Docker

### Build da Imagem
```bash
# Na raiz do projeto
docker build -f services/menu-service/Dockerfile -t menu-service .
```

### Execução Standalone
```bash
docker run -d \
  -p 5003:5003 \
  -e DB_HOST=localhost \
  -e KAFKA_BROKERS=localhost:9092 \
  menu-service
```

## 🧪 Executando os Testes

### Testes Básicos
```bash
docker exec -it top-restaurant_menu-service_1 pytest -v
```

### Testes com Cobertura
```bash
docker exec -it top-restaurant_menu-service_1 pytest --cov=. --cov-report=term --cov-report=html
```

### Relatório HTML
O relatório de cobertura HTML fica disponível em `htmlcov/index.html`

## 📊 Métricas de Qualidade

- **Cobertura de Testes:** 98%+
- **Endpoints:** 5 rotas implementadas
- **Validação:** 100% dos inputs validados
- **Documentação:** Auto-gerada via FastAPI

## 🔗 Integrações

### Dependências
- **PostgreSQL**: Armazenamento persistente
- **Kafka**: Comunicação assíncrona

### Consumidores dos Eventos
- **Order Service**: Atualiza cache local do cardápio

## 🚧 Roadmap

- [ ] Cache Redis para consultas frequentes
- [ ] Versionamento de API (v2)
- [ ] Categorização de itens
- [ ] Upload de imagens dos pratos
- [ ] Filtros avançados (preço, categoria)
