# ClaudeAgent Workspace

동일 에이전트로 여러 프로젝트를 병렬/순차 개발하기 위한 워크스페이스입니다.

## Directory Layout

- `projects/`: 새로 만드는 실제 프로젝트 폴더(프로젝트별 1개 디렉터리)
- `shared/`: 여러 프로젝트에서 공통으로 쓰는 자산/유틸/템플릿
- `docs/`: 운영/개발 문서
- `examples/sample-todo/`: 기존 테스트용 샘플 프로젝트 보관
- `.claude/agents/`: 멀티 에이전트 역할 정의

## Active Starter

- `projects/starter-project/`: 새 프로젝트 시작용 기본 스캐폴드(Python + npm)

## Quick Start (New Project)

1. `projects/` 아래에 새 프로젝트 폴더 생성
2. 필요한 기술 스택 초기화 (예: `npm init`, `python -m venv .venv`)
3. 공통 규칙/템플릿이 필요하면 `shared/`에서 재사용
4. 샘플 참고가 필요하면 `examples/sample-todo/` 확인

## Notes

- 루트는 워크스페이스 역할만 수행합니다.
- 테스트용 산출물(DB/샘플 앱)은 `examples/sample-todo/`로 분리했습니다.