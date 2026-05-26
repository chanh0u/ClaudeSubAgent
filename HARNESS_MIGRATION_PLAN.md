# Harness 방법론 적용 계획

**프로젝트**: ClaudeAgent (AI Agent Development Company Platform)
**작성일**: 2026-05-26
**목적**: Harness의 팀 아키텍처 팩토리 방법론을 현재 프로젝트에 적용하여 에이전트 시스템 고도화

---

## 📊 현황 분석

### 현재 시스템 구조

```
ClaudeAgent/
├── .claude/
│   ├── agents/          ✅ 17개 에이전트 정의 (잘 구성됨)
│   ├── skills/          ⚠️  외부 스킬만 존재 (Pencil Pro)
│   ├── commands/        ❌ 사용하지 않음
│   └── output/          ✅ 작업 산출물 저장
├── CLAUDE.md            ⚠️  200+ 줄, 모든 규칙 포함 (경량화 필요)
└── projects/
    └── starter-project/ ✅ 참조 구현
```

### 주요 에이전트

| 에이전트 | 역할 | 현재 상태 |
|---------|------|----------|
| document-parser | 문서 분석 및 요구사항 추출 | 정의만 존재 |
| project-manager | WBS 생성, workspace-map 작성 | 정의만 존재 |
| backend-developer | FastAPI 백엔드 개발 | 정의만 존재 |
| frontend-developer | React 프론트엔드 개발 | 정의만 존재 |
| database-engineer | DB 스키마 설계 | 정의만 존재 |
| devops-engineer | Docker, CI/CD | 정의만 존재 |
| security-engineer | OWASP 보안 감사 | 정의만 존재 |
| tech-lead | 팀 조율 및 통합 | 정의만 존재 |

### 현재 워크플로우 (암묵적)

```
Phase 1: 문서 분석
    document-parser → parsed-spec.json

Phase 2: 프로젝트 계획
    project-manager → project-plan.md + workspace-map.json

Phase 3: 병렬 개발 (팬아웃/팬인)
    backend-developer  ┐
    frontend-developer ├─→ 병렬 작업
    database-engineer  ┘

Phase 4: 인프라 및 검증
    devops-engineer → security-engineer → tech-lead
```

### 문제점

1. **스킬 부재**: 에이전트가 "무엇을" 하는지만 정의, "어떻게" 하는지는 없음
2. **오케스트레이션 부재**: 워크플로우가 CLAUDE.md에 산발적으로 기술
3. **컨텍스트 비효율**: 모든 규칙이 CLAUDE.md에 집중 (Progressive Disclosure 미적용)
4. **재사용성 부족**: 스킬이 파일로 분리되지 않아 다른 프로젝트에 재사용 불가
5. **팀 vs 서브 구분 불명확**: 언제 에이전트 팀을 쓰고 언제 서브 에이전트를 쓸지 불명확

---

## 🎯 적용 목표

### 핵심 목표

1. **스킬 시스템 도입**: 각 에이전트에 전용 스킬 생성 (`.claude/skills/`)
2. **오케스트레이터 구축**: 전체 워크플로우를 조율하는 메타 스킬 생성
3. **CLAUDE.md 경량화**: 포인터 패턴 적용 (트리거 규칙 + 변경 이력만 유지)
4. **아키텍처 패턴 명시화**: Harness의 6가지 패턴 중 해당 패턴 문서화
5. **Progressive Disclosure 적용**: SKILL.md (< 500줄) + references/ 분리

### 기대 효과

- **컨텍스트 효율 +40%**: 필요한 스킬만 로딩
- **유지보수성 향상**: 역할과 방법 분리, 변경 이력 추적
- **재사용성 확보**: 스킬 단위로 다른 프로젝트에 이식 가능
- **품질 향상**: Harness 방법론 (평균 품질 +60% 입증)

---

## 📋 단계별 실행 계획

### Phase 0: 준비 및 감사 (1일)

**목표**: 현재 시스템 전수 조사 및 백업

#### Step 0-1: 백업
```bash
# 현재 상태 백업
cp -r .claude .claude.backup-20260526
cp CLAUDE.md CLAUDE.md.backup
git commit -am "Backup before Harness migration"
```

