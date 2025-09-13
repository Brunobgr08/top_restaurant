# TopRestaurant

## 🍽️ Sistema de Pedidos - Microserviços com Kafka e Docker

### Descrição

Este projeto é uma aplicação backend simulando um sistema de pedidos para restaurante baseado em uma arquitetura de microserviços, com múltiplos serviços especializados em diferentes funcionalidades: autenticação, gerenciamento de cardápio, pedidos, pagamentos e notificações.

Os serviços se comunicam via Apache Kafka usando arquitetura KRaft (sem Zookeeper). Microserviços estruturados em Python (FastAPI), usando Docker para conteinerização.
Há um frontend simples para interação com o sistema, construído com React, TypeScript e Vite.

## 📦 Estrutura do Projeto

```
.
├── services
│   ├── auth-service (🚧 EM DESENVOLVIMENTO)
│   ├── menu-service (✅ COMPLETO)
│   ├── order-service (✅ COMPLETO)
│   ├── payment-service (✅ COMPLETO)
│   └── notification-service (🚧 EM DESENVOLVIMENTO)
├── frontend (✅ COMPLETO)
├── shared
│   ├── kafka
│   │   ├── create_topics.py
│   │   ├── consumer.py
│   │   └── producer.py
│   └── enums.py
├── .github/workflows
│   └── deploy-to-railway.yml
├── docker-compose.yml
└── README.md
```

---

## 🔧 Serviços

### 🔐 Auth Service (🚧 Em Desenvolvimento)

- **Status:** Feature em desenvolvimento
- **Função:** Cadastro, login e autenticação de usuários com JWT
- **Stack:** FastAPI, SQLAlchemy, PostgreSQL, JWT (jose), Bcrypt
- **Endpoints Planejados:**
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/refresh`
- **Extras:** UUID para identificação do usuário
- **Porta:** 5004

### 📋 Menu Service (✅ Completo)

- **Função:** Gerenciamento do cardápio de itens disponíveis para pedido
- **Stack:** FastAPI, PostgreSQL, Kafka
- **Endpoints:**
  - `GET /api/v1/menu` - Lista itens do menu
  - `POST /api/v1/menu` - Cria novo item
  - `GET /api/v1/menu/{item_id}` - Obtém item específico
  - `PUT /api/v1/menu/{item_id}` - Atualiza item
  - `DELETE /api/v1/menu/{item_id}` - Remove item
- **Eventos Kafka:**
  - Publica: `menu_updated`
- **Porta:** 5003
- **Cobertura de Testes:** 98%+

### 🛒 Order Service (✅ Completo)

- **Função:** Criação e gerenciamento de pedidos
- **Stack:** FastAPI, PostgreSQL, Kafka, Redis
- **Endpoints:**
  - `POST /api/v1/orders` - Cria novo pedido
  - `GET /api/v1/orders` - Lista pedidos
- **Eventos Kafka:**
  - Publica: `order_created`, `order_updated`
  - Consome: `menu_updated`, `payment_updated`
- **Integrações:**
  - Cache de cardápio via Redis
  - Validação de itens com menu-service
- **Porta:** 5001
- **Cobertura de Testes:** 94%+

### 💳 Payment Service (✅ Completo)

- **Função:** Processamento e confirmação de pagamentos
- **Stack:** FastAPI, PostgreSQL, Kafka
- **Fluxo:**
  - Pagamento `manual`: registra como `pending` e aguarda confirmação
  - Pagamento `online`: processa automaticamente
- **Endpoints:**
  - `GET /api/v1/payments` - Lista pagamentos
  - `PUT /api/v1/payments/confirm/{order_id}` - Confirma pagamento manual
- **Eventos Kafka:**
  - Publica: `payment_updated`
  - Consome: `order_created`
- **Porta:** Interno (não exposta)
- **Cobertura de Testes:** 97%+

### 🔔 Notification Service (🚧 Em Desenvolvimento)

- **Status:** Feature em desenvolvimento
- **Função:** Enviar notificações quando eventos são recebidos
- **Stack:** FastAPI, PostgreSQL, Kafka
- **Eventos Consumidos:** `order_created`, `payment_updated`, `order_updated`
- **Futuro:** Integração com e-mail, push notification ou WhatsApp API

---

## 🖥️ Frontend

- **Stack:** React + TypeScript + Vite + Tailwind CSS + ShadCN UI
- **Servidor:** Node.js com `serve` (servidor estático)
- **Funcionalidades:**
  - ✅ Visualização do cardápio
  - ✅ Criação de pedidos com múltiplos itens
  - ✅ Seleção de tipo de pagamento (manual/online)
  - ✅ Validação visual com animações
  - ✅ Design responsivo
  - ✅ Notificações de sucesso/erro
- **Build:** Docker multi-stage com Node.js
- **Porta:** 3000

## 📦 Build e Deploy

### Desenvolvimento Local

1. **Stage 1**: Build com Node.js

   - Instala dependências
   - Executa `npm run build`
   - Gera pasta `dist/`

2. **Stage 2**: Serve com Node.js
   - Copia arquivos do `dist/`
   - Usa servidor `serve` para arquivos estáticos
   - Suporte a SPA com fallback para index.html
   - Expõe na porta 3000

### Deploy em Produção (Railway)

O projeto possui pipeline automatizado de CI/CD via GitHub Actions:

- **Arquivo:** `.github/workflows/deploy-to-railway.yml`
- **Triggers:** Push para `main` e `develop`, PRs para `main`
- **Processo:**
  1. **Testes:** Executa testes de todos os serviços
  2. **Deploy:** Deploy automático para Railway de cada serviço
  3. **Serviços:** menu-service, order-service, payment-service, frontend

#### Configuração Railway

```env
# Secrets necessários no GitHub
RAILWAY_TOKEN=<seu-token-railway>
RAILWAY_PROJECT_ID=<id-do-projeto>
```

#### URLs de Produção

- **Frontend:** https://frontend-production.up.railway.app
- **Menu API:** https://menu-service-production.up.railway.app
- **Order API:** https://order-service-production.up.railway.app
- **Payment API:** https://payment-service-production.up.railway.app

---

## 📬 Kafka - Arquitetura de Eventos

### Configuração

- **Modo:** KRaft (sem Zookeeper)
- **Brokers:** 3 instâncias para alta disponibilidade
- **Portas:** 9092, 9094, 9095

### Tópicos Principais

- `order_created`: Novo pedido criado (order-service → payment-service)
- `payment_updated`: Status de pagamento atualizado (payment-service → order-service)
- `menu_updated`: Cardápio atualizado (menu-service → order-service)
- `order_updated`: Status do pedido atualizado (order-service → notification-service)

---

## ⚙️ Executando o Projeto

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (para desenvolvimento frontend)
- Make (geralmente pré-instalado no Linux/macOS)

### Comandos MakeFile - Execução Rápida

#### **Comandos Essenciais**

```bash
# Setup inicial completo
make setup

