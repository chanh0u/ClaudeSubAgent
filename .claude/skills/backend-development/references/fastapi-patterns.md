# FastAPI Patterns — FastAPI 패턴

FastAPI 백엔드 개발에서 자주 사용하는 패턴과 모범 사례.

---

## 목차

1. [프로젝트 구조](#1-프로젝트-구조)
2. [의존성 주입](#2-의존성-주입)
3. [Pydantic 모델](#3-pydantic-모델)
4. [에러 핸들링](#4-에러-핸들링)
5. [라우팅](#5-라우팅)
6. [미들웨어](#6-미들웨어)

---

## 1. 프로젝트 구조

### 표준 구조

```
src/
├── main.py          # FastAPI 앱 엔트리, CORS, 라우터 등록
├── api/             # API 엔드포인트 (얇은 핸들러)
│   ├── __init__.py
│   ├── todos.py
│   └── users.py
├── service/         # 비즈니스 로직
│   ├── __init__.py
│   ├── todo_service.py
│   └── user_service.py
├── models/          # Pydantic 모델 (요청/응답)
│   ├── __init__.py
│   ├── todo.py
│   └── user.py
└── dependencies.py  # 의존성 주입 함수
```

### main.py 템플릿

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import todos, users

app = FastAPI(
    title="AI Agent Company API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(todos.router, prefix="/api", tags=["todos"])
app.include_router(users.router, prefix="/api", tags=["users"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3003)
```

---

## 2. 의존성 주입

### 패턴 1: 데이터베이스 세션

```python
# dependencies.py
from typing import Generator

def get_db() -> Generator:
    """DB 세션 의존성"""
    db = Database()
    try:
        yield db
    finally:
        db.close()

# api/todos.py
from fastapi import Depends, APIRouter
from dependencies import get_db

router = APIRouter()

@router.get("/todos")
async def get_todos(db = Depends(get_db)):
    return await db.fetch_all("SELECT * FROM todos")
```

### 패턴 2: 인증

```python
# dependencies.py
from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(None)):
    """JWT 토큰 검증"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header 필요")

    token = authorization.replace("Bearer ", "")
    # JWT 검증 로직
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    return token

# api/todos.py
@router.get("/todos")
async def get_todos(token: str = Depends(verify_token)):
    # 인증된 요청만 처리
    return {"todos": []}
```

### 패턴 3: 설정

```python
# dependencies.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    manus_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()

def get_settings():
    return settings

# api/todos.py
@router.get("/todos")
async def get_todos(settings: Settings = Depends(get_settings)):
    # 설정 사용
    return {"db_url": settings.database_url}
```

---

## 3. Pydantic 모델

### 패턴 1: 요청/응답 분리

```python
# models/todo.py
from pydantic import BaseModel
from datetime import datetime

class TodoBase(BaseModel):
    """공통 필드"""
    title: str
    description: str | None = None

class TodoCreate(TodoBase):
    """생성 요청"""
    pass

class TodoUpdate(TodoBase):
    """수정 요청"""
    completed: bool | None = None

class TodoResponse(TodoBase):
    """응답"""
    id: int
    completed: bool
    created_at: datetime

    class Config:
        orm_mode = True  # ORM 객체 → Pydantic 자동 변환
```

### 패턴 2: 검증

```python
from pydantic import BaseModel, Field, validator

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)

    @validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("제목은 공백일 수 없습니다")
        return v.strip()
```

### 패턴 3: 중첩 모델

```python
class User(BaseModel):
    id: int
    name: str

class TodoResponse(BaseModel):
    id: int
    title: str
    owner: User  # 중첩

# 응답 예시
{
  "id": 1,
  "title": "할 일",
  "owner": {
    "id": 123,
    "name": "홍길동"
  }
}
```

---

## 4. 에러 핸들링

### 패턴 1: HTTPException

```python
from fastapi import HTTPException

@router.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    todo = await todo_service.get(todo_id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail=f"Todo {todo_id} not found"
        )
    return todo
```

### 패턴 2: 전역 예외 핸들러

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 로깅
    logger.error(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 패턴 3: 커스텀 예외

```python
class TodoNotFoundError(Exception):
    def __init__(self, todo_id: int):
        self.todo_id = todo_id

@app.exception_handler(TodoNotFoundError)
async def todo_not_found_handler(request: Request, exc: TodoNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Todo {exc.todo_id} not found"}
    )

# 사용
@router.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    todo = await todo_service.get(todo_id)
    if not todo:
        raise TodoNotFoundError(todo_id)
    return todo
```

---

## 5. 라우팅

### 패턴 1: APIRouter 분리

```python
# api/todos.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/todos")
async def list_todos():
    return {"todos": []}

@router.post("/todos")
async def create_todo(todo: TodoCreate):
    return {"id": 1, **todo.dict()}

@router.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    return {"id": todo_id}

@router.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo: TodoUpdate):
    return {"id": todo_id, **todo.dict()}

@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    return {"deleted": True}

# main.py에서 등록
app.include_router(todos.router, prefix="/api", tags=["todos"])
```

### 패턴 2: 경로 파라미터 검증

```python
from fastapi import Path

@router.get("/todos/{todo_id}")
async def get_todo(
    todo_id: int = Path(..., gt=0, description="Todo ID (양수)")
):
    return {"id": todo_id}
```

### 패턴 3: 쿼리 파라미터

```python
from fastapi import Query

@router.get("/todos")
async def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    completed: bool | None = Query(None)
):
    # 페이지네이션 + 필터링
    return {"todos": [], "skip": skip, "limit": limit}
```

---

## 6. 미들웨어

### 패턴 1: 로깅 미들웨어

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response
```

### 패턴 2: 인증 미들웨어

```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # /api/health는 인증 불필요
    if request.url.path == "/api/health":
        return await call_next(request)

    # Authorization 헤더 확인
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header 필요"}
        )

    return await call_next(request)
```

### 패턴 3: CORS 미들웨어

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

---

## 모범 사례

### 1. 비동기 우선

모든 I/O 작업은 `async def`:

```python
# 좋은 예
@router.get("/todos")
async def get_todos():
    result = await database.fetch_all("...")
    return result

# 나쁜 예 (동기 블로킹)
@router.get("/todos")
def get_todos():
    result = database.fetch_all_sync("...")  # 블로킹
    return result
```

### 2. 비즈니스 로직 분리

API 핸들러는 얇게, 비즈니스 로직은 service 레이어로:

```python
# api/todos.py (얇음)
@router.post("/todos")
async def create_todo(todo: TodoCreate):
    result = await todo_service.create(todo)  # service 레이어 호출
    return result

# service/todo_service.py (두꺼움)
async def create(todo: TodoCreate):
    # 유효성 검증
    # DB 저장
    # 이벤트 발행
    return saved_todo
```

### 3. 응답 모델 명시

```python
@router.get("/todos", response_model=list[TodoResponse])
async def get_todos():
    # response_model로 자동 검증 + 문서화
    return await todo_service.list_all()
```

### 4. 상태 코드 명시

```python
from fastapi import status

@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    return await todo_service.create(todo)

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    await todo_service.delete(todo_id)
    return None
```

---

## 참고

- Manus API 통합: [manus-integration.md](manus-integration.md)
- 비동기 패턴: [async-patterns.md](async-patterns.md)
