# /agent-mode

Agent 모드 진입/운영 기준 문서.

## 목적
- `.claude`에 정의된 agent/skill/command 체계를 기준으로 프로젝트를 단계적으로 실행한다.
- Claude와 Codex가 같은 오케스트레이션 자산(`.claude/*`)을 참조하도록 맞춘다.

## 사용
```bash
/agent-mode on
/agent-mode off
```

## on 일 때 동작
1. 역할 로딩: `.claude/agents/*.md`
2. 워크플로우 적용: `.claude/commands/start-project.md`
3. 스킬 참조: `.claude/skills/*/SKILL.md`
4. 산출물 기록: `.claude/output/`

## off 일 때 동작
- 단일 에이전트(일반 모드)로 처리한다.
- 기존 코드/문서 수정 규칙은 동일하게 유지한다.

## 주의사항
- 생성 산출물은 기본적으로 `workspace/` 또는 `projects/*/workspace/` 하위에 둔다.
- `.claude/output/`는 런타임 출력이며 커밋 대상에서 제외한다.