# Subir todos os serviços
make up

# Subir apenas serviços essenciais
make up-core

# Parar todos os serviços
make down
```

### Serviços Disponíveis (Desenvolvimento)

- **Frontend:** http://localhost:3000
- **Menu API:** http://localhost:5003/docs
- **Order API:** http://localhost:5001/docs

### Serviços Disponíveis (Produção)

- **Frontend:** https://frontend-production.up.railway.app
- **Menu API:** https://menu-service-production.up.railway.app/docs
- **Order API:** https://order-service-production.up.railway.app/docs

#### **Verificação e Monitoramento**

```bash
# Verificar saúde de todos os serviços
make health

# Status dos containers
make ps

# Logs de todos os serviços
make logs

# Logs de um serviço específico
make logs-order-service
make logs-payment-service
make logs-menu-service
```

#### **Serviços Individuais**

```bash
# Subir um serviço específico
make up-order-service
make up-payment-service
make up-menu-service

# Parar um serviço específico
make stop-order-service

# Acessar shell de um container
make bash-order-service
make bash-payment-service
make bash-menu-service

# Reinstalar requirements em um serviço
make pip-install-order-service
```

#### **Frontend**

```bash
# Instalar dependências do frontend
make install-frontend

# Executar testes do frontend
make test-frontend

# Iniciar servidor de desenvolvimento do frontend
make dev-frontend

# Buildar frontend para produção
make build-frontend
```

#### **Banco de Dados**

```bash
# Conectar ao banco de dados de um serviço
make db-order-service
make db-payment-service
make db-menu-service

