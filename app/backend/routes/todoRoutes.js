const express = require('express');
const TodoController = require('../controllers/todoController');

const router = express.Router();

// GET /api/todos - 모든 할 일 조회
router.get('/', TodoController.getAllTodos);

// POST /api/todos - 새 할 일 생성
router.post('/', TodoController.createTodo);

// PUT /api/todos/:id - 할 일 수정
router.put('/:id', TodoController.updateTodo);

// DELETE /api/todos/:id - 할 일 삭제
router.delete('/:id', TodoController.deleteTodo);

// PATCH /api/todos/:id/toggle - 완료 상태 토글
router.patch('/:id/toggle', TodoController.toggleTodo);

module.exports = router;