#### Step 0-2: 현황 감사
- [ ] `.claude/agents/` 전체 파일 목록 작성
- [ ] 각 에이전트의 frontmatter 메타데이터 검증
- [ ] CLAUDE.md의 규칙을 카테고리별로 분류
  - 프로젝트 전체 규칙 (CLAUDE.md에 유지)
  - 에이전트별 규칙 (스킬로 이동)
  - 워크플로우 규칙 (오케스트레이터로 이동)

#### Step 0-3: Harness 참조 자료 준비
- [ ] `projects/harness/harness/skills/harness/SKILL.md` 읽기
- [ ] `projects/harness/harness/skills/harness/references/` 전체 읽기
- [ ] 템플릿 추출 및 현재 프로젝트에 맞게 커스터마이징

---

### Phase 1: 오케스트레이터 스킬 생성 (2일)

**목표**: 전체 워크플로우를 조율하는 메타 스킬 구축

#### Step 1-1: 디렉토리 구조 생성
```bash
mkdir -p .claude/skills/project-orchestrator/references
```

#### Step 1-2: 오케스트레이터 스킬 작성
파일: `.claude/skills/project-orchestrator/SKILL.md`

**필수 섹션**:
```yaml
---
name: project-orchestrator
description: "문서 업로드부터 POC 프로젝트 생성까지 전체 워크플로우 조율. '프로젝트 생성', '문서 분석', 'POC 생성', '하네스 실행' 요청 시 사용. 다시 실행, 재실행, 부분 수정, 결과 개선 요청도 처리."
---

# Project Orchestrator — AI Agent Company 워크플로우

## Phase 0: 컨텍스트 확인
- `_workspace/` 존재 여부 확인
- 초기 실행 vs 후속 실행 vs 부분 재실행 판별

## Phase 1: 문서 분석
**실행 모드**: 서브 에이전트 (단독 작업)
- document-parser 호출
- parsed-spec.json 생성

## Phase 2: 프로젝트 계획
**실행 모드**: 서브 에이전트 (단독 작업)
- project-manager 호출
- project-plan.md + workspace-map.json 생성

## Phase 3: 병렬 개발
**실행 모드**: 에이전트 팀 (협업 필요)
- TeamCreate(team_name="dev-team", members=["backend", "frontend", "database", "devops"])
- workspace-map.json 기반 파일 소유권 관리
- TaskCreate로 작업 할당
- SendMessage로 팀원 간 실시간 조율

## Phase 4: 검증 및 통합
**실행 모드**: 서브 에이전트 → 에이전트 팀
- security-engineer (서브)
- qa-lead (서브)
- tech-lead (팀 정리 및 최종 통합)

## 데이터 전달 프로토콜
- Phase 1-2: 파일 기반 (_workspace/)
- Phase 3: 태스크 기반 + 파일 기반 + 메시지 기반
- Phase 4: 반환값 기반 + 파일 기반

## 에러 핸들링
- 1회 재시도 후 재실패 시 해당 결과 없이 진행
- 상충 데이터는 출처 병기하여 보존
```

#### Step 1-3: 참조 문서 작성
- [ ] `references/pipeline-patterns.md` — 4단계 파이프라인 상세
- [ ] `references/error-handling.md` — 에러 유형별 처리 전략
- [ ] `references/team-coordination.md` — TeamCreate/SendMessage/TaskCreate 사용법

#### 산출물
- [ ] `.claude/skills/project-orchestrator/SKILL.md` (< 500줄)
- [ ] `.claude/skills/project-orchestrator/references/*.md` (3개 파일)

---

### Phase 2: 핵심 에이전트 스킬 생성 (3일)

**목표**: project-manager, backend, frontend, database 스킬 구축

#### Step 2-1: project-manager 스킬
파일: `.claude/skills/project-planning/SKILL.md`

**내용**:
```yaml
---
name: project-planning
description: "parsed-spec.json을 읽고 WBS + workspace-map 생성. 프로젝트 계획, 태스크 분해, Agent 배정, 파일 소유권 정의 작업 시 사용."
---

# Project Planning Skill

## 핵심 역할
parsed-spec.json → project-plan.md + workspace-map.json

## 작업 순서
1. parsed-spec.json 읽기
2. Agent 스캔 (.claude/agents/*.md)
3. 태스크 분해
4. Agent 배정 (스킬 매칭 규칙 적용)
5. 의존성 분석
6. 산출물 생성

## Agent 스킬 매칭 규칙
(현재 project-manager.md의 표를 그대로 이동)

## WBS 형식
(현재 project-manager.md의 YAML 형식 이동)

## workspace-map 형식
(현재 project-manager.md의 JSON 형식 이동)
```

