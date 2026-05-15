# Agent Development Platform - 기능 명세서

## 1. 서비스 개요

### 목적
사용자가 요구사항 문서만 업로드하면 AI Agent 팀이 자동으로 프로젝트를 분석, 설계, 개발하여 POC 가능한 레벨의 완성된 시스템을 제공하는 플랫폼

### 주요 기능
- 요구사항 문서 업로드 및 프로젝트 자동 생성
- 프로젝트 목록 조회 및 관리
- Agent 팀 구성 관리
- 실시간 진행 상황 모니터링
- 프로젝트 결과물 다운로드

### 타겟 사용자
- SI 프로젝트 관리자
- 스타트업 창업자
- 개발팀 리더
- 프로토타입이 필요한 기획자

---

## 2. 사용자 시나리오

### 시나리오 1: 신규 프로젝트 생성

1. 사용자가 메인 화면에 접속한다
2. "새 프로젝트 생성" 버튼을 클릭한다
3. 프로젝트 정보를 입력한다
   - 프로젝트 이름
   - 설명
   - 요구사항 문서 업로드 (PDF, Word, Markdown)
4. "프로젝트 생성" 버튼을 클릭한다
5. 시스템이 프로젝트를 생성하고 Agent 파이프라인을 시작한다
6. 실시간 진행 상황 모니터링 화면으로 이동한다

### 시나리오 2: 프로젝트 진행 상황 모니터링

1. 사용자가 프로젝트 목록에서 진행 중인 프로젝트를 클릭한다
2. 실시간 진행 상황 화면이 표시된다
   - 현재 진행 단계 표시
   - 진행률 (0-100%)
   - 각 Agent의 작업 상태
   - 실시간 로그
3. 각 Agent의 산출물을 미리보기할 수 있다
4. 문제 발생 시 알림을 받는다

### 시나리오 3: 완료된 프로젝트 확인

1. 사용자가 완료된 프로젝트를 클릭한다
2. 프로젝트 결과 화면이 표시된다
   - 전체 산출물 목록
   - 검증 결과 리포트
   - 테스트 결과
3. "결과물 다운로드" 버튼으로 전체 프로젝트를 다운로드한다
4. "배포하기" 버튼으로 바로 배포할 수 있다 (선택사항)

### 시나리오 4: Agent 팀 구성 관리

1. 사용자가 "Agent 관리" 메뉴를 클릭한다
2. 사용 가능한 Agent 목록이 표시된다
   - Requirement Analyst
   - Architect
   - Planner
   - DBA
   - Backend Developer
   - Frontend Developer
   - Tester
   - DevOps Engineer
   - Tech Writer
   - Reviewer
3. 프로젝트에 사용할 Agent를 선택/해제할 수 있다
4. Agent별 설정을 조정할 수 있다 (우선순위, 옵션 등)

---

## 3. 화면 목록

| 화면명 | 경로 | 설명 | 접근 권한 |
|--------|------|------|-----------|
| 메인 대시보드 | / | 전체 프로젝트 통계 및 빠른 접근 | 로그인 필요 |
| 프로젝트 목록 | /projects | 모든 프로젝트 목록 조회 | 로그인 필요 |
| 프로젝트 생성 | /projects/new | 새 프로젝트 생성 | 로그인 필요 |
| 프로젝트 상세 | /projects/:id | 프로젝트 진행 상황 및 결과 | 로그인 필요 |
| Agent 관리 | /agents | Agent 팀 구성 관리 | 로그인 필요 |
| 설정 | /settings | 사용자 설정 | 로그인 필요 |
| 로그인 | /login | 사용자 인증 | 비로그인 |

---

## 4. 화면 상세

### 4.1 메인 대시보드 (/)

**표시 요소:**
- 전체 프로젝트 수
- 진행 중인 프로젝트 수
- 완료된 프로젝트 수
- 최근 프로젝트 목록 (최대 5개)
- "새 프로젝트 생성" 버튼

**동작:**
1. 대시보드 데이터 조회 API 호출: GET /api/dashboard
2. 통계 및 최근 프로젝트 표시
3. "새 프로젝트 생성" 클릭 시 → /projects/new 이동

### 4.2 프로젝트 목록 (/projects)

