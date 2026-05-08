const { getDatabase } = require('./database');

class TodoModel {
  // 모든 할 일 조회
  static getAll(callback) {
    const db = getDatabase();
    const sql = 'SELECT * FROM todos ORDER BY created_at DESC';

    db.all(sql, [], (err, rows) => {
      if (err) {
        callback(err, null);
        return;
      }
      // Boolean 변환
      const todos = rows.map(row => ({
        ...row,
        completed: Boolean(row.completed)
      }));
      callback(null, todos);
    });
  }

  // 할 일 생성
  static create(todoData, callback) {
    const db = getDatabase();
    const { title, deadline } = todoData;

    const sql = 'INSERT INTO todos (title, deadline) VALUES (?, ?)';

    db.run(sql, [title, deadline || null], function(err) {
      if (err) {
        callback(err, null);
        return;
      }

      // 생성된 항목 반환
      TodoModel.getById(this.lastID, callback);
    });
  }

  // ID로 할 일 조회
  static getById(id, callback) {
    const db = getDatabase();
    const sql = 'SELECT * FROM todos WHERE id = ?';

    db.get(sql, [id], (err, row) => {
      if (err) {
        callback(err, null);
        return;
      }
      if (row) {
        row.completed = Boolean(row.completed);
      }
      callback(null, row);
    });
  }

  // 할 일 수정
  static update(id, todoData, callback) {
    const db = getDatabase();
    const { title, deadline, completed } = todoData;

    const sql = `
      UPDATE todos
      SET title = ?, deadline = ?, completed = ?
      WHERE id = ?
    `;

    db.run(sql, [title, deadline || null, completed ? 1 : 0, id], function(err) {
      if (err) {
        callback(err, null);
        return;
      }

      if (this.changes === 0) {
        callback(new Error('할 일을 찾을 수 없습니다'), null);
        return;
      }

      TodoModel.getById(id, callback);
    });
  }

  // 할 일 삭제
  static delete(id, callback) {
    const db = getDatabase();
    const sql = 'DELETE FROM todos WHERE id = ?';

    db.run(sql, [id], function(err) {
      if (err) {
        callback(err, null);
        return;
      }

      if (this.changes === 0) {
        callback(new Error('할 일을 찾을 수 없습니다'), null);
        return;
      }

      callback(null, { message: '삭제되었습니다' });
    });
  }

  // 완료 상태 토글
  static toggleComplete(id, callback) {
    const db = getDatabase();

    // 먼저 현재 상태 조회
    TodoModel.getById(id, (err, todo) => {
      if (err) {
        callback(err, null);
        return;
      }

      if (!todo) {
        callback(new Error('할 일을 찾을 수 없습니다'), null);
        return;
      }

      const newCompleted = !todo.completed;
      const sql = 'UPDATE todos SET completed = ? WHERE id = ?';

      db.run(sql, [newCompleted ? 1 : 0, id], function(err) {
        if (err) {
          callback(err, null);
          return;
        }

        callback(null, { id: parseInt(id), completed: newCompleted });
      });
    });
  }
}

module.exports = TodoModel;
