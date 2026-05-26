# Phase 0 감사 보고서

**작성일**: 2026-05-26
**목적**: Harness 방법론 적용 전 현황 파악

---

## 1. 백업 완료

✅ **백업 완료**
- `.claude/` → `.claude.backup-20260526/`
- `CLAUDE.md` → `CLAUDE.md.backup`

---

## 2. 에이전트 현황

### 2.1 전체 에이전트 목록 (16개)

| # | 파일명 | frontmatter | 비고 |
|---|--------|-------------|------|
| 1 | architect.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 2 | backend.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 3 | controller.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 4 | dba.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 5 | devops.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 6 | document-parser.md | ✅ | YAML frontmatter 완전 |
| 7 | frontend.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 8 | planner.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 9 | project-manager.md | ✅ | YAML frontmatter 완전 |
| 10 | requirement-analyst.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 11 | reviewer.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 12 | security-engineer.md | ✅ | YAML frontmatter 완전 |
| 13 | system-analyst.md | ✅ | YAML frontmatter 완전 |
| 14 | tech-lead.md | ✅ | YAML frontmatter 완전 |
| 15 | tech-writer.md | ❌ | 목표/입력/출력 섹션만 존재 |
| 16 | tester.md | ❌ | 목표/입력/출력 섹션만 존재 |

### 2.2 frontmatter 분석

**frontmatter 있음 (5개)**:
- document-parser
- project-manager
- security-engineer
- system-analyst
- tech-lead

**frontmatter 없음 (11개)**:
- architect, backend, controller, dba, devops, frontend, planner, requirement-analyst, reviewer, tech-writer, tester

**결론**: frontmatter 표준화 필요. 5개는 최신 형식, 11개는 구 형식.

### 2.3 에이전트별 역할 요약

