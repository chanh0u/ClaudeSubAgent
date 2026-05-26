# Claude Agent Platform - 사용 가이드

## 실제 코드 생성 기능

이제 Claude Agent Platform은 **실제로 동작하는 코드**를 생성합니다!

### 주요 개선사항

✅ **실제 LLM 기반 코드 생성**
- 사용자의 요구사항을 분석하여 실제 동작하는 HTML, JavaScript, Python 코드 생성
- Claude, OpenAI, Ollama, Manus AI 모두 지원

✅ **완전 동작하는 웹 애플리케이션**
- 단일 HTML 파일로 완전한 웹 앱 생성
- 인라인 CSS로 모던한 UI
- 인라인 JavaScript로 실제 동작하는 기능 구현

✅ **실시간 피드백 반영**
- "버튼 색상을 파란색으로 변경해주세요" 같은 자연어 피드백
- LLM이 코드를 자동으로 수정
- 수정된 코드 즉시 반영

✅ **프로젝트 실행 및 미리보기**
- 생성된 프로젝트를 즉시 실행
- iframe으로 실시간 미리보기
- 새 탭에서 열어서 테스트

## 실행 방법

### 1. 백엔드 실행

```bash
cd C:\workspace\chanho\ClaudeAgent\projects\starter-project\python
python -m src.main
```

**서버 주소**: http://localhost:3003

### 2. 프론트엔드 실행

```bash
cd C:\workspace\chanho\ClaudeAgent\projects\starter-project\web
npm run dev
```

**서버 주소**: http://localhost:5173

## 사용 흐름

### Step 1: LLM 연결
1. 사용하려는 LLM provider 선택 (Claude, OpenAI, Ollama, Manus)
2. API 키 또는 엔드포인트 입력
3. "연결 테스트" 버튼으로 확인
4. ✅ 연결 성공 확인

**권장**:
- **Ollama (로컬)**: 무료, 빠름, API 키 불필요 (`http://llm.aicentro.ai.kr`)
- **Claude**: 가장 높은 품질의 코드 생성
- **OpenAI GPT-4o**: 빠르고 안정적

### Step 2: 요구사항 대화
실제 원하는 서비스를 자연어로 설명하세요.

**예시**:
```
할 일 관리 앱을 만들고 싶어요.
- 할 일 추가, 완료, 삭제 기능
- 완료된 항목은 취소선 표시
- 로컬 스토리지에 저장
- 깔끔한 디자인
```

또는

```
간단한 메모장 앱
- 텍스트 입력 영역
- 저장 버튼
- 저장된 메모 목록 표시
- 메모 삭제 기능
```

### Step 3: 프로젝트 설정
- **프로젝트 타입**: Web Application 또는 Fullstack 선택
- **아키텍처 특성**: 필요한 기능 체크 (파일 처리, 외부 API 등)

### Step 4: 개발팀 선택
- 자동으로 추천된 Agent 확인
- 필요시 추가/제거

### Step 5: 최종 요약 검토
- 모든 설정 확인
- "확인 완료" 버튼 클릭

### Step 6: 프로젝트 생성 🚀
1. "서비스 시작" 버튼 클릭
2. 파이프라인 진행 상황 확인:
   - 📄 문서 파싱
   - 📋 계획 수립
   - 👥 팀 구성 배정
   - **💻 코드 생성** ⬅️ 실제 LLM이 코드 작성!
   - 🧪 테스트 실행
   - 🎉 배포 준비

3. **코드 생성 중 (1-2분 소요)**
   - 로그에서 실시간 진행 상황 확인
   - LLM이 실제로 코드 작성 중

4. 완료!

### Step 7: 프로젝트 미리보기
- 생성된 URL 확인 (예: `http://localhost:4000`)
- iframe에서 실시간 미리보기
- "🔗 열기" 버튼으로 새 탭에서 테스트

### Step 8: 코드 뷰어 및 편집
1. **파일 탐색**
   - 왼쪽 패널에서 파일 선택
   - 📁 디렉토리 구조 확인

2. **코드 보기/편집**
   - 파일 클릭하여 내용 확인
   - "✏️ 편집" 버튼으로 편집 모드
   - 수정 후 "💾 저장"

### Step 9: 피드백 및 다운로드