**표시 요소:**
- 프로젝트 카드 목록
  - 프로젝트 이름
  - 상태 (진행 중, 완료, 실패)
  - 진행률 (%)
  - 생성일
  - 마지막 업데이트 시간
- 필터: 상태별 필터 (전체, 진행 중, 완료, 실패)
- 정렬: 생성일, 이름, 진행률
- 검색: 프로젝트 이름 검색

**동작:**
1. 프로젝트 목록 조회 API 호출: GET /api/projects?status=&sort=&search=
2. 프로젝트 카드 클릭 시 → /projects/:id 이동

### 4.3 프로젝트 생성 (/projects/new)

**입력 요소:**
- 프로젝트 이름 (필수, 최대 100자)
- 설명 (선택, 최대 500자)
- 요구사항 문서 업로드 (필수, PDF/Word/Markdown, 최대 10MB)
- Agent 팀 선택 (선택, 기본값: 전체 Agent)

**버튼:**
- "프로젝트 생성" 버튼
- "취소" 버튼

**동작:**
1. 입력 값 검증
   - 프로젝트 이름: 필수, 1-100자
   - 문서: 필수, PDF/DOCX/MD, 최대 10MB
2. API 호출: POST /api/projects
3. 성공 시 → /projects/:id (진행 상황 모니터링)
4. 실패 시 → 에러 메시지 표시

**에러 처리:**
- 이름 누락: "프로젝트 이름을 입력하세요"
- 문서 누락: "요구사항 문서를 업로드하세요"
- 파일 크기 초과: "파일 크기는 10MB 이하여야 합니다"
- 잘못된 파일 형식: "PDF, Word, Markdown 파일만 업로드 가능합니다"

### 4.4 프로젝트 상세 (/projects/:id)

**탭 구성:**
- **진행 상황 탭**: 실시간 진행 모니터링
- **산출물 탭**: 생성된 파일 목록
- **로그 탭**: 실시간 로그
- **설정 탭**: 프로젝트 설정

#### 4.4.1 진행 상황 탭

**표시 요소:**
- 전체 진행률 (0-100%)
- 진행 단계 시각화 (파이프라인 다이어그램)
  - 요구사항 분석 (10%)
  - 아키텍처 설계 (20%)
  - 기획 (30%)
  - DB 설계 (40%)
  - Backend 구현 (55%)
  - Frontend 구현 (70%)
  - 테스트 (80%)
  - 배포 준비 (90%)
  - 문서화 (95%)
  - 최종 검증 (100%)
- 현재 작업 중인 Agent 표시
- 각 Agent 상태
  - 대기 중 (회색)
  - 진행 중 (파란색)
  - 완료 (초록색)
  - 실패 (빨간색)
- 실시간 로그 (최근 10개)

**동작:**
1. WebSocket 연결로 실시간 업데이트
2. 진행 상황 데이터 수신 및 화면 업데이트
3. Agent 상태 변경 시 알림

#### 4.4.2 산출물 탭

**표시 요소:**
- 산출물 폴더 트리
  - /docs (문서)
    - requirements.md
    - architecture.md
    - spec.md
    - README.md
    - API.md
  - /database
    - schema.sql
  - /backend
    - (소스 코드)
  - /frontend
    - (소스 코드)
  - /tests
    - (테스트 코드)
  - /infra
    - Dockerfile
    - docker-compose.yml
    - (IaC 코드)
- 파일 미리보기
- "전체 다운로드" 버튼 (ZIP)

**동작:**
1. 파일 클릭 시 미리보기 표시
2. "전체 다운로드" 클릭 시 ZIP 파일 다운로드

#### 4.4.3 로그 탭

**표시 요소:**
- 전체 로그 (시간순 정렬)
- 로그 레벨 필터 (전체, 정보, 경고, 에러)
- 검색 기능

**동작:**
1. 로그 조회 API 호출: GET /api/projects/:id/logs
2. WebSocket으로 실시간 로그 수신

### 4.5 Agent 관리 (/agents)

**표시 요소:**
- Agent 카드 목록
  - Agent 이름
  - 설명
  - 상태 (활성/비활성)
  - 사용 횟수
  - 성공률
