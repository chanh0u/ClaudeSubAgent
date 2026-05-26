---
name: project-orchestrator
description: "요구사항 문서를 POC 프로젝트로 자동 변환하는 AI Agent Company 오케스트레이터. '프로젝트 생성', '문서 분석해서 프로젝트 만들어줘', 'POC 생성', '요구사항 문서 업로드', '하네스 실행' 요청 시 사용. 후속 작업: 프로젝트 다시 생성, 재실행, 부분 수정 (백엔드만/프론트만), 결과 개선, 업데이트, 보완 요청 시에도 반드시 이 스킬 사용. 단순 질문(에이전트 목록 보여줘, 설명해줘)은 이 스킬 없이 직접 응답 가능."
---

# Project Orchestrator — AI Agent Company 워크플로우

요구사항 문서를 입력받아 POC 수준의 프로젝트를 자동 생성하는 전체 워크플로우를 조율하는 오케스트레이터 스킬.

## 실행 모드: 하이브리드

Phase별로 서브 에이전트와 에이전트 팀을 혼합 사용한다. Phase 3 병렬 개발 단계에서만 에이전트 팀을 구성하고, 나머지는 서브 에이전트로 실행한다.

| Phase | 모드 | 이유 |
|-------|------|------|
| Phase 0 (컨텍스트 확인) | - | 실행 모드 판별 단계 |
| Phase 1 (문서 분석) | 서브 에이전트 | 단일 에이전트 독립 작업 |
| Phase 2 (프로젝트 계획) | 서브 에이전트 | 단일 에이전트 독립 작업 |
| Phase 3 (병렬 개발) | 에이전트 팀 | 4명 팀원 협업, 파일 소유권 조율 필요 |
| Phase 4 (검증 및 통합) | 서브 → 팀 | 검증은 서브, 최종 통합은 tech-lead 주도 팀 |

## 에이전트 구성

### Phase 1-2: 서브 에이전트

| 에이전트 | subagent_type | 역할 | 입력 | 출력 |
|---------|--------------|------|------|------|
| document-parser | document-parser | 문서 분석 및 요구사항 추출 | 업로드 문서 (PDF, DOCX 등) | `_workspace/01_parsed-spec.json` |
| project-manager | project-manager | WBS, workspace-map 생성 | parsed-spec.json | `_workspace/02_project-plan.md`, `_workspace/02_workspace-map.json` |

### Phase 3: 에이전트 팀

| 팀원 | 에이전트 타입 | 역할 | 스킬 | 출력 |
|------|-------------|------|------|------|
| backend-dev | backend (커스텀) | FastAPI 백엔드 개발 | backend-development | `workspace/{project_id}/src/api/**` |
| frontend-dev | frontend (커스텀) | React 프론트엔드 개발 | frontend-development | `workspace/{project_id}/src/components/**` |
| db-engineer | dba (커스텀) | DB 스키마 설계 | database-design | `workspace/{project_id}/migrations/**` |
| devops | devops (커스텀) | Docker, CI/CD | devops | `workspace/{project_id}/Dockerfile` |

### Phase 4: 서브 에이전트 → 팀

| 에이전트 | subagent_type | 역할 | 출력 |
|---------|--------------|------|------|
| security-engineer | security-engineer | OWASP 보안 감사 | `_workspace/04_security-report.md` |
| tester | tester (커스텀) | 테스트 코드 작성 | `workspace/{project_id}/tests/**` |
| tech-lead (팀) | tech-lead | 최종 통합 및 충돌 해결 | 완성된 프로젝트 |

## 워크플로우

### Phase 0: 컨텍스트 확인 (후속 작업 지원)

기존 산출물 존재 여부를 확인하여 실행 모드를 결정한다:

1. `_workspace/` 디렉토리 존재 여부 확인 (Glob 또는 Bash ls 사용)
2. 실행 모드 결정:
   - **`_workspace/` 미존재** → 초기 실행. Phase 1로 진행
   - **`_workspace/` 존재 + 사용자가 부분 수정 요청** (예: "백엔드만 다시", "프론트 UI 수정")
     - 부분 재실행 모드
     - 해당 에이전트만 재호출
     - 기존 산출물 중 수정 대상만 덮어쓰기
     - Phase 3로 직접 이동, 해당 팀원만 작업
   - **`_workspace/` 존재 + 새 요구사항 문서 제공** → 새 실행
     - 기존 `_workspace/`를 `_workspace_backup_{YYYYMMDD_HHMMSS}/`로 이동
     - Phase 1부터 재시작

