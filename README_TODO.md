# To-Do 앱 (마감일 기능 포함)

할 일 목록을 관리하고 마감일을 설정하여 작업을 효율적으로 추적할 수 있는 웹 기반 To-Do 애플리케이션

## 프로젝트 구조

```
ClaudeAgent/
├── spec.md                    # 서비스 기획서
├── schema.sql                 # 데이터베이스 스키마
├── todos.db                   # SQLite 데이터베이스 (자동 생성)
├── app/
│   ├── backend/              # Node.js + Express 백엔드
│   │   ├── server.js         # 서버 엔트리 포인트
│   │   ├── package.json      # 백엔드 의존성
│   │   ├── routes/           # API 라우트
│   │   │   └── todoRoutes.js
│   │   ├── controllers/      # 비즈니스 로직
│   │   │   └── todoController.js
│   │   └── models/           # 데이터 모델
│   │       ├── database.js
│   │       └── todoModel.js
│   └── frontend/             # React 프론트엔드
│       ├── package.json      # 프론트엔드 의존성
│       ├── public/
│       │   └── index.html
│       └── src/
│           ├── App.jsx       # 메인 앱 컴포넌트
│           ├── index.jsx     # 엔트리 포인트
│           ├── components/   # React 컴포넌트
│           │   ├── TodoForm.jsx
│           │   ├── TodoList.jsx
│           │   └── TodoItem.jsx
│           ├── services/     # API 서비스
│           │   └── api.js
│           └── styles/       # CSS 스타일
│               └── App.css
```

## 주요 기능

- 할 일 생성, 조회, 수정, 삭제 (CRUD)
- 마감일 설정 및 관리
- 완료 상태 토글
- 마감일 지난 항목 시각적 강조 (빨간색)
- 완료된 항목 취소선 표시
- 반응형 디자인 (모바일/데스크톱 지원)
- 실시간 에러 처리 및 로딩 상태 표시

## 기술 스택

### 백엔드
- Node.js
- Express.js
- SQLite3
- CORS

### 프론트엔드
- React 18
- Fetch API
- CSS3

## 설치 및 실행 방법

### 1. 백엔드 설정 및 실행

```bash
# 백엔드 디렉토리로 이동
cd app/backend

# 의존성 설치
npm install

# 서버 실행 (포트 3000)
npm start

# 또는 개발 모드로 실행 (nodemon 사용)
npm run dev
```

서버가 `http://localhost:3000`에서 실행됩니다.

### 2. 프론트엔드 설정 및 실행

새 터미널을 열고:

```bash
# 프론트엔드 디렉토리로 이동
cd app/frontend

# 의존성 설치
npm install

# 개발 서버 실행 (포트 3001 또는 자동 할당)
npm start
```

브라우저가 자동으로 열리며 앱이 실행됩니다.

## API 엔드포인트

### GET /api/todos
모든 할 일 목록 조회

**응답 예시:**
```json
[
  {
    "id": 1,
    "title": "프로젝트 완료하기",
    "completed": false,
    "deadline": "2026-05-15",
    "created_at": "2026-05-08T10:00:00Z"
  }
]
```

### POST /api/todos
새 할 일 생성

**요청 예시:**
```json
{
  "title": "프로젝트 완료하기",
  "deadline": "2026-05-15"
}
```

### PUT /api/todos/:id
할 일 수정

**요청 예시:**
```json
{
  "title": "프로젝트 수정하기",
  "deadline": "2026-05-20",
  "completed": true
}
```

### DELETE /api/todos/:id
할 일 삭제

### PATCH /api/todos/:id/toggle
완료 상태 토글

## 데이터베이스

SQLite를 사용하며, 애플리케이션 첫 실행 시 자동으로 `todos.db` 파일이 생성됩니다.

### 테이블 구조 (todos)
- `id`: INTEGER PRIMARY KEY (자동 증가)
- `title`: VARCHAR(255) NOT NULL
- `completed`: BOOLEAN NOT NULL DEFAULT 0
- `deadline`: DATE (선택)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## 사용 방법

1. **할 일 추가**: 상단 입력 폼에 제목과 마감일(선택)을 입력하고 "추가" 버튼 클릭
2. **완료 처리**: 체크박스를 클릭하여 완료/미완료 상태 전환
3. **수정**: "수정" 버튼을 클릭하여 편집 모드로 전환 후 내용 수정
4. **삭제**: "삭제" 버튼을 클릭하여 항목 제거 (확인 필요)

## 주요 특징

- **마감일 관리**: 마감일이 지난 항목은 자동으로 빨간색으로 강조
- **입력 검증**: 제목 필수 입력, 날짜 형식 검증
- **에러 처리**: 네트워크 오류 시 사용자 친화적 메시지 표시
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모두 최적화
- **UX 개선**: 로딩 상태, 버튼 비활성화, 확인 메시지 등

## 개발 참고사항

- 백엔드 포트: 3000
- 프론트엔드 개발 서버 포트: 3001 (또는 자동 할당)
- CORS가 활성화되어 있어 프론트엔드와 백엔드가 서로 다른 포트에서 실행 가능
- 데이터베이스 파일은 프로젝트 루트에 `todos.db`로 저장됨

## 라이선스

MIT
