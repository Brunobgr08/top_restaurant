# Estágio de construção
FROM node:18-alpine AS builder
WORKDIR /app

# Otimiza cache de dependências
COPY package*.json ./
RUN npm ci --only=production --silent

COPY . .
RUN npm run build

# Estágio de produção
FROM nginx:alpine

# Remove arquivos desnecessários do nginx
RUN rm -rf /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*

# Copia arquivos estáticos
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Copia configuração customizada
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

# Configura permissões
RUN chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80 >/dev/null 2>&1 || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]