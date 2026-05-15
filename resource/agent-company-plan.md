# 나만의 개발 Agent 회사 기획서

> **"AI 에이전트로 SI 개발 회사를 차린다"**
> 
> Version 1.0 | Claude Code CLI 기반 | 2025

---

## 목차

1. [프로젝트 개요 및 핵심 컨셉](#1-프로젝트-개요)
2. [회사 조직 구조 — agent.md 인력 관리](#2-회사-조직-구조)
3. [전체 파이프라인 7단계](#3-전체-파이프라인)
4. [Stage 1–2 — 문서 파싱 전략](#4-문서-파싱-전략)
5. [Stage 3 — PM 작업 분해 포맷](#5-pm-작업-분해-포맷)
6. [Stage 5 — workspace-map 설계 (충돌 방지)](#6-workspace-map-설계)
7. [Claude CLI 적용 방법](#7-claude-cli-적용-방법)
8. [디렉터리 구조 및 Git 연동 전략](#8-디렉터리-구조-및-git-연동)
9. [개발 로드맵](#9-개발-로드맵)
10. [핵심 설계 원칙 요약](#10-핵심-설계-원칙)

---

## 1. 프로젝트 개요

### 1.1 핵심 컨셉

> **"내가 SI 개발 회사를 차린다"**

사람 대신 **Claude Sub-Agent**가 각 직무를 맡는 AI 개발 회사를 구성한다.
각 인력은 `agent.md` 파일로 정의되고, 실제 SI 회사처럼 PM이 일을 분배하고, 개발자들이 병렬로 작업하고, QA가 검수한다.

### 1.2 기존 플랫폼과의 차이

| 항목 | 기존 플랫폼 (v2) | Agent 회사 (v3) |
|------|----------------|----------------|
| 요구사항 입력 | 대화 또는 직접 입력 | **문서 업로드** (RFP, 기능명세서 등) |
| 에이전트 편성 | orchestrator가 자동 결정 | **PM이 WBS 기반으로 인력 배정** |
| 인력 정의 | 역할 중심 | **기술 스킬 명시 (skills 섹션)** |
| 파일 충돌 방지 | 소유권 선언 | **workspace-map.json으로 명시적 격리** |
| 적용 방식 | 독립 플랫폼 | **현재 Git 프로젝트에 직접 통합** |

### 1.3 핵심 가치

- **문서 → 코드**: 고객이 주는 문서를 그대로 올리면 POC 코드가 나온다
- **역할 분리**: 각 에이전트는 자신의 도메인 파일만 손댄다
- **투명한 계획**: PM이 WBS + workspace-map을 먼저 만든 뒤 개발 시작
- **반복 가능**: 문서만 바꾸면 다른 프로젝트에 같은 팀을 재투입할 수 있다

---

## 2. 회사 조직 구조

### 2.1 전체 조직도

```
문서 업로드
    │
    ▼
[document-parser]          ← 전처리 (어떤 형식이든 JSON으로)
    │
    ▼
[project-manager (PM)]     ← 경영진: WBS 작성, 인력 배정, 소유권 맵 생성
    │
    ├──[system-analyst]    ← 중간관리: 요건 정제, API 명세
    ├──[solution-architect]← 중간관리: 기술 스택, 아키텍처
    ├──[tech-lead]         ← 중간관리: 개발 방향, 코드 표준, 머지 담당
    └──[qa-lead]           ← 중간관리: 테스트 계획, 품질 기준
              │
              ├──[backend-developer]    ← 개발인력: Python/Java/Node/C++
              ├──[frontend-developer]   ← 개발인력: React/Vue/Next.js
              ├──[database-engineer]    ← 개발인력: PostgreSQL/MySQL/Redis
              ├──[devops-engineer]      ← 인프라: Docker/K8s/CI-CD
              └──[security-engineer]   ← 보안: OWASP 감사
```

### 2.2 agent.md 인력 정의 형식

모든 인력은 아래 frontmatter 표준을 따른다.

```yaml
---
name: backend-developer
role: senior-engineer
department: development
skills:
  languages: [Python, Java, TypeScript, C, C++]
  frameworks: [FastAPI, Spring Boot, Express, NestJS, Django]
  databases: [PostgreSQL, MySQL, MongoDB, Redis]
  tools: [Docker, Git, pytest, JUnit, Swagger]
domain_expertise: [fintech, public, b2b, b2c]
seniority: senior          # junior / mid / senior / lead
available_for:
  - backend-api
  - batch-processing
  - performance-tuning
tools_allowed: [Read, Write, Edit, Bash, Glob, Grep]
model: claude-sonnet-4-6   # 역할별 모델 최적화
---

시스템 프롬프트 본문...
```

#### PM이 인력을 배정하는 매칭 규칙

| 태스크 유형 | 배정 에이전트 | 권장 모델 |
|------------|------------|----------|
| REST API, 비즈니스 로직 | backend-developer | Sonnet |
| UI 컴포넌트, 라우팅, 상태 관리 | frontend-developer | Sonnet |
| DB 스키마, 마이그레이션 | database-engineer | Sonnet |
| Docker, CI/CD, K8s | devops-engineer | Sonnet |
| OWASP 보안 감사 | security-engineer | Opus |
| 테스트 코드 생성 | qa-lead | Haiku |
| 아키텍처 설계 | solution-architect | Opus |
| 요건 분석, API 명세 | system-analyst | Sonnet |
| 전체 조율, WBS | project-manager | Opus |

---

## 3. 전체 파이프라인

### 3.1 7단계 파이프라인

```
Stage 1 │ 문서 업로드
        │ RFP · 기능명세서 · 사용자스토리 · ERD · 화면설계서
        ▼
Stage 2 │ 문서 파싱 · 정규화                    [document-parser]
        │ 섹션 분리 → 의미 분류 → parsed-spec.json 생성
        ▼
Stage 3 │ PM 검토 · 작업 분해                   [project-manager]
        │ WBS 작성 → 인력 배정 → project-plan.md + workspace-map.json
        ▼
Stage 4 │ 분석 · 설계                           [system-analyst, solution-architect]
        │ 요건 정제 → API 명세 → 아키텍처 → DB 스키마
        ▼
Stage 5 │ 병렬 개발 (핵심)                      [tech-lead 조율]
        │ backend / frontend / database / devops 동시 진행
        │ workspace-map.json 기반 파일 소유권 격리
        ▼
Stage 6 │ 보안 검토 · QA                        [security-engineer, qa-lead]
        │ OWASP 감사 → 테스트 실행 → 품질 게이트 판정
        ▼
Stage 7 │ 패키징 · 납품                         [devops-engineer, PM]
        │ .claude/ 제외 ZIP → Git push → docker-compose up -d
```

### 3.2 피드백 루프

Stage 6 QA 게이트에서 피드백 발생 시, PM이 어느 단계부터 재시작할지 결정한다.

| 피드백 유형 | 재시작 지점 |
|-----------|-----------|
| 기능 누락 | Stage 3 (WBS 재작성) |
| API 명세 오류 | Stage 4 (분석·설계) |
| 특정 모듈 버그 | Stage 5 (해당 에이전트만) |
| 보안 취약점 | Stage 5~6 |

---

## 4. 문서 파싱 전략

### 4.1 파서 동작 5단계

```
① 형식 감지    파일 확장자 + 내용으로 문서 유형 판별
               (PDF, Word, Excel, Markdown, Image, 자연어 텍스트)

② 섹션 분리    기능 요구사항 / 비기능 요구사항 / 화면 목록 / 데이터 모델

③ 의미 분류    각 항목을 아래 태그로 분류
               feature / constraint / persona / integration / nfr

④ 누락 감지    기술 스택 미지정 / 우선순위 없음 / 비기능 요구사항 없음
               → clarifications_needed 목록 생성 → 사용자에게 질의

⑤ JSON 변환   parsed-spec.json (표준 출력) 생성
```

### 4.2 parsed-spec.json 스키마 (회사의 공통 언어)

```json
{
  "project_meta": {
    "name": "프로젝트명",
    "domain": "fintech | public | b2b | b2c | manufacturing",
    "type": "new_build | enhancement | refactoring | poc",
    "quality_level": "prototype | standard | enterprise",
    "deadline": "YYYY-MM-DD"
  },
  "features": [
    {
      "id": "F-001",
      "name": "사용자 인증",
      "description": "JWT 기반 로그인/로그아웃",
      "priority": "must | should | nice",
      "user_story": "As a ... I want to ... so that ...",
      "acceptance_criteria": ["조건1", "조건2"],
      "depends_on": [],
      "estimated_complexity": "low | medium | high"
    }
  ],
  "tech": {
    "preferred_stack": {
      "backend": "FastAPI",
      "frontend": "React",
      "database": "PostgreSQL"
    },
    "constraints": ["Java 11 이상", "기존 Oracle DB 연동"],
    "integrations": ["카카오 로그인", "기존 ERP 시스템"]
  },
  "nfr": {
    "performance": "동시 접속 500명, 응답 3초 이내",
    "security": "OWASP Top 10 준수, 금융보안원 가이드",
    "availability": "99.9% 가용성",
    "compliance": ["개인정보보호법", "전자금융거래법"]
  },
  "clarifications_needed": [
    "기술 스택이 지정되지 않았습니다. 권장: FastAPI + React",
    "성능 목표가 명시되지 않았습니다"
  ]
}
```

### 4.3 설계 원칙

- `clarifications_needed`가 있으면 **파일 저장 후 반드시 사용자에게 목록 제시** (추측으로 채우지 않는다)
- 모든 하위 인력(PM, 개발자, 보안 등)은 이 파일을 읽어 작업 기반으로 삼는다
- 문서 형식이 바뀌어도 이 파일의 스키마는 변하지 않는다 (파서만 교체)

---

## 5. PM 작업 분해 포맷

### 5.1 project-plan.md 구조

PM이 parsed-spec.json을 읽고 생성하는 첫 번째 산출물.

```yaml
# project-plan.md

project_id: "uuid-자동생성"
project_name: "사용자 관리 시스템"
source_spec: ".claude/output/parsed-spec.json"
created_at: "YYYY-MM-DD"

pipeline:
  stages:
    - stage: 1
      name: "분석·설계"
      sequential: true           # 이 스테이지는 순차 실행
      tasks:
        - id: T-000
          name: "요건 정제 및 API 명세 작성"
          agent: system-analyst
          output_files:
            - "docs/requirements.md"
            - "docs/api-spec.md"
          est_hours: 2
          acceptance_criteria:
            - "모든 기능에 API 엔드포인트 매핑 완료"

        - id: T-001
          name: "아키텍처 설계 및 기술 스택 확정"
          agent: solution-architect
          depends_on: [T-000]
          output_files:
            - "docs/architecture.md"
            - "docs/tech-decision.md"
          est_hours: 2

    - stage: 2
      name: "병렬 개발"
      sequential: false          # 이 스테이지는 병렬 실행
      tasks:
        - id: T-002
          name: "백엔드 API 구현"
          agent: backend-developer
          depends_on: [T-001]
          parallel_with: [T-003, T-004]
          output_files: ["src/api/**", "src/service/**"]
          est_hours: 8
          acceptance_criteria:
            - "docs/api-spec.md 모든 엔드포인트 구현"
            - "GET /health 200 응답"

        - id: T-003
          name: "프론트엔드 UI 구현"
          agent: frontend-developer
          depends_on: [T-001]
          parallel_with: [T-002, T-004]
          output_files: ["src/components/**", "src/pages/**"]
          est_hours: 8

        - id: T-004
          name: "DB 스키마 및 마이그레이션"
          agent: database-engineer
          depends_on: [T-001]
          parallel_with: [T-002, T-003]
          output_files: ["migrations/**", "src/db/**"]
          est_hours: 3

    - stage: 3
      name: "인프라·보안·QA"
      sequential: false
      tasks:
        - id: T-005
          name: "Docker 및 CI/CD 구성"
          agent: devops-engineer
          depends_on: [T-002, T-003, T-004]
          output_files: ["Dockerfile", "docker-compose.yml", ".github/**"]
          est_hours: 3

        - id: T-006
          name: "OWASP 보안 감사"
          agent: security-engineer
          depends_on: [T-002, T-003]
          output_files: ["docs/security-report.md"]
          est_hours: 2

        - id: T-007
          name: "테스트 코드 생성"
          agent: qa-lead
          depends_on: [T-002, T-003]
          output_files: ["tests/**"]
          est_hours: 4
```

### 5.2 PM의 에이전트 선발 원칙

1. `parsed-spec.json`의 `domain` 필드 확인 → 해당 도메인 전문 에이전트 우선 배정
2. 태스크 유형별 skills 매칭 (languages, frameworks 일치 여부)
3. 병렬 가능 태스크 식별: `depends_on`이 같은 선행 태스크이면 병렬 처리
4. `quality_level`이 enterprise면 보안·QA 에이전트 필수 포함
5. POC면 devops, security 생략 가능 (빠른 납품 우선)

---

## 6. workspace-map 설계

### 6.1 필요성

병렬 개발(Stage 5)에서 여러 에이전트가 동시에 파일을 쓰면 충돌이 발생한다.
`workspace-map.json`은 **"누가 어느 경로를 소유하는가"** 를 사전에 명시하여 이를 완전히 차단한다.

### 6.2 workspace-map.json 전체 구조

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
        "src/core/**",
        "requirements.txt",
        "pom.xml"
      ],
      "reads": [
        "docs/**",
        "src/db/**"
      ],
      "forbidden": [
        "src/components/**",
        "src/pages/**",
        "src/hooks/**",
        "migrations/**",
        ".claude/**"
      ]
    },

    "frontend-developer": {
      "owns": [
        "src/components/**",
        "src/pages/**",
        "src/hooks/**",
        "src/store/**",
        "src/types/**",
        "src/styles/**",
        "index.html",
        "vite.config.ts",
        "package.json"
      ],
      "reads": [
        "docs/**"
      ],
      "forbidden": [
        "src/api/**",
        "src/service/**",
        "src/domain/**",
        "migrations/**",
        ".claude/**"
      ]
    },

    "database-engineer": {
      "owns": [
        "migrations/**",
        "src/db/**",
        "scripts/seed.sql",
        "scripts/schema.sql"
      ],
      "reads": [
        "docs/**"
      ],
      "forbidden": [
        "src/api/**",
        "src/components/**",
        ".claude/**"
      ]
    },

    "devops-engineer": {
      "owns": [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.dev.yml",
        ".github/**",
        "k8s/**",
        "Makefile",
        "nginx.conf",
        "scripts/deploy.sh"
      ],
      "reads": [
        "docs/**",
        "src/**",
        "requirements.txt",
        "pom.xml",
        "package.json"
      ],
      "forbidden": [
        "src/api/**",
        "src/components/**",
        "migrations/**",
        ".claude/**"
      ]
    },

    "security-engineer": {
      "owns": [
        "docs/security-report.md"
      ],
      "reads": [
        "src/**",
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt"
      ],
      "forbidden": [
        "src/**가 아닌 수정 일체",
        ".claude/**"
      ]
    },

    "qa-lead": {
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
        "src/**",
        "migrations/**",
        ".claude/**"
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
    "src/App.tsx",
    "src/core/config.py"
  ]
}
```

### 6.3 tech-lead의 역할

`tech-lead`가 `workspace-map.json`을 먼저 배포한 뒤 개발을 시작한다.

```
tech-lead 작업 순서:
1. workspace-map.json 전체 에이전트에게 브로드캐스트
2. 각 에이전트에게 "owns 경로만 수정하라" 명시
3. tech_lead_merge_targets 파일은 tech-lead가 단독 관리
4. 병렬 개발 완료 후 Git 브랜치 머지 담당
5. 충돌 발생 시 conflict_resolution: "tech-lead-decides" 규칙 적용
```

---

## 7. Claude CLI 적용 방법

### 7.1 현재 Git 프로젝트에 Agent 회사 구조 추가

```bash
# Git 프로젝트 루트에서 실행
mkdir -p .claude/agents .claude/skills .claude/commands .claude/output
touch CLAUDE.md

# .gitignore에 출력물 디렉터리 추가
echo ".claude/output/" >> .gitignore
echo "/workspace/" >> .gitignore
```

### 7.2 CLAUDE.md — 자동 로드되는 회사 컨텍스트

Claude CLI는 프로젝트를 열 때 `CLAUDE.md`를 자동으로 읽는다.
여기에 회사 규칙을 한 번만 쓰면 모든 에이전트가 동일한 컨텍스트로 시작한다.

```markdown
# [회사명] 개발 Agent 회사 — 프로젝트 컨텍스트

## 회사 운영 규칙
- 모든 인력은 .claude/agents/{역할}.md 로 정의됩니다
- 파이프라인: 문서 업로드 → document-parser → project-manager → 개발팀
- 모든 개발 작업은 /workspace/{project_id}/ 안에서만 수행합니다
- workspace-map.json 에 정의된 소유권 범위를 절대 침범하지 않습니다
- .claude/agents/ 디렉터리는 ZIP 패키징 시 절대 포함하지 않습니다

## 핵심 파일 위치
- 파싱 결과: .claude/output/parsed-spec.json
- 프로젝트 계획: .claude/output/project-plan.md
- 소유권 맵: .claude/output/workspace-map.json
```

### 7.3 핵심 파이프라인 커맨드

```bash
# .claude/commands/start-project.md
```

```markdown
# /start-project — 문서 업로드 후 파이프라인 시작

사용법: /start-project [문서 경로]

예시:
  /start-project ./docs/rfp.pdf
  /start-project ./docs/requirements.xlsx
  /start-project ./docs/기능명세서.md

실행 흐름:
  1. document-parser → .claude/output/parsed-spec.json
  2. clarifications_needed 있으면 사용자 확인
  3. project-manager → project-plan.md + workspace-map.json
  4. 요약 제시 → OK 시 tech-lead 실행
  5. 병렬 개발 시작 → 보안/QA → 패키징
```

### 7.4 Claude CLI에서 실행하는 방법

```bash
# 1. 프로젝트 루트에서 Claude Code CLI 실행
claude

# 2. 문서 경로를 주고 파이프라인 시작
/start-project ./docs/requirements.md

# 또는 에이전트를 직접 호출
document-parser 에이전트로 ./docs/rfp.pdf 를 파싱해서
.claude/output/parsed-spec.json 을 생성해줘

# 3. 파싱 완료 후 PM 실행
project-manager 에이전트로 parsed-spec.json 읽고
project-plan.md 와 workspace-map.json 생성해줘

# 4. 개발 시작
tech-lead 에이전트로 workspace-map.json 배포하고
백엔드/프론트엔드/DB 병렬 개발 시작해줘
```

---

## 8. 디렉터리 구조 및 Git 연동 전략

### 8.1 전체 디렉터리 구조

```
your-git-project/                     ← 현재 진행 중인 Git 프로젝트
│
├── CLAUDE.md                         ← Claude CLI 자동 로드 (회사 컨텍스트)
│
├── .claude/                          ← 회사 자산 (git 커밋 O)
│   ├── agents/
│   │   ├── document-parser.md        ← 전처리 전문가
│   │   ├── project-manager.md        ← PM (WBS + workspace-map)
│   │   ├── system-analyst.md         ← 요건 분석
│   │   ├── solution-architect.md     ← 기술 설계
│   │   ├── tech-lead.md              ← 개발 조율 + 머지
│   │   ├── backend-developer.md      ← 백엔드 (다언어)
│   │   ├── frontend-developer.md     ← 프론트엔드
│   │   ├── database-engineer.md      ← DB 설계
│   │   ├── devops-engineer.md        ← 인프라 구성
│   │   ├── security-engineer.md      ← 보안 감사
│   │   └── qa-lead.md                ← 테스트 생성
│   │
│   ├── commands/
│   │   ├── start-project.md          ← /start-project 진입점
│   │   ├── status.md                 ← /status 현재 진행 상황
│   │   └── review.md                 ← /review 코드 리뷰 요청
│   │
│   ├── skills/                       ← 프레임워크 보일러플레이트
│   │   ├── fastapi-skill.md
│   │   ├── spring-boot-skill.md
│   │   ├── react-vite-skill.md
│   │   └── docker-skill.md
│   │
│   └── output/                       ← .gitignore 처리 (실행 산출물)
│       ├── parsed-spec.json
│       ├── project-plan.md
│       └── workspace-map.json
│
└── workspace/                        ← .gitignore 처리 (생성된 프로젝트 코드)
    └── {project_id}/
        ├── src/
        ├── tests/
        ├── migrations/
        ├── docs/
        ├── Dockerfile
        ├── docker-compose.yml
        ├── .env.example
        └── README.md
```

### 8.2 Git 전략

```bash
# 회사 자산 (에이전트 정의) → 커밋 O
git add .claude/agents/ .claude/commands/ .claude/skills/ CLAUDE.md
git commit -m "feat: add agent company structure"

# 출력물과 workspace → .gitignore (실행마다 달라짐)
echo ".claude/output/" >> .gitignore
echo "/workspace/" >> .gitignore

# 생성된 프로젝트 코드 → 별도 Git 레포
cd workspace/{project_id}
git init
git remote add origin https://github.com/...
git push -u origin main
```

### 8.3 .gitignore 설정

```gitignore
# Agent 회사 실행 산출물 (프로젝트마다 달라지므로 제외)
.claude/output/
/workspace/

# 환경 변수
.env
*.env.local

# 에이전트 정의는 회사 자산이므로 커밋 포함
# .claude/agents/ → 커밋 O
# .claude/commands/ → 커밋 O
# .claude/skills/ → 커밋 O
```

---

## 9. 개발 로드맵

### Phase 1 — 최소 파이프라인 구동 (1~2주)

| 작업 | 내용 | 우선순위 |
|------|------|---------|
| `document-parser.md` 완성 | Markdown 입력 → parsed-spec.json | 최우선 |
| `project-manager.md` 완성 | WBS + workspace-map 생성 | 최우선 |
| `workspace-map.json` 포맷 확정 | 소유권 경로 규칙 정의 | 최우선 |
| 핵심 4인방 md 작성 | backend/frontend/database/devops | 필수 |
| `/start-project` 커맨드 등록 | 진입점 단일화 | 필수 |

**Phase 1 완료 기준**: Markdown 문서 하나를 올리면 docker-compose up -d 로 돌아가는 코드가 나온다

### Phase 2 — 다형식 문서 지원 + 인력 고도화 (2~4주)

| 작업 | 내용 |
|------|------|
| PDF, Excel 파싱 지원 | document-parser 확장 |
| `tech-lead.md` 완성 | 병렬 개발 조율 + Git 머지 |
| `security-engineer.md` 완성 | OWASP 자동 감사 |
| `qa-lead.md` 완성 | 커버리지 기반 테스트 생성 |
| 도메인별 에이전트 특화 | 금융/공공/B2B별 보안·규정 반영 |

### Phase 3 — 관리 플랫폼 + 재사용 생태계 (4~8주)

| 작업 | 내용 |
|------|------|
| 에이전트 라이브러리 웹 UI | 인력 CRUD + 스킬 관리 |
| 프로젝트 히스토리 관리 | 과거 납품 이력 + 재투입 |
| MCP 연동 | GitHub, Jira, Slack |
| 멀티 프로젝트 동시 운영 | 여러 고객사 프로젝트 병렬 관리 |
| 에이전트 마켓플레이스 | 검증된 인력 패키지 공유 |

---

## 10. 핵심 설계 원칙

### 10.1 세 가지 핵심 원칙

**원칙 1 — parsed-spec.json이 회사의 공통 언어다**

어떤 형식의 문서가 들어오든 반드시 이 파일로 수렴한다.
PM, 개발자, 보안 엔지니어 모두 이 파일만 읽고 작업한다.
파싱 품질이 전체 파이프라인 결과를 결정한다.

**원칙 2 — workspace-map.json이 없으면 병렬 개발을 시작하지 않는다**

tech-lead가 이 파일을 먼저 배포한 뒤에만 개발 에이전트들이 시작한다.
"owns" 경로 밖의 파일은 절대 수정하지 않는다.
충돌이 발생하면 tech-lead가 단독으로 해결한다.

**원칙 3 — .claude/agents/는 회사 자산이다**

에이전트 정의 파일은 git에 커밋하고 팀이 공유한다.
생성된 프로젝트 코드(.claude/output/, workspace/)는 gitignore 처리한다.
ZIP 납품 시 .claude/ 디렉터리는 절대 포함하지 않는다.

### 10.2 현재 당장 할 일 (우선순위 순서)

```
1. document-parser.md 작성     ← 파이프라인 입력 안정화
2. project-manager.md 작성     ← WBS + workspace-map 포맷 확정
3. workspace-map.json 포맷 확정← 병렬 개발 충돌 방지
4. backend-developer.md 작성   ← POC 최소 팀 구성
5. frontend-developer.md 작성
6. database-engineer.md 작성
7. devops-engineer.md 작성
8. /start-project 커맨드 등록  ← 데모 가능한 진입점
```

Phase 1만 완성해도 **"문서 하나 올리면 POC 코드가 나오는 데모"** 가 가능하다.

---

*나만의 개발 Agent 회사 기획서 v1.0 | Claude Code CLI 기반 | 2025*
