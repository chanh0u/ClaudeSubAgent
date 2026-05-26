# Manus AI Integration — Manus API 통합

Manus AI Provider와의 통합 방법 상세 가이드.

---

## 목차

1. [Manus API 개요](#1-manus-api-개요)
2. [인증](#2-인증)
3. [Task 기반 워크플로우](#3-task-기반-워크플로우)
4. [요청/응답 형식](#4-요청응답-형식)
5. [에러 핸들링](#5-에러-핸들링)
6. [구현 예시](#6-구현-예시)

---

## 1. Manus API 개요

Manus AI는 다른 LLM Provider (Claude, OpenAI)와 다른 패턴을 사용한다:

| 특징 | Claude/OpenAI | Manus |
|------|--------------|-------|
| 워크플로우 | 단일 요청/응답 | Task 생성 → 폴링 → 응답 추출 |
| 인증 헤더 | `Authorization: Bearer {key}` | `x-manus-api-key: {key}` |
| 엔드포인트 | `/v1/messages`, `/v1/chat/completions` | `/v2/task.create`, `/v2/task.listMessages` |
| 응답 방식 | 즉시 반환 | Task ID 반환 → 비동기 폴링 |

---

## 2. 인증

### 헤더 형식

**잘못된 예 (Claude/OpenAI 방식)**:
```python
headers = {
    "Authorization": f"Bearer {api_key}",  # Manus는 이 방식 사용 안 함
    "Content-Type": "application/json"
}
```

**올바른 예 (Manus 방식)**:
```python
headers = {
    "x-manus-api-key": api_key,  # 커스텀 헤더
    "Content-Type": "application/json"
}
```

### API Key 관리

```python
# 환경 변수에서 로드
import os

MANUS_API_KEY = os.getenv("MANUS_API_KEY")

if not MANUS_API_KEY:
    raise ValueError("MANUS_API_KEY 환경 변수 필요")
```

---

## 3. Task 기반 워크플로우

Manus는 즉시 응답하지 않고 Task를 생성한 후 비동기로 처리한다.

### 전체 흐름

```
1. Task 생성
   POST /v2/task.create
   → { taskId: "..." }

2. Task 상태 폴링 (반복)
   GET /v2/task.listMessages?taskId={taskId}
   → { status: "running" | "completed", messages: [...] }

3. 완료 시 응답 추출
   messages 배열에서 role="assistant" 찾기
```

### Step 1: Task 생성

```python
import httpx

async def create_manus_task(user_message: str, agent_profile: str = "manus-1.6"):
    url = "https://api.manus.ai/v2/task.create"
    headers = {
        "x-manus-api-key": MANUS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "content": [{"text": user_message}]
        },
        "agent_profile": agent_profile  # manus-1.6 | manus-1.6-lite | manus-1.6-max
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["taskId"]
```

### Step 2: 메시지 폴링

```python
import asyncio

async def poll_manus_messages(task_id: str, timeout: int = 300):
    """
    Task 완료까지 폴링.

    Args:
        task_id: Task ID
        timeout: 최대 대기 시간 (초)

    Returns:
        assistant 응답 텍스트
    """
    url = f"https://api.manus.ai/v2/task.listMessages?taskId={task_id}"
    headers = {
        "x-manus-api-key": MANUS_API_KEY
    }

    start_time = asyncio.get_event_loop().time()

    async with httpx.AsyncClient() as client:
        while True:
            # 타임아웃 체크
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Manus task {task_id} 타임아웃")

            # 메시지 조회
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            messages = data.get("messages", [])

            if status == "completed":
                # assistant 메시지 찾기
                for msg in messages:
                    if msg.get("role") == "assistant":
                        content = msg.get("content", [])
                        if content:
                            return content[0].get("text", "")
                raise ValueError("Assistant 응답 없음")

            elif status == "failed":
                error = data.get("error", "Unknown error")
                raise RuntimeError(f"Manus task 실패: {error}")

            # 1초 대기 후 재시도
            await asyncio.sleep(1)
```

### Step 3: 통합 함수

```python
async def call_manus(user_message: str, agent_profile: str = "manus-1.6") -> str:
    """
    Manus AI 호출 (Task 생성 + 폴링)

    Args:
        user_message: 사용자 메시지
        agent_profile: manus-1.6 | manus-1.6-lite | manus-1.6-max

    Returns:
        assistant 응답
    """
    # Task 생성
    task_id = await create_manus_task(user_message, agent_profile)

    # 폴링
    response = await poll_manus_messages(task_id, timeout=300)

    return response
```

---

## 4. 요청/응답 형식

### Task 생성 요청

```json
{
  "message": {
    "content": [
      { "text": "사용자 메시지" }
    ]
  },
  "agent_profile": "manus-1.6"
}
```

**agent_profile 옵션**:
- `manus-1.6`: 표준 (권장)
- `manus-1.6-lite`: 빠르고 저렴, 간단한 작업용
- `manus-1.6-max`: 최고 품질, 복잡한 작업용

### Task 생성 응답

```json
{
  "taskId": "task_abc123..."
}
```

### 메시지 조회 응답

```json
{
  "status": "completed",
  "messages": [
    {
      "role": "user",
      "content": [{ "text": "사용자 메시지" }]
    },
    {
      "role": "assistant",
      "content": [{ "text": "assistant 응답" }]
    }
  ]
}
```

**status 값**:
- `running`: 처리 중
- `completed`: 완료
- `failed`: 실패

---

## 5. 에러 핸들링

### 에러 유형

| 에러 | 원인 | 처리 |
|------|------|------|
| 401 Unauthorized | API Key 잘못됨 | MANUS_API_KEY 확인 |
| 404 Not Found | Task ID 잘못됨 | Task 생성 재시도 |
| 429 Too Many Requests | Rate limit 초과 | 1분 대기 후 재시도 |
| 500 Internal Server Error | Manus 서버 오류 | 재시도 또는 사용자 알림 |
| TimeoutError | 응답 시간 초과 (300초) | 타임아웃 증가 또는 실패 처리 |

### 재시도 전략

```python
async def call_manus_with_retry(user_message: str, max_retries: int = 3):
    """재시도 포함 Manus 호출"""
    for attempt in range(max_retries):
        try:
            return await call_manus(user_message)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit: 1분 대기
                await asyncio.sleep(60)
            elif attempt < max_retries - 1:
                # 기타 에러: 5초 대기 후 재시도
                await asyncio.sleep(5)
            else:
                raise  # 최종 실패
        except TimeoutError:
            if attempt < max_retries - 1:
                # 타임아웃 증가하여 재시도
                pass
            else:
                raise
```

---

## 6. 구현 예시

### FastAPI 엔드포인트

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ManusRequest(BaseModel):
    message: str
    agent_profile: str = "manus-1.6"

class ManusResponse(BaseModel):
    response: str

@router.post("/api/chat/manus", response_model=ManusResponse)
async def chat_with_manus(request: ManusRequest):
    """Manus AI 채팅 엔드포인트"""
    try:
        response = await call_manus(
            user_message=request.message,
            agent_profile=request.agent_profile
        )
        return ManusResponse(response=response)

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Manus API 에러: {e.response.text}"
        )
    except TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Manus 응답 타임아웃 (300초)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )
```

### 프론트엔드 연동

```javascript
// React에서 Manus 호출
async function callManus(message) {
  const response = await fetch("http://localhost:3003/api/chat/manus", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: message,
      agent_profile: "manus-1.6"
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();
  return data.response;
}
```

---

## Claude/OpenAI와의 차이점 요약

| 항목 | Claude/OpenAI | Manus |
|------|--------------|-------|
| 인증 | `Authorization: Bearer` | `x-manus-api-key` |
| 엔드포인트 | `/v1/messages` | `/v2/task.create` + `/v2/task.listMessages` |
| 워크플로우 | 동기 (즉시 응답) | 비동기 (Task 폴링) |
| 응답 시간 | ~1-5초 | ~5-30초 (폴링 포함) |
| 타임아웃 | 60초 (일반적) | 300초 (권장) |

---

## 참고

- FastAPI 패턴: [fastapi-patterns.md](fastapi-patterns.md)
- 비동기 패턴: [async-patterns.md](async-patterns.md)
