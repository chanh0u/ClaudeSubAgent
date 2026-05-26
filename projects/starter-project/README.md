# Starter Project

새 프로젝트 시작용 템플릿입니다.

## Structure

- `python/`: Python 앱
- `web/`: npm 기반 웹 앱

## Python (FastAPI 서버 - 로깅 지원)

```bash
cd python
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 3003 --reload
```

Python 서버는 **상세한 로깅**을 지원합니다:
- 🤖 API 호출 시작/종료
- ✅ 성공 응답 및 데이터 크기
- ❌ 에러 상세 정보
- 📁 Agent 파일 파싱 로그
- 💬 채팅 요청/응답 추적

서버는 기본적으로 `http://localhost:3003` 에서 실행됩니다.
- API 문서: `http://localhost:3003/docs` (Swagger UI)

### 디버깅 모드
더 상세한 로그를 보려면 DEBUG 레벨로 실행:
```bash
# Windows
set LOG_LEVEL=DEBUG && uvicorn src.main:app --host 0.0.0.0 --port 3003 --reload

# Linux/Mac
LOG_LEVEL=DEBUG uvicorn src.main:app --host 0.0.0.0 --port 3003 --reload
```

### OpenAI 호환 API (Claude CLI Proxy)

이 서버는 **OpenAI 호환 API**를 제공하여 Claude Max 구독으로 Claude Code CLI를 사용할 수 있습니다.

#### 사전 요구사항
1. **Claude Max 구독** ($200/월) - [구독하기](https://claude.ai)
2. **Claude Code CLI** 설치 및 인증:
   ```bash
   npm install -g @anthropic-ai/claude-code
   claude auth login
   ```

#### 사용 가능한 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|----------|--------|-------------|
| `/health` | GET | 헬스 체크 (Claude CLI 상태 포함) |
| `/v1/models` | GET | 사용 가능한 모델 목록 |
| `/v1/chat/completions` | POST | 채팅 완성 (스트리밍/논스트리밍) |

#### 사용 가능한 모델

| 모델 ID | Alias | CLI 모델 |
|---------|-------|----------|
| `claude-opus-4` | `opus` | Claude Opus |
| `claude-sonnet-4` | `sonnet` | Claude Sonnet |
| `claude-haiku-4` | `haiku` | Claude Haiku |

#### 사용 예시

**헬스 체크:**
```bash
curl http://localhost:3003/health
```

**모델 목록:**
```bash
curl http://localhost:3003/v1/models
```

**채팅 완성 (논스트리밍):**
```bash
curl -X POST http://localhost:3003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**채팅 완성 (스트리밍):**
```bash
curl -N -X POST http://localhost:3003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

**Python에서 사용:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3003/v1",
    api_key="not-needed"  # 아무 값이나 입력
)

response = client.chat.completions.create(
    model="claude-sonnet-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

DEBUG 모드에서는 다음을 추가로 확인할 수 있습니다:
- 📤 API 요청 본문 (메시지 내용)
- 📥 API 응답 본문 (JSON 구조)
- 🔍 상세한 에러 스택 트레이스

## Server (Node.js)

```bash
cd server
npm install
node server.js
```

서버는 기본적으로 `http://localhost:3001` 에서 실행됩니다.

### 디버깅 모드
```bash
# Windows
set DEBUG=true && node server.js

# Linux/Mac
DEBUG=true node server.js
```

## Web (npm)

```bash
cd web
npm install
npm run dev
```

기본 dev 서버는 `http://localhost:5173` 입니다.