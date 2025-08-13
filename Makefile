# TopRestaurant - Makefile para desenvolvimento
# ===============================================

# Configuracoes
SERVICES = order-service payment-service menu-service
CONTAINERS = top-restaurant_order-service top-restaurant_payment-service top-restaurant_menu-service
FRONTEND_DIR = ./frontend
COV_OPTS = --cov=. --cov-report=term --cov-report=html

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# ===============================================
# Docker - Comandos Gerais
# ===============================================

## Sobe todos os servicos
up:
	@echo "$(GREEN)🚀 Subindo todos os servicos...$(NC)"
	docker compose up -d --build

## Para todos os servicos
down:
	@echo "$(YELLOW)⏹️  Parando todos os servicos...$(NC)"
	docker compose down

## Reinicia todos os servicos
restart:
	@echo "$(YELLOW)🔄 Reiniciando todos os servicos...$(NC)"
	docker compose down && docker compose up -d --build

## Sobe apenas servicos essenciais (sem auth/notification)
up-core:
	@echo "$(GREEN)🚀 Subindo servicos essenciais...$(NC)"
	docker compose up -d --build frontend menu-service order-service payment-service

## Status dos containers
ps:
	@echo "$(GREEN)📊 Status dos containers:$(NC)"
	docker compose ps

## Logs de todos os servicos
logs:
	docker compose logs -f

## Logs de um servico especifico (ex: make logs-order-service)
logs-%:
	@echo "$(GREEN)📋 Logs do $*:$(NC)"
	docker compose logs -f $*

# ===============================================
# Servicos Individuais
# ===============================================

## Builda um servico especifico (ex: make build-order-service)
build-%:
	@echo "$(GREEN)🔨 Buildando $*...$(NC)"
	docker compose build $*

## Sobe um servico especifico (ex: make up-order-service)
up-%:
	@echo "$(GREEN)🚀 Subindo $*...$(NC)"
	docker compose up -d --build $*

## Para um servico especifico (ex: make stop-order-service)
stop-%:
	@echo "$(YELLOW)⏹️  Parando $*...$(NC)"
	docker compose stop $*
	docker compose rm -f $*

## Shell interativo em um servico (ex: make bash-order-service)
bash-%:
	@echo "$(GREEN)💻 Abrindo shell no $*...$(NC)"
	docker exec -it top-restaurant_$* /bin/bash

## Reinstala requirements em um servico (ex: make pip-install-order-service)
pip-install-%:
	@echo "$(GREEN)📦 Reinstalando requirements no $*...$(NC)"
	docker exec -it top-restaurant_$* pip install -r requirements.txt

# ===============================================
# Testes
# ===============================================

## Executa testes de um servico especifico (ex: make test-order-service)
test-%:
	@echo "$(GREEN)🧪 Executando testes do $*...$(NC)"
	docker exec -it top-restaurant_$* pytest $(COV_OPTS)

## Executa testes de todos os servicos
test-all:
	@echo "$(GREEN)🧪 Executando testes de todos os servicos...$(NC)"
	@for svc in $(SERVICES); do \
		echo "$(YELLOW)==> Testando $$svc...$(NC)"; \
		docker exec -it top-restaurant_$${svc} pytest $(COV_OPTS) || exit 1; \
	done
	@echo "$(GREEN)✅ Todos os testes concluidos!$(NC)"

## Executa testes com container temporario (ex: make test-once-order-service)
test-once-%:
	@echo "$(GREEN)🧪 Executando testes do $* (container temporario)...$(NC)"
	docker compose run --rm $* pytest tests

## Executa apenas testes rapidos (sem cobertura)
test-quick-%:
	@echo "$(GREEN)⚡ Testes rapidos do $*...$(NC)"
	docker exec -it top-restaurant_$* pytest -v

## Executa testes com modo watch (desenvolvimento)
test-watch-%:
	@echo "$(GREEN)👀 Testes em modo watch do $*...$(NC)"
	docker exec -it top-restaurant_$* pytest --looponfail

