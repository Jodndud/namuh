# syntax=docker/dockerfile:1.6

# ---- Build stage --------------------------------------------------------
FROM node:22-bookworm-slim AS builder
WORKDIR /app

# 의존성 설치 (캐시 최대화)
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund --include=dev

# 소스 복사 & 빌드
COPY . .

COPY .env.build .env.production

RUN npm run build
 
# ---- Runtime stage ------------------------------------------------------
FROM node:22-alpine
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/package.json .
COPY --from=builder /app/package-lock.json .

COPY --from=builder /app/dist ./dist

COPY --from=builder /app/public ./public

RUN npm ci --omit=dev --no-audit --no-fund

# 웹 대시보드 포트 3001
EXPOSE 3001
CMD ["npm", "start"]
