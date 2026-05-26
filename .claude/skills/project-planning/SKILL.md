---
name: project-planning
description: "parsed-spec.json을 기반으로 WBS와 workspace-map을 생성. 프로젝트 계획, 태스크 분해, Agent 배정, 파일 소유권 정의 작업 시 사용. 요구사항을 실행 가능한 작업 단위로 분해하고, 각 작업에 적합한 Agent를 매칭하며, 병렬 개발 시 파일 충돌을 방지하는 소유권 맵을 생성."
---

# Project Planning Skill

parsed-spec.json을 읽고 **WBS(Work Breakdown Structure)**와 **workspace-map.json**을 생성하는 스킬. AI Agent Company 워크플로우의 Phase 2에서 project-manager 에이전트가 사용한다.

## 핵심 역할

1. **태스크 분해**: 기능 요구사항을 구현 가능한 작업 단위로 분해
2. **Agent 배정**: 작업 유형에 따라 적합한 Agent 매칭
3. **의존성 분석**: 순차 실행 vs 병렬 실행 판별
4. **파일 소유권 정의**: 병렬 개발 시 충돌 방지를 위한 경로 할당

## 작업 순서

### Step 1: parsed-spec.json 읽기

```python
spec = Read("_workspace/01_parsed-spec.json")
project_name = spec["project_name"]
features = spec["features"]  # 기능 목록
tech_stack = spec["tech_stack"]
```

**검증**:
- 필수 필드 존재 확인: project_name, features, tech_stack
- features 배열에 최소 1개 항목

### Step 2: Agent 스캔

`.claude/agents/` 디렉토리의 모든 에이전트 정의 파일을 읽어 사용 가능한 Agent 목록 파악:

```bash
Glob(".claude/agents/*.md")
→ [backend.md, frontend.md, dba.md, devops.md, security-engineer.md, ...]
```

각 에이전트의 frontmatter에서 `skills`, `domain_expertise` 추출하여 매칭에 활용.

### Step 3: 태스크 분해

하나의 기능을 여러 태스크로 분해한다. 원칙: **기능은 무엇을, 태스크는 어떻게**

**예시**:
```
기능: "사용자 인증"
→ 태스크 분해:
  - T-001: API 명세 작성 (system-analyst)
  - T-002: 인증 API 구현 (backend-developer)
  - T-003: 로그인 UI 구현 (frontend-developer)
  - T-004: users 테이블 설계 (database-engineer)
  - T-005: 인증 API 테스트 (tester)
```

**분해 규칙**:
- 백엔드 작업: API 엔드포인트별로 분해
- 프론트 작업: 페이지/컴포넌트별로 분해
- DB 작업: 테이블별로 분해
- 인프라 작업: Docker, CI/CD를 별도 태스크로

> 상세 분해 규칙: [references/task-decomposition-rules.md](references/task-decomposition-rules.md)

### Step 4: Agent 배정

태스크 유형에 따라 Agent 스킬 매칭 규칙을 적용한다.

**기본 매칭 규칙**:

| 태스크 유형 | 배정 Agent | 근거 |
|------------|----------|------|
| REST API, 비즈니스 로직 | backend-developer | API 구현 전문 |
| UI 컴포넌트, 라우팅 | frontend-developer | React 전문 |
| DB 스키마, 마이그레이션 | database-engineer | DB 설계 전문 |
| Docker, CI/CD | devops-engineer | 인프라 전문 |
| OWASP 보안 감사 | security-engineer | 보안 전문 |
| 테스트 코드 | tester | QA 전문 |
| 요건 분석, API 명세 | system-analyst | 요구사항 정제 |
| 아키텍처 설계 | architect | 시스템 설계 |

**기술 스택 기반 매칭**:

parsed-spec의 tech_stack을 확인하여 Agent 선택:

```json
tech_stack: {
  "backend": "FastAPI" → backend-developer
  "frontend": "React" → frontend-developer
  "database": "PostgreSQL" → database-engineer
}
```

> 상세 매칭 규칙: [references/agent-matching-rules.md](references/agent-matching-rules.md)

### Step 5: 의존성 분석

태스크 간 의존성을 분석하여 순차 실행과 병렬 실행을 구분한다.

**의존성 판별 규칙**:

