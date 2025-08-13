# Frontend TopRestaurant

Aplicação frontend para o sistema de pedidos TopRestaurant, construída com React, TypeScript e Vite.

## 🚀 Tecnologias

- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool e dev server
- **Tailwind CSS** - Framework CSS utilitário
- **ShadCN UI** - Componentes UI
- **React Hook Form** - Gerenciamento de formulários
- **Framer Motion** - Animações
- **Sonner** - Notificações toast

## 🏗️ Arquitetura

```
frontend/
├── src/
│   ├── components/     # Componentes React
│   ├── services/       # APIs e tipos
│   ├── lib/           # Utilitários
│   └── main.tsx       # Entry point
├── public/            # Assets estáticos
├── nginx.conf         # Configuração Nginx
└── Dockerfile         # Build multi-stage
```

## 🚀 Como Executar

### 1. Docker Compose (Recomendado)
```bash
# Na raiz do projeto
docker compose up --build frontend
```
Acesse: http://localhost:3000

### 2. Desenvolvimento Local
```bash
cd frontend
npm install
npm run dev
```
Acesse: http://localhost:5173

### 3. Docker Standalone
```bash
cd frontend
docker build -t toprestaurant-frontend .
docker run -p 3000:80 toprestaurant-frontend
```

## 🔧 Configuração

### Variáveis de Ambiente
```env
# APIs (configuradas no nginx.conf)
VITE_API_BASE_ORDERS=http://localhost:5001
VITE_API_BASE_MENU=http://localhost:5003
```

### Proxy de Desenvolvimento
O Vite está configurado para fazer proxy das APIs:
- `/orders/*` → `order-service:5001`
- `/menu/*` → `menu-service:5003`

## 📱 Funcionalidades

### ✅ Implementadas
- [x] Visualização do cardápio completo
- [x] Seleção de itens com quantidade
- [x] Cálculo automático do total
- [x] Formulário de pedido validado
- [x] Seleção de tipo de pagamento
- [x] Animações e feedback visual
- [x] Design responsivo
- [x] Notificações de sucesso/erro

### 🚧 Em Desenvolvimento
- [ ] Autenticação de usuários
- [ ] Histórico de pedidos
- [ ] Status em tempo real
- [ ] Carrinho persistente

## 🎨 Design System

### Cores Principais
- Primary: Blue (pedidos)
- Success: Green (confirmações)
- Warning: Yellow (alertas)
- Error: Red (erros)

### Componentes
- **Card**: Container principal
- **Button**: Ações primárias/secundárias
- **Select**: Seleção de opções
- **Input**: Campos de formulário
- **Toast**: Notificações

## 🧪 Scripts Disponíveis

```bash
npm run dev          # Servidor de desenvolvimento
npm run build        # Build para produção
npm run preview      # Preview do build
npm run lint         # Linting com ESLint
```

## 📦 Build e Deploy

### Processo de Build
1. **Stage 1**: Build com Node.js
   - Instala dependências
   - Executa `npm run build`
   - Gera pasta `dist/`

2. **Stage 2**: Serve com Nginx
   - Copia arquivos do `dist/`
   - Configura proxy para APIs
   - Expõe na porta 80

### Nginx Configuration
```nginx
# Proxy para APIs
location /orders/ {
    proxy_pass http://order-service:5001/;
}

location /menu/ {
    proxy_pass http://menu-service:5003/;
}

# SPA fallback
location / {
    try_files $uri $uri/ /index.html;
}
```

## 🔗 Integrações

### APIs Consumidas
- **Menu Service** (`/api/v1/menu`)
  - GET: Lista itens do cardápio

- **Order Service** (`/api/v1/orders`)
  - POST: Cria novo pedido

### Fluxo de Pedido
1. Usuário seleciona itens do menu
2. Preenche dados do pedido
3. Escolhe tipo de pagamento
4. Submete pedido
5. Recebe confirmação

## 🚀 Próximos Passos

1. **Autenticação**
   - Login/registro de usuários
   - Proteção de rotas
   - Perfil do usuário

2. **Dashboard**
   - Status dos pedidos
   - Histórico completo
   - Favoritos

3. **Real-time**
   - WebSocket para status
   - Notificações push
   - Atualizações automáticas

4. **PWA**
   - Service Worker
   - Offline support
   - Install prompt