# ===============================================
# Cobertura de Testes
# ===============================================

## Limpa arquivos de cobertura
coverage-clean:
	@echo "$(YELLOW)🧹 Limpando arquivos de cobertura...$(NC)"
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

## Abre relatorio de cobertura (ex: make open-coverage-order-service)
open-coverage-%:
	@target=./services/$*/htmlcov/index.html; \
	if [ -f $$target ]; then \
		echo "$(GREEN)📊 Abrindo relatorio de cobertura do $*...$(NC)"; \
		xdg-open $$target || open $$target || echo "$(YELLOW)Abra manualmente $$target$(NC)"; \
	else \
		echo "$(RED)❌ Arquivo de cobertura nao encontrado para $*$(NC)"; \
		echo "$(YELLOW)Execute 'make test-$*' primeiro$(NC)"; \
	fi

## Gera relatorio de cobertura para todos os servicos
coverage-all:
	@echo "$(GREEN)📊 Gerando relatorios de cobertura...$(NC)"
	@for svc in $(SERVICES); do \
		echo "$(YELLOW)==> Cobertura do $$svc...$(NC)"; \
		docker exec -it top-restaurant_$${svc} pytest $(COV_OPTS); \
	done

# ===============================================
# Frontend
# ===============================================

## Instala dependencias do frontend
install-frontend:
	@echo "$(GREEN)📦 Instalando dependencias do frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm install

## Executa testes do frontend
test-frontend:
	@echo "$(GREEN)🧪 Executando testes do frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm test -- --watchAll=false

## Builda o frontend para producao
build-frontend:
	@echo "$(GREEN)🔨 Buildando frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run build

## Executa linting do frontend
lint-frontend:
	@echo "$(GREEN)🔍 Executando lint do frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint || true

## Inicia servidor de desenvolvimento do frontend
dev-frontend:
	@echo "$(GREEN)🚀 Iniciando servidor de desenvolvimento do frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run dev

# ===============================================
# Kafka
# ===============================================

## Cria topicos do Kafka
kafka-topics:
	@echo "$(GREEN)📬 Criando topicos do Kafka...$(NC)"
	docker compose up -d kafka-controller kafka-broker-2 kafka-broker-3
	sleep 10
	docker compose run --rm kafka-init

## Lista topicos do Kafka
kafka-list:
	@echo "$(GREEN)📋 Listando topicos do Kafka...$(NC)"
	docker exec -it top-restaurant_kafka-controller kafka-topics --bootstrap-server localhost:9092 --list

# ===============================================
# Banco de Dados
# ===============================================

## Conecta ao banco de um servico (ex: make db-order-service)
db-%:
	@echo "$(GREEN)🗄️  Conectando ao banco do $*...$(NC)"
	@case $* in \
		order-service) docker exec -it top-restaurant_order-db psql -U user -d orderdb ;; \
		payment-service) docker exec -it top-restaurant_payment-db psql -U user -d paymentdb ;; \
		menu-service) docker exec -it top-restaurant_menu-db psql -U user -d menudb ;; \
		*) echo "$(RED)❌ Servico $* nao reconhecido$(NC)" ;; \
	esac

## Backup do banco de um servico (ex: make backup-order-service)
backup-%:
	@echo "$(GREEN)💾 Fazendo backup do banco do $*...$(NC)"
	@case $* in \
		order-service) docker exec top-restaurant_order-db pg_dump -U user orderdb > backup_orderdb_$(shell date +%Y%m%d_%H%M%S).sql ;; \
		payment-service) docker exec top-restaurant_payment-db pg_dump -U user paymentdb > backup_paymentdb_$(shell date +%Y%m%d_%H%M%S).sql ;; \
		menu-service) docker exec top-restaurant_menu-db pg_dump -U user menudb > backup_menudb_$(shell date +%Y%m%d_%H%M%S).sql ;; \
		*) echo "$(RED)❌ Servico $* nao reconhecido$(NC)" ;; \
	esac

# ===============================================
# Limpeza e Reset
# ===============================================