**references**:
- [ ] `references/wbs-templates.md` — 도메인별 WBS 템플릿 (웹앱, 모바일, 데이터파이프라인)
- [ ] `references/agent-matching-rules.md` — 태스크 유형별 Agent 배정 상세 규칙

#### Step 2-2: backend-development 스킬
파일: `.claude/skills/backend-development/SKILL.md`

**내용**:
```yaml
---
name: backend-development
description: "FastAPI 백엔드 개발. REST API, 비즈니스 로직, 서비스 레이어 구현. workspace-map에서 owns로 지정된 경로만 수정. Manus/Claude/OpenAI/Ollama 다중 LLM 지원."
---

# Backend Development Skill

## 기술 스택
- FastAPI (Python 3.10+)
- 다중 LLM 통합 (Claude, OpenAI, Ollama, Manus)
- UTF-8 인코딩 필수

## 작업 원칙
1. workspace-map.json의 owns 경로만 수정
2. API 엔드포인트: /api/* 규칙
3. 비동기 패턴 우선 (async/await)
4. Manus API 특수 처리 (x-manus-api-key 헤더)

## 출력 구조
src/
├── main.py
├── adapters/
├── claude_subprocess/
└── ...

## 참조
- Manus API 상세: references/manus-integration.md
- FastAPI 패턴: references/fastapi-patterns.md
```

**references**:
- [ ] `references/manus-integration.md` — Manus API 특수 처리 (현재 CLAUDE.md에서 이동)
- [ ] `references/fastapi-patterns.md` — 라우팅, 의존성 주입, 에러 처리 패턴
- [ ] `references/async-patterns.md` — async/await, 콜백 처리 (현재 CLAUDE.md에서 이동)

#### Step 2-3: frontend-development 스킬
파일: `.claude/skills/frontend-development/SKILL.md`

**내용**:
```yaml
---
name: frontend-development
description: "React + Vite 프론트엔드 개발. 컴포넌트, 라우팅, 상태 관리 구현. workspace-map의 owns 경로만 수정. CORS 설정 고려."
---

# Frontend Development Skill

## 기술 스택
- React 18
- Vite
- JavaScript (camelCase)

## 작업 원칙
1. workspace-map.json의 owns 경로만 수정
2. 함수형 컴포넌트 + hooks
3. API 베이스 URL: localhost:3003
4. CORS 화이트리스트: localhost:5173

## 출력 구조
src/
├── App.jsx
├── components/
└── ...
```

**references**:
- [ ] `references/react-patterns.md` — 컴포넌트 설계, 훅 사용
- [ ] `references/api-integration.md` — 백엔드 API 호출 패턴

#### Step 2-4: database-design 스킬
파일: `.claude/skills/database-design/SKILL.md`

**내용**: 스키마 설계, 마이그레이션 스크립트 작성

#### 산출물
- [ ] `.claude/skills/project-planning/SKILL.md` + references/ 2개
- [ ] `.claude/skills/backend-development/SKILL.md` + references/ 3개
- [ ] `.claude/skills/frontend-development/SKILL.md` + references/ 2개
- [ ] `.claude/skills/database-design/SKILL.md` + references/ 1개

---

### Phase 3: 보조 에이전트 스킬 생성 (2일)

**목표**: devops, security, qa, tech-lead 스킬 구축

#### Step 3-1: devops 스킬
파일: `.claude/skills/devops/SKILL.md`
- Docker, docker-compose, CI/CD 파이프라인