| 상황 | 의존성 | 예시 |
|------|--------|------|
| A의 산출물을 B가 사용 | B depends_on A | API 명세(A) → API 구현(B) |
| A와 B가 같은 파일 수정 | 순차 실행 | 같은 src/main.py 수정 |
| A와 B가 독립적 | 병렬 실행 | 백엔드(A)와 프론트(B) |

**병렬 실행 가능 조건**:
- 서로 다른 파일 경로 수정
- 산출물 의존 없음
- 같은 선행 작업에 의존 (예: 둘 다 API 명세에 의존)

**Stage 분할**:
```yaml
Stage 1: 분석·설계 (순차)
  - API 명세 작성
  - 아키텍처 설계

Stage 2: 병렬 개발 (병렬)
  - 백엔드 API
  - 프론트 UI
  - DB 스키마

Stage 3: 인프라·검증 (순차)
  - Docker 설정
  - 보안 감사
  - 테스트
```

### Step 6: project-plan.md 생성

WBS를 YAML 형식으로 작성한다.

**형식**:
```yaml
project_id: "uuid-자동생성"
project_name: "프로젝트명"
source_spec: ".claude/output/parsed-spec.json"
created_at: "YYYY-MM-DD"

pipeline:
  stages:
    - stage: 1
      name: "분석·설계"
      sequential: true
      tasks:
        - id: T-001
          name: "API 명세 작성"
          agent: system-analyst
          output_files:
            - "docs/api-spec.md"
          est_hours: 2
          acceptance_criteria:
            - "모든 엔드포인트 정의 완료"

    - stage: 2
      name: "병렬 개발"
      sequential: false
      tasks:
        - id: T-002
          name: "백엔드 API 구현"
          agent: backend-developer
          depends_on: [T-001]
          parallel_with: [T-003, T-004]
          output_files: ["src/api/**", "src/service/**"]
          est_hours: 8

        - id: T-003
          name: "프론트 UI 구현"
          agent: frontend-developer
          depends_on: [T-001]
          parallel_with: [T-002, T-004]
          output_files: ["src/components/**"]
          est_hours: 8

        - id: T-004
          name: "DB 스키마"
          agent: database-engineer
          depends_on: [T-001]
          parallel_with: [T-002, T-003]
          output_files: ["migrations/**"]
          est_hours: 3
```

**필수 필드**:
- `id`: 태스크 고유 ID
- `name`: 태스크명
- `agent`: 담당 Agent
- `output_files`: 산출물 경로 (workspace-map 생성에 사용)
- `depends_on`: 선행 작업 (선택)
- `parallel_with`: 병렬 작업 (선택)

> WBS 템플릿: [references/wbs-templates.md](references/wbs-templates.md)

### Step 7: workspace-map.json 생성

파일 소유권을 정의하여 병렬 개발 시 충돌을 방지한다.

**형식**:
```json
{
  "project_id": "uuid",
  "root": "/workspace/{project_id}",
  "created_by": "project-manager",
  "created_at": "YYYY-MM-DD",
  "conflict_resolution": "tech-lead-decides",

  "ownership": {
    "backend-developer": {
      "owns": [
        "src/api/**",
        "src/service/**",
        "src/domain/**",
        "requirements.txt"
      ],
      "reads": [
        "docs/**",
        "src/db/**"
      ],
      "forbidden": [
        "src/components/**",
        "src/pages/**",
        "migrations/**"
      ]
    },

    "frontend-developer": {
      "owns": [
        "src/components/**",
        "src/pages/**",
        "src/hooks/**",
        "package.json"
      ],
      "reads": [
        "docs/**"
      ],
      "forbidden": [
        "src/api/**",
        "migrations/**"
      ]
    },

    "database-engineer": {
      "owns": [
        "migrations/**",
        "src/db/**"
      ],
      "reads": [
        "docs/**"
      ],
      "forbidden": [
        "src/api/**",
        "src/components/**"
      ]
    },

    "devops-engineer": {
      "owns": [
        "Dockerfile",
        "docker-compose.yml",
        ".github/**",
        "Makefile"
      ],
      "reads": [
        "docs/**",
        "src/**",
        "requirements.txt",
        "package.json"
      ],
      "forbidden": []
    },

    "security-engineer": {
      "owns": [
        "docs/security-report.md"
      ],
      "reads": [
        "src/**",
        "Dockerfile"
      ],
      "forbidden": [
        "src/** (수정 금지)"
      ]
    },

    "tester": {
      "owns": [
        "tests/**",
        "pytest.ini",
        "jest.config.ts"
      ],
      "reads": [
        "src/**",
        "docs/**"
      ],
      "forbidden": [
        "src/**"
      ]
    }
  },

  "shared_readonly": [
    "docs/**",
    ".claude/output/parsed-spec.json",
    ".claude/output/project-plan.md"
  ],

  "tech_lead_merge_targets": [
    "src/main.py",
    "src/main.tsx",
    "src/App.tsx"
  ]
}
```

