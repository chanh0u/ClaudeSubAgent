const TodoModel = require('../models/todoModel');

class TodoController {
  // GET /api/todos - 모든 할 일 조회
  static getAllTodos(req, res) {
    TodoModel.getAll((err, todos) => {
      if (err) {
        return res.status(500).json({ error: '할 일 목록을 불러오는데 실패했습니다' });
      }
      res.json(todos);
    });
  }

  // POST /api/todos - 새 할 일 생성
  static createTodo(req, res) {
    const { title, deadline } = req.body;

    // 입력 검증
    if (!title || title.trim() === '') {
      return res.status(400).json({ error: '제목은 필수 입력 항목입니다' });
    }

    // 마감일 검증 (있는 경우)
    if (deadline && !isValidDate(deadline)) {
      return res.status(400).json({ error: '올바른 날짜 형식이 아닙니다 (YYYY-MM-DD)' });
    }

    TodoModel.create({ title: title.trim(), deadline }, (err, todo) => {
      if (err) {
        return res.status(500).json({ error: '할 일 생성에 실패했습니다' });
      }
      res.status(201).json(todo);
    });
  }

  // PUT /api/todos/:id - 할 일 수정
  static updateTodo(req, res) {
    const { id } = req.params;
    const { title, deadline, completed } = req.body;

    // 입력 검증
    if (!title || title.trim() === '') {
      return res.status(400).json({ error: '제목은 필수 입력 항목입니다' });
    }

    // 마감일 검증 (있는 경우)
    if (deadline && !isValidDate(deadline)) {
      return res.status(400).json({ error: '올바른 날짜 형식이 아닙니다 (YYYY-MM-DD)' });
    }

    TodoModel.update(id, {
      title: title.trim(),
      deadline,
      completed: Boolean(completed)
    }, (err, todo) => {
      if (err) {
        if (err.message === '할 일을 찾을 수 없습니다') {
          return res.status(404).json({ error: err.message });
        }
        return res.status(500).json({ error: '할 일 수정에 실패했습니다' });
      }
      res.json(todo);
    });
  }

  // DELETE /api/todos/:id - 할 일 삭제
  static deleteTodo(req, res) {
    const { id } = req.params;

    TodoModel.delete(id, (err, result) => {
      if (err) {
        if (err.message === '할 일을 찾을 수 없습니다') {
          return res.status(404).json({ error: err.message });
        }
        return res.status(500).json({ error: '할 일 삭제에 실패했습니다' });
      }
      res.json(result);
    });
  }

  // PATCH /api/todos/:id/toggle - 완료 상태 토글
  static toggleTodo(req, res) {
    const { id } = req.params;

    TodoModel.toggleComplete(id, (err, result) => {
      if (err) {
        if (err.message === '할 일을 찾을 수 없습니다') {
          return res.status(404).json({ error: err.message });
        }
        return res.status(500).json({ error: '상태 변경에 실패했습니다' });
      }
      res.json(result);
    });
  }
}

// 날짜 형식 검증 헬퍼 함수
function isValidDate(dateString) {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  if (!regex.test(dateString)) return false;

  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date);
}

module.exports = TodoController;
