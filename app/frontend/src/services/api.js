const API_BASE_URL = 'http://localhost:3000/api';

// API 호출 헬퍼 함수
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '요청 처리에 실패했습니다');
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      throw new Error('서버에 연결할 수 없습니다');
    }
    throw error;
  }
}

// Todo API
export const todoAPI = {
  // 모든 할 일 조회
  getAll: () => apiCall('/todos'),

  // 새 할 일 생성
  create: (todoData) => apiCall('/todos', {
    method: 'POST',
    body: JSON.stringify(todoData),
  }),

  // 할 일 수정
  update: (id, todoData) => apiCall(`/todos/${id}`, {
    method: 'PUT',
    body: JSON.stringify(todoData),
  }),

  // 할 일 삭제
  delete: (id) => apiCall(`/todos/${id}`, {
    method: 'DELETE',
  }),

  // 완료 상태 토글
  toggle: (id) => apiCall(`/todos/${id}/toggle`, {
    method: 'PATCH',
  }),
};
