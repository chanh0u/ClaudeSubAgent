const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const DB_PATH = path.join(__dirname, '../../../todos.db');

let db = null;

function getDatabase() {
  if (!db) {
    db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('데이터베이스 연결 실패:', err.message);
      } else {
        console.log('SQLite 데이터베이스에 연결되었습니다');
      }
    });
  }
  return db;
}

function initDatabase() {
  const db = getDatabase();
  const schemaPath = path.join(__dirname, '../../../schema.sql');

  // 스키마 파일 읽기
  const schema = fs.readFileSync(schemaPath, 'utf8');

  // 각 SQL 문을 분리하여 실행
  const statements = schema
    .split(';')
    .map(s => s.trim())
    .filter(s => s.length > 0);

  statements.forEach((statement) => {
    db.run(statement, (err) => {
      if (err && !err.message.includes('already exists')) {
        console.error('스키마 실행 오류:', err.message);
      }
    });
  });
}

module.exports = {
  getDatabase,
  initDatabase
};
