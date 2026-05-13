# Claude Agent View 사용 가이드

이 문서는 현재 프로젝트의 AI Agents를 Claude Code Agent View를 통해 효율적으로 사용하는 방법을 안내합니다.

## 목차

1. [Agent View 소개](#agent-view-소개)
2. [시작하기](#시작하기)
3. [프로젝트 Agents 목록](#프로젝트-agents-목록)
4. [기본 사용법](#기본-사용법)
5. [실전 워크플로우](#실전-워크플로우)
6. [주요 단축키](#주요-단축키)
7. [병렬 작업 활용](#병렬-작업-활용)
8. [세션 관리](#세션-관리)
9. [팁과 모범 사례](#팁과-모범-사례)
10. [문제 해결](#문제-해결)

---

## Agent View 소개

**Agent View**는 여러 Claude Code 백그라운드 세션을 한 화면에서 관리하는 기능입니다.

### 주요 특징

- 모든 백그라운드 세션을 한 테이블에서 모니터링
- 각 세션의 상태를 실시간 아이콘으로 표시
- 터미널을 열지 않아도 백그라운드에서 계속 작업 진행
- 여러 작업을 병렬로 실행하여 개발 속도 향상
- 특정 세션에 필요할 때만 개입 가능

### 세션 상태 표시

| 아이콘 | 상태 | 의미 |
|--------|------|------|
| `✽` (애니메이션) | Working | Claude가 활발히 도구 실행 중 |
| `✻` | Needs input | 사용자 입력 대기 중 |
| `∙` | Idle | 준비 완료 (프로세스 종료됨) |
| `✢` | Loop | `/loop` 세션 대기 중 |
| Green | Completed | 성공적으로 완료 |
| Red | Failed | 오류로 종료 |

---

## 시작하기

### Agent View 실행

```bash
claude agents
```

이 명령으로 Agent View UI가 열립니다.

### 첫 번째 Agent 디스패치

Agent View에서 프롬프트를 입력하고 Enter를 누르세요:

```
planner 사용자 프로필 페이지 추가
```

---

## 프로젝트 Agents 목록

현재 프로젝트에는 6개의 전문 AI Agents가 정의되어 있습니다:

| Agent | 역할 | 입력 | 출력 | 사용 예시 |
|-------|------|------|------|-----------|
| **planner** | 서비스 기획자 | 사용자 요구사항 | spec.md | `planner 로그인 기능 추가` |
| **dba** | 데이터베이스 설계자 | spec.md | schema.sql | `dba users 테이블 설계` |
| **backend** | 백엔드 개발자 | spec.md, schema.sql | /app/backend/* | `backend 로그인 API 구현` |
| **frontend** | 프론트엔드 개발자 | spec.md, API 정의 | /app/frontend/* | `frontend 로그인 화면 구현` |
| **controller** | 프로젝트 매니저 | 요구사항 | 전체 시스템 | `controller 로그인 기능 전체 구현` |
| **reviewer** | 품질 검증자 | 모든 결과물 | 문제 리스트 | `reviewer 로그인 기능 검증` |

### Agent 역할 상세

#### 1. Planner (기획자)

**책임:**
- 서비스 개요 정의
- 사용자 시나리오 정의
- 화면 구조 정의 (UI 구조까지만)
- 기능 목록 정리
- API 요구사항 정의

**금지사항:**
- 코드 작성 금지
- DB 설계 금지
- CSS/UI 디자인 금지

#### 2. DBA (데이터베이스 설계자)

**책임:**
- 데이터 모델링
- 테이블 설계
- 관계 정의
- 인덱스 설정

**금지사항:**
- API 설계 금지
- UI 관련 작업 금지
- 비즈니스 로직 구현 금지

#### 3. Backend (백엔드 개발자)

**책임:**
- API 구현
- 비즈니스 로직 처리
- DB 연동
- 에러 처리 및 인증/검증 로직

**금지사항:**
- DB 스키마 변경 금지
- UI 구현 금지
- 요구사항 변경 금지

#### 4. Frontend (프론트엔드 개발자)

**책임:**
- UI 구현
- UX 개선
- 사용자 인터랙션 최적화
- 반응형 UI 적용

**금지사항:**
- 기능 추가 금지
- API 수정 금지
- 요구사항 변경 금지

#### 5. Controller (프로젝트 매니저)

**책임:**
- 전체 프로세스 자동화
- Agent 간 조율
- 검증 루프 관리

**실행 순서:**
1. Planner 실행 → spec.md 생성
2. DBA 실행 → schema.sql 생성
3. Backend 실행 → API 생성
4. Frontend 실행 → UI 생성
5. Reviewer 실행 → 검증

#### 6. Reviewer (품질 검증자)

**검사 항목:**
- spec ↔ DB 일치 여부
- DB ↔ API 일치 여부
- API ↔ Frontend 일치 여부

**출력:**
- 문제 리스트
- 불일치 항목 보고

---

## 기본 사용법

### 1. Agent 디스패치 방법

#### 방법 A: Agent 이름으로 시작

```
planner 새로운 기능 기획
dba 테이블 설계
backend API 구현
```

#### 방법 B: @ 멘션 사용

```
@planner 알림 기능 추가
@dba notifications 테이블 설계
@backend 알림 API 구현
```

#### 방법 C: Tab 자동완성

```
pl[Tab]  → planner
db[Tab]  → dba
ba[Tab]  → backend
```

### 2. 세션 모니터링

- **↑/↓**: 세션 목록 탐색
- **Space**: Peek 패널 열기 (빠른 미리보기)
- **Enter**: 세션에 Attach (전체 대화창)
- **←**: Detach (Agent View로 복귀)

### 3. 작업 흐름

```
1. Agent View 열기 (claude agents)
   ↓
2. 프롬프트 입력 및 디스패치 (Enter)
   ↓
3. 상태 모니터링 (자동)
   ↓
4. 필요시 Peek (Space) 또는 Attach (Enter)
   ↓
5. 작업 완료 확인 (Green 상태)
```

---

## 실전 워크플로우

### 시나리오 1: 개별 Agent 순차 실행

신규 "사용자 댓글" 기능 개발:

```bash
# 1. Agent View 시작
claude agents

# 2. 기획 단계
planner 사용자 댓글 기능 추가

# 3. Space로 결과 확인 후, DB 설계
dba comments 테이블 설계

# 4. API 개발
backend 댓글 CRUD API 구현

# 5. UI 개발
frontend 댓글 컴포넌트 구현

# 6. 검증
reviewer 댓글 기능 일관성 검증
```

### 시나리오 2: Controller 자동화

한 번에 전체 프로세스 실행:

```bash
# Agent View에서
controller 사용자 댓글 기능 전체 구현
```

Controller가 자동으로:
1. Planner 실행 → spec.md 작성
2. DBA 실행 → schema.sql 작성
3. Backend 실행 → API 코드 생성
4. Frontend 실행 → UI 코드 생성
5. Reviewer 실행 → 검증 및 피드백

### 시나리오 3: 병렬 기획

여러 기능을 동시에 기획:

```bash
# Agent View에서 순차적으로 디스패치
planner 알림 기능 추가
planner 검색 기능 추가
planner 통계 대시보드 추가
```

세 개의 기획이 동시에 백그라운드에서 진행됩니다.

---

## 주요 단축키

### Agent View 내 단축키

| 키 | 기능 |
|----|------|
| `↑/↓` | 세션 선택 이동 |
| `Enter` | 세션에 Attach |
| `Space` | Peek 패널 열기 (빠른 미리보기) |
| `Shift+Enter` | 디스패치 후 즉시 Attach |
| `→` | Attach |
| `←` | Detach (Agent View로 복귀) |
| `Ctrl+S` | 그룹 방식 전환 (상태/디렉토리) |
| `Ctrl+T` | 세션 고정/해제 (Pin/Unpin) |
| `Ctrl+R` | 세션 이름 변경 |
| `Ctrl+X` | 세션 중지 (2초 내 다시 누르면 삭제) |
| `Shift+↑/↓` | 세션 순서 변경 |
| `?` | 단축키 도움말 표시 |

### Shell 명령어

```bash
# Agent View 관리
claude agents              # Agent View 열기
claude attach <id>        # 특정 세션에 Attach
claude logs <id>          # 세션 최근 출력 보기

# 세션 제어
claude stop <id>          # 세션 중지
claude respawn <id>       # 중지된 세션 재시작
claude respawn --all      # 모든 중지 세션 재시작
claude rm <id>            # 세션 삭제

# 백그라운드 디스패치
claude --bg "prompt"                    # 기본
claude --bg "prompt" --agent planner    # Agent 지정
claude --bg "prompt" --model opus-4-5   # 모델 지정
```

### 세션 내 명령어

```bash
/bg <prompt>             # 현재 세션을 백그라운드로 이동
/background              # 동일 (긴 형식)
```

---

## 병렬 작업 활용

### 예시 1: 다중 기능 동시 개발

```bash
# Agent View에서
controller 알림 기능 구현
controller 검색 기능 구현
controller 통계 기능 구현
```

세 개의 기능이 독립적으로 병렬 개발됩니다.

### 예시 2: 단계별 병렬 실행

```bash
# 여러 기능의 기획을 먼저 완료
planner 기능A 추가
planner 기능B 추가
planner 기능C 추가

# 기획 완료 후, DB 설계 병렬 실행
dba 기능A 테이블 설계
dba 기능B 테이블 설계
dba 기능C 테이블 설계
```

### 주의사항

- **Quota 소비**: 10개 세션 병렬 = 약 10배 빠른 quota 소비
- **파일 충돌**: Git 리포지토리의 경우 자동으로 worktree 생성하여 충돌 방지
- **리소스 관리**: 너무 많은 세션을 동시에 실행하면 시스템 리소스 고갈 가능

---

## 세션 관리

### 세션 그룹

Agent View는 세션을 자동으로 그룹화합니다:

- **Pinned**: 고정된 세션 (Ctrl+T)
- **Ready for review**: Pull request 대기
- **Needs input**: 사용자 입력 필요
- **Working**: 실행 중
- **Completed**: 완료

### 그룹 조작

- `Ctrl+S`: 상태 기준 ↔ 디렉토리 기준 전환
- `Shift+↑/↓`: 세션 순서 변경
- Group 헤더에서 `Enter`: 그룹 접기/펼치기

### 세션 필터링

Agent View 입력창에서 필터 사용:

```
a:planner          # planner agent 세션만 표시
a:controller       # controller agent 세션만 표시
status:working     # 실행 중인 세션만 표시
status:completed   # 완료된 세션만 표시
```

### 세션 정리

```bash
# 완료된 세션 삭제
Ctrl+X (세션 선택 후)

# Shell에서 일괄 삭제
claude rm <id1> <id2> <id3>

# 중지된 모든 세션 삭제
claude rm --all-stopped
```

---

## 팁과 모범 사례

### 1. Controller 우선 사용

단순한 작업이 아니라면 Controller를 먼저 사용하세요:

```bash
# 좋은 예
controller 사용자 인증 기능 추가

# 나쁜 예 (수동으로 모든 단계 실행)
planner 인증 기획
# 완료 대기...
dba 인증 테이블 설계
# 완료 대기...
# ... (비효율적)
```

### 2. 세션 이름 변경

작업 내용을 명확히 하기 위해 이름을 변경하세요:

```bash
# Ctrl+R 누르고
"login-feature-planning"
"database-schema-refactor"
"api-endpoint-bugfix"
```

### 3. 자주 사용하는 세션 고정

```bash
# Ctrl+T로 고정
# Pinned 그룹 상단에 항상 표시됨
```

### 4. Peek 적극 활용

매번 Attach하지 말고 Space로 빠르게 확인:

```bash
Space → 빠른 확인 → Esc → 다음 세션
```

### 5. 병렬 작업 계획

독립적인 작업은 병렬로, 의존성 있는 작업은 순차로:

```bash
# 병렬 OK
planner 기능A
planner 기능B

# 순차 필요
planner 기능C
# 완료 대기 후
dba 기능C 테이블 설계
```

### 6. 정기적 정리

완료된 세션은 주기적으로 삭제:

```bash
# 매일 또는 매주
# Completed 그룹의 세션들 Ctrl+X로 삭제
```

---

## 문제 해결

### Q1: Agent가 인식되지 않아요

**확인사항:**
```bash
# .claude/agents/ 디렉토리 확인
ls .claude/agents/

# planner.md, dba.md 등이 있어야 함
```

**해결:**
```bash
# 프로젝트 루트에서 Agent View 실행
cd /workspace/chanho/ClaudeAgent
claude agents
```

### Q2: 세션이 멈춰있어요 (✻ 상태)

**원인:** 사용자 입력 대기 중

**해결:**
```bash
# Space로 Peek 또는 Enter로 Attach
# 질문 확인 후 답변 입력
```

### Q3: 세션이 실패했어요 (Red)

**확인:**
```bash
# Enter로 Attach하여 오류 메시지 확인
# 또는 Shell에서
claude logs <id>
```

**해결:**
- 오류 원인 파악 후 수정
- 필요시 세션 재시작: `claude respawn <id>`

### Q4: 여러 세션이 같은 파일을 수정하면?

**자동 처리:** Git 리포지토리의 경우 각 세션에 별도 worktree 생성

**수동 병합:**
```bash
# 세션 완료 후 변경사항 확인
git status

# 필요시 수동 병합
```

### Q5: 세션이 너무 느려요

**원인:**
- 복잡한 작업
- 많은 파일 읽기
- 네트워크 지연

**해결:**
- 작업을 더 작은 단위로 분할
- 구체적인 프롬프트 제공
- 불필요한 세션 중지: `claude stop <id>`

### Q6: Quota를 너무 빨리 소비해요

**원인:** 너무 많은 병렬 세션

**해결:**
```bash
# 병렬 세션 수 제한 (예: 3-5개)
# 완료된 세션은 즉시 중지
Ctrl+X
```

---

## 추가 리소스

### 공식 문서

- [Agents 및 병렬 작업](https://code.claude.com/docs/en/agents.md)
- [Subagents 설정](https://code.claude.com/docs/en/sub-agents.md)
- [Agent Teams](https://code.claude.com/docs/en/agent-teams.md)

### 프로젝트 문서

- [CLAUDE.md](./CLAUDE.md) - 프로젝트 개요 및 개발 가이드
- [spec.md](./spec.md) - 서비스 명세서
- [schema.sql](./schema.sql) - 데이터베이스 스키마

### Agent 정의 파일

- [.claude/agents/planner.md](./.claude/agents/planner.md)
- [.claude/agents/dba.md](./.claude/agents/dba.md)
- [.claude/agents/backend.md](./.claude/agents/backend.md)
- [.claude/agents/frontend.md](./.claude/agents/frontend.md)
- [.claude/agents/controller.md](./.claude/agents/controller.md)
- [.claude/agents/reviewer.md](./.claude/agents/reviewer.md)

---

## 시작하기

지금 바로 Agent View를 실행해보세요:

```bash
claude agents
```

그리고 첫 번째 작업을 디스패치하세요:

```
controller To-Do 앱에 카테고리 기능 추가
```

즐거운 개발 되세요! 🚀
