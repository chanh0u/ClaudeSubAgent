---
name: backend-development
description: "FastAPI 백엔드 개발. REST API, 비즈니스 로직, 서비스 레이어 구현. workspace-map에서 owns로 지정된 경로만 수정. 다중 LLM 통합 (Claude, OpenAI, Ollama, Manus) 지원. 비동기 패턴 우선 사용. UTF-8 인코딩 필수."
---

# Backend Development Skill

FastAPI 기반 백엔드 API를 구현하는 스킬. AI Agent Company 워크플로우의 Phase 3에서 backend-developer 에이전트가 사용한다.

## 핵심 역할

1. **REST API 구현**: 엔드포인트, 요청/응답 처리
2. **비즈니스 로직**: 서비스 레이어 구현
3. **다중 LLM 통합**: Claude, OpenAI, Ollama, Manus API 연동
4. **비동기 패턴**: async/await 기반 효율적 처리
5. **파일 소유권 준수**: workspace-map의 owns 경로만 수정

## 기술 스택

- **Framework**: FastAPI (Python 3.10+)
- **HTTP 클라이언트**: httpx (비동기)
- **LLM Providers**: Claude API, OpenAI API, Ollama, Manus API
- **서브프로세스**: claude_subprocess (Claude CLI 통합)

## 작업 원칙

### 원칙 1: workspace-map 준수

**필수**: Phase 3 시작 전 `_workspace/02_workspace-map.json` 읽기

```python
workspace_map = json.load("_workspace/02_workspace-map.json")
my_owns = workspace_map["ownership"]["backend-developer"]["owns"]
my_forbidden = workspace_map["ownership"]["backend-developer"]["forbidden"]

# owns 경로만 수정
# 예: ["src/api/**", "src/service/**", "requirements.txt"]

# forbidden 경로는 절대 수정 금지
# 예: ["src/components/**", "migrations/**"]
```

충돌 발생 시 Phase 4 tech-lead가 해결.

### 원칙 2: API 엔드포인트 규칙

- 모든 API는 `/api/*` 경로 사용
- RESTful 규칙 준수: GET(조회), POST(생성), PUT(수정), DELETE(삭제)
- 비동기 핸들러 우선: `async def`

```python
# 예시: /api/todos
@app.get("/api/todos")
async def get_todos():
    # 비동기로 처리
    return {"todos": [...]}

@app.post("/api/todos")
async def create_todo(todo: TodoCreate):
    # 비즈니스 로직은 서비스 레이어로 분리
    result = await todo_service.create(todo)
    return result
```

### 원칙 3: 비즈니스 로직 분리

API 핸들러는 얇게 유지하고, 비즈니스 로직은 서비스 레이어로 분리:

```
src/
├── main.py          # FastAPI 앱 엔트리, 라우팅
├── api/             # API 엔드포인트 (얇은 핸들러)
│   ├── todos.py
│   └── users.py
└── service/         # 비즈니스 로직
    ├── todo_service.py
    └── user_service.py
```

### 원칙 4: UTF-8 인코딩

- 모든 파일 읽기/쓰기는 UTF-8
- BOM(Byte Order Mark) 생성 금지
- 한글 작업 중 텍스트 깨짐 발생 시 즉시 보고

```python
# 파일 읽기
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 파일 쓰기
with open("file.txt", "w", encoding="utf-8") as f:
    f.write(content)
```

## 출력 구조

```
workspace/{project_id}/
├── src/
│   ├── main.py              # FastAPI 앱 엔트리
│   ├── api/                 # API 엔드포인트
│   │   ├── __init__.py
│   │   ├── todos.py
│   │   └── users.py
│   ├── service/             # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── todo_service.py
│   │   └── user_service.py
│   ├── adapters/            # LLM 통합 (필요 시)
│   │   └── format_adapter.py
│   └── claude_subprocess/   # Claude CLI 통합 (필요 시)
│       └── claude_cli.py
└── requirements.txt         # Python 의존성
```

