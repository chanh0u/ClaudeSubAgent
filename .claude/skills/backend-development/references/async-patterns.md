# Async Patterns — 비동기 패턴

Python async/await 비동기 프로그래밍 패턴과 Claude CLI Subprocess 통합.

---

## 목차

1. [async/await 기본](#1-asyncawait-기본)
2. [httpx 사용법](#2-httpx-사용법)
3. [콜백 처리](#3-콜백-처리)
4. [Claude CLI Subprocess](#4-claude-cli-subprocess)
5. [주의사항](#5-주의사항)

---

## 1. async/await 기본

### 규칙 1: I/O 작업은 async

I/O 작업 (DB, API 호출, 파일 읽기)은 반드시 `async def`:

```python
# 좋은 예: 비동기
@app.get("/api/todos")
async def get_todos():
    result = await database.fetch_all("SELECT * FROM todos")
    return result

# 나쁜 예: 동기 블로킹
@app.get("/api/todos")
def get_todos():
    result = database.fetch_all_sync("SELECT * FROM todos")  # 블로킹
    return result
```

### 규칙 2: CPU 작업은 동기 가능

CPU 집약적 작업 (계산, 변환)은 동기 가능:

```python
@app.get("/api/calculate")
def calculate():  # async 불필요
    result = heavy_computation()  # CPU 작업
    return {"result": result}
```

### 규칙 3: await는 async 내에서만

```python
async def fetch_data():
    data = await database.query()  # OK
    return data

def sync_function():
    data = await database.query()  # 에러: await는 async 내에서만
```

---

## 2. httpx 사용법

외부 API 호출은 `httpx` (비동기) 사용. `requests`는 동기 블로킹이므로 금지.

### 패턴 1: AsyncClient

```python
import httpx

async def call_external_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/endpoint",
            json={"key": "value"},
            headers={"Authorization": "Bearer token"}
        )
        response.raise_for_status()  # 4xx, 5xx 에러 발생
        return response.json()
```

### 패턴 2: timeout 설정

```python
async def call_with_timeout():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get("https://slow-api.com")
        return response.json()
```

### 패턴 3: 재시도

```python
async def call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 지수 백오프
            else:
                raise
```

---

## 3. 콜백 처리

콜백은 async 또는 sync일 수 있으므로 통합 호출 헬퍼 사용.

### _call_callback 헬퍼

```python
import asyncio
import inspect

async def _call_callback(callback, *args, **kwargs):
    """
    async/sync 콜백 통합 호출

    Args:
        callback: 호출할 함수 (async 또는 sync)
        *args, **kwargs: 콜백에 전달할 인자

    Returns:
        콜백 반환값
    """
    if callback is None:
        return None

    if asyncio.iscoroutinefunction(callback):
        # async 콜백
        return await callback(*args, **kwargs)
    else:
        # sync 콜백
        return callback(*args, **kwargs)
```

### 사용 예시

```python
# 콜백 정의 (async)
async def async_on_chunk(chunk):
    await save_to_db(chunk)
    print(chunk)

# 콜백 정의 (sync)
def sync_on_chunk(chunk):
    print(chunk)

# 통합 호출
on_chunk = async_on_chunk  # or sync_on_chunk

# 콜백 호출 (async/sync 구분 없이)
await _call_callback(on_chunk, "데이터 청크")
```

---

## 4. Claude CLI Subprocess

Claude Code CLI를 서브프로세스로 실행하여 스트리밍 출력 파싱.

### 기본 사용법

```python
from claude_subprocess.claude_cli import run_claude_cli_async

async def generate_code(prompt: str):
    """Claude CLI로 코드 생성"""
    result = await run_claude_cli_async(
        prompt=prompt,
        output_format="stream-json",
        on_chunk=lambda chunk: print(chunk),
        on_error=lambda err: logger.error(err)
    )
    return result
```

### 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| prompt | str | O | Claude에게 전달할 프롬프트 |
| output_format | str | X | "stream-json" (기본값) |
| on_chunk | callable | X | 청크 수신 시 호출 (async/sync 가능) |
| on_error | callable | X | 에러 발생 시 호출 (async/sync 가능) |
| timeout | int | X | 타임아웃 (초, 기본 600) |

### JSON 이벤트 파싱

Claude CLI는 `--output-format stream-json`으로 JSON 이벤트 스트림 반환:

```json
{"type": "content_block_start"}
{"type": "content_block_delta", "delta": {"text": "코드..."}}
{"type": "content_block_delta", "delta": {"text": "더 많은 코드..."}}
{"type": "result", "content": "전체 응답"}
{"type": "status_update", "status": "done"}
```

파싱:
```python
async def on_chunk(chunk):
    event = json.loads(chunk)
    event_type = event.get("type")

    if event_type == "content_block_delta":
        text = event.get("delta", {}).get("text", "")
        print(text, end="")

    elif event_type == "result":
        full_content = event.get("content")
        await save_result(full_content)

    elif event_type == "status_update":
        status = event.get("status")
        logger.info(f"Status: {status}")
```

### 주의사항

#### ❌ 잘못된 예: async generator에 직접 wait_for

```python
async def run_claude():
    # 에러: async generator에 직접 wait_for 사용 금지
    async for chunk in asyncio.wait_for(stream_json_output(), timeout=300):
        print(chunk)
```

#### ✅ 올바른 예: 소비 함수 전체를 wait_for

```python
async def process_stream():
    """스트림을 소비하는 함수"""
    async for chunk in stream_json_output():
        await _call_callback(on_chunk, chunk)

async def run_claude():
    # OK: 전체 함수를 wait_for로 래핑
    await asyncio.wait_for(process_stream(), timeout=300)
```

---

## 5. 주의사항

### 주의 1: 동기 블로킹 금지

FastAPI는 비동기 기반. 동기 블로킹 함수는 전체 성능 저하:

```python
# 금지: requests (동기 블로킹)
import requests
response = requests.get("https://api.com")  # 블로킹

# 사용: httpx (비동기)
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.com")  # 비블로킹
```

```python
# 금지: time.sleep (동기 블로킹)
import time
time.sleep(5)  # 블로킹

# 사용: asyncio.sleep (비동기)
import asyncio
await asyncio.sleep(5)  # 비블로킹
```

### 주의 2: run_in_executor for CPU 작업

CPU 집약적 작업을 async에서 실행하려면 `run_in_executor`:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def async_heavy_task():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, heavy_cpu_task)
    return result

def heavy_cpu_task():
    # CPU 집약적 작업
    return sum(range(10000000))
```

### 주의 3: 리소스 관리

`async with`로 리소스 자동 정리:

```python
# 좋은 예
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.com")
    # client 자동 close

# 나쁜 예
client = httpx.AsyncClient()
response = await client.get("https://api.com")
# client가 닫히지 않음 (메모리 누수)
```

### 주의 4: asyncio.gather for 병렬 실행

여러 비동기 작업을 병렬로:

```python
async def fetch_multiple():
    # 병렬 실행
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
    return results

async def fetch_user(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.com/users/{user_id}")
        return response.json()
```

---

## 체크리스트

비동기 코드 작성 시 확인:

- [ ] I/O 작업은 `async def`로 정의
- [ ] `await` 키워드 사용
- [ ] 외부 API 호출은 `httpx` 사용 (`requests` 금지)
- [ ] `time.sleep` 대신 `asyncio.sleep`
- [ ] 콜백 호출 시 `_call_callback` 헬퍼 사용
- [ ] async generator에 직접 `wait_for` 사용 금지
- [ ] `async with`로 리소스 관리
- [ ] CPU 작업은 `run_in_executor` 고려

---

## 참고

- Manus API 통합: [manus-integration.md](manus-integration.md)
- FastAPI 패턴: [fastapi-patterns.md](fastapi-patterns.md)
