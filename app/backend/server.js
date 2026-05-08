const express = require('express');
const cors = require('cors');
const todoRoutes = require('./routes/todoRoutes');
const { initDatabase } = require('./models/database');

const app = express();
const PORT = process.env.PORT || 3000;

// 미들웨어
app.use(cors());
app.use(express.json());

// 데이터베이스 초기화
initDatabase();

// 라우트
app.use('/api/todos', todoRoutes);

// 에러 핸들링 미들웨어
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: '서버 오류가 발생했습니다' });
});

app.listen(PORT, () => {
  console.log(`서버가 포트 ${PORT}에서 실행 중입니다`);
});

module.exports = app;