**소유권 규칙**:
- `owns`: 이 Agent만 수정 가능
- `reads`: 읽기 전용
- `forbidden`: 접근 금지

**충돌 방지**:
- 동일 경로가 여러 Agent의 `owns`에 있으면 에러
- `tech_lead_merge_targets`: 여러 Agent가 수정 가능, tech-lead가 Phase 4에서 병합

## 출력 경로

- `_workspace/02_project-plan.md` (WBS)
- `_workspace/02_workspace-map.json` (파일 소유권)

## 절대 금지

- ❌ 직접 코드 작성 금지 (계획만 수립)
- ❌ Agent 스킬 무시하고 임의 배정 금지
- ❌ workspace-map 없이 Phase 3 시작 금지

## 핵심 규칙

**Rule 1**: workspace-map.json이 없으면 병렬 개발(Phase 3)을 시작하지 않는다.

**Rule 2**: 병렬 가능 태스크 식별 시 `depends_on`이 같은 선행 태스크면 `parallel_with` 설정.

**Rule 3**: 모든 개발 Agent는 workspace-map의 `owns` 경로만 수정 가능. `forbidden` 경로 수정 시 Phase 4 tech-lead가 롤백.

## 검증

생성된 파일의 유효성을 확인한다:

1. **project-plan.md 검증**:
   - 최소 1개 stage 존재
   - 모든 task에 id, name, agent, output_files 존재
   - depends_on의 태스크 ID가 실제 존재

2. **workspace-map.json 검증**:
   - JSON 형식 유효성
   - 모든 개발 Agent의 `owns` 경로 정의
   - `owns` 경로 간 충돌 없음 (교집합 검사)
   - `forbidden` 경로가 다른 Agent의 `owns`에 포함되는지 확인

## 참조

- 태스크 분해 규칙: [references/task-decomposition-rules.md](references/task-decomposition-rules.md)
- Agent 매칭 규칙: [references/agent-matching-rules.md](references/agent-matching-rules.md)
- WBS 템플릿: [references/wbs-templates.md](references/wbs-templates.md)

## 사용 예시

**입력** (parsed-spec.json):
```json
{
  "project_name": "TODO App",
  "features": [
    { "id": "F001", "name": "할 일 추가" },
    { "id": "F002", "name": "할 일 목록 보기" }
  ],
  "tech_stack": {
    "backend": "FastAPI",
    "frontend": "React",
    "database": "PostgreSQL"
  }
}
```

**출력** (project-plan.md):
```yaml
project_id: "todo-app-20260526"
project_name: "TODO App"

pipeline:
  stages:
    - stage: 1
      name: "분석·설계"
      sequential: true
      tasks:
        - id: T-001
          name: "API 명세 작성"
          agent: system-analyst

    - stage: 2
      name: "병렬 개발"
      sequential: false
      tasks:
        - id: T-002
          name: "할 일 API 구현"
          agent: backend-developer
          depends_on: [T-001]
          parallel_with: [T-003, T-004]

        - id: T-003
          name: "할 일 UI 구현"
          agent: frontend-developer
          depends_on: [T-001]
          parallel_with: [T-002, T-004]

        - id: T-004
          name: "todos 테이블 설계"
          agent: database-engineer
          depends_on: [T-001]
          parallel_with: [T-002, T-003]
```

**출력** (workspace-map.json):
```json
{
  "project_id": "todo-app-20260526",
  "ownership": {
    "backend-developer": {
      "owns": ["src/api/**", "src/service/**"]
    },
    "frontend-developer": {
      "owns": ["src/components/**"]
    },
    "database-engineer": {
      "owns": ["migrations/**"]
    }
  }
}
```
