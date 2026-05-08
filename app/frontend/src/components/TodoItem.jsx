import React, { useState } from 'react';

function TodoItem({ todo, onToggle, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDeadline, setEditDeadline] = useState(todo.deadline || '');

  // 마감일이 지났는지 확인
  const isOverdue = todo.deadline && !todo.completed &&
    new Date(todo.deadline) < new Date(new Date().setHours(0, 0, 0, 0));

  const handleSave = async () => {
    if (!editTitle.trim()) {
      alert('제목을 입력해주세요');
      return;
    }

    await onUpdate(todo.id, {
      title: editTitle.trim(),
      deadline: editDeadline || null,
      completed: todo.completed
    });

    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(todo.title);
    setEditDeadline(todo.deadline || '');
    setIsEditing(false);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isEditing) {
    return (
      <div className="todo-item editing">
        <div className="todo-edit-form">
          <input
            type="text"
            className="form-input"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            autoFocus
          />
          <input
            type="date"
            className="form-input date-input"
            value={editDeadline}
            onChange={(e) => setEditDeadline(e.target.value)}
          />
          <div className="edit-actions">
            <button className="btn btn-success" onClick={handleSave}>
              저장
            </button>
            <button className="btn btn-secondary" onClick={handleCancel}>
              취소
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`todo-item ${todo.completed ? 'completed' : ''} ${isOverdue ? 'overdue' : ''}`}>
      <input
        type="checkbox"
        className="todo-checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
      />

      <div className="todo-content">
        <div className="todo-title">{todo.title}</div>
        <div className="todo-meta">
          {todo.deadline && (
            <span className="todo-deadline">
              마감: {formatDate(todo.deadline)}
            </span>
          )}
          <span className="todo-created">
            생성: {formatDate(todo.created_at)}
          </span>
        </div>
      </div>

      <div className="todo-actions">
        <button
          className="btn btn-edit"
          onClick={() => setIsEditing(true)}
        >
          수정
        </button>
        <button
          className="btn btn-delete"
          onClick={() => onDelete(todo.id)}
        >
          삭제
        </button>
      </div>
    </div>
  );
}

export default TodoItem;
