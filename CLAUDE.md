# [회사명] 개발 Agent 회사 — 프로젝트 컨텍스트

## 회사 구조
이 프로젝트는 Agent 회사 방식으로 운영됩니다.
- 모든 인력은 .claude/agents/{역할}.md 로 정의됩니다
- 문서 업로드 → document-parser → project-manager → 개발팀 순서로 진행합니다
- 모든 개발 작업은 /workspace/{project_id}/ 안에서만 수행합니다
- workspace-map.json 에 정의된 소유권 범위를 절대 침범하지 않습니다

## 핵심 파일 위치
- 파싱 결과: .claude/output/parsed-spec.json
- 프로젝트 계획: .claude/output/project-plan.md
- 소유권 맵: .claude/output/workspace-map.json