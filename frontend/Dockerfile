## PRODUÇÃO
# Estágio de construção
FROM node:18-alpine AS builder
WORKDIR /app

# 1. Copia arquivos necessários para instalação
COPY package.json package-lock.json ./
COPY vite.config.js ./
COPY tsconfig*.json ./

# 2. Instala dependências
RUN npm install --no-audit --prefer-offline --legacy-peer-deps

# 3. Copia o código fonte
COPY . .

# 4. Copia variáveis de produção
COPY env.production .env

# 5. Executa o BUILD de produção (não dev!)
RUN npm run build

# 6. Verifica se o build gerou arquivos
RUN ls -la /app/dist/ || exit 1

# Estágio de produção com Node.js
FROM node:18-alpine
WORKDIR /app

# Instala serve globalmente
RUN npm install -g serve

# Copia arquivos estáticos do build
COPY --from=builder /app/dist ./dist

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]