3. **부분 재실행 시 주의사항:**
   - 이전 산출물 경로를 에이전트 프롬프트에 포함
   - 에이전트가 기존 결과를 Read로 읽고 피드백 반영
   - workspace-map.json은 재사용 (파일 소유권 유지)

### Phase 1: 문서 분석

**실행 모드:** 서브 에이전트

1. 사용자가 제공한 요구사항 문서 경로 확인
   - PDF, DOCX, XLSX, Markdown, 텍스트 파일 등
   - 구두 요구사항인 경우 사용자 메시지를 텍스트로 저장

2. `_workspace/` 디렉토리 생성
   - 초기 실행: 새 `_workspace/` 생성
   - 새 실행: 기존 백업 후 새 `_workspace/` 재생성

3. document-parser 에이전트 호출:
   ```
   Agent(
     prompt: "업로드된 요구사항 문서를 분석하여 parsed-spec.json을 생성하라.
             문서 경로: {document_path}
             출력 경로: _workspace/01_parsed-spec.json

             parsed-spec.json 형식:
             - project_name: 프로젝트명
             - description: 프로젝트 설명
             - features: 기능 목록 (배열)
             - tech_stack: 기술 스택
             - non_functional_requirements: 비기능 요구사항",
     subagent_type: "document-parser",
     model: "opus"
   )
   ```

4. 산출물 검증:
   - `_workspace/01_parsed-spec.json` 파일 존재 확인
   - JSON 형식 유효성 확인 (Read로 읽어서 파싱 가능한지 확인)

### Phase 2: 프로젝트 계획

**실행 모드:** 서브 에이전트

1. project-manager 에이전트 호출:
   ```
   Agent(
     prompt: "parsed-spec.json을 기반으로 WBS와 workspace-map을 생성하라.
             입력: _workspace/01_parsed-spec.json
             출력:
               - _workspace/02_project-plan.md (WBS)
               - _workspace/02_workspace-map.json (파일 소유권 맵)

             에이전트 스캔: .claude/agents/ 디렉토리의 모든 에이전트 정의 읽기

             WBS 생성 규칙:
             - Stage 1: 분석·설계 (system-analyst, architect)
             - Stage 2: 병렬 개발 (backend, frontend, database, devops)
             - Stage 3: 검증·통합 (security-engineer, tester, tech-lead)

             workspace-map 생성 규칙:
             - backend-developer: src/api/**, src/service/**
             - frontend-developer: src/components/**, src/pages/**
             - database-engineer: migrations/**, src/db/**
             - devops-engineer: Dockerfile, docker-compose.yml, .github/**
             - security-engineer: 읽기 전용 (docs/security-report.md만 작성)
             - tester: tests/** (읽기 전용: src/**)
             - tech-lead: 충돌 해결 권한, 모든 파일 수정 가능",
     subagent_type: "project-manager",
     model: "opus"
   )
   ```

2. 산출물 검증:
   - `_workspace/02_project-plan.md` 존재 확인
   - `_workspace/02_workspace-map.json` 존재 확인 및 JSON 유효성 확인

3. 프로젝트 ID 생성 및 workspace 디렉토리 생성:
   ```bash
   project_id=$(cat _workspace/02_project-plan.md | grep "project_id:" | cut -d'"' -f2)
   mkdir -p workspace/${project_id}
   ```

### Phase 3: 병렬 개발

**실행 모드:** 에이전트 팀

이 Phase에서만 에이전트 팀을 구성한다. 4명의 개발 에이전트가 workspace-map.json에 정의된 파일 소유권을 기반으로 병렬 작업한다.

#### Step 3-1: 팀 구성

