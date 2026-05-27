# Agent Development Company

> **"나만의 개발 Agent 회사를 만들자"**
>
> AI Agent 팀이 요구사항 문서를 받아 자동으로 POC 가능한 프로젝트를 생성합니다.

---

## 프로젝트 개요

이 프로젝트는 **SI 개발 회사를 AI Agent로 구현**한 시스템입니다.
사용자가 요구사항 문서(PDF, Word, Markdown 등)를 업로드하면, 전문화된 Agent 팀이 자동으로:

1. 📄 문서 파싱 및 요구사항 추출
2. 📋 프로젝트 계획 수립 (WBS)
3. 🏗️ 아키텍처 설계
4. 💻 Backend/Frontend 개발
5. 🔒 보안 감사
6. ✅ 테스트 및 배포 준비
7. 📚 문서 작성

---

## 디렉토리 구조

```
ClaudeAgent/
├── CLAUDE.md                        # Claude Code 자동 로드 (회사 컨텍스트)
├── spec.md                          # Agent 관리 플랫폼 명세서
│
├── .claude/                         # Agent 회사 자산 (git 커밋 O)
│   ├── agents/                      # Agent 역할 정의 (16개)
│   │   ├── controller.md                # AI Tech Lead (파이프라인 오케스트레이터)
│   │   ├── requirement-analyst.md       # 요구사항 분석
│   │   ├── architect.md                 # 아키텍처 설계
│   │   ├── planner.md                   # 기능 명세 작성
│   │   ├── dba.md                       # DB 설계
│   │   ├── backend.md                   # Backend 개발
│   │   ├── frontend.md                  # Frontend 개발
│   │   ├── tester.md                    # 테스트
│   │   ├── devops.md                    # 인프라 구성
│   │   ├── tech-writer.md               # 문서 작성
│   │   ├── reviewer.md                  # 최종 검증
│   │   ├── document-parser.md           # 문서 파싱 전문가
│   │   ├── project-manager.md           # PM (WBS + workspace-map)
│   │   ├── system-analyst.md            # 요건 분석
│   │   ├── tech-lead.md                 # 병렬 개발 조율
│   │   └── security-engineer.md         # 보안 감사
│   │
│   ├── commands/                    # 커맨드
│   │   └── start-project.md             # /start-project 진입점
│   │
│   ├── skills/                      # 스킬 (전문 역할 실행 단위)
│   │   ├── project-orchestrator/        # 전체 파이프라인 오케스트레이션
│   │   ├── project-planning/            # WBS + workspace-map 생성
│   │   ├── backend-development/         # FastAPI 백엔드 개발
│   │   ├── frontend-development/        # React 프론트엔드 개발
│   │   ├── database-design/             # DB 스키마 설계
│   │   ├── devops/                      # Docker/CI-CD 구성
│   │   ├── security-audit/              # 보안 감사
│   │   ├── qa-testing/                  # 테스트
│   │   └── tech-integration/            # 기술 통합
│   │
│   └── output/                      # 실행 산출물 (.gitignore)
│       ├── parsed-spec.json             # 파싱 결과
│       ├── project-plan.md              # WBS
│       └── workspace-map.json           # 파일 소유권 맵
│
├── projects/                        # 프로젝트 모음
│   ├── starter-project/             # 레퍼런스 구현체 (Python FastAPI + React)
│   │   ├── python/                      # FastAPI 백엔드 (port 3003)
│   │   ├── web/                         # React 프론트엔드 (port 5173)
│   │   ├── server/                      # Proxy 서버 (port 3456)
│   │   └── workspace/                   # 생성된 프로젝트 작업 공간
│   │
│   └── harness/                     # Agent 하네스 (실행 프레임워크)
│
├── examples/                        # 예제 프로젝트
│   └── sample-todo/                     # 할일 앱 예제
│
├── docs/                            # 문서
├── resource/                        # 리소스 파일
└── workspace/                       # 생성된 프로젝트 (.gitignore)
    └── {project_id}/                    # 프로젝트별 격리된 작업 공간
```

---

## 빠른 시작

### 방법 1: 스킬 명령어 사용 (권장)

```
/start-project ./docs/requirements.md
```

Claude Code 대화창에서 요구사항 문서 경로를 전달하면 전체 파이프라인이 자동 실행됩니다.

### 방법 2: 팀 직접 활성화

`agent-company` 팀을 사용하면 11개 Agent가 병렬로 협업합니다:

```
요구사항을 controller에게 전달 → 전체 파이프라인 자동 실행
```

### 방법 3: 스타터 프로젝트 직접 실행

```bash
# Backend (FastAPI, port 3003)
cd projects/starter-project/python
pip install -r requirements.txt
python -m src.main

# Frontend (React, port 5173)
cd projects/starter-project/web
npm install
npm run dev

# Proxy 서버 (port 3456, POC 코드 생성용)
cd projects/starter-project/server
npm install
npm start
```

---

## Agent 파이프라인

### 실행 순서

```
요구사항 문서
    ↓
[1] requirement-analyst  → requirements.md  (10%)
    ↓
[2] architect            → architecture.md  (20%)
    ↓
[3] planner              → spec.md          (30%)
    ↓
[4] dba                  → schema.sql       (40%)
    ↓
[5] backend              → /app/backend/*   (55%)
    ↓
[6] frontend             → /app/frontend/*  (70%)
    ↓
[7] tester               → /tests/*         (80%)
    ↓
[8] devops               → Dockerfile 등    (90%)
    ↓
[9] tech-writer          → 문서 일체        (95%)
    ↓
[10] reviewer            → 최종 검증        (100%)
```

