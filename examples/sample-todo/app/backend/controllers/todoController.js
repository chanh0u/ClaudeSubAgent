const todoModel = require('../models/todoModel');

// GET /api/todos - 모든 할 일 조회
const getTodos = async (req, res) => {
  try {
    const todos = await todoModel.getAllTodos();
    res.json(todos);
  } catch (error) {
    res.status(500).json({ error: '할 일 목록을 불러오는데 실패했습니다' });
  }
};

// POST /api/todos - 새 할 일 생성
const createTodo = async (req, res) => {
  try {
    const { title, deadline } = req.body;

    // 입력 검증
    if (!title || title.trim() === '') {
      return res.status(400).json({ error: '제목은 필수 입력 항목입니다' });
    }

    const todo = await todoModel.createTodo(title, deadline);
    res.status(201).json(todo);
  } catch (error) {
    res.status(500).json({ error: '할 일을 생성하는데 실패했습니다' });
  }
};

// PUT /api/todos/:id - 할 일 수정
const updateTodo = async (req, res) => {
  try {
    const { id } = req.params;
    const { title, deadline, completed } = req.body;

    // 입력 검증
    if (!title || title.trim() === '') {
      return res.status(400).json({ error: '제목은 필수 입력 항목입니다' });
    }

    const todo = await todoModel.updateTodo(id, title, deadline, completed);
    res.json(todo);
  } catch (error) {
    if (error.message === 'Todo not found') {
      res.status(404).json({ error: '해당 할 일을 찾을 수 없습니다' });
    } else {
      res.status(500).json({ error: '할 일을 수정하는데 실패했습니다' });
    }
  }
};

// DELETE /api/todos/:id - 할 일 삭제
const deleteTodo = async (req, res) => {
  try {
    const { id } = req.params;
    await todoModel.deleteTodo(id);
    res.json({ message: '삭제되었습니다' });
  } catch (error) {
    if (error.message === 'Todo not found') {
      res.status(404).json({ error: '해당 할 일을 찾을 수 없습니다' });
    } else {
      res.status(500).json({ error: '할 일을 삭제하는데 실패했습니다' });
    }
  }
};

// PATCH /api/todos/:id/toggle - 완료 상태 토글
const toggleTodo = async (req, res) => {
  try {
    const { id } = req.params;
    const result = await todoModel.toggleTodo(id);
    res.json(result);
  } catch (error) {
    if (error.message === 'Todo not found') {
      res.status(404).json({ error: '해당 할 일을 찾을 수 없습니다' });
    } else {
      res.status(500).json({ error: '상태를 변경하는데 실패했습니다' });
    }
  }
};

module.exports = {
  getTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  toggleTodo
};
