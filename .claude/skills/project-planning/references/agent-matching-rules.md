# Agent Matching Rules — Agent 매칭 규칙

태스크 유형에 따라 적합한 Agent를 배정하는 상세 규칙.

---

## 목차

1. [기본 매칭 규칙](#1-기본-매칭-규칙)
2. [기술 스택 기반 매칭](#2-기술-스택-기반-매칭)
3. [도메인 전문성 매칭](#3-도메인-전문성-매칭)
4. [태스크 분해 규칙](#4-태스크-분해-규칙)
5. [Edge Cases](#5-edge-cases)

---

## 1. 기본 매칭 규칙

### 백엔드 작업

| 태스크 유형 | Agent | 모델 | 근거 |
|------------|-------|------|------|
| REST API 구현 | backend-developer | Sonnet | API 엔드포인트 개발 |
| 비즈니스 로직 | backend-developer | Sonnet | 서비스 레이어 구현 |
| 인증/인가 | backend-developer | Sonnet | JWT, OAuth 등 |
| 파일 업로드/다운로드 | backend-developer | Sonnet | 멀티파트, 스트리밍 |
| 웹소켓/실시간 통신 | backend-developer | Sonnet | WebSocket, SSE |

**산출물 경로**: `src/api/**`, `src/service/**`, `src/domain/**`

### 프론트엔드 작업

| 태스크 유형 | Agent | 모델 | 근거 |
|------------|-------|------|------|
| UI 컴포넌트 | frontend-developer | Sonnet | React 컴포넌트 |
| 페이지/라우팅 | frontend-developer | Sonnet | React Router |
| 상태 관리 | frontend-developer | Sonnet | Redux, Context API |
| API 호출 | frontend-developer | Sonnet | fetch, axios |
| 폼/밸리데이션 | frontend-developer | Sonnet | React Hook Form |

**산출물 경로**: `src/components/**`, `src/pages/**`, `src/hooks/**`

### 데이터베이스 작업

| 태스크 유형 | Agent | 모델 | 근거 |
|------------|-------|------|------|
| DB 스키마 설계 | database-engineer | Sonnet | ERD, 정규화 |
| 마이그레이션 스크립트 | database-engineer | Sonnet | Alembic, Flyway |
| 인덱스 최적화 | database-engineer | Sonnet | 성능 튜닝 |
| 프로시저/트리거 | database-engineer | Sonnet | 복잡한 비즈니스 로직 |

**산출물 경로**: `migrations/**`, `src/db/**`

### 인프라 작업

| 태스크 유형 | Agent | 모델 | 근거 |
|------------|-------|------|------|
| Docker 설정 | devops-engineer | Sonnet | Dockerfile, docker-compose |
| CI/CD 파이프라인 | devops-engineer | Sonnet | GitHub Actions, Jenkins |
| 환경 설정 | devops-engineer | Sonnet | .env, secrets |
| 모니터링/로깅 | devops-engineer | Sonnet | Prometheus, ELK |

**산출물 경로**: `Dockerfile`, `docker-compose.yml`, `.github/**`

### 보안 작업

| 태스크 유형 | Agent | 모델 | 근거 |
|------------|-------|------|------|
| OWASP Top 10 체크 | security-engineer | Opus | 보안 전문성 필요 |
| 침투 테스트 | security-engineer | Opus | 취약점 탐지 |
| 보안 감사 | security-engineer | Opus | 코드 리뷰 |

**산출물 경로**: `docs/security-report.md`

**중요**: security-engineer는 읽기 전용. 코드 수정 금지.

### QA 작업

| 태스크 유형 | Agent | 모델 | 근거 |
|------------|-------|------|------|
| 단위 테스트 | tester | Haiku | pytest, Jest |
| 통합 테스트 | tester | Haiku | API 테스트 |
| E2E 테스트 | tester | Haiku | Selenium, Playwright |
| 경계면 교차 비교 | tester | Haiku | API ↔ 프론트 검증 |

**산출물 경로**: `tests/**`, `pytest.ini`, `jest.config.ts`

### 분석·설계 작업

| 태스크 유형 | Agent | 모델 | 근거 |
|------------|-------|------|------|
| 요건 분석 | system-analyst | Sonnet | 요구사항 정제 |
| API 명세 작성 | system-analyst | Sonnet | OpenAPI, Swagger |
| 아키텍처 설계 | architect | Opus | 시스템 구조 |
| 기술 스택 선정 | architect | Opus | 기술 의사결정 |

**산출물 경로**: `docs/requirements.md`, `docs/api-spec.md`, `docs/architecture.md`

---

## 2. 기술 스택 기반 매칭

parsed-spec.json의 `tech_stack`을 확인하여 Agent 선택.

### 백엔드 프레임워크

| tech_stack.backend | Agent | 추가 고려사항 |
|-------------------|-------|--------------|
| "FastAPI" | backend-developer | Python 3.10+, 비동기 패턴 |
| "Django" | backend-developer | MTV 패턴, ORM |
| "Express" | backend-developer | Node.js, middleware |
| "Spring Boot" | backend-developer | Java, DI |

### 프론트엔드 프레임워크

| tech_stack.frontend | Agent | 추가 고려사항 |
|--------------------|-------|--------------|
| "React" | frontend-developer | JSX, hooks |
| "Vue" | frontend-developer | SFC, Composition API |
| "Angular" | frontend-developer | TypeScript, RxJS |
| "Svelte" | frontend-developer | 컴파일러 기반 |

### 데이터베이스

| tech_stack.database | Agent | 추가 고려사항 |
|--------------------|-------|--------------|
| "PostgreSQL" | database-engineer | RDBMS, ACID |
| "MongoDB" | database-engineer | NoSQL, 문서 DB |
| "Redis" | database-engineer | 인메모리, 캐시 |
| "Elasticsearch" | database-engineer | 검색 엔진 |

---

## 3. 도메인 전문성 매칭

parsed-spec.json의 `domain` 또는 `features`를 보고 도메인 전문 Agent 선택.

### 금융(Fintech)

보안이 중요하므로 security-engineer를 필수 포함:

```yaml
tasks:
  - name: "결제 API 구현"
    agent: backend-developer
  - name: "보안 감사 (금융 규정 준수)"
    agent: security-engineer  # 필수
```

### 헬스케어

개인정보 보호가 중요:

```yaml
tasks:
  - name: "환자 정보 암호화"
    agent: security-engineer  # 필수
  - name: "HIPAA 준수 체크"
    agent: security-engineer
```

### 이커머스

결제 + 인벤토리 관리:

```yaml
tasks:
  - name: "장바구니 API"
    agent: backend-developer
  - name: "재고 관리 DB"
    agent: database-engineer
  - name: "결제 보안 감사"
    agent: security-engineer
```

---

## 4. 태스크 분해 규칙

### 규칙 1: 기능 → 태스크 매핑

하나의 기능(Feature)을 여러 태스크로 분해:

```
기능: "사용자 인증"

태스크 분해:
1. API 명세 작성 (system-analyst)
   - 엔드포인트: POST /auth/login, POST /auth/register
   - 요청/응답 형식 정의

2. 인증 API 구현 (backend-developer)
   - JWT 토큰 발급
   - 비밀번호 해싱 (bcrypt)
   - src/api/auth.py

3. 로그인 UI 구현 (frontend-developer)
   - 로그인 폼 컴포넌트
   - 토큰 저장 (localStorage)
   - src/components/Login.jsx

4. users 테이블 설계 (database-engineer)
   - 컬럼: id, email, password_hash, created_at
   - migrations/001_create_users.sql

5. 인증 API 테스트 (tester)
   - 로그인 성공/실패 케이스
   - tests/test_auth.py
```

### 규칙 2: 1 태스크 = 1 Agent

태스크는 단일 Agent에게만 할당. 여러 Agent가 필요하면 태스크를 분할:

**나쁜 예**:
```yaml
- name: "사용자 관리 전체"
  agent: backend-developer + frontend-developer  # 불가능
```

**좋은 예**:
```yaml
- name: "사용자 관리 API"
  agent: backend-developer

- name: "사용자 관리 UI"
  agent: frontend-developer
```

### 규칙 3: 산출물 기반 분해

태스크는 명확한 산출물을 가져야 함:

```yaml
- name: "할 일 API 구현"
  agent: backend-developer
  output_files:
    - "src/api/todos.py"
    - "src/service/todo_service.py"
```

산출물이 불명확하면 태스크가 너무 추상적. 더 구체적으로 분해.

### 규칙 4: 크기 제한

태스크는 4-8시간 내 완료 가능해야 함:

- **너무 큼**: "백엔드 전체" (X) → "할 일 API", "사용자 API"로 분해
- **너무 작음**: "변수명 변경" (X) → 다른 태스크에 통합
- **적정**: "할 일 CRUD API 구현" (O)

---

## 5. Edge Cases

### Case 1: 풀스택 기능

백엔드와 프론트가 밀접한 기능:

```yaml
- id: T-001
  name: "실시간 채팅 API (WebSocket)"
  agent: backend-developer
  output_files: ["src/api/chat.py"]

- id: T-002
  name: "실시간 채팅 UI (WebSocket 클라이언트)"
  agent: frontend-developer
  depends_on: [T-001]  # 백엔드 먼저
  output_files: ["src/components/Chat.jsx"]
```

**의존성 설정**: 프론트가 백엔드의 WebSocket 엔드포인트에 의존하므로 `depends_on`

### Case 2: 여러 Agent가 같은 파일 수정

예: `src/main.py`를 backend와 devops가 모두 수정해야 함

**해결**:
1. workspace-map의 `tech_lead_merge_targets`에 추가
2. Phase 3에서는 각자 수정
3. Phase 4 tech-lead가 병합

```json
"tech_lead_merge_targets": [
  "src/main.py",
  "src/App.tsx"
]
```

### Case 3: 기술 스택 미정

parsed-spec에 tech_stack이 없거나 "미정"인 경우:

**해결**:
1. architect에게 "기술 스택 선정" 태스크 할당
2. architect 완료 후 나머지 태스크 분해

```yaml
- stage: 0
  name: "기술 스택 결정"
  tasks:
    - id: T-000
      name: "기술 스택 선정"
      agent: architect

- stage: 1
  name: "개발"
  tasks:
    - id: T-001
      name: "백엔드 API"
      agent: backend-developer
      depends_on: [T-000]  # 기술 스택 결정 후
```

### Case 4: 단일 Agent만 필요

예: 정적 사이트 (프론트만)

**해결**:
workspace-map에 사용하는 Agent만 포함. 나머지 Agent는 생략:

```json
"ownership": {
  "frontend-developer": {
    "owns": ["src/**", "public/**"]
  }
  // backend, database 생략
}
```

### Case 5: Agent 부재

필요한 Agent가 `.claude/agents/`에 없는 경우:

**해결**:
1. 가장 유사한 Agent에게 할당
2. 태스크 이름에 특수 기술 명시

```yaml
- name: "GraphQL API 구현 (FastAPI + Strawberry)"
  agent: backend-developer  # GraphQL 전문 Agent 없음, backend가 대신
```

---

## Agent 우선순위

동일 태스크에 여러 Agent가 적합할 때 우선순위:

| 순위 | 기준 | 예시 |
|------|------|------|
| 1 | 전문성 매칭 | "REST API" → backend-developer (명확) |
| 2 | 기술 스택 매칭 | "FastAPI" → backend-developer |
| 3 | 도메인 매칭 | "금융 보안" → security-engineer |
| 4 | 산출물 경로 | "src/api/**" → backend-developer |

---

## 검증 체크리스트

태스크 분해 완료 후 확인:

- [ ] 모든 태스크에 agent 할당
- [ ] 모든 태스크에 output_files 정의
- [ ] depends_on의 태스크 ID가 실제 존재
- [ ] parallel_with 태스크들이 서로 다른 파일 수정
- [ ] workspace-map의 owns 경로가 output_files와 일치
- [ ] 충돌하는 owns 경로 없음
- [ ] security-engineer는 읽기 전용
- [ ] tester는 src/** 수정 금지

---

## 참고

- WBS 템플릿: [wbs-templates.md](wbs-templates.md)
