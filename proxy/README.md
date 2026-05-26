# Claude Agent Proxy Server

HTTP 프록시 서버로, 프론트엔드(React)와 백엔드(FastAPI) 사이의 API 요청을 중계합니다.

## 개요

이 프록시 서버는 Claude CLI를 통한 POC 코드 생성 시 사용되며, OpenAI 호환 API 엔드포인트(`/v1/*`)를 제공합니다. 일반적인 LLM API 호출에는 사용되지 않으며, **수동으로 시작해야 합니다**.

### 주요 기능

- **API 프록싱**: 프론트엔드의 `/api` 및 `/v1` 요청을 백엔드로 전달
- **CORS 처리**: localhost:5173 (프론트엔드) 요청 허용
- **요청/응답 로깅**: 모든 프록시 트래픽을 콘솔에 출력
- **에러 핸들링**: 프록시 오류 시 적절한 에러 응답 반환

## 아키텍처

```
Frontend (React:5173)
    ↓
Proxy Server (Express:3456)
    ↓
Backend (FastAPI:3003)
    ↓
Claude CLI Subprocess (POC 생성용)
```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd proxy
npm install
```

### 2. 서버 실행

```bash
npm start
```

**실행 결과:**
```
============================================================
🔌 Claude Agent Proxy Server Started
📡 Listening on: http://localhost:3456
🎯 Backend target: http://localhost:3003
⏰ Started at: 2026-05-26T12:34:56.789Z
============================================================
```

### 3. 서버 확인

Health check 엔드포인트로 서버 상태 확인:

```bash
curl http://localhost:3456/health
```

**응답:**
```json
{
  "status": "ok",
  "proxy": true,
  "backend": "http://localhost:3003"
}
```

## 구성

### 포트 및 엔드포인트

| 설정 | 값 | 설명 |
|-----|-----|-----|
| 프록시 포트 | `3456` | 프록시 서버 리스닝 포트 |
| 백엔드 URL | `http://localhost:3003` | FastAPI 백엔드 주소 |
| 허용 Origin | `http://localhost:5173` | CORS 허용 도메인 (React 개발 서버) |

### 프록시 경로

#### 1. `/api/*` - 일반 API 요청

프론트엔드에서 `/api/*`로 요청하면 백엔드의 `/api/*`로 전달됩니다.

**예시:**
```javascript
// Frontend (React)
fetch('http://localhost:3456/api/health')

// → Proxied to
// Backend: http://localhost:3003/api/health
```

#### 2. `/v1/*` - OpenAI 호환 API

Claude CLI subprocess가 사용하는 OpenAI 호환 엔드포인트입니다.

**예시:**
```javascript
// Claude CLI (POC 생성 시)
POST http://localhost:3456/v1/chat/completions

// → Proxied to
// Backend: http://localhost:3003/v1/chat/completions
```

## 사용 시나리오

### POC 코드 생성 (Step 6 in UI)

프록시 서버는 **POC 프로젝트 자동 생성** 단계에서 사용됩니다:

1. 사용자가 프론트엔드 UI에서 "프로젝트 생성" 버튼 클릭
2. 프론트엔드가 백엔드에 프로젝트 생성 요청 → 프록시 통과
3. 백엔드가 Claude CLI subprocess를 시작
4. **Claude CLI가 프록시 서버의 `/v1/chat/completions` 엔드포인트 사용**
5. 프록시가 요청을 백엔드로 전달 → 백엔드가 실제 LLM API 호출
6. 응답이 역순으로 전달: LLM → Backend → Proxy → Claude CLI → 생성된 코드

### 일반 LLM API 호출 (프록시 미사용)

프론트엔드의 일반적인 채팅 기능은 **프록시를 거치지 않고** 직접 백엔드와 통신합니다:

```javascript
// Frontend가 직접 백엔드 호출 (프록시 미사용)
fetch('http://localhost:3003/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: 'Hello', provider: 'claude' })
})
```

## 로그 예시

### 정상 요청
```
[2026-05-26T12:34:56.789Z] GET /health
[2026-05-26T12:35:01.234Z] POST /api/chat
  → Proxy to: http://localhost:3003/api/chat
  ← Response: 200
```

### 에러 발생
```
[2026-05-26T12:35:10.456Z] POST /v1/chat/completions
  → Proxy to: http://localhost:3003/v1/chat/completions
  ✗ Proxy error: connect ECONNREFUSED 127.0.0.1:3003
```

## 문제 해결

### 프록시가 시작되지 않음

**증상:**
```
Error: listen EADDRINUSE: address already in use :::3456
```

**해결:**
- 3456 포트를 사용 중인 프로세스를 종료하거나
- `index.js`에서 `PORT` 변수를 다른 값으로 변경

### 백엔드 연결 실패

**증상:**
```
✗ Proxy error: connect ECONNREFUSED 127.0.0.1:3003
```

**해결:**
1. 백엔드 서버가 실행 중인지 확인:
   ```bash
   cd ../projects/starter-project/python
   python -m src.main
   ```
2. 백엔드가 3003 포트에서 실행 중인지 확인

### CORS 에러

**증상:**
```
Access to fetch at 'http://localhost:3456/api/...' from origin 'http://localhost:XXXX' has been blocked by CORS policy
```

**해결:**
`index.js:11`의 `origin` 값을 프론트엔드 포트에 맞게 수정:
```javascript
app.use(cors({
  origin: 'http://localhost:5173',  // 프론트엔드 포트에 맞게 변경
  credentials: true
}));
```

## 기술 스택

- **Express** (^4.18.2) - Node.js 웹 프레임워크
- **http-proxy-middleware** (^2.0.6) - HTTP 프록시 미들웨어
- **cors** (^2.8.5) - CORS 처리

## 파일 구조

```
proxy/
├── index.js          # 메인 서버 파일
├── package.json      # 의존성 정의
├── package-lock.json # 의존성 잠금 파일
└── README.md         # 이 문서
```

## 개발 시 주의사항

### 포트 변경

포트를 변경해야 할 경우, 다음 파일들을 함께 수정해야 합니다:

1. `proxy/index.js:6` - `PORT` 변수
2. 프론트엔드 API 호출 코드 - 프록시 URL
3. Claude CLI 설정 (있다면) - base URL 설정

### 로깅 레벨 조정

더 자세한 로그가 필요한 경우 `index.js:30, 46`의 `logLevel` 변경:

```javascript
createProxyMiddleware({
  // ...
  logLevel: 'debug',  // 'silent' | 'info' | 'debug'
  // ...
})
```

### 환경 변수 사용

하드코딩된 설정을 환경 변수로 변경하려면:

```javascript
const PORT = process.env.PROXY_PORT || 3456;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3003';
```

## 관련 문서

- [프로젝트 전체 가이드](../CLAUDE.md)
- [백엔드 문서](../projects/starter-project/python/README.md) (있다면)
- [프론트엔드 문서](../projects/starter-project/web/README.md) (있다면)
