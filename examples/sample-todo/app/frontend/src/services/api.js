const API_BASE = 'http://localhost:3000/api/todos';

// 에러 처리 헬퍼
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || '요청에 실패했습니다');
  }
  return response.json();
};

// 모든 할 일 조회
export const getTodos = async () => {
  const response = await fetch(API_BASE);
  return handleResponse(response);
};

// 할 일 생성
export const createTodo = async (title, deadline) => {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, deadline })
  });
  return handleResponse(response);
};

// 할 일 수정
export const updateTodo = async (id, title, deadline, completed) => {
  const response = await fetch(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, deadline, completed })
  });
  return handleResponse(response);
};

// 할 일 삭제
export const deleteTodo = async (id) => {
  const response = await fetch(`${API_BASE}/${id}`, {
    method: 'DELETE'
  });
  return handleResponse(response);
};

// 완료 상태 토글
export const toggleTodo = async (id) => {
  const response = await fetch(`${API_BASE}/${id}/toggle`, {
    method: 'PATCH'
  });
  return handleResponse(response);
};