- Agent 상세 정보
  - 역할
  - 입력/출력
  - 책임 범위

**동작:**
1. Agent 목록 조회 API 호출: GET /api/agents
2. Agent 활성화/비활성화 토글
3. Agent 설정 변경

---

## 5. 기능 목록

### Must Have (필수)

#### 프로젝트 관리
- [ ] 프로젝트 생성 (요구사항 문서 업로드)
- [ ] 프로젝트 목록 조회
- [ ] 프로젝트 상세 조회
- [ ] 프로젝트 삭제

#### Agent 파이프라인
- [ ] Requirement Analyst 실행
- [ ] Architect 실행
- [ ] Planner 실행
- [ ] DBA 실행
- [ ] Backend 실행
- [ ] Frontend 실행
- [ ] Tester 실행
- [ ] DevOps 실행
- [ ] Tech Writer 실행
- [ ] Reviewer 실행

#### 진행 상황 모니터링
- [ ] 실시간 진행률 표시
- [ ] 각 Agent 상태 표시
- [ ] 실시간 로그 표시
- [ ] WebSocket 연결

#### 산출물 관리
- [ ] 산출물 파일 목록 조회
- [ ] 파일 미리보기
- [ ] 전체 프로젝트 다운로드 (ZIP)

### Should Have (권장)

- [ ] 프로젝트 검색 기능
- [ ] 프로젝트 필터링 (상태별)
- [ ] Agent 팀 커스터마이징
- [ ] 프로젝트 복제 기능
- [ ] 에러 재시도 기능
- [ ] 이메일 알림 (프로젝트 완료 시)

### Nice to Have (선택)

- [ ] 프로젝트 템플릿 기능
- [ ] Agent 성능 통계
- [ ] 프로젝트 공유 기능
- [ ] 다국어 지원
- [ ] 다크 모드

---

## 6. API 요구사항

### 6.1 인증

**POST /api/auth/login**

Request:
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

Response (200):
```json
{
  "token": "string",
  "user": {
    "id": "number",
    "email": "string",
    "name": "string"
  }
}
```

**인증 방식:** JWT Bearer Token

---

### 6.2 대시보드

**GET /api/dashboard**

Response (200):
```json
{
  "totalProjects": 10,
  "inProgressProjects": 3,
  "completedProjects": 7,
  "recentProjects": [
    {
      "id": 1,
      "name": "Todo App",
      "status": "completed",
      "progress": 100,
      "createdAt": "2026-01-15T10:00:00Z",
      "updatedAt": "2026-01-15T15:00:00Z"
    }
  ]
}
```

---

### 6.3 프로젝트 API

**POST /api/projects**

Request (multipart/form-data):
```
name: string (required, max 100)
description: string (optional, max 500)
document: file (required, PDF/DOCX/MD, max 10MB)
agents: array of string (optional, default: all)
```

Response (201):
```json
{
  "id": 1,
  "name": "Todo App",
  "description": "할일 관리 앱",
  "status": "in_progress",
  "progress": 0,
  "createdAt": "2026-01-15T10:00:00Z"
}
```

**GET /api/projects**

Query Parameters:
- status: string (optional) - `all`, `in_progress`, `completed`, `failed`
- sort: string (optional) - `created_at`, `name`, `progress`
- search: string (optional)

Response (200):
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Todo App",
      "description": "할일 관리 앱",
      "status": "in_progress",
      "progress": 55,
      "createdAt": "2026-01-15T10:00:00Z",
      "updatedAt": "2026-01-15T11:30:00Z"
    }
  ],
  "total": 10
}
```

**GET /api/projects/:id**

Response (200):
```json
{
  "id": 1,
  "name": "Todo App",
  "description": "할일 관리 앱",
  "status": "in_progress",
  "progress": 55,
  "currentStage": "backend",
  "agents": [
    {
      "name": "Requirement Analyst",
      "status": "completed",
      "progress": 100
    },
    {
      "name": "Architect",
      "status": "completed",
      "progress": 100
    },
    {
      "name": "Backend",
      "status": "in_progress",
      "progress": 55
    }
  ],
  "outputs": [
    "/docs/requirements.md",
    "/docs/architecture.md",
    "/docs/spec.md",
    "/database/schema.sql"
  ],
  "createdAt": "2026-01-15T10:00:00Z",
  "updatedAt": "2026-01-15T11:30:00Z"
}
```

**DELETE /api/projects/:id**

Response (200):
```json
{
  "deleted": true
}
```

---

### 6.4 프로젝트 산출물 API

**GET /api/projects/:id/files**

Response (200):
```json
{
  "files": [
    {
      "path": "/docs/requirements.md",
      "size": 12345,
      "createdAt": "2026-01-15T10:05:00Z"
    },
    {
      "path": "/docs/architecture.md",
      "size": 23456,
      "createdAt": "2026-01-15T10:10:00Z"
    }
  ]
}
```

**GET /api/projects/:id/files/*path**

Response (200):
```
(파일 내용)
```

**GET /api/projects/:id/download**

Response (200):
```
Content-Type: application/zip
Content-Disposition: attachment; filename="project-1.zip"

