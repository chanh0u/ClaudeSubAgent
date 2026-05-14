import express from "express";
import cors from "cors";

const app = express();
app.use(cors({ origin: "http://localhost:5173" }));
app.use(express.json({ limit: "1mb" }));

const PORT = process.env.PORT || 3001;

const toRoleMessages = (messages) =>
  messages.map((m) => ({
    role: m.role === "assistant" ? "assistant" : "user",
    content: m.text
  }));

async function callClaude({ apiKey, model, messages }) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model,
      max_tokens: 1024,
      messages: toRoleMessages(messages)
    })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || `Claude API ${res.status}`);
  return data.content?.map((c) => c.text).join("") || "";
}

async function callOpenAI({ apiKey, model, messages }) {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model,
      messages: toRoleMessages(messages)
    })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || `OpenAI API ${res.status}`);
  return data.choices?.[0]?.message?.content || "";
}

async function callOllama({ endpoint, model, messages }) {
  const url = endpoint.replace(/\/$/, "") + "/api/chat";
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model,
      stream: false,
      messages: toRoleMessages(messages)
    })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `Ollama ${res.status}`);
  return data.message?.content || "";
}

const handlers = {
  claude: callClaude,
  codex: callOpenAI,
  local: callOllama
};

app.post("/api/chat", async (req, res) => {
  const { provider, config, messages } = req.body || {};
  if (provider === "cursor") {
    return res
      .status(501)
      .json({ error: "Cursor는 공개 채팅 API가 없어 현재 미지원입니다." });
  }
  const handler = handlers[provider];
  if (!handler) {
    return res.status(400).json({ error: `지원하지 않는 provider: ${provider}` });
  }
  try {
    const text = await handler({ ...config, messages });
    res.json({ text });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post("/api/connection-test", async (req, res) => {
  const { provider, config } = req.body || {};
  try {
    if (provider === "claude") {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": config.apiKey,
          "anthropic-version": "2023-06-01"
        },
        body: JSON.stringify({
          model: config.model,
          max_tokens: 1,
          messages: [{ role: "user", content: "ping" }]
        })
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.error?.message || `HTTP ${r.status}`);
      }
    } else if (provider === "codex") {
      const r = await fetch("https://api.openai.com/v1/models", {
        headers: { authorization: `Bearer ${config.apiKey}` }
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
    } else if (provider === "local") {
      const url = config.endpoint.replace(/\/$/, "") + "/api/tags";
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
    } else if (provider === "cursor") {
      throw new Error("Cursor 공개 API 미지원");
    } else {
      throw new Error(`지원하지 않는 provider: ${provider}`);
    }
    res.json({ ok: true });
  } catch (e) {
    res.status(200).json({ ok: false, error: e.message });
  }
});

app.get("/api/health", (_req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`server running on http://localhost:${PORT}`);
});
