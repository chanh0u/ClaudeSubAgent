const express = require('express');
const cors = require('cors');
const todoRoutes = require('./routes/todos');

const app = express();
const PORT = 3000;

// 미들웨어
app.use(cors());
app.use(express.json());

// 라우트
app.use('/api/todos', todoRoutes);

// 헬스체크
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// 404 핸들러
app.use((req, res) => {
  res.status(404).json({ error: '요청한 엔드포인트를 찾을 수 없습니다' });
});

// 에러 핸들러
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: '서버 오류가 발생했습니다' });
});

app.listen(PORT, () => {
  console.log(`✅ Backend server running on http://localhost:${PORT}`);
  console.log(`📊 API endpoint: http://localhost:${PORT}/api/todos`);
});
