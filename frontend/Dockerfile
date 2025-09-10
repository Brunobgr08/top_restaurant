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

# Estágio de construção - Instala dependências de BUILD
FROM node:18-alpine AS builder
WORKDIR /app

# 1. Copia apenas os arquivos necessários para instalação de dependências
COPY package*..json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./

# 2. Instala APENAS as dependências necessárias para build (não todas as devDependencies)
RUN npm ci --silent --include=dev

# 3. Copia o código fonte
COPY . .

# 4. Executa o build de produção
RUN npm run build

# Estágio de produção - Serve os arquivos estáticos
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Remove configuração padrão do nginx
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copia arquivos estáticos do build
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Copia configuração customizada do nginx
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

# Configura permissões
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx /var/run

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80 >/dev/null 2>&1 || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]