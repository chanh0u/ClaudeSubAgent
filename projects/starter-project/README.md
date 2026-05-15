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
python src/main.py
```

Python 서버는 **상세한 로깅**을 지원합니다:
- 🤖 API 호출 시작/종료
- ✅ 성공 응답 및 데이터 크기
- ❌ 에러 상세 정보
- 📁 Agent 파일 파싱 로그
- 💬 채팅 요청/응답 추적

서버는 기본적으로 `http://localhost:3001` 에서 실행됩니다.
- API 문서: `http://localhost:3001/docs` (Swagger UI)

### 디버깅 모드
더 상세한 로그를 보려면 DEBUG 레벨로 실행:
```bash
# Windows
set LOG_LEVEL=DEBUG && python src/main.py

# Linux/Mac
LOG_LEVEL=DEBUG python src/main.py
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