| 에이전트 | 주요 역할 | 입력 | 출력 |
|---------|----------|------|------|
| document-parser | 문서 분석 및 요구사항 추출 | PDF/DOCX/XLSX/CSV 등 | parsed-spec.json |
| project-manager | WBS, workspace-map 생성 | parsed-spec.json | project-plan.md, workspace-map.json |
| requirement-analyst | 비정형 자료 → 구조화된 요구사항 | 업로드 문서, 구두 요구사항 | requirements.md |
| system-analyst | 요구사항 정제, API 명세 | requirements.md | requirements.md, api-spec.md |
| architect | 시스템 아키텍처 설계 | requirements.md | architecture.md |
| planner | 서비스 정의, 요구사항 문서화 | 사용자 요구사항 | spec.md |
| dba | DB 스키마 설계 | spec.md | schema.sql |
| backend | REST API 구현 | spec.md, schema.sql | /app/backend/* |
| frontend | UI 구현 | spec.md, API 정의 | /app/frontend/* |
| devops | 배포 파이프라인 구축 | architecture.md, 앱 코드 | Dockerfile, CI/CD |
| security-engineer | OWASP 보안 감사 | 전체 코드 | security-report.md |
| tester | 테스트 및 품질 보증 | requirements.md, 앱 코드 | tests/*, test-report.md |
| reviewer | 일관성 검증 | spec.md, schema.sql, 앱 코드 | review-report.md |
| tech-writer | 문서화 | 전체 산출물 | README.md, 사용자 가이드 |
| tech-lead | 팀 조율, 충돌 해결 | workspace-map.json | 최종 통합 |
| controller | 전체 프로세스 자동 수행 | 요구사항 문서 | POC 프로젝트 |

---

## 3. 스킬 현황

### 3.1 현재 스킬 디렉토리
```
.claude/skills/
└── Pencil Pro/          # 외부 스킬 (UI 디자인)
```

**문제점**:
- ❌ 에이전트 전용 스�ील이 하나도 없음
- ❌ 오케스트레이터 스킬 부재
- ❌ Progressive Disclosure 미적용

**필요 스킬 (9개)**:
1. project-orchestrator (오케스트레이터)
2. project-planning (project-manager 전용)
3. backend-development (backend 전용)
4. frontend-development (frontend 전용)
5. database-design (dba 전용)
6. devops (devops-engineer 전용)
7. security-audit (security-engineer 전용)
8. qa-testing (tester 전용)
9. tech-integration (tech-lead 전용)

---

## 4. CLAUDE.md 분석

### 4.1 기본 정보
- **총 줄 수**: 293줄
- **목표 줄 수**: 120줄 (경량화 후)
- **감소 목표**: 173줄 (59% 감소)

### 4.2 섹션별 분류

#### 유지할 섹션 (프로젝트 전체 규칙)
- [ ] Project Overview
- [ ] Architecture (3-Tier 구조)
- [ ] Development Commands
- [ ] LLM Provider Integration (개요만)
- [ ] 프로젝트 규칙 및 설정 (인코딩, 빌드, 테스트)
- [ ] Git Strategy

#### 스킬로 이동할 섹션
| CLAUDE.md 섹션 | 이동 대상 스킬 | 줄 수 |
|---------------|--------------|------|
| Agent Company Workflow (상세) | project-orchestrator | ~40줄 |
| Critical Files 설명 | project-orchestrator (references/) | ~20줄 |
| Workspace Isolation | project-orchestrator (references/) | ~15줄 |
| Manus API Special Handling | backend-development (references/) | ~30줄 |
| Claude CLI Subprocess Integration | backend-development (references/) | ~25줄 |
| Async Patterns | backend-development (references/) | ~15줄 |
| Agent Framework (상세) | project-planning (references/) | ~20줄 |
| Agent Definitions 파싱 규칙 | project-planning (references/) | ~10줄 |

**예상 이동량**: ~175줄 → 목표 달성 가능

#### 추가할 섹션 (Harness 포인터)
```markdown
## 프로젝트 하네스: AI Agent Company

**목표**: 요구사항 문서 → POC 프로젝트 자동 생성

**트리거**: 문서 업로드, 프로젝트 생성 요청 시 `/project-orchestrator` 스킬 사용

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
```

---

## 5. 워크플로우 패턴 분석

### 5.1 현재 워크플로우 (암묵적)

```
사용자 요구사항
    ↓
[Phase 1] 문서 분석
    document-parser → parsed-spec.json
    ↓
[Phase 2] 프로젝트 계획
    project-manager → project-plan.md + workspace-map.json
    ↓
[Phase 3] 병렬 개발 (팬아웃/팬인)
    backend-developer  ┐
    frontend-developer ├─→ 병렬 작업
    database-engineer  ┘
    devops-engineer    (인프라)
    ↓
[Phase 4] 검증 및 통합
    security-engineer → tester → tech-lead
    ↓
POC 프로젝트
```

### 5.2 Harness 아키텍처 패턴 매핑

| Phase | Harness 패턴 | 실행 모드 | 에이전트 수 |
|-------|-------------|----------|-----------|
| Phase 1 | 파이프라인 | 서브 에이전트 | 1 (document-parser) |
| Phase 2 | 파이프라인 | 서브 에이전트 | 1 (project-manager) |
| Phase 3 | 팬아웃/팬인 | 에이전트 팀 | 4 (backend, frontend, dba, devops) |
| Phase 4 | 생성-검증 | 서브 에이전트 → 팀 | 3 (security, tester, tech-lead) |

**특이사항**:
- Phase 3에서만 에이전트 팀 사용 (협업 필요)
- 나머지는 서브 에이전트 (독립 작업)
- 하이브리드 패턴 적용

---

## 6. Harness 참조 자료 준비

### 6.1 필수 읽기 자료
- [x] `projects/harness/harness/README_KO.md` (읽음)
- [x] `projects/harness/harness/.claude-plugin/plugin.json` (읽음)
- [x] `projects/harness/harness/skills/harness/SKILL.md` (읽음)
- [ ] `projects/harness/harness/skills/harness/references/agent-design-patterns.md`
- [ ] `projects/harness/harness/skills/harness/references/orchestrator-template.md`
- [ ] `projects/harness/harness/skills/harness/references/skill-writing-guide.md`
- [ ] `projects/harness/harness/skills/harness/references/skill-testing-guide.md`
- [ ] `projects/harness/harness/skills/harness/references/qa-agent-guide.md`
- [ ] `projects/harness/harness/skills/harness/references/team-examples.md`

### 6.2 템플릿 추출 필요
- [ ] 오케스트레이터 SKILL.md 템플릿
- [ ] 에이전트별 스킬 SKILL.md 템플릿
- [ ] frontmatter 표준 형식
- [ ] references/ 구조 예시

---

## 7. 문제점 및 권장사항

### 7.1 발견된 문제점

1. **frontmatter 불일치** (중요도: 중)
   - 5개는 YAML frontmatter, 11개는 Markdown 섹션만
   - 표준화 필요

2. **스킬 시스템 부재** (중요도: 높)
   - 에이전트 정의만 있고 실행 스킬 없음
   - "누가"는 정의되었으나 "어떻게"는 없음

3. **오케스트레이션 불명확** (중요도: 높)
   - 워크플로우가 CLAUDE.md에 산발적으로 기술
   - Phase별 전환 로직 없음

4. **컨텍스트 비효율** (중요도: 중)
   - CLAUDE.md 293줄 전체가 매 세션 로딩
   - Progressive Disclosure 미적용

5. **재사용성 부족** (중요도: 중)
   - 규칙이 CLAUDE.md에 집중
   - 다른 프로젝트에 이식 불가

### 7.2 권장 조치사항

#### 즉시 조치 (Phase 1-2)
1. 오케스트레이터 스킬 생성
2. 핵심 4개 스킬 생성 (project-planning, backend, frontend, database)
3. CLAUDE.md에서 해당 규칙 이동

#### 단기 조치 (Phase 3-5)
4. 보조 4개 스킬 생성 (devops, security, qa, tech-integration)
5. 모든 에이전트 frontmatter 표준화
6. CLAUDE.md 경량화 및 포인터 패턴 적용

#### 장기 조치 (Phase 6-7)
7. 통합 테스트 및 검증
8. 문서화 및 이관 가이드 작성
9. 실행 후 피드백 수집 체계 구축

---

## 8. Phase 1 준비 완료

### 8.1 준비된 사항
- ✅ 백업 완료
- ✅ 에이전트 16개 전수 조사 완료
- ✅ CLAUDE.md 293줄 분석 완료
- ✅ 워크플로우 패턴 매핑 완료
- ✅ 문제점 식별 완료

### 8.2 다음 단계: Phase 1
**목표**: 오케스트레이터 스킬 생성 (2일)

**작업 항목**:
1. `.claude/skills/project-orchestrator/` 디렉토리 생성
2. `SKILL.md` 작성 (4 Phase 워크플로우)
3. `references/` 3개 파일 작성
   - pipeline-patterns.md
   - error-handling.md
   - team-coordination.md
4. Harness references 읽기 (agent-design-patterns.md, orchestrator-template.md)

**준비 완료**: Phase 1로 진행 가능 ✅

---

**작성자**: Claude Sonnet 4.5
**문서 버전**: 1.0