### Controller 오케스트레이션

`controller`는 위 10단계를 자동으로 관리합니다:
- 각 단계 완료 후 산출물 검증
- 문제 발생 시 해당 Agent에게 수정 요청 (최대 3회)
- 실시간 진행률 보고

---

## Agent 팀 구성 (`agent-company`)

| Agent | 역할 | 산출물 |
|-------|------|--------|
| `controller` | AI Tech Lead - 전체 오케스트레이션 | 실시간 진행 보고 |
| `requirement-analyst` | 요구사항 분석 | requirements.md |
| `architect` | 시스템 아키텍처 설계 | architecture.md |
| `planner` | 기능 명세 작성 | spec.md |
| `dba` | DB 스키마 설계 | schema.sql |
| `backend` | REST API 구현 | /app/backend/* |
| `frontend` | React UI 구현 | /app/frontend/* |
| `tester` | 테스트 코드 작성 | /tests/* |
| `devops` | 배포 환경 구성 | Dockerfile, docker-compose.yml |
| `tech-writer` | 기술 문서 작성 | README.md, API.md 등 |
| `reviewer` | 계층 간 일관성 검증 | 검증 리포트 |

---

## 스타터 프로젝트 아키텍처

```
Frontend (React + Vite, port 5173)
    ↓
Backend (FastAPI + Python, port 3003)
    ↓
Multiple LLM Providers
    ├── Claude (Anthropic API)
    ├── OpenAI (Codex)
    ├── Ollama (Local LLM)
    └── Manus AI
```

### 주요 API 엔드포인트

| 경로 | 설명 |
|------|------|
| `GET /api/health` | 헬스 체크 |
| `POST /api/chat` | 멀티 프로바이더 채팅 |
| `POST /api/connection-test` | LLM 연결 테스트 |
| `GET /api/agents` | 에이전트 목록 조회 |
| `POST /v1/chat/completions` | OpenAI 호환 엔드포인트 |

---

## 핵심 설계 원칙

### 1. parsed-spec.json이 공통 언어
- 모든 Agent는 이 파일을 읽고 작업
- 문서 형식이 바뀌어도 스키마는 동일

### 2. workspace-map.json으로 충돌 방지
- 각 Agent는 자신의 `owns` 경로만 수정
- 병렬 개발 시 파일 충돌 완전 차단

### 3. .claude/agents/는 회사 자산
- Agent 정의는 Git 커밋 (팀 공유)
- 생성된 프로젝트 코드는 .gitignore (별도 관리)

---

## 주요 파일

| 파일 | 설명 |
|------|------|
| `CLAUDE.md` | Claude Code 자동 로드 - 회사 운영 규칙 |
| `spec.md` | Agent 관리 플랫폼 명세 |
| `.claude/agents/*.md` | Agent 역할 정의 (16개) |
| `.claude/commands/start-project.md` | `/start-project` 커맨드 |
| `.claude/output/parsed-spec.json` | 표준 요구사항 포맷 |
| `.claude/output/project-plan.md` | WBS 작업 분해 |
| `.claude/output/workspace-map.json` | 파일 소유권 맵 |

---

## Git 전략

### 커밋 포함 (회사 자산)
```bash
git add .claude/agents/
git add .claude/commands/
git add .claude/skills/
git add CLAUDE.md
git add projects/starter-project/
```

### .gitignore (실행 산출물)
```bash
.claude/output/         # 프로젝트마다 다름
workspace/              # 생성된 코드
projects/*/workspace/   # 프로젝트별 작업 공간
```

### 생성된 프로젝트는 별도 관리
```bash
cd workspace/{project_id}
git init
git remote add origin https://github.com/...
git push -u origin main
```

---

## 개발 로드맵

### Phase 1 - 최소 파이프라인 구동 ✅
- [x] 핵심 Agent 정의 (16개)
- [x] `/start-project` 커맨드 등록
- [x] 스타터 프로젝트 (FastAPI + React)
- [x] 멀티 LLM 지원 (Claude, OpenAI, Ollama, Manus)
- [x] `agent-company` 팀 구성 (11 Agent)

### Phase 2 - 고도화 (진행 중)
- [ ] PDF, Excel 파싱 지원
- [ ] tech-lead 병렬 개발 조율 고도화
- [ ] security-engineer 고도화
- [ ] Agent 하네스 연동

### Phase 3 - 관리 플랫폼 (예정)
- [ ] Agent 관리 웹 UI
- [ ] 프로젝트 히스토리 관리
- [ ] MCP 연동 (GitHub, Jira, Slack)
- [ ] Agent 마켓플레이스

---

## 참고 자료

- [CLAUDE.md](./CLAUDE.md) - 회사 운영 규칙 및 개발 가이드
- [spec.md](./spec.md) - Agent 관리 플랫폼 명세
- [projects/starter-project/README.md](./projects/starter-project/README.md) - 스타터 프로젝트 가이드
- [resource/](./resource/) - 기획 문서 및 리소스

---

## 라이선스

MIT License

---

**Agent Development Company v2.0 | Claude Code CLI 기반 | 2026**
