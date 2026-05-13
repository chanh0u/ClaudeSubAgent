import React, { useState } from 'react';

function TodoItem({ todo, onToggle, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDeadline, setEditDeadline] = useState(todo.deadline || '');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // 마감일 지났는지 확인
  const isOverdue = () => {
    if (!todo.deadline) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const deadlineDate = new Date(todo.deadline);
    return deadlineDate < today && !todo.completed;
  };

  const handleSave = async () => {
    if (!editTitle.trim()) {
      setError('제목을 입력해주세요');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await onUpdate(todo.id, editTitle, editDeadline || null, todo.completed);
      setIsEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(todo.title);
    setEditDeadline(todo.deadline || '');
    setError('');
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('정말 삭제하시겠습니까?')) {
      setLoading(true);
      try {
        await onDelete(todo.id);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }
  };

  const handleToggle = async () => {
    setLoading(true);
    try {
      await onToggle(todo.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (isEditing) {
    return (
      <div className="todo-item editing">
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          disabled={loading}
          className="input-text"
        />
        <input
          type="date"
          value={editDeadline}
          onChange={(e) => setEditDeadline(e.target.value)}
          disabled={loading}
          className="input-date"
        />
        <button onClick={handleSave} disabled={loading} className="btn-save">
          저장
        </button>
        <button onClick={handleCancel} disabled={loading} className="btn-cancel">
          취소
        </button>
        {error && <div className="error-message">{error}</div>}
      </div>
    );
  }

  return (
    <div className={`todo-item ${todo.completed ? 'completed' : ''} ${isOverdue() ? 'overdue' : ''}`}>
      <input
        type="checkbox"
        checked={todo.completed === 1}
        onChange={handleToggle}
        disabled={loading}
        className="checkbox"
      />
      <div className="todo-content">
        <span className="todo-title">{todo.title}</span>
        {todo.deadline && (
          <span className="todo-deadline">
            마감: {new Date(todo.deadline).toLocaleDateString('ko-KR')}
          </span>
        )}
        <span className="todo-created">
          생성: {new Date(todo.created_at).toLocaleDateString('ko-KR')}
        </span>
      </div>
      <div className="todo-actions">
        <button onClick={() => setIsEditing(true)} disabled={loading} className="btn-edit">
          수정
        </button>
        <button onClick={handleDelete} disabled={loading} className="btn-delete">
          삭제
        </button>
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default TodoItem;
