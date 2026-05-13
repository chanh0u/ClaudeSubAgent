import React, { useState } from 'react';

function TodoForm({ onAdd }) {
  const [title, setTitle] = useState('');
  const [deadline, setDeadline] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 입력 검증
    if (!title.trim()) {
      setError('제목을 입력해주세요');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await onAdd(title, deadline || null);
      setTitle('');
      setDeadline('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="todo-form">
      <div className="form-group">
        <input
          type="text"
          placeholder="할 일을 입력하세요"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={loading}
          className="input-text"
        />
        <input
          type="date"
          value={deadline}
          onChange={(e) => setDeadline(e.target.value)}
          disabled={loading}
          className="input-date"
        />
        <button type="submit" disabled={loading} className="btn-add">
          {loading ? '추가 중...' : '추가'}
        </button>
      </div>
      {error && <div className="error-message">{error}</div>}
    </form>
  );
}

export default TodoForm;
