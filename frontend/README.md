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
- **Serve** - Servidor estático Node.js

## 🏗️ Arquitetura

```
frontend/
├── src/
│   ├── components/     # Componentes React
│   ├── services/       # APIs e tipos
│   ├── lib/           # Utilitários
│   └── main.tsx       # Entry point
├── public/            # Assets estáticos
├── .env.development   # Variáveis de desenvolvimento
├── .env.production    # Variáveis de produção
└── Dockerfile         # Build multi-stage com Node.js
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
docker run -p 3000:3000 toprestaurant-frontend
```

## 🔧 Configuração

### Variáveis de Ambiente

#### Desenvolvimento (`.env.development`)
```env
VITE_API_BASE_ORDERS=http://localhost:5001
VITE_API_BASE_MENU=http://localhost:5003
```

#### Produção (`.env.production`)
```env
VITE_API_BASE_ORDERS=https://order-service-production.up.railway.app
VITE_API_BASE_MENU=https://menu-service-production.up.railway.app
```

### Proxy de Desenvolvimento
O Vite está configurado para fazer proxy das APIs em desenvolvimento:
- `/orders/*` → `order-service:5001`
- `/menu/*` → `menu-service:5003`

## � Build e Deploy

### Processo de Build Local
1. **Stage 1**: Build com Node.js
   - Instala dependências
   - Executa `npm run build`
   - Gera pasta `dist/`

2. **Stage 2**: Serve com Node.js
   - Copia arquivos do `dist/`
   - Usa `serve` para servir arquivos estáticos
   - Expõe na porta 3000

### Deploy Automatizado (Railway)

O frontend é automaticamente deployado via GitHub Actions:

```yaml
# .github/workflows/deploy-to-railway.yml
deploy-frontend:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Deploy Frontend
      run: railway up --service frontend --detach
```

**URLs:**
- **Desenvolvimento:** http://localhost:3000
- **Produção:** https://frontend-production.up.railway.app

### Servidor Node.js (serve)
```bash
# Comando de produção
serve -s dist -l 3000

# Flags importantes:
# -s: SPA mode (fallback para index.html)
# -l: Listen port
```

## 🔗 Integrações

### APIs Consumidas

#### Desenvolvimento
- **Menu Service:** http://localhost:5003/api/v1/menu
- **Order Service:** http://localhost:5001/api/v1/orders

#### Produção
- **Menu Service:** https://menu-service-production.up.railway.app/api/v1/menu
- **Order Service:** https://order-service-production.up.railway.app/api/v1/orders

### Fluxo de Pedido
1. Usuário seleciona itens do menu
2. Preenche dados do pedido
3. Escolhe tipo de pagamento
4. Submete pedido
5. Recebe confirmação

## 🧪 Scripts Disponíveis

```bash
npm run dev          # Servidor de desenvolvimento
npm run build        # Build para produção
npm run preview      # Preview do build
npm run lint         # Linting com ESLint
npm run start        # Servidor de produção
npm run serve        # Alias para start
```

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
