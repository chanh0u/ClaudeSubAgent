---
name: devops
description: "Docker 컨테이너화, CI/CD 파이프라인 구축, Infrastructure as Code 작성. workspace-map의 owns 경로만 수정. GitHub Actions, Terraform 사용. 배포 가이드 문서 생성."
---

# DevOps Skill

인프라 자동화와 배포 파이프라인을 구축하는 스킬. AI Agent Company 워크플로우의 Phase 4에서 devops-engineer 에이전트가 사용한다.

## 핵심 역할

1. **컨테이너화**: Dockerfile, docker-compose.yml 작성
2. **CI/CD 구축**: GitHub Actions 워크플로우 작성
3. **Infrastructure as Code**: Terraform으로 인프라 정의
4. **모니터링 설정**: CloudWatch, Prometheus 설정
5. **파일 소유권 준수**: workspace-map의 owns 경로만 수정

## 기술 스택

- **컨테이너**: Docker, docker-compose
- **CI/CD**: GitHub Actions
- **IaC**: Terraform
- **클라우드**: AWS (EC2, ECS, RDS, CloudWatch)
- **모니터링**: CloudWatch, Prometheus + Grafana

## 작업 원칙

### 원칙 1: workspace-map 준수

**필수**: `_workspace/02_workspace-map.json` 읽기

```dockerfile
# owns 경로만 수정
# 예: ["Dockerfile", "docker-compose.yml", ".github/workflows/**", "infra/**"]

# forbidden 경로는 절대 수정 금지
# 예: ["src/api/**", "src/components/**"]
```

### 원칙 2: 멀티 스테이지 빌드

이미지 크기 최소화:

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER nodejs
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### 원칙 3: Infrastructure as Code

모든 인프라를 코드로 관리:

```hcl
# infra/main.tf
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}
```

### 원칙 4: 시크릿 관리

하드코딩 금지, 환경 변수 사용:

```yaml
# GitHub Actions
env:
  DB_HOST: ${{ secrets.DB_HOST }}
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

## 출력 구조

```
workspace/{project_id}/
├── Dockerfile                      # Backend 컨테이너
├── docker-compose.yml              # 로컬 개발 환경
├── .github/
│   └── workflows/
│       ├── test.yml                # 테스트 자동화
│       └── deploy.yml              # 배포 자동화
├── infra/
│   ├── main.tf                     # Terraform 메인
│   ├── variables.tf                # 변수 정의
│   └── outputs.tf                  # 출력값
└── docs/
    └── deployment.md               # 배포 가이드
```

## 컨테이너화 패턴

### 패턴 1: Backend Dockerfile (Python)

```dockerfile
# Multi-stage build for FastAPI
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

# Copy from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/src ./src

# Create non-root user
RUN useradd -m -u 1001 appuser
USER appuser

EXPOSE 3003

CMD ["python", "-m", "src.main"]
```

### 패턴 2: Frontend Dockerfile (React + Vite)

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

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 패턴 3: docker-compose.yml

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
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    volumes:
      - ./python/src:/app/src

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

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

> 상세: [references/docker-patterns.md](references/docker-patterns.md)

## CI/CD 파이프라인

### GitHub Actions 워크플로우

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: myapp

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Backend Tests
        run: |
          cd python
          pip install -r requirements.txt
          pytest tests/

      - name: Run Frontend Tests
        run: |
          cd web
          npm ci
          npm test

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push Backend image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:backend-$IMAGE_TAG ./python
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:backend-$IMAGE_TAG

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster myapp-cluster \
            --service myapp-backend \
            --force-new-deployment
```

> 상세: [references/cicd-patterns.md](references/cicd-patterns.md)

## Infrastructure as Code

### Terraform 기본 구조

```hcl
# infra/main.tf
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  enable_dns_hostnames = true
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier        = "${var.project_name}-db"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t3.small"
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  backup_retention_period = 7
  multi_az                = true
}
```

> 상세: [references/terraform-basics.md](references/terraform-basics.md)

## 협업 프로토콜 (Phase 4)

### backend/frontend-dev와 협업

**Dockerfile 최적화**:

```
[devops → backend-dev]
"Dockerfile을 작성했습니다.
빌드 명령어: docker build -t myapp-backend ./python
실행: docker run -p 3003:3003 myapp-backend"

[backend-dev → devops]
"확인했습니다. 환경 변수 DB_HOST, DB_PASSWORD 필요합니다."

[devops → backend-dev]
"docker-compose.yml에 환경 변수 추가 완료."
```

### tech-lead와 협업

**배포 완료 보고**:

```
[devops → tech-lead]
"CI/CD 파이프라인 구축 완료.
- GitHub Actions: .github/workflows/deploy.yml
- Dockerfile: python/Dockerfile, web/Dockerfile
- docker-compose.yml: 로컬 개발 환경
- infra/: Terraform 코드
deployment.md 확인하세요."
```

## 절대 금지

- ❌ forbidden 경로 수정 금지 (src/api/**, src/components/**)
- ❌ 시크릿 하드코딩 금지
- ❌ 프로덕션 환경에서 직접 수정 금지
- ❌ 백업 없이 인프라 변경 금지

## 핵심 규칙

**Rule 1**: 모든 인프라를 코드로 관리 (IaC)

**Rule 2**: 시크릿은 환경 변수 또는 시크릿 관리 서비스 사용

**Rule 3**: workspace-map의 `owns` 경로만 수정

**Rule 4**: 멀티 스테이지 빌드로 이미지 최적화

**Rule 5**: 작업 완료 시 deployment.md 작성 및 리더에게 보고

## 검증

구현 완료 후 확인:

- [ ] Dockerfile (Backend, Frontend) 존재
- [ ] docker-compose.yml 존재
- [ ] .github/workflows/*.yml 존재
- [ ] infra/*.tf 존재
- [ ] deployment.md 존재
- [ ] workspace-map의 `owns` 경로만 수정
- [ ] `forbidden` 경로 미수정

## 참조

- Docker 패턴: [references/docker-patterns.md](references/docker-patterns.md)
- CI/CD 패턴: [references/cicd-patterns.md](references/cicd-patterns.md)
- Terraform 기본: [references/terraform-basics.md](references/terraform-basics.md)
