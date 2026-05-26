# /start-project — 문서 업로드 후 프로젝트 파이프라인 시작

SI 개발 Agent 회사의 전체 파이프라인을 시작하는 진입점 커맨드입니다.

---

## 사용법

```bash
/start-project [문서 경로]
```

---

## 예시

```bash
/start-project ./docs/rfp.pdf
/start-project ./docs/requirements.xlsx
/start-project ./docs/기능명세서.md
/start-project ./docs/requirements.txt
```

---

## 실행 흐름

### Stage 1: 문서 파싱
```
document-parser 에이전트 실행
→ .claude/output/parsed-spec.json 생성
→ clarifications_needed 확인
```

**clarifications_needed가 있으면:**
- 사용자에게 질문 목록 제시
- 사용자 답변 받아 parsed-spec.json 업데이트

### Stage 2: 프로젝트 계획
```
project-manager 에이전트 실행
→ .claude/output/project-plan.md 생성
→ .claude/output/workspace-map.json 생성
→ 사용자에게 요약 제시
```

**사용자 확인 후:**
- OK → Stage 3 진행
- 수정 요청 → project-manager 재실행

### Stage 3: 분석·설계
```
tech-lead가 workspace-map.json 배포
→ system-analyst 실행 (요건 정제, API 명세)
→ solution-architect 실행 (아키텍처 설계)
```

### Stage 4: 병렬 개발
```
tech-lead 조율 하에 병렬 실행:
- backend-developer (API 구현)
- frontend-developer (UI 구현)
- database-engineer (DB 스키마)
```

### Stage 5: 인프라·보안·QA
```
병렬 실행:
- devops-engineer (Docker, CI/CD)
- security-engineer (OWASP 감사)
- qa-lead (테스트 코드)
```

### Stage 6: 문서화 및 검증
```
- tech-writer (문서 작성)
- reviewer (최종 검증)
```

### Stage 7: 패키징
```
devops-engineer가 최종 패키징:
- .claude/ 디렉토리 제외
- ZIP 파일 생성
- 별도 Git 레포 생성 가능
```

---

## 진행 상황 확인

```bash
/status [project_id]
```

현재 진행 중인 단계 및 완료된 태스크 확인

---

## 파이프라인 중단

```bash
/stop [project_id]
```

---

## 주의사항

1. **문서 형식**: PDF, DOCX, XLSX, MD, TXT 지원
2. **파일 크기**: 최대 10MB
3. **workspace 격리**: 모든 작업은 `/workspace/{project_id}/` 내에서만 수행
4. **소유권 준수**: workspace-map.json 정의된 경로만 수정 가능
5. **.claude/ 제외**: 최종 납품 시 .claude/ 디렉토리는 ZIP에 포함하지 않음

---

## 출력물

### 문서
- `docs/requirements.md` - 상세 요구사항
- `docs/api-spec.md` - API 명세
- `docs/architecture.md` - 아키텍처 설계
- `docs/security-report.md` - 보안 감사 보고서
- `README.md` - 프로젝트 개요

### 코드
- `src/` - 소스 코드 (backend, frontend)
- `migrations/` - DB 마이그레이션
- `tests/` - 테스트 코드

### 인프라
- `Dockerfile` - 컨테이너 정의
- `docker-compose.yml` - 로컬 실행 환경
- `.github/workflows/` - CI/CD 파이프라인

---

## 에러 처리

### 문서 파싱 실패
```
document-parser가 파싱에 실패한 경우:
1. 문서 형식 확인
2. 문서 내용 구조 확인
3. 수동으로 Markdown 형식으로 작성하여 재시도
```

### Agent 배정 실패
```
project-manager가 적절한 Agent를 찾지 못한 경우:
1. .claude/agents/ 디렉토리 확인
2. 필요한 Agent 추가 작성
3. project-manager 재실행
```

### 보안 취약점 발견
```
security-engineer가 Critical 취약점 발견:
1. 파이프라인 일시 중단
2. 해당 Agent에게 수정 요청
3. 수정 완료 후 security-engineer 재실행
```

---

## 고급 옵션

### 특정 단계부터 시작
```bash
/start-project ./docs/rfp.pdf --from stage-3
```

### 특정 Agent 제외
```bash
/start-project ./docs/rfp.pdf --skip security-engineer
```

### POC 모드 (빠른 납품)
```bash
/start-project ./docs/rfp.pdf --mode poc
# devops, security 생략
```

---

## 참고

- 핵심 파일: `.claude/output/parsed-spec.json`, `project-plan.md`, `workspace-map.json`
- 회사 규칙: `CLAUDE.md`
- Agent 목록: `.claude/agents/*.md`
