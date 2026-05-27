# Repository Guidelines

## Project Structure & Module Organization
This repository is an agent-platform monorepo. Core orchestration assets live in `.claude/` (`agents/`, `commands/`, `skills/`, and runtime output in `.claude/output/`).  
Product code is centered in `projects/starter-project/`:
- `python/`: FastAPI backend (`src/main.py`, adapters, CLI integration)
- `web/`: React + Vite frontend
- `server/`: Express proxy/server utilities

Reference implementations are under `examples/`, shared docs in `docs/`, and generated project workspaces in `workspace/` and `projects/*/workspace/` (treated as runtime output).

## Build, Test, and Development Commands
Run commands from the relevant module directory.

- Backend setup/run:
  `cd projects/starter-project/python && pip install -r requirements.txt && uvicorn src.main:app --host 0.0.0.0 --port 3003 --reload`
- Frontend dev:
  `cd projects/starter-project/web && npm install && npm run dev`
- Frontend production build:
  `cd projects/starter-project/web && npm run build`
- Starter server:
  `cd projects/starter-project/server && npm install && npm run dev` (or `npm start`)
- Top-level proxy:
  `cd proxy && npm install && npm start`

## Coding Style & Naming Conventions
Use 4-space indentation in Python and standard ES module style in JS/TS (`type: "module"` packages).  
Follow existing naming patterns:
- Python: `snake_case` functions/files, `PascalCase` Pydantic models
- Frontend: component files in `PascalCase` when adding React components
- Markdown agent definitions: kebab-case filenames in `.claude/agents/`

Keep changes scoped; do not commit generated output from `workspace/` or `.claude/output/`.

## Testing Guidelines
Current tests are script-style integration checks (not a full pytest suite):
- `projects/starter-project/python/test_api.py`
- `projects/starter-project/python/test_claude_cli.py`
- `projects/starter-project/test-ollama.py`

Run them with `python <script>` after starting required local services (typically backend on `:3003`). Add new tests near the module they validate, named `test_*.py`.

## Commit & Pull Request Guidelines
Recent commits use short, task-focused subjects (often date-prefixed, e.g. `20260526 - ...`, plus phase-based messages). Prefer:
- one logical change per commit
- imperative, specific subject lines

For PRs, include:
- what changed and why
- impacted paths (for example, `projects/starter-project/python/src/main.py`)
- verification steps/commands run
- screenshots or API examples when UI/behavior changes are user-visible

## Agent Mode Activation
Use `.claude/` as the source of truth for agent orchestration in this repo.

- Agent definitions: `.claude/agents/*.md`
- Workflow command spec: `.claude/commands/start-project.md`
- Skill packs: `.claude/skills/*/SKILL.md`
- Runtime outputs: `.claude/output/`

For Codex runs, when the user asks for "agent mode" (or equivalent), treat it as:
1. Load the relevant role definitions from `.claude/agents/`.
2. Follow the staged workflow in `.claude/commands/start-project.md`.
3. Keep artifacts under `.claude/output/` and project work under `workspace/`.

Claude-side experimental team mode is enabled by:
- `.claude/settings.json` -> `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`
