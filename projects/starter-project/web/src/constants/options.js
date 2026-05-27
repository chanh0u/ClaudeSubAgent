export const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:3003";

export const projectTypeOptions = [
  { id: "web", label: "🌐 Web Application", desc: "React/Vue 기반 웹 서비스" },
  { id: "mobile", label: "📱 Mobile App", desc: "React Native/Flutter 앱" },
  { id: "api", label: "🔌 API Server", desc: "Backend Only API 서버" },
  { id: "fullstack", label: "🚀 Fullstack", desc: "Web + API 통합" },
  { id: "desktop", label: "💻 Desktop App", desc: "Electron 데스크톱 앱" },
  { id: "cli", label: "🔧 CLI Tool", desc: "커맨드라인 도구" },
  { id: "mcp", label: "🤖 MCP Server", desc: "Model Context Protocol 서버" }
];

export const architectureFeatures = [
  { id: "realtime", label: "실시간 통신", desc: "WebSocket/SSE" },
  { id: "auth", label: "인증/권한 관리", desc: "로그인, JWT, OAuth" },
  { id: "database", label: "데이터베이스 집약적", desc: "복잡한 데이터 구조" },
  { id: "file", label: "파일 처리/업로드", desc: "이미지, 문서 처리" },
  { id: "external", label: "외부 API 연동", desc: "서드파티 API 통합" },
  { id: "ai", label: "AI/ML 기능", desc: "인공지능, 머신러닝" }
];

export const providers = [
  {
    id: "claude",
    label: "Claude",
    desc: "Anthropic API",
    fields: [
      { key: "apiKey", label: "API Key", type: "password", placeholder: "sk-ant-..." },
      {
        key: "model",
        label: "모델",
        type: "select",
        options: ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]
      }
    ],
    defaults: { apiKey: "", model: "claude-opus-4-7" }
  },
  {
    id: "codex",
    label: "Codex (OpenAI)",
    desc: "OpenAI API",
    fields: [
      { key: "apiKey", label: "API Key", type: "password", placeholder: "sk-..." },
      {
        key: "model",
        label: "모델",
        type: "select",
        options: ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini"]
      }
    ],
    defaults: { apiKey: "", model: "gpt-4o" }
  },
  {
    id: "cursor",
    label: "Cursor",
    desc: "Cursor API (현재 미지원)",
    unsupported: true,
    fields: [
      { key: "apiKey", label: "API Key", type: "password", placeholder: "cursor-..." },
      { key: "model", label: "모델", type: "text", placeholder: "auto" }
    ],
    defaults: { apiKey: "", model: "auto" }
  },
  {
    id: "local",
    label: "로컬 LLM",
    desc: "Ollama / LM Studio / vLLM 등",
    fields: [
      { key: "endpoint", label: "엔드포인트", type: "text", placeholder: "http://llm.aicentro.ai.kr" },
      { key: "model", label: "모델", type: "text", placeholder: "qwen3:8b, qwen2.5-coder ..." }
    ],
    defaults: { endpoint: "http://llm.aicentro.ai.kr", model: "qwen3:8b" }
  },
  {
    id: "manus",
    label: "Manus",
    desc: "Manus AI API",
    fields: [
      { key: "apiKey", label: "API Key", type: "password", placeholder: "sk-..." },
      {
        key: "model",
        label: "Agent Profile",
        type: "select",
        options: ["manus-1.6", "manus-1.6-lite", "manus-1.6-max"]
      }
    ],
    defaults: { apiKey: "", model: "manus-1.6" }
  }
];

export const initialConfigs = providers.reduce((acc, provider) => {
  acc[provider.id] = { ...provider.defaults };
  return acc;
}, {});
