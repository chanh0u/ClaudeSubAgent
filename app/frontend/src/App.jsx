import React, { useState, useEffect } from 'react';
import TodoList from './components/TodoList';
import TodoForm from './components/TodoForm';
import './styles/App.css';
import { todoAPI } from './services/api';

function App() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 할 일 목록 불러오기
  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await todoAPI.getAll();
      setTodos(data);
    } catch (err) {
      setError('할 일 목록을 불러오는데 실패했습니다');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 새 할 일 추가
  const handleAddTodo = async (todoData) => {
    try {
      setError(null);
      const newTodo = await todoAPI.create(todoData);
      setTodos([newTodo, ...todos]);
    } catch (err) {
      setError('할 일 추가에 실패했습니다');
      console.error(err);
    }
  };

  // 할 일 수정
  const handleUpdateTodo = async (id, todoData) => {
    try {
      setError(null);
      const updatedTodo = await todoAPI.update(id, todoData);
      setTodos(todos.map(todo =>
        todo.id === id ? updatedTodo : todo
      ));
    } catch (err) {
      setError('할 일 수정에 실패했습니다');
      console.error(err);
    }
  };

  // 할 일 삭제
  const handleDeleteTodo = async (id) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) {
      return;
    }

    try {
      setError(null);
      await todoAPI.delete(id);
      setTodos(todos.filter(todo => todo.id !== id));
    } catch (err) {
      setError('할 일 삭제에 실패했습니다');
      console.error(err);
    }
  };

  // 완료 상태 토글
  const handleToggleTodo = async (id) => {
    try {
      setError(null);
      const result = await todoAPI.toggle(id);
      setTodos(todos.map(todo =>
        todo.id === id ? { ...todo, completed: result.completed } : todo
      ));
    } catch (err) {
      setError('상태 변경에 실패했습니다');
      console.error(err);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1 className="app-title">To-Do 앱</h1>

        {error && (
          <div className="error-message">
            {error}
            <button
              className="error-close"
              onClick={() => setError(null)}
            >
              ×
            </button>
          </div>
        )}

        <TodoForm onSubmit={handleAddTodo} />

        {loading ? (
          <div className="loading">로딩 중...</div>
        ) : (
          <TodoList
            todos={todos}
            onToggle={handleToggleTodo}
            onUpdate={handleUpdateTodo}
            onDelete={handleDeleteTodo}
          />
        )}
      </div>
    </div>
  );
}

export default App;
