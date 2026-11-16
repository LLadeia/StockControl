# syntax=docker/dockerfile:1

# ─── Build: gera os arquivos estáticos com o Vite ──────────────────────────
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Endereço da API embutido no bundle. O padrão é relativo porque o nginx
# abaixo entrega o front-end e encaminha /api/ para o Django na mesma origem.
ARG VITE_API_URL=/api/
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ─── Servidor: nginx entrega o front-end e faz o proxy para a API ──────────
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
