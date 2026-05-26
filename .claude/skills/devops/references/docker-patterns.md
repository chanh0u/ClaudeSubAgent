# Docker Patterns — Docker 패턴

컨테이너화를 위한 Dockerfile 및 docker-compose 패턴.

## Dockerfile 패턴

### 1. Python (FastAPI) Dockerfile

```dockerfile
# Multi-stage build for production
FROM python:3.10-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Production stage
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/src ./src

# Create non-root user
RUN useradd -m -u 1001 appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:3003/health')"

EXPOSE 3003

CMD ["python", "-m", "src.main"]
```

### 2. Node.js (Backend) Dockerfile

```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3000

CMD ["node", "dist/server.js"]
```

### 3. React + Vite Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. nginx.conf (React용)

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # React Router 지원 (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Gzip 압축
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # 캐싱 설정
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## docker-compose 패턴

### 1. 전체 스택 (Backend + Frontend + DB)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./python
      dockerfile: Dockerfile
    ports:
      - "3003:3003"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=myapp
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./python/src:/app/src
    networks:
      - app-network

  frontend:
    build:
      context: ./web
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:3003
    volumes:
      - ./web/src:/app/src
      - /app/node_modules
    networks:
      - app-network

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### 2. 개발 환경 vs 프로덕션 환경

**docker-compose.dev.yml** (개발):

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./python
      dockerfile: Dockerfile.dev
    volumes:
      - ./python/src:/app/src  # Hot reload
    environment:
      - DEBUG=True
      - LOG_LEVEL=DEBUG

  frontend:
    build:
      context: ./web
      dockerfile: Dockerfile.dev
    volumes:
      - ./web/src:/app/src  # Hot reload
      - /app/node_modules
```

**docker-compose.prod.yml** (프로덕션):

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./python
      dockerfile: Dockerfile
    restart: always
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO

  frontend:
    build:
      context: ./web
      dockerfile: Dockerfile
    restart: always
```

## 이미지 최적화

### 1. .dockerignore

```
# 빌드에서 제외할 파일
node_modules
npm-debug.log
.git
.gitignore
*.md
.env
.env.local
dist
build
coverage
.vscode
.idea
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
```

### 2. 레이어 캐싱 최적화

```dockerfile
# ❌ 나쁜 예: 모든 파일 복사 후 npm install
COPY . .
RUN npm install

# ✅ 좋은 예: package.json만 먼저 복사
COPY package*.json ./
RUN npm ci
COPY . .
```

### 3. 멀티 스테이지 빌드

```dockerfile
# Build stage (크기 큼)
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage (크기 작음)
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

## 보안 Best Practices

### 1. Non-root 사용자

```dockerfile
# Python
RUN useradd -m -u 1001 appuser
USER appuser

# Node.js
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs
```

### 2. 최소 권한 이미지 사용

```dockerfile
# ❌ 나쁜 예: Full OS
FROM ubuntu:latest

# ✅ 좋은 예: Alpine
FROM node:20-alpine
FROM python:3.10-slim
```

### 3. Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3003/health || exit 1
```

## 참조

- CI/CD 패턴: [cicd-patterns.md](cicd-patterns.md)
- Terraform 기본: [terraform-basics.md](terraform-basics.md)
