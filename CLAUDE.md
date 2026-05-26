# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Agent Development Company platform that automatically generates POC-ready projects from requirement documents. The system consists of:

1. **Agent Company Framework** - `.claude/agents/` contains specialized agent role definitions
2. **Starter Project** - `projects/starter-project/` is a working reference implementation with:
   - Python FastAPI backend (port 3003)
   - React frontend (port 5173)
   - Proxy server (port 3456) for Claude CLI integration
   - Multi-LLM support (Claude, OpenAI, Ollama, Manus)

## Architecture

### Three-Tier Structure

```
Frontend (React + Vite)
    ↓
Backend (FastAPI + Python)
    ↓
Multiple LLM Providers (Claude API, OpenAI, Ollama, Manus API)
```

**Key Integration**: The backend includes `claude_subprocess/` module for spawning Claude CLI processes with JSON streaming output parsing.

### Agent Company Workflow

```
Document Upload → document-parser → project-manager → Development Team
                                                     ↓
                                    Backend/Frontend/Database/DevOps agents work in parallel
                                                     ↓
                                    Security/QA/Documentation → Final Review
```

**Critical Files:**
- `.claude/output/parsed-spec.json` - Standardized requirements (shared by all agents)
- `.claude/output/workspace-map.json` - File ownership map (prevents conflicts during parallel development)
- `.claude/output/project-plan.md` - WBS breakdown

**Workspace Isolation**: All generated project code lives in `/workspace/{project_id}/` and agents must respect ownership boundaries defined in workspace-map.json.

## Development Commands

### Backend (Python)

```bash
# Navigate to backend
cd projects/starter-project/python

# Install dependencies
pip install -r requirements.txt

# Run server (port 3003)
python -m src.main
# or with custom port
PORT=8000 python -m src.main
```

### Frontend (React)

```bash
# Navigate to frontend
cd projects/starter-project/web

# Install dependencies
npm install

# Run dev server (port 5173)
npm run dev

# Build for production
npm run build
```

### Proxy Server

```bash
# Navigate to proxy
cd proxy

# Install dependencies
npm install

# Run proxy (port 3456)
npm start
```

**Note**: The proxy server is currently manual-start only. It's used for POC code generation (Step 6 in the UI), not for regular LLM API calls.

## LLM Provider Integration

### Supported Providers

The system supports multiple LLM providers with a unified interface:

1. **Claude (Anthropic API)** - Direct API calls to `https://api.anthropic.com/v1/messages`
2. **OpenAI (Codex)** - Direct API calls to `https://api.openai.com/v1/chat/completions`
3. **Ollama (Local LLM)** - Calls to local Ollama server at configurable endpoint
4. **Manus AI** - Task-based API using `https://api.manus.ai/v2/task.*` endpoints

### Manus API Special Handling

Manus uses a different pattern than other providers:

- **Authentication**: Custom `x-manus-api-key` header (NOT `Authorization: Bearer`)
- **Workflow**: Create task → Poll `task.listMessages` → Extract assistant responses
- **Request Format**:
  ```json
  {
    "message": { "content": [{"text": "..."}] },
    "agent_profile": "manus-1.6|manus-1.6-lite|manus-1.6-max"
  }
  ```

See `src/main.py:call_manus()` for implementation details.

### Claude CLI Subprocess Integration

The `claude_subprocess/claude_cli.py` module manages Claude Code CLI as a subprocess:

- Uses `--output-format stream-json` for real-time streaming
- Parses JSON events: `content_block_delta`, `result`, `status_update`
- Supports both async and sync callbacks via `_call_callback()` helper
- Critical: Must use `asyncio.wait_for()` on the entire processing function, not on the async generator directly

## Critical Implementation Notes

### Async Patterns

When working with the Claude CLI subprocess module:
- `on_error` callbacks may be async or sync - always use `await _call_callback(on_error, error)`
- Do NOT wrap async generators directly with `asyncio.wait_for()` - wrap the function that consumes them

### API Endpoints

Backend exposes:
- `/api/health` - Health check
- `/api/chat` - Multi-provider chat endpoint
- `/api/connection-test` - Test LLM provider credentials
- `/api/agents` - List available agent profiles
- `/v1/chat/completions` - OpenAI-compatible endpoint (for Claude CLI proxy)
- `/v1/models` - OpenAI-compatible models list

### CORS Configuration

Frontend (localhost:5173) is whitelisted in backend CORS middleware. Update `main.py:36-42` if frontend port changes.

## Agent Framework

### Agent Definitions

All agents are defined in `.claude/agents/` with standardized markdown format:

