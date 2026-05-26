# Team Coordination — 팀 조율 프로토콜

에이전트 팀 모드에서 TeamCreate, SendMessage, TaskCreate를 사용한 팀 조율 방법.

---

## 목차

1. [팀 조율 개요](#1-팀-조율-개요)
2. [TeamCreate 사용법](#2-teamcreate-사용법)
3. [TaskCreate 사용법](#3-taskcreate-사용법)
4. [SendMessage 사용법](#4-sendmessage-사용법)
5. [팀 모니터링](#5-팀-모니터링)
6. [팀 정리](#6-팀-정리)

---

## 1. 팀 조율 개요

### 에이전트 팀의 특징

에이전트 팀 모드는 Phase 3 병렬 개발에서만 사용된다. 4명의 팀원(backend-dev, frontend-dev, db-engineer, devops)이 독립적으로 작업하면서 필요 시 직접 통신한다.

```
[리더/오케스트레이터]
       │
       ├── TeamCreate → 팀 생성
       ├── TaskCreate → 작업 할당
       │
       └── [팀 자체 조율]
             ↓
       [backend-dev] ←→ [frontend-dev]
             ↓              ↓
       [db-engineer] ←→ [devops]
```

### 팀 vs 서브 에이전트

| 특징 | 에이전트 팀 | 서브 에이전트 |
|------|------------|--------------|
| 통신 | 팀원 간 직접 통신 (SendMessage) | 메인에게만 반환 |
| 조율 | 공유 작업 목록 (TaskCreate) | 메인이 전체 조율 |
| 적합 상황 | 협업 필수 (API 협의, 스키마 공유) | 독립 작업 |
| 사용 Phase | Phase 3 (병렬 개발) | Phase 1, 2, 4 |

---

## 2. TeamCreate 사용법

### 기본 구조

```
TeamCreate(
  team_name: "dev-team",
  members: [
    {
      name: "backend-dev",
      agent_type: "backend",
      model: "opus",
      prompt: "당신은 FastAPI 백엔드 개발자입니다. ..."
    },
    {
      name: "frontend-dev",
      agent_type: "frontend",
      model: "opus",
      prompt: "당신은 React 프론트엔드 개발자입니다. ..."
    },
    ...
  ]
)
```

### members 파라미터

각 팀원은 다음 필드를 가진다:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| name | string | O | 팀원 고유 ID (SendMessage에서 사용) |
| agent_type | string | O | .claude/agents/{name}.md 또는 빌트인 타입 |
| model | string | O | "opus" 필수 (품질 보장) |
| prompt | string | O | 팀원의 역할, 작업, 협업 규칙 |

### prompt 작성 규칙

팀원 prompt는 다음을 포함해야 한다:

1. **역할 정의**: "당신은 {역할} 전문가입니다"
2. **입력 파일**: 읽어야 하는 파일 경로 명시
3. **작업 내용**: 구체적 작업 목록 (번호 매기기)
4. **출력 경로**: 산출물을 저장할 절대 경로
5. **협업 규칙**: 누구와 어떤 정보를 교환하는지

**예시**:
```
"당신은 FastAPI 백엔드 개발자입니다.

입력:
- _workspace/02_project-plan.md (당신의 작업 확인)
- _workspace/02_workspace-map.json (파일 소유권 확인)
- _workspace/01_parsed-spec.json (요구사항)

작업:
1. workspace-map.json에서 당신이 owns하는 경로 확인
2. project-plan.md에서 backend 관련 태스크 확인
3. FastAPI 기반 REST API 구현
4. 다중 LLM 통합 (Claude, OpenAI, Ollama, Manus)
5. src/main.py, src/api/*, src/service/* 생성

출력: workspace/{project_id}/src/api/**, workspace/{project_id}/src/service/**

협업 규칙:
- frontend-dev와 API 엔드포인트 협의 (SendMessage 사용)
- db-engineer와 스키마 확인 (SendMessage 사용)
- 작업 완료 시 리더에게 보고"
```

### 팀 크기 가이드라인

| 프로젝트 규모 | 팀원 수 | 구성 |
|--------------|--------|------|
| 소규모 (5-10개 작업) | 2-3명 | backend, frontend, (db 생략) |
| 중규모 (10-20개 작업) | 4명 | backend, frontend, db, devops |
| 대규모 (20개+ 작업) | 5-6명 | backend, frontend, db, devops, security, tester |

> 팀원이 많을수록 조율 오버헤드 증가. 4명이 최적.

---

## 3. TaskCreate 사용법

### 기본 구조

```
TaskCreate(tasks: [
  {
    title: "FastAPI 백엔드 구현",
    description: "REST API, 비즈니스 로직, 다중 LLM 통합",
    assignee: "backend-dev",
    depends_on: []
  },
  {
    title: "React 프론트엔드 구현",
    description: "UI 컴포넌트, 라우팅, API 호출",
    assignee: "frontend-dev",
    depends_on: []
  },
  {
    title: "인프라 구성",
    description: "Docker, CI/CD 파이프라인",
    assignee: "devops",
    depends_on: ["FastAPI 백엔드 구현", "React 프론트엔드 구현"]
  }
])
```

### task 필드

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| title | string | O | 작업명 (짧고 명확하게) |
| description | string | O | 상세 설명 (무엇을, 어떻게) |
| assignee | string | O | 담당 팀원 name (TeamCreate의 name과 일치) |
| depends_on | string[] | X | 선행 작업 title 배열 (의존성 명시) |

### 작업 할당 전략

#### 전략 1: 균등 분배

각 팀원에게 비슷한 수의 작업 할당. 팀원당 1-2개 작업이 적정.

```
backend-dev: 1개 (백엔드 API)
frontend-dev: 1개 (프론트 UI)
db-engineer: 1개 (DB 스키마)
devops: 1개 (인프라, depends_on: 다른 3개)
```

#### 전략 2: 우선순위 기반

depends_on이 없는 작업을 먼저 할당, 의존 작업은 나중에.

```
우선순위 1: backend, frontend, db (병렬 가능)
우선순위 2: devops (backend, frontend에 의존)
```

### 의존성 관리

**depends_on 규칙**:
- devops는 backend, frontend 코드가 필요하므로 의존성 설정
- backend와 frontend는 독립적이므로 의존성 없음
- db와 backend는 상호 의존 (스키마 ↔ API)이지만 병렬 진행 가능 (SendMessage로 조율)

**주의**: 순환 의존 금지 (A depends_on B, B depends_on A)

---

## 4. SendMessage 사용법

### 기본 구조

```
SendMessage(
  to: "backend-dev",
  message: "POST /todos 엔드포인트 필요해요. 요청 바디 형식은?"
)
```

### to 파라미터

| 값 | 의미 | 사용 상황 |
|---|------|----------|
| "{name}" | 특정 팀원에게 | 1:1 통신 (가장 흔함) |
| "all" | 전체 브로드캐스트 | 전체 공지 (비용 높음, 드물게) |

### 메시지 작성 규칙

1. **구체적으로**: "정보 필요" (X) → "POST /todos 엔드포인트 형식 필요" (O)
2. **맥락 포함**: 무엇을 위해 필요한지 명시
3. **요청과 응답 구분**: 질문인지, 정보 전달인지 명확히
4. **파일 경로 명시**: "스키마 확인해주세요" (X) → "migrations/001_todos.sql 스키마 확인해주세요" (O)

### 통신 패턴

#### 패턴 1: API 협의 (frontend ↔ backend)

```
[frontend-dev → backend-dev]
"POST /todos 엔드포인트가 필요합니다.
요청 바디: { title: string, description: string }
응답 형식을 알려주세요."

[backend-dev → frontend-dev]
"POST /todos 구현 완료.
요청: { title: string, description: string }
응답: { id: number, title: string, description: string, completed: boolean, created_at: string }
src/api/todos.py 참고하세요."
```

#### 패턴 2: 스키마 공유 (db ↔ backend)

```
[db-engineer → backend-dev]
"todos 테이블 스키마 완성.
컬럼: id (PK), title (VARCHAR), description (TEXT), completed (BOOLEAN), created_at (TIMESTAMP)
migrations/001_create_todos.sql 확인하세요."

[backend-dev → db-engineer]
"확인했습니다. user_id 외래키도 필요할 것 같아요.
users 테이블 있나요?"
```

#### 패턴 3: 의존성 확인 (devops → 팀 전체)

```
[devops → all]
"Docker 설정을 위해 의존성 파일이 필요합니다.
requirements.txt (backend), package.json (frontend) 생성 완료 시 알려주세요."

[backend-dev → devops]
"requirements.txt 완성. fastapi==0.95.0, uvicorn==0.21.0 등."

[frontend-dev → devops]
"package.json 완성. react@18, vite@4."
```

#### 패턴 4: 리더 보고 (팀원 → 리더)

팀원은 작업 완료 시 자동으로 유휴 상태가 되어 리더에게 알림이 간다. 명시적 보고는 불필요하지만, 중간 진행 상황을 알리고 싶을 때 SendMessage 사용 가능.

```
[backend-dev → leader]
"백엔드 API 50% 완성. /todos GET, POST 구현 완료. PUT, DELETE는 30분 내 완료 예상."
```

### SendMessage 주의사항

1. **브로드캐스트 지양**: `to: "all"`은 모든 팀원에게 전달되어 컨텍스트 비용 증가. 특정 팀원에게만 필요한 정보는 1:1로.
2. **파일 기반 우선**: 긴 데이터는 파일로 저장 후 경로 전달. 메시지에 JSON 전체 붙여넣기 금지.
3. **응답 기대**: SendMessage는 비동기. 즉시 응답을 기대하지 말고, 팀원이 자신의 턴에 응답.

---

## 5. 팀 모니터링

### 리더의 모니터링 방법

리더(오케스트레이터)는 팀 진행 상황을 다음 방법으로 확인한다:

#### 방법 1: 유휴 알림 (자동)

팀원이 작업을 완료하거나 중지하면 리더에게 자동 알림:

```
"backend-dev가 유휴 상태입니다."
```

**조치**:
1. 작업 완료인지 확인 (TaskGet)
2. 에러로 중지했는지 확인 (SendMessage로 상태 질문)
3. 다음 작업 할당 또는 대기

#### 방법 2: TaskGet (수동)

공유 작업 목록 상태 조회:

```
TaskGet()
→ [
  { title: "백엔드 API", assignee: "backend-dev", status: "in_progress", progress: 60% },
  { title: "프론트 UI", assignee: "frontend-dev", status: "completed" },
  { title: "DB 스키마", assignee: "db-engineer", status: "in_progress", progress: 80% },
  { title: "인프라", assignee: "devops", status: "pending", blocked_by: ["백엔드 API"] }
]
```

**조치**:
- pending + blocked_by: 의존 작업 대기 중 (정상)
- in_progress: 진행 중 (정상)
- completed: 완료 (정상)
- failed: 실패 (에러 핸들링 필요)

#### 방법 3: SendMessage (직접 질문)

특정 팀원에게 진행 상황 질문:

```
SendMessage(to: "backend-dev", message: "진행 상황이 어떤가요? 막힌 부분이 있나요?")
→ "50% 완성. /todos GET, POST 완료. PUT, DELETE 작업 중."
```

### 모니터링 주기

- **유휴 알림**: 즉시 대응 (자동)
- **TaskGet**: 10분마다 (수동)
- **SendMessage**: 30분 이상 응답 없을 때 (수동)

---

## 6. 팀 정리

### 팀 정리 시점

Phase 3 종료 시 반드시 팀을 정리한다. 세션당 1팀만 활성 가능하므로 Phase 4에서 새 팀을 만들려면 Phase 3 팀을 삭제해야 한다.

### 정리 절차

```
1단계: 모든 팀원에게 종료 알림
SendMessage(to: "all", message: "모든 작업이 완료되었습니다. 팀을 종료합니다. 수고하셨습니다.")

2단계: 산출물 수집 (필요 시)
backend_files = glob("workspace/{project_id}/src/api/**")
frontend_files = glob("workspace/{project_id}/src/components/**")

3단계: 팀 삭제
TeamDelete()

4단계: 확인
→ "dev-team이 삭제되었습니다. 모든 팀원이 종료되었습니다."
```

### 정리 후 데이터 보존

팀을 삭제해도 팀원들이 생성한 파일은 `workspace/{project_id}/`에 보존된다. Phase 4에서 Read 도구로 접근 가능.

---

## 팀 조율 Best Practices

### 1. 팀 크기 최소화

팀원이 많을수록 조율 오버헤드 증가. 4명이 최적, 6명 초과는 지양.

### 2. 명확한 책임 분리

workspace-map.json으로 파일 소유권을 명확히 정의. 충돌 방지의 핵심.

### 3. SendMessage 효율화

- 1:1 통신 우선
- 파일 경로 명시
- 브로드캐스트 최소화

### 4. 의존성 최소화

depends_on을 최소화하여 병렬 작업 비율 증가. 팀원 간 SendMessage로 실시간 조율 가능하므로 강한 의존성은 불필요.

### 5. 리더 개입 최소화

팀원들이 자체 조율하도록 신뢰. 리더는 막혔을 때만 개입.

---

## 실전 예시: Phase 3 전체 흐름

```
[10:00] TeamCreate → dev-team (4명) 생성
[10:01] TaskCreate → 작업 4개 할당

[10:05] backend-dev 시작 (FastAPI API 구현)
[10:05] frontend-dev 시작 (React UI 구현)
[10:05] db-engineer 시작 (DB 스키마)

[10:15] db-engineer → backend-dev: "스키마 완성. migrations/001_todos.sql 확인하세요."
[10:16] backend-dev → db-engineer: "확인했습니다. user_id 외래키 추가 부탁드려요."
[10:20] db-engineer → backend-dev: "user_id 추가 완료."

[10:25] frontend-dev → backend-dev: "POST /todos 형식 알려주세요."
[10:27] backend-dev → frontend-dev: "요청: {title, description}, 응답: {id, title, ...}"

[10:30] db-engineer 유휴 상태 → 리더 알림
[10:30] frontend-dev 유휴 상태 → 리더 알림
[10:35] backend-dev 유휴 상태 → 리더 알림

[10:36] devops 시작 (Dockerfile 작성, backend/frontend 의존성 확인)
[10:45] devops 유휴 상태 → 리더 알림

[10:46] TaskGet → 모든 작업 completed
[10:47] SendMessage(to: "all", "작업 완료. 팀 종료.")
[10:48] TeamDelete()
```

---

## 참고

- 파이프라인 패턴: [pipeline-patterns.md](pipeline-patterns.md)
- 에러 핸들링: [error-handling.md](error-handling.md)