## Remove containers, volumes e imagens
clean:
	@echo "$(RED)🧹 Limpeza completa do sistema...$(NC)"
	docker compose down --volumes --remove-orphans
	docker volume prune -f
	docker system prune -af

## Reset completo (limpa tudo e reconstroi)
reset:
	@echo "$(RED)🔄 Reset completo do projeto...$(NC)"
	make clean
	make up

## Remove apenas volumes (mantem imagens)
clean-volumes:
	@echo "$(YELLOW)🗑️  Removendo volumes...$(NC)"
	docker compose down --volumes
	docker volume prune -f

# ===============================================
# Desenvolvimento
# ===============================================

## Setup inicial do projeto
setup:
	@echo "$(GREEN)🎯 Setup inicial do projeto...$(NC)"
	make install-frontend
	make up
	sleep 30
	make kafka-topics
	@echo "$(GREEN)✅ Setup concluido! Acesse http://localhost:3000$(NC)"

## Verifica saude dos servicos
health:
	@echo "$(GREEN)🏥 Verificando saude dos servicos...$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Order API: http://localhost:5001/docs"
	@echo "Menu API: http://localhost:5003/docs"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)✅ Frontend OK$(NC)" || echo "$(RED)❌ Frontend DOWN$(NC)"
	@curl -s http://localhost:5001/docs > /dev/null && echo "$(GREEN)✅ Order Service OK$(NC)" || echo "$(RED)❌ Order Service DOWN$(NC)"
	@curl -s http://localhost:5003/docs > /dev/null && echo "$(GREEN)✅ Menu Service OK$(NC)" || echo "$(RED)❌ Menu Service DOWN$(NC)"

## Mostra ajuda
help:
	@echo "$(GREEN)TopRestaurant - Comandos Disponiveis:$(NC)"
	@echo ""
	@echo "$(YELLOW)🐳 Docker:$(NC)"
	@echo "  make up              - Sobe todos os servicos"
	@echo "  make up-core         - Sobe apenas servicos essenciais"
	@echo "  make down            - Para todos os servicos"
	@echo "  make restart         - Reinicia todos os servicos"
	@echo "  make ps              - Status dos containers"
	@echo "  make logs            - Logs de todos os servicos"
	@echo ""
	@echo "$(YELLOW)🔧 Servicos Individuais:$(NC)"
	@echo "  make up-<service>    - Sobe um servico especifico"
	@echo "  make stop-<service>  - Para um servico especifico"
	@echo "  make bash-<service>  - Shell no container"
	@echo "  make logs-<service>  - Logs de um servico"
	@echo ""
	@echo "$(YELLOW)🧪 Testes:$(NC)"
	@echo "  make test-<service>  - Testes com cobertura"
	@echo "  make test-all        - Testes de todos os servicos"
	@echo "  make test-quick-<service> - Testes rapidos"
	@echo ""
	@echo "$(YELLOW)📊 Cobertura:$(NC)"
	@echo "  make open-coverage-<service> - Abre relatorio HTML"
	@echo "  make coverage-clean  - Limpa arquivos de cobertura"
	@echo ""
	@echo "$(YELLOW)🖥️  Frontend:$(NC)"
	@echo "  make install-frontend - Instala dependencias"
	@echo "  make test-frontend   - Testes do frontend"
	@echo "  make dev-frontend    - Servidor de desenvolvimento"
	@echo ""
	@echo "$(YELLOW)🎯 Utilitarios:$(NC)"
	@echo "  make setup           - Setup inicial completo"
	@echo "  make health          - Verifica saude dos servicos"
	@echo "  make clean           - Limpeza completa"
	@echo "  make help            - Esta ajuda"

.PHONY: up down restart up-core ps logs build-% up-% stop-% bash-% pip-install-% test-% test-all test-once-% test-quick-% test-watch-% coverage-clean open-coverage-% coverage-all install-frontend test-frontend build-frontend lint-frontend dev-frontend kafka-topics kafka-list db-% backup-% clean reset clean-volumes setup health help
