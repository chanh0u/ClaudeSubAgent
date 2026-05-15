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
├── CLAUDE.md                    # Claude Code 자동 로드 (회사 컨텍스트)
├── spec.md                      # Agent 관리 플랫폼 명세서
│
├── .claude/                     # Agent 회사 자산 (git 커밋 O)
│   ├── agents/                  # Agent 역할 정의
│   │   ├── document-parser.md       # 문서 파싱 전문가
│   │   ├── project-manager.md       # PM (WBS + workspace-map)
│   │   ├── system-analyst.md        # 요건 분석
│   │   ├── solution-architect.md    # 아키텍처 설계 (architect.md)
│   │   ├── tech-lead.md             # 병렬 개발 조율
│   │   ├── backend-developer.md     # Backend 개발 (backend.md)
│   │   ├── frontend-developer.md    # Frontend 개발 (frontend.md)
│   │   ├── database-engineer.md     # DB 설계 (dba.md)
│   │   ├── devops-engineer.md       # 인프라 구성 (devops.md)
│   │   ├── security-engineer.md     # 보안 감사
│   │   ├── qa-lead.md               # 테스트 (tester.md)
│   │   ├── tech-writer.md           # 문서 작성
│   │   ├── reviewer.md              # 최종 검증
│   │   └── controller.md            # 전체 조율
│   │
│   ├── commands/                # 커맨드
│   │   └── start-project.md         # /start-project 진입점
│   │
│   ├── skills/                  # 프레임워크 보일러플레이트 (예정)
│   └── output/                  # 실행 산출물 (.gitignore)
│       ├── parsed-spec.json         # 파싱 결과
│       ├── project-plan.md          # WBS
│       └── workspace-map.json       # 파일 소유권 맵
│
├── workspace/                   # 생성된 프로젝트 (.gitignore)
│   └── {project_id}/                # 프로젝트별 격리된 작업 공간
│       ├── src/
│       ├── tests/
│       ├── migrations/
│       ├── docs/
│       ├── Dockerfile
│       └── docker-compose.yml
│
└── app/                         # Agent 관리 플랫폼 (개발 예정)
    ├── backend/                     # Node.js + Express
    └── frontend/                    # React
```

---

## 빠른 시작

### 1. 요구사항 문서 준비

```bash
# 지원 형식: PDF, DOCX, XLSX, MD, TXT
docs/requirements.md
docs/rfp.pdf
docs/기능명세서.docx
```

### 2. Claude Code CLI 실행

```bash
claude
```

### 3. 프로젝트 시작

```bash
/start-project ./docs/requirements.md
```

---

## 실행 흐름

### Stage 1: 문서 파싱
```
document-parser → parsed-spec.json 생성
→ clarifications_needed 확인 (누락된 정보 질문)
```

### Stage 2: 프로젝트 계획
```
project-manager → project-plan.md + workspace-map.json 생성
→ 사용자 확인
```

### Stage 3: 분석·설계
```
system-analyst → 요건 정제 + API 명세
solution-architect → 아키텍처 설계
```

### Stage 4: 병렬 개발
```
tech-lead 조율:
├─ backend-developer (API 구현)
├─ frontend-developer (UI 구현)
└─ database-engineer (DB 스키마)
```

### Stage 5: 인프라·보안·QA
```
├─ devops-engineer (Docker, CI/CD)
├─ security-engineer (OWASP 감사)
└─ qa-lead (테스트 코드)
```

### Stage 6: 문서화 및 검증
```
tech-writer → 문서 작성
reviewer → 최종 검증
```

---

## 핵심 설계 원칙

### 1. parsed-spec.json이 회사의 공통 언어
- 모든 Agent는 이 파일을 읽고 작업
- 문서 형식이 바뀌어도 스키마는 동일

### 2. workspace-map.json으로 충돌 방지
- 각 Agent는 자신의 "owns" 경로만 수정
- 병렬 개발 시 파일 충돌 완전 차단

### 3. .claude/agents/는 회사 자산
- Agent 정의는 Git 커밋 (팀 공유)
- 생성된 프로젝트 코드는 .gitignore (별도 관리)

---

## Agent 팀 구성

| Agent | 역할 | 모델 | 산출물 |
|-------|------|------|--------|
| document-parser | 문서 파싱 | Sonnet | parsed-spec.json |
| project-manager | WBS 작성 | Opus | project-plan.md, workspace-map.json |
| system-analyst | 요건 분석 | Sonnet | requirements.md, api-spec.md |
| solution-architect | 아키텍처 | Opus | architecture.md |
| tech-lead | 병렬 조율 | Sonnet | (조율만) |
| backend-developer | API 구현 | Sonnet | src/api/**, src/service/** |
| frontend-developer | UI 구현 | Sonnet | src/components/**, src/pages/** |
| database-engineer | DB 설계 | Sonnet | migrations/**, src/db/** |
| devops-engineer | 인프라 | Sonnet | Dockerfile, docker-compose.yml |
| security-engineer | 보안 감사 | Opus | security-report.md |
| qa-lead | 테스트 | Haiku | tests/** |
| tech-writer | 문서화 | Sonnet | README.md, API.md |
| reviewer | 최종 검증 | Opus | 검증 리포트 |

---

## 주요 파일

### 핵심 산출물
- `.claude/output/parsed-spec.json` - 표준 요구사항 포맷
- `.claude/output/project-plan.md` - WBS 작업 분해
- `.claude/output/workspace-map.json` - 파일 소유권 맵

### 회사 규칙
- `CLAUDE.md` - Claude Code 자동 로드
- `.claude/agents/*.md` - Agent 역할 정의
- `.claude/commands/*.md` - 커맨드 정의

---

## Git 전략

### 커밋 포함 (회사 자산)
```bash
git add .claude/agents/
git add .claude/commands/
git add CLAUDE.md
git commit -m "feat: add agent company structure"
```

### .gitignore (실행 산출물)
```bash
.claude/output/     # 프로젝트마다 다름
/workspace/         # 생성된 코드
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
- [x] document-parser 완성
- [x] project-manager 완성
- [x] workspace-map.json 포맷 확정
- [x] 핵심 4인방 (backend, frontend, database, devops)
- [x] /start-project 커맨드 등록

### Phase 2 - 다형식 문서 지원 (진행 중)
- [ ] PDF, Excel 파싱 지원
- [ ] tech-lead 고도화
- [ ] security-engineer 고도화
- [ ] 도메인별 Agent 특화

### Phase 3 - 관리 플랫폼 (예정)
- [ ] Agent 관리 웹 UI
- [ ] 프로젝트 히스토리 관리
- [ ] MCP 연동 (GitHub, Jira, Slack)
- [ ] Agent 마켓플레이스

---

## 참고 자료

- [agent-company-plan.md](./resource/agent-company-plan.md) - 전체 기획서
- [spec.md](./spec.md) - Agent 관리 플랫폼 명세
- [CLAUDE.md](./CLAUDE.md) - 회사 운영 규칙

---

## 라이선스

MIT License

---

**나만의 개발 Agent 회사 v1.0 | Claude Code CLI 기반 | 2025**
