const express = require('express');
const router = express.Router();
const todoController = require('../controllers/todoController');

// 할 일 라우트 정의
router.get('/', todoController.getTodos);
router.post('/', todoController.createTodo);
router.put('/:id', todoController.updateTodo);
router.delete('/:id', todoController.deleteTodo);
router.patch('/:id/toggle', todoController.toggleTodo);

module.exports = router;