```
TeamCreate(
  team_name: "dev-team",
  members: [
    {
      name: "backend-dev",
      agent_type: "backend",
      model: "opus",
      prompt: "당신은 FastAPI 백엔드 개발자입니다.

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
    },
    {
      name: "frontend-dev",
      agent_type: "frontend",
      model: "opus",
      prompt: "당신은 React 프론트엔드 개발자입니다.

              입력:
              - _workspace/02_project-plan.md
              - _workspace/02_workspace-map.json
              - _workspace/01_parsed-spec.json

              작업:
              1. workspace-map.json에서 owns 경로 확인
              2. project-plan.md에서 frontend 태스크 확인
              3. React + Vite 기반 UI 구현
              4. API 호출 (backend-dev와 협의)
              5. src/App.jsx, src/components/* 생성

              출력: workspace/{project_id}/src/components/**, workspace/{project_id}/src/pages/**

              협업 규칙:
              - backend-dev에게 필요한 API 엔드포인트 요청 (SendMessage)
              - 작업 완료 시 리더에게 보고"
    },
    {
      name: "db-engineer",
      agent_type: "dba",
      model: "opus",
      prompt: "당신은 데이터베이스 엔지니어입니다.

              입력:
              - _workspace/02_project-plan.md
              - _workspace/02_workspace-map.json
              - _workspace/01_parsed-spec.json

              작업:
              1. workspace-map.json에서 owns 경로 확인
              2. DB 스키마 설계 (parsed-spec의 데이터 모델 기반)
              3. 마이그레이션 스크립트 생성
              4. migrations/*, src/db/* 생성

              출력: workspace/{project_id}/migrations/**, workspace/{project_id}/src/db/**

              협업 규칙:
              - backend-dev에게 스키마 공유 (SendMessage)
              - 작업 완료 시 리더에게 보고"
    },
    {
      name: "devops",
      agent_type: "devops",
      model: "opus",
      prompt: "당신은 DevOps 엔지니어입니다.

              입력:
              - _workspace/02_project-plan.md
              - _workspace/02_workspace-map.json
              - workspace/{project_id}/ (다른 팀원의 코드)

              작업:
              1. workspace-map.json에서 owns 경로 확인
              2. Dockerfile, docker-compose.yml 생성
              3. CI/CD 파이프라인 설정 (.github/workflows/)
              4. 환경변수 템플릿 (.env.example)

              출력: workspace/{project_id}/Dockerfile, docker-compose.yml, .github/**

              협업 규칙:
              - 다른 팀원의 의존성 파일 확인 (requirements.txt, package.json)
              - 작업 완료 시 리더에게 보고"
    }
  ]
)
```

#### Step 3-2: 작업 할당

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
    title: "DB 스키마 설계",
    description: "마이그레이션 스크립트, DB 모델",
    assignee: "db-engineer",
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

> 팀원당 1-2개 작업. devops는 다른 팀원의 코드에 의존하므로 depends_on 설정.

#### Step 3-3: 병렬 실행 및 모니터링

**팀원 자체 조율:**
팀원들은 공유 작업 목록에서 작업을 수행하며 필요 시 SendMessage로 직접 통신한다.

**리더 모니터링:**
- 팀원이 유휴 상태가 되면 자동 알림 수신
- TaskGet으로 진행률 확인
- 특정 팀원이 막혔을 때 SendMessage로 지시

**파일 소유권 충돌 방지:**
workspace-map.json에 정의된 owns 경로를 각 팀원이 준수해야 한다. 충돌 발생 시 tech-lead가 Phase 4에서 해결.

#### Step 3-4: 산출물 수집

모든 팀원의 작업 완료 대기 후:
1. `workspace/{project_id}/` 디렉토리 구조 확인 (Glob 사용)
2. 주요 파일 존재 확인:
   - `src/main.py` (backend)
   - `src/App.jsx` (frontend)
   - `migrations/` (database)
   - `Dockerfile` (devops)

### Phase 4: 검증 및 통합

**실행 모드:** 서브 에이전트 → 에이전트 팀

Phase 3의 팀을 정리한 후, 검증 에이전트들을 서브로 실행하고, 최종 통합은 tech-lead 주도 팀으로 수행한다.

#### Step 4-1: Phase 3 팀 정리

```
SendMessage(to: "all", message: "모든 작업이 완료되었습니다. 팀을 종료합니다.")
TeamDelete()
```

#### Step 4-2: 보안 감사 (서브 에이전트)

```
Agent(
  prompt: "workspace/{project_id}/ 전체 코드를 OWASP Top 10 기준으로 보안 감사하라.

          입력: workspace/{project_id}/ (전체 코드)
          출력: _workspace/04_security-report.md

          체크리스트:
          - SQL Injection
          - XSS
          - 인증/인가 취약점
          - 민감 정보 노출
          - 설정 오류

          읽기 전용 모드. 코드 수정 금지.",
  subagent_type: "security-engineer",
  model: "opus"
)
```

#### Step 4-3: 테스트 코드 작성 (서브 에이전트)

