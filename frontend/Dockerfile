# # Estágio de construção
# FROM node:18-alpine AS builder
# WORKDIR /app

# # Otimiza cache de dependências
# COPY package*.json ./
# RUN npm ci --only=production --silent

# COPY . .
# RUN npm run build

# # Estágio de produção
# FROM nginx:alpine

# # Remove arquivos desnecessários do nginx
# RUN rm -rf /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*

# # Copia arquivos estáticos
# COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# # Copia configuração customizada
# COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

# # Configura permissões
# RUN chmod -R 755 /usr/share/nginx/html

# # Health check
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#     CMD wget -qO- http://localhost:80 >/dev/null 2>&1 || exit 1

# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]

##################################################################################################

# Estágio de construção
FROM node:18-alpine AS builder
WORKDIR /app

# 1. Copia arquivos necessários para instalação
COPY package.json package-lock.json ./
COPY vite.config.js ./
COPY tsconfig*.json ./

# 2. Instala dependências
RUN npm ci --no-audit --prefer-offline

# 3. Copia o código fonte
COPY . .

# 4. Executa o build de produção
RUN npm run build

# Estágio de produção
FROM nginx:alpine

# Copia configuração principal do nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copia arquivos estáticos do build
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Configura permissões
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]