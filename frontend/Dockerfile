# Estágio de construção
FROM node:18-alpine AS builder
WORKDIR /app
# Suprime notificações do npm
ENV NPM_CONFIG_UPDATE_NOTIFIER=false
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Estágio de produção
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=builder /app/dist .
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -rf /etc/nginx/conf.d/default.conf.default
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]