## 다중 LLM 통합

AI Agent Company 프로젝트는 4개의 LLM Provider를 지원한다. LLM 통합이 필요한 프로젝트에서만 구현.

### Supported Providers

1. **Claude (Anthropic API)**: `https://api.anthropic.com/v1/messages`
2. **OpenAI**: `https://api.openai.com/v1/chat/completions`
3. **Ollama**: 로컬 LLM (설정 가능한 엔드포인트)
4. **Manus AI**: `https://api.manus.ai/v2/task.*`

### Manus API 특수 처리

Manus는 다른 Provider와 패턴이 다르므로 주의:

**인증**:
```python
headers = {
    "x-manus-api-key": api_key,  # NOT "Authorization: Bearer"
    "Content-Type": "application/json"
}
```

**워크플로우**:
1. Task 생성: `POST /v2/task.create`
2. 메시지 조회: `GET /v2/task.listMessages?taskId={task_id}`
3. Assistant 응답 추출

**요청 형식**:
```python
request_body = {
    "message": {
        "content": [{"text": user_message}]
    },
    "agent_profile": "manus-1.6"  # or manus-1.6-lite, manus-1.6-max
}
```

> 상세: [references/manus-integration.md](references/manus-integration.md)

### Claude CLI Subprocess

Claude Code CLI를 서브프로세스로 실행하여 POC 코드 생성:

```python
from claude_subprocess.claude_cli import run_claude_cli_async

result = await run_claude_cli_async(
    prompt="할 일 API 구현해줘",
    output_format="stream-json",
    on_chunk=lambda chunk: print(chunk),
    on_error=lambda err: logger.error(err)
)
```

**주의사항**:
- `--output-format stream-json` 사용
- JSON 이벤트 파싱: `content_block_delta`, `result`, `status_update`
- `asyncio.wait_for()`는 전체 함수에, async generator에 직접 사용 금지

> 상세: [references/async-patterns.md](references/async-patterns.md)

## API 엔드포인트 설계

### 필수 엔드포인트

프로젝트 종류에 관계없이 구현:

```python
@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "ok"}
```

### CORS 설정

프론트엔드(localhost:5173)와의 통신을 위해 CORS 설정:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

프론트 포트 변경 시 `allow_origins` 업데이트.

## 비동기 패턴

FastAPI는 비동기를 기본 지원. 다음 규칙 준수:

### 규칙 1: async def 우선

I/O 작업(DB, API 호출, 파일 읽기)은 반드시 `async def`:

```python
# 좋은 예
@app.get("/api/todos")
async def get_todos():
    result = await database.fetch_all("SELECT * FROM todos")
    return result

# 나쁜 예 (동기 블로킹)
@app.get("/api/todos")
def get_todos():  # async 없음
    result = database.fetch_all_sync("SELECT * FROM todos")  # 블로킹
    return result
```

### 규칙 2: httpx 사용 (requests 금지)

외부 API 호출은 `httpx` (비동기) 사용:

```python
import httpx

async def call_external_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/endpoint",
            json={"key": "value"}
        )
        return response.json()
```

`requests` 라이브러리는 동기 블로킹이므로 금지.

### 규칙 3: 콜백 처리

콜백은 async/sync 모두 가능. `_call_callback()` 헬퍼 사용:

```python
async def _call_callback(callback, *args):
    """async/sync 콜백 통합 호출"""
    if asyncio.iscoroutinefunction(callback):
        return await callback(*args)
    else:
        return callback(*args)

# 사용
on_error = some_callback  # async 또는 sync
await _call_callback(on_error, error_message)
```

> 상세: [references/async-patterns.md](references/async-patterns.md)

## FastAPI 패턴

### 패턴 1: 의존성 주입

데이터베이스, 설정 등은 의존성 주입:

```python
from fastapi import Depends

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/todos")
async def get_todos(db = Depends(get_db)):
    return await db.fetch_all("SELECT * FROM todos")
```

