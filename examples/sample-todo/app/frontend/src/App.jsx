import React, { useState, useEffect } from 'react';
import TodoForm from './components/TodoForm';
import TodoList from './components/TodoList';
import * as api from './services/api';
import './index.css';

function App() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 할 일 목록 불러오기
  const loadTodos = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getTodos();
      setTodos(data);
    } catch (err) {
      setError('할 일 목록을 불러오는데 실패했습니다: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // 초기 로드
  useEffect(() => {
    loadTodos();
  }, []);

  // 할 일 추가
  const handleAdd = async (title, deadline) => {
    const newTodo = await api.createTodo(title, deadline);
    setTodos([newTodo, ...todos]);
  };

  // 할 일 수정
  const handleUpdate = async (id, title, deadline, completed) => {
    const updatedTodo = await api.updateTodo(id, title, deadline, completed);
    setTodos(todos.map(todo => todo.id === id ? updatedTodo : todo));
  };

  // 할 일 삭제
  const handleDelete = async (id) => {
    await api.deleteTodo(id);
    setTodos(todos.filter(todo => todo.id !== id));
  };

  // 완료 상태 토글
  const handleToggle = async (id) => {
    const result = await api.toggleTodo(id);
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: result.completed ? 1 : 0 } : todo
    ));
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>To-Do 일정관리</h1>
      </header>

      <main className="app-main">
        <TodoForm onAdd={handleAdd} />

        {error && <div className="error-message global">{error}</div>}

        <TodoList
          todos={todos}
          onToggle={handleToggle}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
          loading={loading}
        />
      </main>
    </div>
  );
}

export default App;