#### Step 3-2: security-audit 스킬
파일: `.claude/skills/security-audit/SKILL.md`
- OWASP Top 10 체크리스트
- 읽기 전용 (src/** 수정 금지)

#### Step 3-3: qa-testing 스킬
파일: `.claude/skills/qa-testing/SKILL.md`
- 경계면 교차 비교 (API ↔ 프론트 훅)
- Incremental QA

#### Step 3-4: tech-integration 스킬
파일: `.claude/skills/tech-integration/SKILL.md`
- 팀 정리 및 최종 통합
- workspace-map의 merge_targets 처리

#### 산출물
- [ ] 4개 스킬 파일 + references 각 1-2개

---

### Phase 4: CLAUDE.md 리팩토링 (1일)

**목표**: 포인터 패턴 적용, 경량화

#### Step 4-1: 기존 CLAUDE.md 분석
- [ ] 프로젝트 전체 규칙 (유지)
- [ ] 에이전트별 규칙 (스킬로 이동)
- [ ] 워크플로우 규칙 (오케스트레이터로 이동)

#### Step 4-2: 새 CLAUDE.md 작성
```markdown
# CLAUDE.md

## Project Overview
(기존 개요 유지)

## Architecture
(기존 아키텍처 유지)

## 프로젝트 하네스: AI Agent Company

**목표**: 요구사항 문서 → POC 프로젝트 자동 생성

**트리거**: 문서 업로드, 프로젝트 생성, POC 생성 요청 시 `/project-orchestrator` 스킬 사용. 단순 질문은 직접 응답.

**아키텍처 패턴**:
- Phase 1-2: 파이프라인 (순차)
- Phase 3: 팬아웃/팬인 (병렬)
- Phase 4: 생성-검증 (순차)

**변경 이력**:
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-05-14 | 초기 에이전트 구성 | 전체 | - |
| 2026-05-15 | Manus API 지원 | backend | 다중 LLM 지원 |
| 2026-05-26 | Harness 방법론 적용 | 전체 | 스킬 시스템 도입 |

## 개발 명령어
(기존 Development Commands 유지)

## LLM Provider Integration
(기존 내용 유지, Manus 상세는 backend 스킬로 이동)

## 프로젝트 규칙 및 설정
(기존 인코딩, 빌드, 테스트 규칙 유지)
```

#### Step 4-3: 이동된 내용 검증
- [ ] 워크플로우 규칙 → project-orchestrator 스킬
- [ ] Manus API 상세 → backend-development 스킬
- [ ] Agent 매칭 규칙 → project-planning 스킬
- [ ] Async 패턴 → backend-development 스킬

#### 산출물
- [ ] CLAUDE.md (200줄 → 120줄)
- [ ] 이동 매핑 문서

---

### Phase 5: 에이전트 정의 업데이트 (1일)

**목표**: 에이전트 정의에 스킬 참조 추가

#### Step 5-1: frontmatter에 스킬 참조 추가
기존:
```yaml
---
name: project-manager
role: pm
skills:
  reads: [parsed-spec.json]
  produces: [project-plan.md, workspace-map.json]
---
```

변경:
```yaml
---
name: project-manager
role: pm
uses_skill: project-planning
skills:
  reads: [parsed-spec.json]
  produces: [project-plan.md, workspace-map.json]
---
```

#### Step 5-2: 본문에 스킬 포인터 추가
```markdown
# Role: Project Manager

**전용 스킬**: `.claude/skills/project-planning/SKILL.md` 참조

(역할 설명만 유지, 상세 작업 순서는 스킬에 위임)
```

#### Step 5-3: 전체 에이전트 업데이트
- [ ] project-manager.md
- [ ] backend.md → backend-development 스킬
- [ ] frontend.md → frontend-development 스킬
- [ ] dba.md → database-design 스킬
- [ ] devops.md → devops 스킬
- [ ] security-engineer.md → security-audit 스킬
- [ ] tester.md → qa-testing 스킬
- [ ] tech-lead.md → tech-integration 스킬

#### 산출물
- [ ] 8개 에이전트 정의 파일 업데이트

---

### Phase 6: 검증 및 테스트 (2일)

**목표**: 전체 시스템 통합 테스트

#### Step 6-1: 구조 검증
```bash
# 스킬 구조 확인
find .claude/skills -name "SKILL.md" -type f

# frontmatter 검증
for file in .claude/skills/*/SKILL.md; do
  echo "=== $file ==="
  head -10 "$file"
done
```

- [ ] 모든 스킬에 name, description 존재
- [ ] SKILL.md < 500줄
- [ ] references/ 파일에 ToC 존재 (300줄 이상일 경우)

#### Step 6-2: 트리거 검증
각 스킬의 description으로 Should-trigger 쿼리 테스트:

**project-orchestrator**:
- ✅ "문서 업로드해서 프로젝트 생성해줘"
- ✅ "POC 만들어줘"
- ✅ "이전 결과 다시 실행"
- ❌ "에이전트 목록 보여줘" (단순 질문)

**project-planning**:
- ✅ "WBS 만들어줘"
- ✅ "태스크 분해해줘"
- ❌ "코드 작성해줘" (다른 스킬)

#### Step 6-3: 실행 테스트
실제 워크플로우 테스트:

1. **테스트 케이스 1**: 새 프로젝트 생성
   ```
   프롬프트: "간단한 TODO 앱 프로젝트 생성해줘. FastAPI + React 사용."
   기대: project-orchestrator 트리거 → Phase 1-4 순차 실행
   ```

2. **테스트 케이스 2**: 부분 재실행
   ```
   프롬프트: "프론트엔드 UI 다시 만들어줘"
   기대: project-orchestrator Phase 0에서 부분 재실행 판별 → Phase 3 frontend만 재실행
   ```

3. **테스트 케이스 3**: 에러 복구
   ```
   시나리오: backend 개발 중 에러 발생
   기대: 1회 재시도 → 재실패 시 해당 결과 없이 진행, 보고서에 누락 명시
   ```

#### Step 6-4: With-Harness vs Without-Harness 비교 (선택)
- 같은 프롬프트를 Harness 적용 전후 비교
- 품질 점수, 완성도, 컨텍스트 사용량 측정

#### 산출물
- [ ] 검증 체크리스트 완료
- [ ] 테스트 시나리오 3개 통과
- [ ] 비교 결과 (선택)

---

### Phase 7: 문서화 및 배포 (1일)

#### Step 7-1: 디렉토리 구조 문서화
```markdown
# .claude/skills/README.md

## 스킬 구조

### 오케스트레이터
- `project-orchestrator/` — 전체 워크플로우 조율

### 핵심 개발 스킬
- `project-planning/` — WBS, workspace-map 생성
- `backend-development/` — FastAPI 백엔드
- `frontend-development/` — React 프론트엔드
- `database-design/` — DB 스키마

### 보조 스킬
- `devops/` — Docker, CI/CD
- `security-audit/` — OWASP 보안 감사
- `qa-testing/` — 통합 테스트
- `tech-integration/` — 최종 통합

## 트리거 규칙
(각 스킬의 description 요약)
```

#### Step 7-2: 이관 가이드 작성
```markdown
# HARNESS_MIGRATION_GUIDE.md

## 변경 사항

### 사용자 관점
- 기존 사용법 그대로 유지
- "프로젝트 생성해줘" → 자동으로 project-orchestrator 트리거

### 개발자 관점
- 규칙 수정 시 CLAUDE.md가 아닌 해당 스킬 파일 수정
- 에이전트 추가 시 전용 스킬도 생성
- 변경 이력 CLAUDE.md에 기록

## FAQ
Q: 기존 프로젝트 영향?
A: 없음. starter-project는 그대로 유지.

Q: 에이전트 정의 변경?
A: frontmatter에 uses_skill 추가, 본문 경량화
```

#### Step 7-3: Git 커밋
```bash
git add .claude/skills/
git add CLAUDE.md
git add .claude/agents/
git commit -m "Apply Harness methodology: skill system + orchestrator

- Add project-orchestrator skill for workflow coordination
- Create 8 agent-specific skills with Progressive Disclosure
- Refactor CLAUDE.md with pointer pattern (200 → 120 lines)
- Update agent definitions with skill references

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

#### 산출물
- [ ] `.claude/skills/README.md`
- [ ] `HARNESS_MIGRATION_GUIDE.md`
- [ ] Git 커밋 완료

---

## 📅 타임라인

| Phase | 소요 | 누적 | 주요 마일스톤 |
|-------|------|------|--------------|
| Phase 0: 준비 및 감사 | 1일 | 1일 | 현황 파악, 백업 완료 |
| Phase 1: 오케스트레이터 | 2일 | 3일 | 워크플로우 조율 스킬 완성 |
| Phase 2: 핵심 스킬 | 3일 | 6일 | 4개 주요 스킬 완성 |
| Phase 3: 보조 스킬 | 2일 | 8일 | 4개 보조 스킬 완성 |
| Phase 4: CLAUDE.md | 1일 | 9일 | 포인터 패턴 적용 |
| Phase 5: 에이전트 업데이트 | 1일 | 10일 | 스킬 참조 추가 |
| Phase 6: 검증 및 테스트 | 2일 | 12일 | 통합 테스트 통과 |
| Phase 7: 문서화 및 배포 | 1일 | 13일 | 배포 준비 완료 |

**총 소요**: 약 13일 (2주)

---

## ✅ 최종 산출물 체크리스트

### 스킬 시스템
- [ ] `.claude/skills/project-orchestrator/SKILL.md` + references/ 3개
- [ ] `.claude/skills/project-planning/SKILL.md` + references/ 2개
- [ ] `.claude/skills/backend-development/SKILL.md` + references/ 3개
- [ ] `.claude/skills/frontend-development/SKILL.md` + references/ 2개
- [ ] `.claude/skills/database-design/SKILL.md` + references/ 1개
- [ ] `.claude/skills/devops/SKILL.md` + references/ 1개
- [ ] `.claude/skills/security-audit/SKILL.md` + references/ 1개
- [ ] `.claude/skills/qa-testing/SKILL.md` + references/ 1개
- [ ] `.claude/skills/tech-integration/SKILL.md` + references/ 1개

**총 9개 스킬, 15개 references 파일**

### 에이전트 정의 업데이트
- [ ] 8개 에이전트 정의에 `uses_skill` 추가
- [ ] 본문 경량화 (상세 작업은 스킬 위임)

### CLAUDE.md
- [ ] 200줄 → 120줄 경량화
- [ ] 하네스 포인터 섹션 추가
- [ ] 변경 이력 테이블 추가

### 문서
- [ ] `.claude/skills/README.md`
- [ ] `HARNESS_MIGRATION_GUIDE.md`
- [ ] 이 파일 (`HARNESS_MIGRATION_PLAN.md`)

### 검증
- [ ] 모든 스킬 frontmatter 검증 통과
- [ ] 트리거 검증 통과
- [ ] 실행 테스트 3개 시나리오 통과

---

## 🎯 성공 지표

### 정량 지표
- **컨텍스트 효율**: CLAUDE.md 토큰 사용량 40% 감소
- **스킬 로딩**: 평균 3개 스킬만 로딩 (전체 9개 중)
- **테스트 통과율**: 100% (3/3 시나리오)

### 정성 지표
- **유지보수성**: 규칙 변경 시 단일 파일만 수정
- **재사용성**: 스킬 단위로 다른 프로젝트 이식 가능
- **명확성**: 아키텍처 패턴이 명시적으로 문서화됨

---

## 🚧 주의사항

### 필수 확인 사항
1. **UTF-8 인코딩**: 모든 새 파일 UTF-8로 작성
2. **BOM 금지**: Byte Order Mark 포함하지 않음
3. **기존 기능 보존**: starter-project 참조 구현은 변경하지 않음
4. **점진적 적용**: Phase 단위로 커밋, 롤백 가능하게 유지

### 에러 예방
1. **스킬 description**: 적극적("pushy")으로 작성, 후속 키워드 포함
2. **SKILL.md 크기**: 500줄 초과 시 references/ 분리
3. **순환 참조**: 에이전트 ↔ 스킬 간 순환 참조 금지
4. **에이전트 팀 실험 플래그**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 확인

---

## 📚 참고 자료

### Harness 공식 문서
- `projects/harness/harness/README_KO.md`
- `projects/harness/harness/skills/harness/SKILL.md`
- `projects/harness/harness/skills/harness/references/agent-design-patterns.md`
- `projects/harness/harness/skills/harness/references/orchestrator-template.md`
- `projects/harness/harness/skills/harness/references/skill-writing-guide.md`

### 현재 프로젝트
- `CLAUDE.md` (현재 상태)
- `.claude/agents/` (17개 에이전트 정의)

### 외부 참고
- [revfactory/harness](https://github.com/revfactory/harness)
- [revfactory/harness-100](https://github.com/revfactory/harness-100)

---

## 🔄 진화 계획

Harness는 고정물이 아니라 진화하는 시스템입니다. 적용 후:

1. **실행 후 피드백 수집**: 매 프로젝트 생성 후 사용자 피드백 요청
2. **반복 패턴 번들링**: 공통 코드는 scripts/에 번들
3. **변경 이력 추적**: CLAUDE.md 테이블에 모든 변경 기록
4. **진화 트리거**:
   - 같은 피드백 2회 이상 반복 시
   - 에이전트 반복 실패 패턴 발견 시
   - 사용자 수동 우회 패턴 관찰 시

---

**작성자**: Claude Sonnet 4.5
**문서 버전**: 1.0
**최종 수정**: 2026-05-26