```
Agent(
  prompt: "workspace/{project_id}/ 코드에 대한 테스트 코드를 작성하라.

          입력:
          - workspace/{project_id}/src/api/** (백엔드 코드)
          - workspace/{project_id}/src/components/** (프론트 코드)
          - _workspace/01_parsed-spec.json (요구사항)

          출력: workspace/{project_id}/tests/**

          테스트 작성 규칙:
          - 백엔드: pytest 기반 API 테스트
          - 프론트: Jest 기반 컴포넌트 테스트
          - 경계면 교차 비교 (API 응답 ↔ 프론트 훅)
          - Incremental QA (모듈별 점진적 검증)",
  subagent_type: "tester",
  model: "opus"
)
```

#### Step 4-4: 최종 통합 (에이전트 팀)

tech-lead를 리더로 하는 소규모 팀 구성하여 최종 통합 수행:

```
TeamCreate(
  team_name: "integration-team",
  members: [
    {
      name: "tech-lead",
      agent_type: "tech-lead",
      model: "opus",
      prompt: "당신은 Tech Lead입니다. 최종 통합 및 충돌 해결을 담당합니다.

              입력:
              - workspace/{project_id}/ (전체 프로젝트)
              - _workspace/04_security-report.md (보안 감사 결과)
              - _workspace/02_workspace-map.json (파일 소유권)

              작업:
              1. workspace-map의 tech_lead_merge_targets 파일 확인
              2. 파일 충돌 해결 (src/main.py, src/App.jsx 등)
              3. 보안 감사 결과 반영 (critical 이슈만)
              4. README.md 생성 (프로젝트 설명, 실행 방법)
              5. 최종 검증 (빌드 가능 여부, 주요 파일 존재 확인)

              출력: 완성된 workspace/{project_id}/

              협업 규칙:
              - 필요 시 이전 개발자에게 질문 불가 (팀이 이미 해체됨)
              - 문제 발견 시 직접 수정 또는 리더(오케스트레이터)에게 보고"
    }
  ]
)
```

Task 할당:
```
TaskCreate(tasks: [
  {
    title: "최종 통합 및 README 생성",
    description: "충돌 해결, 보안 이슈 반영, 문서화",
    assignee: "tech-lead"
  }
])
```

작업 완료 대기 후 팀 정리:
```
TeamDelete()
```

### Phase 5: 정리 및 보고

1. `_workspace/` 디렉토리 보존
   - 중간 산출물 삭제하지 않음 (사후 검증·감사 추적용)

2. 최종 산출물 경로 확인:
   - `workspace/{project_id}/` (전체 프로젝트)
   - `_workspace/01_parsed-spec.json`
   - `_workspace/02_project-plan.md`
   - `_workspace/02_workspace-map.json`
   - `_workspace/04_security-report.md`

3. 사용자에게 결과 요약 보고:
   ```
   프로젝트 생성 완료!

   프로젝트 경로: workspace/{project_id}/

   생성된 파일:
   - 백엔드: src/main.py, src/api/*, src/service/*
   - 프론트엔드: src/App.jsx, src/components/*
   - 데이터베이스: migrations/*, src/db/*
   - 인프라: Dockerfile, docker-compose.yml
   - 테스트: tests/*
   - 문서: README.md

   중간 산출물: _workspace/ (보존됨)

   실행 방법은 workspace/{project_id}/README.md를 참고하세요.
   ```

## 데이터 흐름

```
[사용자 요구사항 문서]
          ↓
    Phase 1: document-parser (서브) → 01_parsed-spec.json
          ↓
    Phase 2: project-manager (서브) → 02_project-plan.md, 02_workspace-map.json
          ↓
    Phase 3: dev-team (팀)
         [backend-dev] ←SendMessage→ [frontend-dev]
         [db-engineer] ←SendMessage→ [backend-dev]
         [devops]
              ↓
         workspace/{project_id}/*
          ↓
    Phase 4-1: security-engineer (서브) → 04_security-report.md
    Phase 4-2: tester (서브) → tests/*
    Phase 4-3: integration-team (팀)
         [tech-lead] → 최종 통합
              ↓
         완성된 workspace/{project_id}/
```

## 에러 핸들링

### Phase 1-2 (서브 에이전트) 에러

| 상황 | 전략 |
|------|------|
| document-parser 실패 | 1회 재시도. 재실패 시 사용자에게 문서 형식 확인 요청 |
| parsed-spec.json 형식 오류 | JSON 수동 수정 또는 재실행 |
| project-manager 실패 | 1회 재시도. 재실패 시 기본 WBS 템플릿 사용 |

### Phase 3 (에이전트 팀) 에러