(ZIP 파일)
```

---

### 6.5 로그 API

**GET /api/projects/:id/logs**

Query Parameters:
- level: string (optional) - `all`, `info`, `warning`, `error`
- limit: number (optional, default: 100)

Response (200):
```json
{
  "logs": [
    {
      "timestamp": "2026-01-15T10:00:00Z",
      "level": "info",
      "agent": "Requirement Analyst",
      "message": "요구사항 분석 시작"
    },
    {
      "timestamp": "2026-01-15T10:05:00Z",
      "level": "info",
      "agent": "Requirement Analyst",
      "message": "requirements.md 작성 완료"
    }
  ]
}
```

---

### 6.6 WebSocket API

**WS /api/projects/:id/progress**

Server → Client:
```json
{
  "type": "progress_update",
  "data": {
    "progress": 55,
    "currentStage": "backend",
    "agentStatus": {
      "Backend": "in_progress"
    }
  }
}
```

```json
{
  "type": "log",
  "data": {
    "timestamp": "2026-01-15T10:30:00Z",
    "level": "info",
    "agent": "Backend",
    "message": "API 구현 시작"
  }
}
```

```json
{
  "type": "completed",
  "data": {
    "projectId": 1,
    "status": "completed",
    "progress": 100
  }
}
```

---

### 6.7 Agent API

**GET /api/agents**

Response (200):
```json
{
  "agents": [
    {
      "id": "requirement-analyst",
      "name": "Requirement Analyst",
      "description": "요구사항 분석 전문가",
      "status": "active",
      "usageCount": 150,
      "successRate": 98.5
    }
  ]
}
```

---

## 7. 비기능 요구사항

### 성능
- API 응답시간: 평균 300ms 이하
- 파일 업로드: 10MB 파일 업로드 5초 이내
- WebSocket 지연: 실시간 업데이트 1초 이내

### 보안
- HTTPS 필수
- JWT 토큰 기반 인증
- 파일 업로드: 바이러스 스캔
- XSS, CSRF 방지

### 확장성
- 동시 프로젝트: 최소 100개 처리 가능
- 사용자: 최소 1,000명 지원

### 가용성
- 시스템 가동률: 99% 이상

---

## 8. 제약사항

- 요구사항 문서 크기: 최대 10MB
- 프로젝트 이름: 최대 100자
- 동시 생성 가능 프로젝트: 사용자당 10개
- 프로젝트 보관 기간: 30일 (이후 자동 삭제 또는 아카이브)

---

## 9. 용어 정리

| 용어 | 정의 |
|------|------|
| Agent | 특정 역할을 수행하는 AI 작업 단위 |
| 파이프라인 | Agent들이 순차적으로 실행되는 프로세스 |
| 산출물 | Agent가 생성한 파일 (코드, 문서 등) |
| POC | Proof of Concept, 개념 증명 |
| 진행률 | 전체 파이프라인 중 완료된 비율 (0-100%) |

---

## 10. 향후 확장 계획

- Agent Marketplace: 커스텀 Agent 추가 가능
- 협업 기능: 팀원 초대 및 권한 관리
- 버전 관리: 프로젝트 버전 히스토리
- 배포 연동: AWS, GCP 등 직접 배포
- AI 코치: Agent 추천 및 최적화 제안
