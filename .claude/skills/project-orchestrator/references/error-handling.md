# Error Handling — 에러 핸들링 전략

AI Agent Company 워크플로우에서 발생 가능한 에러 유형과 처리 전략.

---

## 목차

1. [에러 핸들링 원칙](#1-에러-핸들링-원칙)
2. [Phase별 에러 유형](#2-phase별-에러-유형)
3. [재시도 전략](#3-재시도-전략)
4. [부분 실패 처리](#4-부분-실패-처리)
5. [사용자 알림 기준](#5-사용자-알림-기준)

---

## 1. 에러 핸들링 원칙

### 핵심 원칙

1. **1회 재시도**: 모든 에러는 1회 재시도 후 재실패 시 다음 전략 적용
2. **부분 진행**: 일부 실패해도 가능한 범위에서 진행
3. **누락 명시**: 실패한 부분은 최종 보고서에 명확히 기록
4. **데이터 보존**: 실패한 작업의 부분 산출물도 삭제하지 않고 보존
5. **상충 데이터 병기**: 충돌하는 정보는 출처를 명시하여 모두 보존

### 실패의 정의

| 수준 | 정의 | 조치 |
|------|------|------|
| **Critical** | Phase 전체 실패, 다음 Phase 진행 불가 | 사용자에게 알리고 중단 |
| **Major** | 핵심 에이전트 실패, 산출물 품질 저하 | 1회 재시도, 실패 시 대체 전략 |
| **Minor** | 보조 에이전트 실패, 진행 가능 | 누락 명시하고 계속 |

---

## 2. Phase별 에러 유형

### Phase 1: 문서 분석 에러

#### 에러 1-1: 문서 읽기 실패

**원인**:
- 파일 경로 오류
- 지원하지 않는 형식
- 파일 암호화/손상

**탐지**:
```python
if not exists(document_path):
    raise Error("문서 파일을 찾을 수 없습니다")
if file_extension not in [".pdf", ".docx", ".xlsx", ".md", ".txt"]:
    raise Error("지원하지 않는 파일 형식")
```

**처리 전략**:
1. 파일 경로 재확인 (사용자에게 질문)
2. 대체 형식 변환 제안 (예: PDF → 텍스트 추출)
3. 구두 요구사항으로 대체 (사용자 메시지 → parsed-spec.json)

**심각도**: Critical (다음 Phase 진행 불가)

#### 에러 1-2: parsed-spec.json 형식 오류

**원인**:
- document-parser가 잘못된 JSON 생성
- 필수 필드 누락

**탐지**:
```python
try:
    spec = json.load("_workspace/01_parsed-spec.json")
    assert "project_name" in spec
    assert "features" in spec
    assert "tech_stack" in spec
except (JSONDecodeError, AssertionError) as e:
    raise Error("parsed-spec.json 형식 오류")
```

**처리 전략**:
1. 1회 재시도: document-parser 재호출
2. 수동 수정: 오케스트레이터가 JSON 직접 수정 (기본 구조 보완)
3. 사용자 확인: 수정된 spec을 사용자에게 보여주고 승인 요청

**심각도**: Major

---

### Phase 2: 프로젝트 계획 에러

#### 에러 2-1: project-manager 실패

**원인**:
- .claude/agents/ 읽기 실패
- WBS 생성 로직 에러

**탐지**:
```python
if not exists("_workspace/02_project-plan.md"):
    raise Error("project-plan.md 생성 실패")
```

**처리 전략**:
1. 1회 재시도
2. 기본 WBS 템플릿 사용:
   ```yaml
   stages:
     - stage: 1
       name: "분석·설계"
       tasks: [{ id: T-001, name: "요건 분석", agent: system-analyst }]
     - stage: 2
       name: "개발"
       tasks: [
         { id: T-002, name: "백엔드", agent: backend-developer },
         { id: T-003, name: "프론트", agent: frontend-developer }
       ]
   ```
3. 사용자에게 기본 템플릿 사용 알림

**심각도**: Major

#### 에러 2-2: workspace-map.json 충돌

**원인**:
- 여러 에이전트가 같은 경로를 owns
- forbidden 규칙 위반

**탐지**:
```python
ownership_map = json.load("_workspace/02_workspace-map.json")
all_owns = []
for agent, paths in ownership_map["ownership"].items():
    all_owns.extend(paths["owns"])

# 중복 검사
if len(all_owns) != len(set(all_owns)):
    raise Error("파일 소유권 충돌")
```

**처리 전략**:
1. 오케스트레이터가 충돌 해결:
   - 충돌 경로를 먼저 명시한 에이전트에게 할당
   - 나머지 에이전트의 owns에서 제거
2. workspace-map.json 재생성
3. 수정 사항을 Phase 3 팀원 프롬프트에 반영

**심각도**: Major (해결 가능)

---

### Phase 3: 병렬 개발 에러

#### 에러 3-1: 팀원 1명 중지

**원인**:
- 에이전트 크래시
- 컨텍스트 윈도우 초과
- 네트워크 타임아웃

**탐지**:
- 리더가 유휴 알림 수신: "backend-dev가 응답하지 않습니다"
- TaskGet으로 작업 상태 확인: status = "failed"

**처리 전략**:

```
1단계: 상태 확인
SendMessage(to: "backend-dev", message: "상태 확인. 진행 중인 작업이 있나요?")
→ 응답 없음

2단계: 재시작 시도
Agent(
  prompt: "이전 작업을 이어서 수행하세요. 기존 산출물: workspace/{project_id}/src/api/",
  subagent_type: "backend",
  model: "opus"
)
→ 재시작 성공 시 계속 진행

3단계: 재시작 실패 시 작업 재할당
SendMessage(to: "frontend-dev", message: "backend-dev 작업 실패. 모의 API로 대체 가능한가요?")
→ frontend-dev: "네, 모의 데이터로 진행하겠습니다"

4단계: 최종 보고서에 누락 명시
README.md에 추가:
"## 알려진 이슈
- 백엔드 API 미구현. 프론트엔드는 모의 데이터 사용 중.
- 실제 배포 전 backend 구현 필요."
```

**심각도**: Major (대체 전략 가능)

#### 에러 3-2: 팀원 과반 실패

**원인**:
- 시스템 전체 장애
- 잘못된 요구사항 (구현 불가능)

**탐지**:
```python
failed_count = sum(1 for member in team_members if member.status == "failed")
if failed_count >= len(team_members) / 2:
    raise Error("팀원 과반 실패")
```

**처리 전략**:
1. 사용자에게 즉시 알림:
   ```
   "Phase 3에서 팀원 과반(backend-dev, frontend-dev)이 실패했습니다.
   부분 결과로 진행하시겠습니까? (예: DB 스키마와 인프라만)"
   ```
2. 사용자 선택:
   - "진행": 성공한 팀원의 산출물만으로 Phase 4 진행
   - "중단": 전체 프로세스 중단, 디버깅 필요

**심각도**: Critical

#### 에러 3-3: 파일 소유권 충돌

**원인**:
- 팀원이 workspace-map 무시하고 타 경로 수정
- Git 충돌 발생

**탐지**:
```bash
# Phase 3 종료 시 workspace-map 검증
for agent in team_members:
  for file in modified_files[agent]:
    if file not in workspace_map[agent]["owns"]:
      raise Warning(f"{agent}가 소유하지 않은 파일 수정: {file}")
```

**처리 전략**:
1. 즉시 복구하지 않음 (Phase 4 tech-lead에게 위임)
2. 충돌 파일 목록을 `_workspace/03_conflicts.txt`에 기록:
   ```
   src/main.py: backend-dev 수정, frontend-dev도 수정
   → tech-lead가 Phase 4에서 병합 필요
   ```
3. Phase 4 tech-lead 프롬프트에 충돌 목록 전달

**심각도**: Minor (Phase 4에서 해결 가능)

---

### Phase 4: 검증 및 통합 에러

#### 에러 4-1: security-engineer 실패

**원인**:
- 보안 도구 설치 실패
- 코드 분석 타임아웃

**탐지**:
```python
if not exists("_workspace/04_security-report.md"):
    raise Error("보안 감사 실패")
```

**처리 전략**:
1. 1회 재시도
2. 재실패 시 보안 감사 생략:
   - `_workspace/04_security-report.md` 생성 (빈 파일)
   - 내용: "보안 감사 미완료. 수동 보안 리뷰 권장."
3. README.md에 "보안 감사 미완료" 명시

**심각도**: Minor (배포 전 수동 리뷰로 대체 가능)

#### 에러 4-2: tester 실패

**원인**:
- 테스트 프레임워크 설치 실패
- 코드 구조가 테스트 불가능

**탐지**:
```python
if not glob("workspace/{project_id}/tests/*.py"):
    raise Warning("테스트 코드 생성 실패")
```

**처리 전략**:
1. 1회 재시도
2. 재실패 시 테스트 없이 진행:
   - README.md에 "테스트 코드 미작성" 명시
   - "수동 테스트 체크리스트" 섹션 추가
3. 사용자에게 수동 테스트 권장

**심각도**: Minor

#### 에러 4-3: tech-lead 통합 실패

**원인**:
- Git 병합 충돌 해결 실패
- 빌드 에러

**탐지**:
```python
# 통합 후 빌드 검증
result = run_command("docker-compose build")
if result.returncode != 0:
    raise Error("빌드 실패")
```

**처리 전략**:
1. 통합 전 상태로 롤백:
   - `workspace/{project_id}/` → Phase 3 종료 직후 상태 유지
   - 충돌 파일만 `workspace/{project_id}/_conflicts/`로 이동
2. README.md에 "알려진 이슈" 섹션 추가:
   ```markdown
   ## 알려진 이슈
   - 빌드 실패: src/main.py와 src/App.jsx 간 충돌
   - 해결 방법: [상세 설명]
   ```
3. 사용자에게 수동 통합 필요 안내

**심각도**: Major (사용자 개입 필요)

---

## 3. 재시도 전략

### 재시도 조건

| 에러 유형 | 재시도 | 이유 |
|----------|--------|------|
| 네트워크 타임아웃 | O | 일시적 장애 가능성 높음 |
| 파일 읽기 실패 | O | 경로 오타, 권한 문제 등 해결 가능 |
| JSON 파싱 에러 | O | 에이전트 재실행으로 수정 가능 |
| 컨텍스트 윈도우 초과 | X | 재시도해도 동일 결과 |
| 구현 불가능 (요구사항 문제) | X | 에이전트 문제 아님 |
| 도구 미설치 | X | 환경 문제, 재시도 무의미 |

### 재시도 구현

```python
def retry_agent(agent_type, prompt, max_retries=1):
    for attempt in range(max_retries + 1):
        try:
            result = Agent(
                prompt=prompt,
                subagent_type=agent_type,
                model="opus"
            )
            return result
        except Exception as e:
            if attempt < max_retries:
                print(f"재시도 {attempt + 1}/{max_retries}...")
                time.sleep(5)  # 5초 대기 후 재시도
            else:
                raise Error(f"{agent_type} 실패: {e}")
```

### 재시도 간격

- 1회 재시도: 5초 대기 (네트워크 복구, 리소스 정리 시간)
- 에이전트 팀: 재시도 없음 (팀원 재시작 또는 작업 재할당으로 대체)

---

## 4. 부분 실패 처리

### 부분 진행 원칙

**"최선의 부분 결과를 제공하라"**

일부 실패해도 성공한 부분은 사용자에게 가치가 있다. 전체 중단보다 부분 진행을 우선한다.

### 부분 진행 예시

#### 예시 1: backend 실패, frontend 성공

**상황**:
- Phase 3에서 backend-dev 실패
- frontend-dev, db-engineer, devops 성공

**조치**:
1. frontend가 모의 API 사용하도록 수정
2. Phase 4 진행 (보안 감사는 frontend만, 테스트는 모의 API 기반)
3. README.md:
   ```markdown
   ## 현재 상태
   - ✅ 프론트엔드 UI
   - ✅ DB 스키마
   - ✅ Docker 설정
   - ❌ 백엔드 API (미구현)

   ## 다음 단계
   1. backend 수동 구현
   2. 모의 API 제거
   3. 통합 테스트
   ```

**사용자 가치**: 프론트엔드 UI 확인 가능, 디자인 검토 가능

#### 예시 2: 보안 감사 실패, 나머지 성공

**상황**:
- Phase 4-1 security-engineer 실패
- Phase 4-2, 4-3 성공

**조치**:
1. 보안 감사 생략
2. README.md "보안" 섹션에 수동 체크리스트 추가:
   ```markdown
   ## 보안 체크리스트 (수동 확인 필요)
   - [ ] SQL Injection 방어 확인
   - [ ] XSS 필터링 확인
   - [ ] 인증 토큰 검증
   - [ ] HTTPS 강제
   ```

**사용자 가치**: 완전한 프로젝트, 수동 보안 리뷰로 보완 가능

---

## 5. 사용자 알림 기준

### 즉시 알림 (Immediate)

사용자 개입이 필요한 Critical 에러:

- Phase 1-2 실패 (다음 Phase 진행 불가)
- Phase 3 팀원 과반 실패
- Phase 4 tech-lead 통합 실패 + 빌드 불가

**알림 형식**:
```
⚠️  Phase {N} 실패

에러: {에러 메시지}

조치 필요:
1. [옵션 1]
2. [옵션 2]

부분 결과: _workspace/ 디렉토리 참고
```

### 완료 후 알림 (Post-completion)

Minor 에러는 완료 보고서에 포함:

- 보안 감사 실패
- 테스트 코드 누락
- 팀원 1명 실패 (대체 전략으로 진행 완료)

**알림 형식**:
```
✅ 프로젝트 생성 완료

프로젝트 경로: workspace/{project_id}/

⚠️  알려진 이슈:
- 보안 감사 미완료 (수동 리뷰 권장)
- 테스트 코드 미작성 (수동 테스트 필요)

상세: workspace/{project_id}/README.md 참고
```

### 알림하지 않음 (Silent)

자동 복구 가능한 에러:

- 1회 재시도로 성공
- workspace-map 충돌 (오케스트레이터가 자동 해결)
- 파일 경로 자동 수정

---

## 에러 로그 형식

모든 에러는 `_workspace/error-log.txt`에 기록:

```
[2026-05-26 10:23:45] Phase 1 - document-parser
Error: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
Retry: 1/1
Status: 재시도 성공

[2026-05-26 10:35:12] Phase 3 - backend-dev
Error: AgentTimeout: No response after 300s
Retry: 1/1
Status: 재시도 실패, 작업 재할당 (frontend-dev에게 모의 API 지시)

[2026-05-26 10:50:33] Phase 4 - security-engineer
Error: Tool not found: owasp-zap
Retry: 0/1 (재시도 불가)
Status: 보안 감사 생략, README에 수동 체크리스트 추가
```

---

## 참고

- 파이프라인 패턴: [pipeline-patterns.md](pipeline-patterns.md)
- 팀 조율 프로토콜: [team-coordination.md](team-coordination.md)
