# Pipeline Patterns — 파이프라인 패턴 상세

AI Agent Company 워크플로우에서 사용되는 파이프라인 패턴의 상세 설명.

---

## 목차

1. [파이프라인 개요](#1-파이프라인-개요)
2. [4 Phase 구조](#2-4-phase-구조)
3. [Phase 간 데이터 전달](#3-phase-간-데이터-전달)
4. [하이브리드 실행 모드](#4-하이브리드-실행-모드)
5. [팀 재구성 패턴](#5-팀-재구성-패턴)

---

## 1. 파이프라인 개요

파이프라인 패턴은 순차적 작업 흐름을 의미한다. 이전 Phase의 출력이 다음 Phase의 입력이 되며, 각 Phase는 명확한 책임을 가진다.

### AI Agent Company의 파이프라인

```
Phase 1: 문서 분석
    └→ parsed-spec.json

Phase 2: 프로젝트 계획
    └→ project-plan.md + workspace-map.json

Phase 3: 병렬 개발 (파이프라인 내 팬아웃/팬인 구간)
    └→ workspace/{project_id}/*

Phase 4: 검증 및 통합
    └→ 완성된 프로젝트
```

### 파이프라인의 장점

- **명확한 단계**: 각 Phase의 시작과 끝이 분명
- **디버깅 용이**: Phase별 산출물이 파일로 보존되어 문제 지점 파악 쉬움
- **점진적 진행**: 사용자가 중간 결과를 확인하고 진행 여부 결정 가능
- **병목 식별**: 어느 Phase가 느린지 즉시 파악

### 파이프라인의 단점

- **병목 전파**: 한 Phase의 지연이 전체를 지연시킴
- **순차 의존**: 병렬화 어려움 (단, Phase 내 팬아웃은 가능)

---

## 2. 4 Phase 구조

### Phase 1: 문서 분석 (Document Parsing)

**목적**: 비정형 요구사항 문서를 구조화된 JSON으로 변환

**입력**:
- 사용자 업로드 문서 (PDF, DOCX, XLSX, Markdown, 텍스트)
- 구두 요구사항 (사용자 메시지)

**처리**:
- document-parser 에이전트 (서브)가 문서 파싱
- 텍스트 추출, 기능 목록 식별, 기술 스택 추론

**출력**:
- `_workspace/01_parsed-spec.json`

**구조**:
```json
{
  "project_name": "TODO App",
  "description": "간단한 할 일 관리 애플리케이션",
  "features": [
    { "id": "F001", "name": "할 일 추가", "priority": "high" },
    { "id": "F002", "name": "할 일 완료 처리", "priority": "medium" },
    { "id": "F003", "name": "할 일 목록 보기", "priority": "high" }
  ],
  "tech_stack": {
    "backend": "FastAPI",
    "frontend": "React",
    "database": "PostgreSQL"
  },
  "non_functional_requirements": {
    "security": ["HTTPS", "인증"],
    "performance": ["응답시간 < 1초"]
  }
}
```

**검증**:
- JSON 형식 유효성 (Read로 파싱 가능한지 확인)
- 필수 필드 존재 여부 (project_name, features, tech_stack)

---

### Phase 2: 프로젝트 계획 (Project Planning)

**목적**: WBS(Work Breakdown Structure)와 파일 소유권 맵 생성

**입력**:
- `_workspace/01_parsed-spec.json`
- `.claude/agents/*.md` (에이전트 목록 및 스킬)

**처리**:
- project-manager 에이전트 (서브)가 작업 분해
- 기능을 태스크로 분해 (1 기능 → N 태스크)
- 에이전트 스킬 매칭 규칙 적용
- 의존성 분석 (순차 vs 병렬)

**출력**:
- `_workspace/02_project-plan.md` (WBS)
- `_workspace/02_workspace-map.json` (파일 소유권 맵)

**WBS 구조**:
```yaml
pipeline:
  stages:
    - stage: 1
      name: "분석·설계"
      sequential: true
      tasks:
        - id: T-001
          name: "API 명세 작성"
          agent: system-analyst
          output_files: ["docs/api-spec.md"]
          est_hours: 2

    - stage: 2
      name: "병렬 개발"
      sequential: false
      tasks:
        - id: T-002
          name: "백엔드 API 구현"
          agent: backend-developer
          parallel_with: [T-003, T-004]
          output_files: ["src/api/**"]
```

**workspace-map 구조**:
```json
{
  "project_id": "todo-app-20260526",
  "root": "/workspace/todo-app-20260526",
  "ownership": {
    "backend-developer": {
      "owns": ["src/api/**", "src/service/**"],
      "reads": ["docs/**"],
      "forbidden": ["src/components/**"]
    },
    "frontend-developer": {
      "owns": ["src/components/**", "src/pages/**"],
      "reads": ["docs/**"],
      "forbidden": ["src/api/**"]
    }
  }
}
```

**검증**:
- project-plan.md에 최소 1개 stage 존재
- workspace-map.json에 모든 개발 에이전트의 owns 경로 정의
- 충돌하는 owns 경로 없음 (교집합 검사)

---

### Phase 3: 병렬 개발 (Parallel Development)

**목적**: 백엔드, 프론트엔드, DB, 인프라를 병렬로 구현

**입력**:
- `_workspace/02_project-plan.md` (작업 목록)
- `_workspace/02_workspace-map.json` (파일 소유권)
- `_workspace/01_parsed-spec.json` (요구사항)

**처리**:
- **에이전트 팀 모드** (Phase 3에서만 팀 사용)
- backend-dev, frontend-dev, db-engineer, devops 4명 팀 구성
- TaskCreate로 작업 할당
- 팀원들이 SendMessage로 실시간 협업
- workspace-map.json 기반 파일 소유권 준수

**팀 통신 예시**:
```
[frontend-dev] → [backend-dev]: "POST /todos 엔드포인트 필요해요. 요청 바디 형식은?"
[backend-dev] → [frontend-dev]: "{ title: string, description: string } 형식입니다. src/api/todos.py 참고하세요."
[db-engineer] → [backend-dev]: "todos 테이블 스키마 완성. id, title, description, completed, created_at 컬럼 있어요."
```

**출력**:
- `workspace/{project_id}/src/api/**` (backend)
- `workspace/{project_id}/src/components/**` (frontend)
- `workspace/{project_id}/migrations/**` (database)
- `workspace/{project_id}/Dockerfile` (devops)

**검증**:
- 주요 엔트리 파일 존재 (src/main.py, src/App.jsx)
- Dockerfile, docker-compose.yml 존재
- migrations/ 디렉토리에 최소 1개 파일

---

### Phase 4: 검증 및 통합 (Validation & Integration)

**목적**: 보안 감사, 테스트 코드 작성, 최종 통합

**입력**:
- `workspace/{project_id}/` (Phase 3 산출물)
- `_workspace/02_workspace-map.json`

**처리**:
1. **보안 감사** (서브 에이전트): security-engineer가 OWASP Top 10 체크
2. **테스트 코드 작성** (서브 에이전트): tester가 pytest, Jest 테스트 생성
3. **최종 통합** (에이전트 팀): tech-lead가 충돌 해결 및 README 생성

**팀 재구성**:
- Phase 3 dev-team을 TeamDelete로 정리
- Phase 4-3에서 integration-team (tech-lead 리더) 재구성

**출력**:
- `_workspace/04_security-report.md` (보안 감사 결과)
- `workspace/{project_id}/tests/**` (테스트 코드)
- `workspace/{project_id}/README.md` (프로젝트 문서)

**검증**:
- security-report.md에 critical 이슈 0개 (또는 해결됨)
- tests/ 디렉토리에 최소 1개 테스트 파일
- README.md에 실행 방법 섹션 존재

---

## 3. Phase 간 데이터 전달

### 파일 기반 전달 (기본)

모든 Phase 간 데이터 전달은 **파일 기반**으로 수행한다. 이유:
- 감사 추적 가능 (모든 중간 산출물 보존)
- 디버깅 용이 (Phase별 결과 확인)
- 재실행 가능 (특정 Phase부터 재시작)

**경로 규칙**:
- Phase 1 산출물: `_workspace/01_*`
- Phase 2 산출물: `_workspace/02_*`
- Phase 3 산출물: `workspace/{project_id}/*`
- Phase 4 산출물: `_workspace/04_*` + `workspace/{project_id}/README.md`

### Phase 전환 체크포인트

각 Phase 종료 시 산출물 검증:

```python
# Phase 1 → Phase 2 전환
if not exists("_workspace/01_parsed-spec.json"):
    raise Error("Phase 1 산출물 누락")
if not is_valid_json("_workspace/01_parsed-spec.json"):
    raise Error("Phase 1 산출물 형식 오류")

# Phase 2 → Phase 3 전환
if not exists("_workspace/02_project-plan.md"):
    raise Error("Phase 2 산출물 누락")
if not exists("_workspace/02_workspace-map.json"):
    raise Error("workspace-map 누락")

# Phase 3 → Phase 4 전환
if not exists(f"workspace/{project_id}/src/main.py"):
    warn("백엔드 엔트리 파일 누락")
if not exists(f"workspace/{project_id}/src/App.jsx"):
    warn("프론트엔드 엔트리 파일 누락")
```

---

## 4. 하이브리드 실행 모드

### 모드 선택 이유

| Phase | 모드 | 이유 |
|-------|------|------|
| 1 | 서브 에이전트 | 단일 에이전트 독립 작업. 팀 오버헤드 불필요 |
| 2 | 서브 에이전트 | 단일 에이전트 독립 작업. 팀 오버헤드 불필요 |
| 3 | 에이전트 팀 | 4명 협업 필수. API 협의, 스키마 공유 등 실시간 통신 필요 |
| 4 | 서브 → 팀 | 검증(서브)은 독립 작업, 통합(팀)은 tech-lead 주도 조율 |

### 하이브리드 전환 규칙

**서브 → 서브**: 그대로 연속 호출

**서브 → 팀**:
```
Agent(...) # Phase 2 종료
→ TeamCreate(...) # Phase 3 시작
```

**팀 → 서브**:
```
TeamDelete() # Phase 3 종료
→ Agent(...) # Phase 4 시작
```

**팀 → 팀**:
```
TeamDelete() # Phase 3 dev-team 종료
→ TeamCreate(...) # Phase 4 integration-team 시작
```

> 세션당 1팀만 활성 가능하므로 반드시 TeamDelete 후 새 TeamCreate

---

## 5. 팀 재구성 패턴

### Phase 3 → Phase 4 팀 재구성

Phase 3의 dev-team (4명)과 Phase 4의 integration-team (1-2명)은 구성원이 다르므로 팀을 재구성한다.

**재구성 절차**:

1. **Phase 3 종료**:
   ```
   SendMessage(to: "all", message: "모든 작업 완료. 팀 종료합니다.")
   TeamDelete()
   ```

2. **Phase 4-1, 4-2: 서브 에이전트로 검증**:
   ```
   Agent(prompt: "보안 감사...", subagent_type: "security-engineer", model: "opus")
   Agent(prompt: "테스트 코드...", subagent_type: "tester", model: "opus")
   ```

3. **Phase 4-3: 새 팀 구성**:
   ```
   TeamCreate(
     team_name: "integration-team",
     members: [
       { name: "tech-lead", agent_type: "tech-lead", model: "opus", prompt: "최종 통합..." }
     ]
   )
   ```

4. **Phase 4-3 종료**:
   ```
   TeamDelete()
   ```

### 팀 재구성 시 데이터 전달

이전 팀의 산출물은 `workspace/{project_id}/`와 `_workspace/`에 보존되므로 새 팀이 Read 도구로 접근 가능하다.

**예시**:
```
tech-lead 프롬프트:
"입력:
 - workspace/{project_id}/ (Phase 3 dev-team의 산출물)
 - _workspace/04_security-report.md (Phase 4-1 산출물)
 - _workspace/02_workspace-map.json (Phase 2 산출물)

 작업:
 1. Phase 3 산출물 읽기 (Read 도구)
 2. 보안 이슈 반영
 3. README.md 생성"
```

---

## 파이프라인 최적화 팁

### 병목 Phase 식별

각 Phase 실행 시간 측정:
- Phase 1: ~2-5분 (문서 크기에 따라)
- Phase 2: ~3-5분 (에이전트 수에 따라)
- Phase 3: ~20-40분 (프로젝트 복잡도에 따라) ← 가장 긴 Phase
- Phase 4: ~10-15분

**최적화 포인트**: Phase 3

### Phase 3 최적화 전략

1. **팀원 수 조절**: 4명이 표준이지만, 소규모 프로젝트는 3명(devops 생략), 대규모는 5명(추가 전문가)
2. **작업 세분화**: 큰 태스크를 작은 서브태스크로 분해하여 진행률 추적 개선
3. **depends_on 최소화**: 순차 의존을 줄이고 병렬 작업 비율 증가

### 체크포인트 기반 재실행

Phase별 산출물이 파일로 보존되므로, 특정 Phase부터 재실행 가능:

```
사용자: "Phase 3부터 다시 실행해줘"
→ Phase 0에서 _workspace/02_* 존재 확인
→ Phase 1-2 건너뛰고 Phase 3부터 시작
```

---

## 참고

- 에러 핸들링 전략: [error-handling.md](error-handling.md)
- 팀 조율 프로토콜: [team-coordination.md](team-coordination.md)