# Fazer backup do banco de dados
make backup-order-service
make backup-payment-service
make backup-menu-service
```

#### **Kafka**

```bash
# Criar tópicos do Kafka
make kafka-topics

# Listar tópicos do Kafka
make kafka-list
```

#### **Limpeza e Reset**

```bash
# Limpeza completa (remove containers, volumes, imagens)
make clean

# Reset completo (limpa tudo e reconstrói)
make reset

# Limpar apenas volumes
make clean-volumes

# Limpar arquivos de cobertura
make coverage-clean
```

### Comandos Docker Tradicionais (Alternativa)

```bash
# Comando principal
docker compose up --build

# Apenas serviços essenciais
docker compose up -d --build frontend menu-service order-service payment-service

# Logs de um serviço específico
docker compose logs -f order-service

# Executar testes manualmente
docker exec -it top-restaurant_payment-service_1 pytest --cov=.

# Parar tudo
docker compose down --volumes
```

---

## 🧪 Testes e Qualidade

### Cobertura Atual

- **Payment Service:** 98%+
- **Menu Service:** 98%+
- **Order Service:** 98%+

### Executando Testes

```bash
# Executar testes de um serviço específico com cobertura
make test-order-service
make test-payment-service
make test-menu-service

# Executar testes de todos os serviços
make test-all

# Executar testes rápidos (sem cobertura)
make test-quick-order-service

# Abrir relatório de cobertura HTML
make open-coverage-order-service
```

---

## 🚧 Roadmap

### Próximas Funcionalidades

- [ ] **Auth Service:** Sistema completo de autenticação
- [ ] **Notification Service:** Notificações por e-mail/WhatsApp
- [ ] **Frontend:** Integração com auth-service
- [ ] **Dashboard:** Painel administrativo para pedidos
- [ ] **Gateway:** API Gateway com rate limiting
- [ ] **Monitoring:** Prometheus + Grafana
- [x] **CI/CD:** Pipeline automatizado (Railway)

### Melhorias Técnicas

- [ ] Refresh tokens no auth-service
- [ ] Integração com gateway de pagamento real
- [ ] Logs estruturados (JSON)
- [ ] Health checks mais robustos
- [ ] Backup automatizado dos bancos
- [x] Deploy automatizado via GitHub Actions

---

## 🚀 Deploy e Produção

### GitHub Actions Pipeline

O projeto utiliza GitHub Actions para CI/CD automatizado:

```yaml
# .github/workflows/deploy-to-railway.yml
name: Deploy to Railway

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

**Etapas do Pipeline:**

1. **Testes:** Execução completa da suíte de testes
2. **Build:** Construção das imagens Docker
3. **Deploy:** Deploy automático para Railway

### Configuração de Produção

#### Variáveis de Ambiente (Railway)

```env
# Frontend
VITE_API_BASE_ORDERS=https://order-service-production.up.railway.app
VITE_API_BASE_MENU=https://menu-service-production.up.railway.app

# Backend Services
DB_HOST=<railway-postgres-host>
DB_PORT=5432
KAFKA_BROKERS=<kafka-cloud-brokers>
```

#### Monitoramento

- **Logs:** Centralizados via Railway Dashboard
- **Health Checks:** Configurados para cada serviço
- **Uptime:** Monitoramento automático Railway

---

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente Importantes

```env
# Kafka
KAFKA_BROKERS=kafka-controller:9092,kafka-broker-2:9094,kafka-broker-3:9095

# Databases
DB_HOST=<service>-db
DB_PORT=5432
DB_USER=user
DB_PASS=pass

# Auth (quando disponível)
JWT_SECRET=super-secret-key
```

### Portas dos Bancos

- Auth DB: 5437
- Order DB: 5433
- Payment DB: 5434
- Notification DB: 5435
- Menu DB: 5436
- Redis: 6379

---

## 📝 Observações Técnicas

- **Desenvolvimento:** `UVICORN_RELOAD=true` no payment-service (removido em produção)
- **Rede:** Todos os serviços na mesma rede Docker para comunicação interna
- **Volumes:** Dados persistidos em volumes nomeados
- **Logs:** Centralizados via Docker Compose logs
- **Saúde:** Health checks configurados para dependências críticas
