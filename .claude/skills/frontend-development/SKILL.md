---
name: frontend-development
description: "React + Vite 프론트엔드 개발. 컴포넌트, 라우팅, 상태 관리, API 통합 구현. workspace-map의 owns 경로만 수정. CORS 설정 고려 (백엔드 localhost:3003). camelCase 네이밍, 함수형 컴포넌트 + hooks 사용."
---

# Frontend Development Skill

React + Vite 기반 프론트엔드 UI를 구현하는 스킬. AI Agent Company 워크플로우의 Phase 3에서 frontend-developer 에이전트가 사용한다.

## 핵심 역할

1. **UI 컴포넌트**: React 컴포넌트 구현
2. **라우팅**: React Router 기반 페이지 네비게이션
3. **API 통합**: 백엔드 API 호출 및 데이터 처리
4. **상태 관리**: useState, useContext 등 hooks 사용
5. **파일 소유권 준수**: workspace-map의 owns 경로만 수정

## 기술 스택

- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: JavaScript (camelCase)
- **API Client**: fetch API

## 작업 원칙

### 원칙 1: workspace-map 준수

**필수**: `_workspace/02_workspace-map.json` 읽기

```javascript
// owns 경로만 수정
// 예: ["src/components/**", "src/pages/**", "package.json"]

// forbidden 경로는 절대 수정 금지
// 예: ["src/api/**", "migrations/**"]
```

### 원칙 2: 함수형 컴포넌트 + hooks

클래스 컴포넌트 대신 함수형 컴포넌트 사용:

```jsx
// 좋은 예: 함수형 컴포넌트
import { useState } from 'react';

function TodoList() {
  const [todos, setTodos] = useState([]);

  return <div>{todos.map(todo => <div key={todo.id}>{todo.title}</div>)}</div>;
}

// 나쁜 예: 클래스 컴포넌트
class TodoList extends React.Component {
  // 사용하지 않음
}
```

### 원칙 3: camelCase 네이밍

```javascript
const userName = "홍길동";  // camelCase
const UserName = "홍길동";  // PascalCase (컴포넌트명만)
const user_name = "홍길동"; // snake_case (금지)
```

### 원칙 4: API 베이스 URL

```javascript
const API_BASE_URL = "http://localhost:3003";  // 백엔드 포트

async function fetchTodos() {
  const response = await fetch(`${API_BASE_URL}/api/todos`);
  return response.json();
}
```

## 출력 구조

```
workspace/{project_id}/
├── src/
│   ├── App.jsx              # 메인 앱 컴포넌트
│   ├── main.jsx             # 엔트리 포인트
│   ├── components/          # 재사용 컴포넌트
│   │   ├── TodoList.jsx
│   │   └── TodoItem.jsx
│   ├── pages/               # 페이지 컴포넌트
│   │   ├── Home.jsx
│   │   └── TodoPage.jsx
│   └── hooks/               # 커스텀 hooks (선택)
│       └── useTodos.js
├── index.html
├── package.json
└── vite.config.js
```

## React 컴포넌트 패턴

### 패턴 1: 기본 컴포넌트

```jsx
// src/components/TodoItem.jsx
import React from 'react';

function TodoItem({ todo, onToggle }) {
  return (
    <div onClick={() => onToggle(todo.id)}>
      <input type="checkbox" checked={todo.completed} readOnly />
      <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
        {todo.title}
      </span>
    </div>
  );
}

export default TodoItem;
```

### 패턴 2: useState

```jsx
import { useState } from 'react';

function TodoForm({ onAdd }) {
  const [title, setTitle] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd({ title });
    setTitle('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="할 일 입력"
      />
      <button type="submit">추가</button>
    </form>
  );
}
```

### 패턴 3: useEffect

```jsx
import { useState, useEffect } from 'react';

function TodoList() {
  const [todos, setTodos] = useState([]);

  useEffect(() => {
    // 컴포넌트 마운트 시 API 호출
    fetch('http://localhost:3003/api/todos')
      .then(res => res.json())
      .then(data => setTodos(data.todos));
  }, []); // 빈 배열: 마운트 시 1회만

  return <div>{/* 렌더링 */}</div>;
}
```

> 상세: [references/react-patterns.md](references/react-patterns.md)

## API 통합

### fetch 사용법

```javascript
// GET 요청
async function getTodos() {
  const response = await fetch('http://localhost:3003/api/todos');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

// POST 요청
async function createTodo(todo) {
  const response = await fetch('http://localhost:3003/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo)
  });
  return response.json();
}

// PUT 요청
async function updateTodo(id, updates) {
  const response = await fetch(`http://localhost:3003/api/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  });
  return response.json();
}

// DELETE 요청
async function deleteTodo(id) {
  await fetch(`http://localhost:3003/api/todos/${id}`, {
    method: 'DELETE'
  });
}
```

> 상세: [references/api-integration.md](references/api-integration.md)

## 협업 프로토콜 (Phase 3)

### backend-dev와 협업

**API 엔드포인트 요청**:

```
[frontend-dev → backend-dev]
"POST /todos 엔드포인트가 필요합니다.
요청 바디: { title: string, description: string }
응답 형식을 알려주세요."

[backend-dev → frontend-dev]
"POST /api/todos 구현 완료.
요청: { title: string, description: string }
응답: { id: number, title: string, description: string, completed: boolean }
src/api/todos.py 참고하세요."
```

### devops와 협업

**의존성 파일 공유**:

```
[devops → frontend-dev]
"Docker 설정을 위해 package.json이 필요합니다."

[frontend-dev → devops]
"package.json 완성.
react@18.2.0
vite@4.3.9
..."
```

## App.jsx 템플릿

```jsx
import { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:3003';

function App() {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState('');

  useEffect(() => {
    fetchTodos();
  }, []);

  async function fetchTodos() {
    const res = await fetch(`${API_BASE_URL}/api/todos`);
    const data = await res.json();
    setTodos(data.todos || []);
  }

  async function addTodo() {
    if (!newTodo.trim()) return;

    const res = await fetch(`${API_BASE_URL}/api/todos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTodo })
    });
    const todo = await res.json();
    setTodos([...todos, todo]);
    setNewTodo('');
  }

  return (
    <div className="App">
      <h1>TODO App</h1>
      <div>
        <input
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          placeholder="할 일 입력"
        />
        <button onClick={addTodo}>추가</button>
      </div>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>{todo.title}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
```

## 절대 금지

- ❌ forbidden 경로 수정 금지 (src/api/**, migrations/**)
- ❌ 클래스 컴포넌트 사용
- ❌ var 키워드 사용 (const, let만)
- ❌ 인라인 스타일 남용 (CSS 파일 사용)

## 핵심 규칙

**Rule 1**: 함수형 컴포넌트 + hooks

**Rule 2**: API 베이스 URL은 localhost:3003

**Rule 3**: workspace-map의 `owns` 경로만 수정

**Rule 4**: camelCase 네이밍

**Rule 5**: 작업 완료 시 리더에게 보고

## 검증

구현 완료 후 확인:

- [ ] `src/App.jsx` 파일 존재
- [ ] `package.json` 파일 존재
- [ ] 함수형 컴포넌트만 사용
- [ ] API 호출 코드 포함
- [ ] workspace-map의 `owns` 경로만 수정
- [ ] `forbidden` 경로 미수정

## 참조

- React 패턴: [references/react-patterns.md](references/react-patterns.md)
- API 통합: [references/api-integration.md](references/api-integration.md)