| 상황 | 전략 |
|------|------|
| 팀원 1명 실패/중지 | 리더가 유휴 알림 수신 → SendMessage로 상태 확인 → 재시작 시도 |
| 팀원 재시작 실패 | 해당 팀원 작업을 다른 팀원에게 재할당 (SendMessage로 지시) |
| 팀원 과반(2명 이상) 실패 | 사용자에게 알리고 진행 여부 확인. 부분 결과로 진행 가능하면 계속 |
| 파일 소유권 충돌 | workspace-map.json에 명시된 경로 준수 강조. 충돌 발견 시 Phase 4 tech-lead가 해결 |
| 팀원 간 API 불일치 | backend-dev와 frontend-dev가 SendMessage로 협의. 합의 실패 시 리더 중재 |

### Phase 4 (검증 및 통합) 에러

| 상황 | 전략 |
|------|------|
| security-engineer 실패 | 보안 감사 없이 진행, 보고서에 "보안 감사 미완료" 명시 |
| tester 실패 | 테스트 코드 없이 진행, 사용자에게 수동 테스트 권장 |
| tech-lead 통합 실패 | 통합 전 상태(Phase 3 결과)를 최종 산출물로 제공, 수동 통합 필요 안내 |
| 빌드 실패 | README에 알려진 이슈 섹션 추가, 해결 방법 제시 |

### 전체 프로세스 타임아웃

- Phase별 최대 실행 시간: Phase 1-2 각 10분, Phase 3 30분, Phase 4 20분
- 타임아웃 시 현재까지 수집된 부분 결과 사용
- 미완료 Phase를 보고서에 명시

## 테스트 시나리오

### 정상 흐름

1. 사용자가 "간단한 TODO 앱 프로젝트 생성해줘. FastAPI + React 사용." 요청
2. Phase 0에서 `_workspace/` 미존재 확인 → 초기 실행
3. Phase 1에서 document-parser가 요구사항을 parsed-spec.json으로 변환
4. Phase 2에서 project-manager가 WBS와 workspace-map 생성
5. Phase 3에서 dev-team (4명)이 병렬 개발
   - backend-dev: src/main.py, src/api/todos.py 생성
   - frontend-dev: src/App.jsx, src/components/TodoList.jsx 생성
   - db-engineer: migrations/001_create_todos.sql 생성
   - devops: Dockerfile, docker-compose.yml 생성
6. Phase 4에서 보안 감사 → 테스트 코드 작성 → tech-lead 통합
7. 예상 결과: `workspace/{project_id}/` 완성, README.md 포함

### 부분 재실행 흐름

1. 사용자가 "프론트엔드 UI만 다시 만들어줘" 요청
2. Phase 0에서 `_workspace/` 존재 확인 + 부분 수정 요청 감지
3. Phase 3로 직접 이동, frontend-dev만 재호출
4. 기존 `workspace/{project_id}/src/components/*` 덮어쓰기
5. Phase 4 건너뛰고 바로 정리
6. 예상 결과: 프론트엔드만 업데이트된 프로젝트

### 에러 흐름

1. Phase 3에서 backend-dev가 에러로 중지
2. 리더가 유휴 알림 수신
3. SendMessage로 backend-dev 상태 확인 → 응답 없음
4. backend-dev 재시작 시도 (Agent 도구 재호출)
5. 재시작 실패 시 frontend-dev에게 "백엔드 작업 대신 모의 API 사용" 지시
6. Phase 4에서 tech-lead가 "백엔드 미구현, 모의 API 사용 중" README에 명시
7. 예상 결과: 프론트엔드 + 모의 API로 구성된 부분 프로젝트

## 참조

- 파이프라인 패턴 상세: [references/pipeline-patterns.md](references/pipeline-patterns.md)
- 에러 핸들링 전략: [references/error-handling.md](references/error-handling.md)
- 팀 조율 프로토콜: [references/team-coordination.md](references/team-coordination.md)

## 주의사항

1. **Phase 3에서만 에이전트 팀 사용**: Phase 1-2, 4는 서브 에이전트로 충분. 팀 오버헤드 최소화.
2. **workspace-map.json 준수**: 파일 소유권 충돌 방지의 핵심. 팀원 프롬프트에 명확히 명시.
3. **_workspace/ 보존**: 중간 산출물을 삭제하지 않음. 디버깅 및 감사 추적에 필수.
4. **후속 작업 지원**: Phase 0 컨텍스트 확인으로 초기/후속/부분 재실행 구분.
5. **모든 Agent 호출에 model: "opus" 명시**: 품질 보장을 위해 opus 사용 필수.
