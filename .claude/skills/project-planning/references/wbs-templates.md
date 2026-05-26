# WBS Templates — 도메인별 WBS 템플릿

도메인별로 자주 사용되는 WBS(Work Breakdown Structure) 템플릿.

---

## 목차

1. [웹 애플리케이션 (CRUD)](#1-웹-애플리케이션-crud)
2. [REST API 서비스](#2-rest-api-서비스)
3. [실시간 채팅 애플리케이션](#3-실시간-채팅-애플리케이션)
4. [이커머스](#4-이커머스)
5. [데이터 대시보드](#5-데이터-대시보드)

---

## 1. 웹 애플리케이션 (CRUD)

기본적인 CRUD (Create, Read, Update, Delete) 웹 애플리케이션.

### 기술 스택
- Backend: FastAPI
- Frontend: React
- Database: PostgreSQL

### WBS

```yaml
project_id: "webapp-crud-template"
project_name: "CRUD 웹 애플리케이션"

pipeline:
  stages:
    - stage: 1
      name: "분석·설계"
      sequential: true
      tasks:
        - id: T-001
          name: "요구사항 정제 및 API 명세 작성"
          agent: system-analyst
          output_files:
            - "docs/requirements.md"
            - "docs/api-spec.md"
          est_hours: 2
          acceptance_criteria:
            - "모든 CRUD 엔드포인트 정의 완료"
            - "요청/응답 스키마 정의"

        - id: T-002
          name: "아키텍처 설계"
          agent: architect
          depends_on: [T-001]
          output_files:
            - "docs/architecture.md"
          est_hours: 2
          acceptance_criteria:
            - "3-tier 아키텍처 정의"
            - "데이터 흐름도 작성"

    - stage: 2
      name: "병렬 개발"
      sequential: false
      tasks:
        - id: T-003
          name: "백엔드 API 구현"
          agent: backend-developer
          depends_on: [T-002]
          parallel_with: [T-004, T-005]
          output_files:
            - "src/main.py"
            - "src/api/**"
            - "src/service/**"
          est_hours: 8
          acceptance_criteria:
            - "CRUD API 엔드포인트 구현"
            - "비즈니스 로직 분리"

        - id: T-004
          name: "프론트엔드 UI 구현"
          agent: frontend-developer
          depends_on: [T-002]
          parallel_with: [T-003, T-005]
          output_files:
            - "src/App.jsx"
            - "src/components/**"
            - "src/pages/**"
          est_hours: 8
          acceptance_criteria:
            - "리스트/상세/생성/수정/삭제 화면"
            - "API 연동"

        - id: T-005
          name: "DB 스키마 설계"
          agent: database-engineer
          depends_on: [T-002]
          parallel_with: [T-003, T-004]
          output_files:
            - "migrations/**"
            - "src/db/**"
          est_hours: 3
          acceptance_criteria:
            - "테이블 정의"
            - "인덱스 설정"

    - stage: 3
      name: "인프라·보안·QA"
      sequential: false
      tasks:
        - id: T-006
          name: "Docker 및 CI/CD"
          agent: devops-engineer
          depends_on: [T-003, T-004, T-005]
          output_files:
            - "Dockerfile"
            - "docker-compose.yml"
            - ".github/workflows/**"
          est_hours: 3

        - id: T-007
          name: "OWASP 보안 감사"
          agent: security-engineer
          depends_on: [T-003, T-004]
          output_files:
            - "docs/security-report.md"
          est_hours: 2

        - id: T-008
          name: "테스트 코드"
          agent: tester
          depends_on: [T-003, T-004]
          output_files:
            - "tests/**"
          est_hours: 4
```

---

## 2. REST API 서비스

프론트엔드 없이 백엔드 API만 제공하는 서비스.

### 기술 스택
- Backend: FastAPI
- Database: PostgreSQL
- API Documentation: Swagger/OpenAPI

### WBS

```yaml
project_id: "rest-api-template"
project_name: "REST API 서비스"

pipeline:
  stages:
    - stage: 1
      name: "API 설계"
      sequential: true
      tasks:
        - id: T-001
          name: "API 명세 작성 (OpenAPI)"
          agent: system-analyst
          output_files:
            - "docs/openapi.yaml"
          est_hours: 3

        - id: T-002
          name: "데이터 모델 설계"
          agent: architect
          depends_on: [T-001]
          output_files:
            - "docs/data-model.md"
          est_hours: 2

    - stage: 2
      name: "구현"
      sequential: false
      tasks:
        - id: T-003
          name: "API 엔드포인트 구현"
          agent: backend-developer
          depends_on: [T-002]
          parallel_with: [T-004]
          output_files:
            - "src/api/**"
            - "src/service/**"
          est_hours: 10

        - id: T-004
          name: "DB 스키마 및 마이그레이션"
          agent: database-engineer
          depends_on: [T-002]
          parallel_with: [T-003]
          output_files:
            - "migrations/**"
          est_hours: 4

    - stage: 3
      name: "검증 및 배포"
      sequential: true
      tasks:
        - id: T-005
          name: "API 테스트 (pytest)"
          agent: tester
          depends_on: [T-003, T-004]
          output_files:
            - "tests/test_api.py"
          est_hours: 5

        - id: T-006
          name: "보안 감사 (OWASP)"
          agent: security-engineer
          depends_on: [T-003]
          output_files:
            - "docs/security-report.md"
          est_hours: 2

        - id: T-007
          name: "Docker 컨테이너화"
          agent: devops-engineer
          depends_on: [T-005, T-006]
          output_files:
            - "Dockerfile"
            - "docker-compose.yml"
          est_hours: 2
```

---

## 3. 실시간 채팅 애플리케이션

WebSocket 기반 실시간 통신.

### 기술 스택
- Backend: FastAPI + WebSocket
- Frontend: React + WebSocket
- Database: PostgreSQL + Redis (메시지 큐)

### WBS

```yaml
project_id: "realtime-chat-template"
project_name: "실시간 채팅 애플리케이션"

pipeline:
  stages:
    - stage: 1
      name: "설계"
      sequential: true
      tasks:
        - id: T-001
          name: "실시간 통신 아키텍처 설계"
          agent: architect
          output_files:
            - "docs/architecture.md"
          est_hours: 3
          acceptance_criteria:
            - "WebSocket 통신 흐름 정의"
            - "메시지 큐 구조 설계"

    - stage: 2
      name: "개발"
      sequential: false
      tasks:
        - id: T-002
          name: "WebSocket 서버 구현"
          agent: backend-developer
          depends_on: [T-001]
          parallel_with: [T-004]
          output_files:
            - "src/websocket/**"
            - "src/api/chat.py"
          est_hours: 8

        - id: T-003
          name: "채팅 UI 구현"
          agent: frontend-developer
          depends_on: [T-002]  # WebSocket 엔드포인트 필요
          output_files:
            - "src/components/Chat.jsx"
            - "src/hooks/useWebSocket.js"
          est_hours: 6

        - id: T-004
          name: "메시지 DB + Redis 설정"
          agent: database-engineer
          depends_on: [T-001]
          parallel_with: [T-002]
          output_files:
            - "migrations/001_messages.sql"
            - "redis.conf"
          est_hours: 3

    - stage: 3
      name: "최적화 및 배포"
      sequential: true
      tasks:
        - id: T-005
          name: "실시간 통신 테스트"
          agent: tester
          depends_on: [T-002, T-003, T-004]
          output_files:
            - "tests/test_websocket.py"
          est_hours: 4

        - id: T-006
          name: "Docker + Redis 오케스트레이션"
          agent: devops-engineer
          depends_on: [T-005]
          output_files:
            - "docker-compose.yml"
          est_hours: 3
```

---

## 4. 이커머스

상품, 장바구니, 결제 기능 포함.

### 기술 스택
- Backend: FastAPI
- Frontend: React
- Database: PostgreSQL
- Payment: Stripe API

### WBS

```yaml
project_id: "ecommerce-template"
project_name: "이커머스 플랫폼"

pipeline:
  stages:
    - stage: 1
      name: "요구사항 분석"
      sequential: true
      tasks:
        - id: T-001
          name: "비즈니스 요구사항 정의"
          agent: system-analyst
          output_files:
            - "docs/requirements.md"
          est_hours: 4
          acceptance_criteria:
            - "상품 카탈로그 요구사항"
            - "장바구니 로직 정의"
            - "결제 플로우 정의"

    - stage: 2
      name: "핵심 기능 개발"
      sequential: false
      tasks:
        - id: T-002
          name: "상품 관리 API"
          agent: backend-developer
          depends_on: [T-001]
          parallel_with: [T-003, T-005]
          output_files:
            - "src/api/products.py"
          est_hours: 6

        - id: T-003
          name: "장바구니 API"
          agent: backend-developer
          depends_on: [T-001]
          parallel_with: [T-002, T-005]
          output_files:
            - "src/api/cart.py"
          est_hours: 4

        - id: T-004
          name: "결제 API (Stripe 연동)"
          agent: backend-developer
          depends_on: [T-003]  # 장바구니 의존
          output_files:
            - "src/api/payment.py"
          est_hours: 6

        - id: T-005
          name: "DB 스키마 (상품, 주문, 결제)"
          agent: database-engineer
          depends_on: [T-001]
          parallel_with: [T-002, T-003]
          output_files:
            - "migrations/**"
          est_hours: 5

        - id: T-006
          name: "상품 카탈로그 UI"
          agent: frontend-developer
          depends_on: [T-002]
          output_files:
            - "src/pages/ProductList.jsx"
            - "src/components/ProductCard.jsx"
          est_hours: 5

        - id: T-007
          name: "장바구니 UI"
          agent: frontend-developer
          depends_on: [T-003]
          output_files:
            - "src/pages/Cart.jsx"
          est_hours: 4

        - id: T-008
          name: "결제 UI"
          agent: frontend-developer
          depends_on: [T-004]
          output_files:
            - "src/pages/Checkout.jsx"
          est_hours: 5

    - stage: 3
      name: "보안 및 배포"
      sequential: false
      tasks:
        - id: T-009
          name: "결제 보안 감사 (PCI DSS)"
          agent: security-engineer
          depends_on: [T-004]
          output_files:
            - "docs/security-report.md"
          est_hours: 4

        - id: T-010
          name: "통합 테스트"
          agent: tester
          depends_on: [T-002, T-003, T-004, T-006, T-007, T-008]
          output_files:
            - "tests/test_ecommerce_flow.py"
          est_hours: 6

        - id: T-011
          name: "Docker 및 CI/CD"
          agent: devops-engineer
          depends_on: [T-009, T-010]
          output_files:
            - "Dockerfile"
            - "docker-compose.yml"
          est_hours: 3
```

---

## 5. 데이터 대시보드

데이터 시각화 및 리포팅.

### 기술 스택
- Backend: FastAPI
- Frontend: React + Chart.js
- Database: PostgreSQL + BigQuery

### WBS

```yaml
project_id: "dashboard-template"
project_name: "데이터 대시보드"

pipeline:
  stages:
    - stage: 1
      name: "데이터 분석 및 설계"
      sequential: true
      tasks:
        - id: T-001
          name: "데이터 소스 분석"
          agent: system-analyst
          output_files:
            - "docs/data-sources.md"
          est_hours: 3

        - id: T-002
          name: "대시보드 와이어프레임"
          agent: architect
          depends_on: [T-001]
          output_files:
            - "docs/wireframe.md"
          est_hours: 2

    - stage: 2
      name: "데이터 파이프라인 구축"
      sequential: false
      tasks:
        - id: T-003
          name: "데이터 집계 API"
          agent: backend-developer
          depends_on: [T-002]
          parallel_with: [T-004]
          output_files:
            - "src/api/analytics.py"
          est_hours: 8

        - id: T-004
          name: "데이터 웨어하우스 스키마"
          agent: database-engineer
          depends_on: [T-002]
          parallel_with: [T-003]
          output_files:
            - "bigquery/schema.sql"
          est_hours: 5

    - stage: 3
      name: "시각화 구현"
      sequential: true
      tasks:
        - id: T-005
          name: "차트 컴포넌트 구현"
          agent: frontend-developer
          depends_on: [T-003]
          output_files:
            - "src/components/Chart/**"
            - "src/pages/Dashboard.jsx"
          est_hours: 10

        - id: T-006
          name: "대시보드 성능 테스트"
          agent: tester
          depends_on: [T-005]
          output_files:
            - "tests/test_performance.py"
          est_hours: 3

        - id: T-007
          name: "Docker 배포"
          agent: devops-engineer
          depends_on: [T-006]
          output_files:
            - "Dockerfile"
          est_hours: 2
```

---

## 템플릿 사용 가이드

### 1. 템플릿 선택

parsed-spec.json의 `project_type` 또는 `features`를 보고 가장 유사한 템플릿 선택:

```python
if "CRUD" in features or "게시판" in features:
    template = "웹 애플리케이션 (CRUD)"
elif "API" in project_type:
    template = "REST API 서비스"
elif "실시간" in features or "채팅" in features:
    template = "실시간 채팅"
elif "결제" in features or "상품" in features:
    template = "이커머스"
elif "대시보드" in features or "분석" in features:
    template = "데이터 대시보드"
else:
    template = "웹 애플리케이션 (CRUD)"  # 기본값
```

### 2. 템플릿 커스터마이징

선택한 템플릿을 parsed-spec에 맞게 수정:

1. **project_id, project_name 변경**
2. **task name 구체화**: "백엔드 API" → "할 일 관리 API"
3. **output_files 구체화**: "src/api/**" → "src/api/todos.py"
4. **불필요한 task 제거**: 실시간 통신 불필요하면 WebSocket 관련 제거
5. **필수 task 추가**: 금융 도메인이면 보안 감사 강화

### 3. 검증

- [ ] 모든 task에 agent 할당
- [ ] stage별 sequential 설정 확인
- [ ] depends_on 의존성 타당성
- [ ] parallel_with 충돌 없음
- [ ] output_files와 workspace-map 일치

---

## 참고

- Agent 매칭 규칙: [agent-matching-rules.md](agent-matching-rules.md)
