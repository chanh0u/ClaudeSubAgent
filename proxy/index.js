import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import cors from 'cors';

const app = express();
const PORT = 3456;
const BACKEND_URL = 'http://localhost:3003';

// CORS 설정
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}));

// 로깅 미들웨어
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', proxy: true, backend: BACKEND_URL });
});

// 모든 /api 요청을 백엔드로 프록시
app.use('/api', createProxyMiddleware({
  target: BACKEND_URL,
  changeOrigin: true,
  logLevel: 'info',
  onProxyReq: (proxyReq, req, res) => {
    console.log(`  → Proxy to: ${BACKEND_URL}${req.url}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`  ← Response: ${proxyRes.statusCode}`);
  },
  onError: (err, req, res) => {
    console.error(`  ✗ Proxy error:`, err.message);
    res.status(500).json({ error: 'Proxy error', message: err.message });
  }
}));

// 모든 /v1 요청도 백엔드로 프록시 (OpenAI 호환 API)
app.use('/v1', createProxyMiddleware({
  target: BACKEND_URL,
  changeOrigin: true,
  logLevel: 'info',
  onProxyReq: (proxyReq, req, res) => {
    console.log(`  → Proxy to: ${BACKEND_URL}${req.url}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`  ← Response: ${proxyRes.statusCode}`);
  },
  onError: (err, req, res) => {
    console.error(`  ✗ Proxy error:`, err.message);
    res.status(500).json({ error: 'Proxy error', message: err.message });
  }
}));

app.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log(`🔌 Claude Agent Proxy Server Started`);
  console.log(`📡 Listening on: http://localhost:${PORT}`);
  console.log(`🎯 Backend target: ${BACKEND_URL}`);
  console.log(`⏰ Started at: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
});
