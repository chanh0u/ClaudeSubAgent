# API Integration — API 통합

프론트엔드에서 백엔드 API를 호출하는 패턴.

## fetch API

```javascript
const API_BASE_URL = 'http://localhost:3003';

// GET
async function getTodos() {
  const res = await fetch(`${API_BASE_URL}/api/todos`);
  return res.json();
}

// POST
async function createTodo(todo) {
  const res = await fetch(`${API_BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo)
  });
  return res.json();
}

// PUT
async function updateTodo(id, updates) {
  const res = await fetch(`${API_BASE_URL}/api/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  });
  return res.json();
}

// DELETE
async function deleteTodo(id) {
  await fetch(`${API_BASE_URL}/api/todos/${id}`, {
    method: 'DELETE'
  });
}
```

## 에러 핸들링

```javascript
async function fetchTodosWithErrorHandling() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/todos`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return res.json();
  } catch (error) {
    console.error('API 호출 실패:', error);
    return [];
  }
}
```

## React 통합

```jsx
import { useState, useEffect } from 'react';

function TodoList() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTodos();
  }, []);

  async function fetchTodos() {
    setLoading(true);
    const data = await getTodos();
    setTodos(data);
    setLoading(false);
  }

  return loading ? <div>Loading...</div> : <div>{/* 렌더링 */}</div>;
}
```

## 참조

- React 패턴: [react-patterns.md](react-patterns.md)
