# CI/CD Patterns — CI/CD 패턴

GitHub Actions을 사용한 지속적 통합 및 배포 파이프라인 패턴.

## GitHub Actions 기본 구조

### 1. 테스트 자동화

```yaml
# .github/workflows/test.yml
name: Run Tests

on:
  push:
    branches: ['**']
  pull_request:
    branches: [main, develop]

jobs:
  backend-test:
    name: Backend Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd python
          pip install -r requirements.txt

      - name: Run tests
        env:
          DB_HOST: localhost
          DB_PORT: 5432
          DB_NAME: test_db
          DB_USER: postgres
          DB_PASSWORD: postgres
        run: |
          cd python
          pytest tests/ -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./python/coverage.xml

  frontend-test:
    name: Frontend Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: web/package-lock.json

      - name: Install dependencies
        run: |
          cd web
          npm ci

      - name: Run tests
        run: |
          cd web
          npm test

      - name: Build
        run: |
          cd web
          npm run build
```

### 2. 배포 자동화 (AWS ECS)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: myapp
  ECS_CLUSTER: myapp-cluster
  ECS_SERVICE_BACKEND: myapp-backend
  ECS_SERVICE_FRONTEND: myapp-frontend

jobs:
  test:
    name: Run Tests
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

  build-backend:
    name: Build Backend Image
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.build.outputs.image-tag }}
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

      - name: Build, tag, and push image
        id: build
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd python
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:backend-$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:backend-$IMAGE_TAG
          echo "image-tag=backend-$IMAGE_TAG" >> $GITHUB_OUTPUT

  build-frontend:
    name: Build Frontend Image
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.build.outputs.image-tag }}
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

      - name: Build, tag, and push image
        id: build
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd web
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:frontend-$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:frontend-$IMAGE_TAG
          echo "image-tag=frontend-$IMAGE_TAG" >> $GITHUB_OUTPUT

  deploy:
    name: Deploy to ECS
    needs: [build-backend, build-frontend]
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy Backend to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE_BACKEND }} \
            --force-new-deployment

      - name: Deploy Frontend to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE_FRONTEND }} \
            --force-new-deployment

      - name: Wait for Backend deployment
        run: |
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE_BACKEND }}

      - name: Wait for Frontend deployment
        run: |
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE_FRONTEND }}

  notify:
    name: Notify Deployment
    needs: deploy
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "Deployment ${{ job.status }}: ${{ github.event.head_commit.message }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Deployment Status*: ${{ job.status }}\n*Commit*: ${{ github.sha }}\n*Branch*: ${{ github.ref }}\n*Author*: ${{ github.actor }}"
                  }
                }
              ]
            }
```

### 3. 롤백 워크플로우

```yaml
# .github/workflows/rollback.yml
name: Rollback

on:
  workflow_dispatch:
    inputs:
      service:
        description: 'Service to rollback (backend/frontend)'
        required: true
        type: choice
        options:
          - backend
          - frontend
      image_tag:
        description: 'Image tag to rollback to'
        required: true
        type: string

env:
  AWS_REGION: us-east-1
  ECS_CLUSTER: myapp-cluster

jobs:
  rollback:
    name: Rollback Service
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Get current task definition
        id: current-task
        run: |
          TASK_DEF=$(aws ecs describe-services \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services myapp-${{ inputs.service }} \
            --query 'services[0].taskDefinition' \
            --output text)
          echo "task-def=$TASK_DEF" >> $GITHUB_OUTPUT

      - name: Rollback service
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service myapp-${{ inputs.service }} \
            --task-definition ${{ inputs.image_tag }} \
            --force-new-deployment

      - name: Wait for rollback
        run: |
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services myapp-${{ inputs.service }}

      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "Rollback ${{ job.status }}: ${{ inputs.service }} to ${{ inputs.image_tag }}"
            }
```

## 배포 전략

### 1. Blue-Green Deployment

```yaml
jobs:
  deploy-blue:
    name: Deploy to Blue Environment
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Blue
        run: |
          aws ecs update-service \
            --cluster myapp-cluster \
            --service myapp-backend-blue \
            --force-new-deployment

      - name: Wait for Blue deployment
        run: |
          aws ecs wait services-stable \
            --cluster myapp-cluster \
            --services myapp-backend-blue

      - name: Run smoke tests
        run: |
          curl -f https://blue.example.com/health || exit 1

  switch-traffic:
    name: Switch Traffic to Blue
    needs: deploy-blue
    runs-on: ubuntu-latest
    steps:
      - name: Update Load Balancer
        run: |
          # Switch traffic from Green to Blue
          aws elbv2 modify-listener \
            --listener-arn ${{ secrets.LISTENER_ARN }} \
            --default-actions Type=forward,TargetGroupArn=${{ secrets.BLUE_TG_ARN }}
```

### 2. Canary Deployment

```yaml
jobs:
  deploy-canary:
    name: Deploy Canary (10% traffic)
    runs-on: ubuntu-latest
    steps:
      - name: Deploy Canary
        run: |
          aws ecs update-service \
            --cluster myapp-cluster \
            --service myapp-backend-canary \
            --desired-count 1

      - name: Monitor metrics
        run: |
          # Wait 10 minutes and monitor error rate
          sleep 600

      - name: Check error rate
        run: |
          # Query CloudWatch metrics
          ERROR_RATE=$(aws cloudwatch get-metric-statistics \
            --namespace AWS/ECS \
            --metric-name ErrorRate \
            --dimensions Name=ServiceName,Value=myapp-backend-canary \
            --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
            --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
            --period 600 \
            --statistics Average \
            --query 'Datapoints[0].Average' \
            --output text)

          if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
            echo "Error rate too high: $ERROR_RATE"
            exit 1
          fi

  promote-canary:
    name: Promote Canary to 100%
    needs: deploy-canary
    runs-on: ubuntu-latest
    steps:
      - name: Scale up to 100%
        run: |
          aws ecs update-service \
            --cluster myapp-cluster \
            --service myapp-backend-canary \
            --desired-count 10
```

## 모니터링 통합

### CloudWatch Logs

```yaml
- name: Check CloudWatch Logs
  run: |
    aws logs tail /ecs/myapp-backend \
      --since 10m \
      --follow \
      --filter-pattern "ERROR"
```

### Sentry 통합

```yaml
- name: Create Sentry Release
  uses: getsentry/action-release@v1
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: myorg
    SENTRY_PROJECT: myapp
  with:
    environment: production
    version: ${{ github.sha }}
```

## 참조

- Docker 패턴: [docker-patterns.md](docker-patterns.md)
- Terraform 기본: [terraform-basics.md](terraform-basics.md)
