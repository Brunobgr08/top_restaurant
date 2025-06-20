# Frontend TopRestaurant

Aplicação frontend para o sistema de pedidos TopRestaurant, construída com React, TypeScript e Vite.

## 🚀 Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Node.js v18+ (para desenvolvimento local)

### 📦 Opções de Instalação

#### 1. Usando Docker Compose (Recomendado)

```bash
# Na raiz do projeto (onde está o docker-compose.yml)
docker-compose up --build frontend
```

Acesse `http://localhost:3000` no navegador.

#### 2. Desenvolvimento Local

```bash
# Na pasta frontend
cd frontend
npm install    # Instalar dependências
npm run dev
```

Acesse `http://localhost:5173` no navegador.

#### 3. Apenas Frontend com Docker

```bash
# Na pasta frontend
cd frontend
docker build -t frontend .
docker run -p 3000:80 frontend
```

Acesse `http://localhost:5173` no navegador.