#### 💬 피드백 제출
자연어로 수정 요청:

**예시**:
```
버튼 색상을 파란색으로 변경해주세요
```

```
할 일 추가 시 애니메이션 효과를 추가해주세요
```

```
전체적인 색상 테마를 다크 모드로 변경해주세요
```

1. 수정하려는 파일 선택 (선택 사항)
2. 피드백 입력
3. "📤 피드백 제출" 클릭
4. LLM이 자동으로 코드 수정
5. 수정된 코드 자동 반영

#### 📦 프로젝트 다운로드
- "⬇️ 프로젝트 다운로드 (ZIP)" 버튼
- 완성된 코드를 ZIP 파일로 다운로드
- 압축 해제 후 로컬에서 실행 가능

## 생성된 코드 구조

### Web Application
```
project-YYYYMMDD-HHMMSS/
├── README.md
└── frontend/
    └── index.html      # 완전한 웹 애플리케이션 (HTML+CSS+JS)
```

### Fullstack
```
project-YYYYMMDD-HHMMSS/
├── README.md
├── frontend/
│   └── index.html      # 프론트엔드
└── backend/
    ├── main.py         # FastAPI 백엔드
    └── requirements.txt
```

## 실제 생성되는 코드의 품질

### HTML/JavaScript (Frontend)
- ✅ 완전한 HTML5 문서
- ✅ 반응형 디자인 (모바일/태블릿/데스크톱)
- ✅ 모던한 CSS (Flexbox, Grid, 애니메이션)
- ✅ 실제 동작하는 JavaScript
- ✅ 이벤트 처리, DOM 조작
- ✅ 로컬 스토리지 활용
- ✅ 폼 검증 및 에러 처리

### Python/FastAPI (Backend)
- ✅ FastAPI 프레임워크
- ✅ RESTful API 엔드포인트
- ✅ CORS 설정
- ✅ Pydantic 모델 검증
- ✅ 에러 처리 (try-except, HTTPException)
- ✅ 인메모리 데이터 저장소
- ✅ 즉시 실행 가능

## 예제 요구사항

### 1. 할 일 관리 앱
```
할 일을 추가하고 관리할 수 있는 웹 앱을 만들어주세요.
기능:
- 할 일 입력 폼
- 추가 버튼
- 할 일 목록 (체크박스 포함)
- 완료된 항목은 취소선
- 삭제 버튼
- 로컬 스토리지에 저장
- 깔끔한 카드 디자인
```

### 2. 간단한 계산기
```
웹 기반 계산기를 만들어주세요.
기능:
- 숫자 버튼 (0-9)
- 연산자 (+, -, *, /)
- 계산 결과 표시
- 초기화 버튼
- 모던한 버튼 디자인
- 키보드 입력 지원
```

### 3. 타이머 앱
```
카운트다운 타이머 앱
기능:
- 시간 설정 (분, 초)
- 시작/일시정지/리셋 버튼
- 남은 시간 표시
- 시간 종료 시 알림
- 깔끔한 UI
```

### 4. 메모장 앱
```
간단한 메모장 앱
기능:
- 제목과 내용 입력
- 저장 버튼
- 저장된 메모 목록
- 메모 클릭 시 수정 모드
- 메모 삭제
- 로컬 스토리지 사용
```

## 트러블슈팅

### 코드 생성이 실패하는 경우
1. LLM 연결 상태 확인
2. API 키 유효성 확인
3. 요구사항을 더 구체적으로 작성
4. 다른 LLM provider 시도

### 생성된 코드가 동작하지 않는 경우
1. 브라우저 콘솔에서 에러 확인
2. 피드백 기능으로 수정 요청
3. 코드 뷰어에서 직접 수정

### 프로젝트 실행이 안 되는 경우
1. 포트 충돌 확인 (4000-5000 범위)
2. 방화벽 설정 확인
3. 프로젝트 재생성

## 기술 스택

### Frontend
- React 18
- Vite
- Google Fonts (Orbitron, Roboto Mono)

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- httpx

### LLM Integration
- Claude API (Anthropic)
- OpenAI API
- Ollama (로컬 LLM)
- Manus AI

## 라이선스

MIT License

## 문의

이슈가 있거나 기능 제안이 있으시면 GitHub Issues에 등록해주세요.