- `# {Name}` - Agent name
- `## 기본 정보` - Role, specialty, experience, level
- `## 기술 스택` - Technologies
- `## 역할` - Responsibilities
- `## 적합한 프로젝트` - Project fit
- `## 기본 선택 조건` - Auto-selection criteria

The backend parses these files and exposes them via `/api/agents` endpoint for the frontend team selection UI.

### Agent Roles

Key agents include:
- **document-parser** - Extracts requirements from uploaded documents
- **project-manager** - Creates WBS and workspace ownership maps
- **backend-developer, frontend-developer, database-engineer** - Core development
- **devops-engineer** - Infrastructure (Docker, CI/CD)
- **security-engineer** - Security audits
- **qa-lead** - Test implementation
- **tech-lead** - Coordinates parallel development

## Git Strategy

**Committed (Company Assets):**
- `.claude/agents/` - Agent definitions
- `.claude/commands/` - Custom commands
- `CLAUDE.md` - This file
- `projects/starter-project/` - Reference implementation

**Ignored (Generated Artifacts):**
- `.claude/output/` - Project-specific outputs
- `workspace/` - Generated project code (managed separately)

Generated projects should be initialized as separate git repositories.

## 프로젝트 규칙 및 설정

### 인코딩 및 문자 처리 (필수)

- 모든 파일의 읽기 및 쓰기는 반드시 **UTF-8 인코딩**을 기준으로 수행하십시오.
- BOM(Byte Order Mark)을 생성하지 않아야 합니다.
- 기존 파일 수정 시, 기존 인코딩을 유지하고 UTF-8이 아닐 경우 UTF-8로 변환하여 저장하십시오.
- 한글 작업 중 텍스트 깨짐 현상이 발생하면 즉시 작업을 중단하고 사용자에게 보고하십시오.
- Python 파일은 파일 상단에 `# -*- coding: utf-8 -*-` 선언이 필요하지 않습니다 (Python 3 기본값).

### 빌드 및 테스트

**Backend (Python/FastAPI):**
```bash
# Lint (if configured)
# ruff check src/
# black --check src/

# Run tests (when test suite exists)
# pytest tests/

# Type checking (if using mypy)
# mypy src/
```

**Frontend (React/Vite):**
```bash
# Development build with hot reload
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint (if configured)
# npm run lint
```

**Proxy Server:**
```bash
# Run proxy server
npm start

# No build step required (plain Node.js)
```

### 테스트 규칙

- **Backend Tests**: Place test files in `tests/` directory with `test_*.py` naming convention
- **Frontend Tests**: Co-locate tests with components using `*.test.jsx` or `*.spec.jsx` naming
- **API Tests**: Test all `/api/*` endpoints for proper error handling and validation
- **LLM Integration Tests**: Mock external LLM API calls to avoid rate limits and API key requirements
- **Claude CLI Tests**: Mock subprocess calls when testing `claude_subprocess/` module

### 코딩 스타일

**Python (Backend):**
- Follow PEP 8 conventions
- Use `snake_case` for functions, variables, and module names
- Use `PascalCase` for class names
- Maximum line length: 88 characters (Black formatter default)
- Use type hints for function signatures
- Docstrings: Use Google-style or NumPy-style format
- Async functions: Prefix with `async def`, always `await` coroutines
- Logging: Use structured logging with `logger.info/debug/error` with context

**JavaScript/React (Frontend):**
- Use `camelCase` for variables and functions
- Use `PascalCase` for React components
- Prefer functional components with hooks over class components
- Use `const` by default, `let` only when reassignment is needed, never `var`
- Use arrow functions for callbacks and inline functions
- Component file naming: `ComponentName.jsx`
- Maximum line length: 100 characters

**Node.js (Proxy):**
- Use ES modules (`import/export`) not CommonJS (`require/module.exports`)
- Use `camelCase` for variables and functions
- Use `UPPER_SNAKE_CASE` for constants
- Async/await over callbacks
- Express route handlers should have proper error handling

### File Organization

**Backend:**
- `src/main.py` - FastAPI application entry point and route definitions
- `src/claude_subprocess/` - Claude CLI subprocess management
- `src/adapters/` - Format adapters (OpenAI ↔ Claude CLI)
- Keep route handlers in main.py, move complex business logic to separate modules

**Frontend:**
- `src/App.jsx` - Main application component
- Co-locate related components and styles
- Keep API base URL configuration at the top of files using it
- Use inline styles for now (consider CSS modules or styled-components for larger apps)

**Agents:**
- `/.claude/agents/*.md` - One file per agent role
- Follow the standardized format: basic info, tech stack, role, suitable projects, selection criteria
- Use Korean for agent definitions (this is a Korean-language project)