### 패턴 2: Pydantic 모델

요청/응답은 Pydantic 모델로 검증:

```python
from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    description: str | None = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: str

@app.post("/api/todos", response_model=TodoResponse)
async def create_todo(todo: TodoCreate):
    # 자동 검증
    return await todo_service.create(todo)
```

### 패턴 3: 에러 핸들링

HTTPException 사용:

```python
from fastapi import HTTPException

@app.get("/api/todos/{todo_id}")
async def get_todo(todo_id: int):
    todo = await todo_service.get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
```

> 상세: [references/fastapi-patterns.md](references/fastapi-patterns.md)

## 협업 프로토콜 (Phase 3)

Phase 3 에이전트 팀에서 다른 팀원과 협업:

### frontend-dev와 협업

**API 엔드포인트 협의**:

```
[frontend-dev → backend-dev]
"POST /todos 엔드포인트 형식 알려주세요."

[backend-dev → frontend-dev]
"POST /api/todos
요청: { title: string, description: string }
응답: { id: number, title: string, description: string, completed: boolean, created_at: string }
src/api/todos.py 참고하세요."
```

### db-engineer와 협업

**스키마 확인**:

```
[db-engineer → backend-dev]
"todos 테이블 스키마 완성.
컬럼: id, title, description, completed, created_at
migrations/001_todos.sql 확인하세요."

[backend-dev → db-engineer]
"확인했습니다. user_id 외래키도 필요해요."
```

### devops와 협업

**의존성 파일 공유**:

```
[devops → backend-dev]
"Docker 설정을 위해 requirements.txt가 필요합니다."

[backend-dev → devops]
"requirements.txt 완성.
fastapi==0.95.0
uvicorn==0.21.0
httpx==0.24.0
..."
```

## 절대 금지

- ❌ forbidden 경로 수정 금지 (src/components/**, migrations/**)
- ❌ 동기 블로킹 코드 (requests, time.sleep)
- ❌ UTF-8 외 인코딩 사용
- ❌ BOM 포함 파일 생성
- ❌ 보안 취약점 (SQL Injection, XSS, 하드코딩된 시크릿)

## 핵심 규칙

**Rule 1**: 모든 I/O 작업은 비동기 (`async def`, `await`)

**Rule 2**: API 엔드포인트는 `/api/*` 경로 사용

**Rule 3**: workspace-map의 `owns` 경로만 수정

**Rule 4**: Manus API는 특수 처리 (`x-manus-api-key` 헤더)

**Rule 5**: 작업 완료 시 리더에게 보고 (또는 자동 유휴 알림)

## 검증

구현 완료 후 확인:

- [ ] `src/main.py` 파일 존재
- [ ] `/api/health` 엔드포인트 존재
- [ ] `requirements.txt` 파일 존재
- [ ] 모든 API 핸들러가 `async def`
- [ ] CORS 설정 포함 (localhost:5173)
- [ ] workspace-map의 `owns` 경로만 수정
- [ ] `forbidden` 경로 미수정
- [ ] UTF-8 인코딩

## 참조

- Manus API 통합: [references/manus-integration.md](references/manus-integration.md)
- FastAPI 패턴: [references/fastapi-patterns.md](references/fastapi-patterns.md)
- 비동기 패턴: [references/async-patterns.md](references/async-patterns.md)

## 사용 예시

**입력** (project-plan.md):
```yaml
- id: T-002
  name: "할 일 API 구현"
  agent: backend-developer
  output_files: ["src/api/todos.py", "src/service/todo_service.py"]
```

**출력** (src/main.py):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import todos

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
```

**출력** (src/api/todos.py):
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TodoCreate(BaseModel):
    title: str
    description: str | None = None

@router.get("/todos")
async def get_todos():
    return {"todos": []}

@router.post("/todos")
async def create_todo(todo: TodoCreate):
    # 비즈니스 로직은 service 레이어로
    return {"id": 1, **todo.dict(), "completed": False}
```
