# syntax=docker/dockerfile:1.6

# ---- Build stage --------------------------------------------------------
FROM node:22-bookworm-slim AS builder
WORKDIR /app

# 의존성 설치 (캐시 활용)
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund --include=dev

COPY . .

COPY .env.build .env.production

RUN npm run build

# ---- Runtime stage ------------------------------------------------------
FROM node:22-alpine
WORKDIR /app

RUN apk add --no-cache tzdata
ENV TZ=Asia/Seoul

ENV NODE_ENV=production

COPY --from=builder /app/package.json .
COPY --from=builder /app/package-lock.json .

COPY --from=builder /app/dist ./dist

COPY --from=builder /app/public ./public

RUN npm ci --omit=dev --no-audit --no-fund

# PWA 포트 3000
EXPOSE 3000
CMD ["npm", "start"]