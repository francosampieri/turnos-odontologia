# syntax=docker/dockerfile:1
FROM node:22-alpine AS builder

WORKDIR /app

ARG VITE_API_URL=http://localhost:8000/api/v1
ARG VITE_API_BASE=/api/v1
ENV VITE_API_URL=
ENV VITE_API_BASE=

COPY package*.json ./

RUN npm ci --legacy-peer-deps

COPY . .

RUN npm run build

FROM nginx:alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
