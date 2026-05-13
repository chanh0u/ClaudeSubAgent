const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// 데이터베이스 연결
const dbPath = path.join(__dirname, '../../..', 'todos.db');
const db = new sqlite3.Database(dbPath);

// 스키마 초기화
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS todos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title VARCHAR(255) NOT NULL,
      completed BOOLEAN NOT NULL DEFAULT 0,
      deadline DATE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  db.run('CREATE INDEX IF NOT EXISTS idx_todos_title ON todos(title)');
  db.run('CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed)');
  db.run('CREATE INDEX IF NOT EXISTS idx_todos_deadline ON todos(deadline)');
  db.run('CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at)');
});

// 모든 할 일 조회
const getAllTodos = () => {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM todos ORDER BY created_at DESC', [], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
};

// 할 일 생성
const createTodo = (title, deadline) => {
  return new Promise((resolve, reject) => {
    const query = 'INSERT INTO todos (title, deadline) VALUES (?, ?)';
    db.run(query, [title, deadline || null], function(err) {
      if (err) reject(err);
      else {
        db.get('SELECT * FROM todos WHERE id = ?', [this.lastID], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      }
    });
  });
};

// 할 일 수정
const updateTodo = (id, title, deadline, completed) => {
  return new Promise((resolve, reject) => {
    const query = 'UPDATE todos SET title = ?, deadline = ?, completed = ? WHERE id = ?';
    db.run(query, [title, deadline || null, completed ? 1 : 0, id], function(err) {
      if (err) reject(err);
      else if (this.changes === 0) reject(new Error('Todo not found'));
      else {
        db.get('SELECT * FROM todos WHERE id = ?', [id], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      }
    });
  });
};

// 할 일 삭제
const deleteTodo = (id) => {
  return new Promise((resolve, reject) => {
    db.run('DELETE FROM todos WHERE id = ?', [id], function(err) {
      if (err) reject(err);
      else if (this.changes === 0) reject(new Error('Todo not found'));
      else resolve();
    });
  });
};

// 완료 상태 토글
const toggleTodo = (id) => {
  return new Promise((resolve, reject) => {
    db.get('SELECT completed FROM todos WHERE id = ?', [id], (err, row) => {
      if (err) reject(err);
      else if (!row) reject(new Error('Todo not found'));
      else {
        const newCompleted = row.completed === 1 ? 0 : 1;
        db.run('UPDATE todos SET completed = ? WHERE id = ?', [newCompleted, id], (err) => {
          if (err) reject(err);
          else resolve({ id: parseInt(id), completed: newCompleted === 1 });
        });
      }
    });
  });
};

module.exports = {
  getAllTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  toggleTodo
};
