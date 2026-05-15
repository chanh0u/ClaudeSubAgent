import express from "express";
import cors from "cors";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors({ origin: "http://localhost:5173" }));
app.use(express.json({ limit: "1mb" }));

const PORT = process.env.PORT || 3001;

// Agent 파일 파싱 함수
function parseAgentFile(content, filename) {
  const lines = content.split("\n");
  const agent = {
    id: filename.replace(".md", ""),
    name: "",
    specialty: "",
    experience: "",
    level: "",
    techStack: [],
    role: "",
    suitableProjects: "",
    defaultConditions: ""
  };

  let currentSection = "";
  let techStackStarted = false;

  for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed.startsWith("# ")) {
      agent.name = trimmed.substring(2);
    } else if (trimmed.startsWith("## ")) {
      currentSection = trimmed.substring(3);
      techStackStarted = false;
    } else if (trimmed.startsWith("- **이름**:")) {
      agent.name = trimmed.split(":")[1].trim();
    } else if (trimmed.startsWith("- **전문분야**:")) {
      agent.specialty = trimmed.split(":")[1].trim();
    } else if (trimmed.startsWith("- **경력**:")) {
      agent.experience = trimmed.split(":")[1].trim();
    } else if (trimmed.startsWith("- **레벨**:")) {
      agent.level = trimmed.split(":")[1].trim();
    } else if (currentSection === "기술 스택" && trimmed.startsWith("- ")) {
      agent.techStack.push(trimmed.substring(2));
    } else if (currentSection === "역할" && trimmed && !trimmed.startsWith("#")) {
      agent.role += (agent.role ? " " : "") + trimmed;
    } else if (currentSection === "적합한 프로젝트" && trimmed.startsWith("- ")) {
      agent.suitableProjects += (agent.suitableProjects ? ", " : "") + trimmed.substring(2);
    } else if (currentSection === "기본 선택 조건" && trimmed.startsWith("- ")) {
      agent.defaultConditions += (agent.defaultConditions ? ", " : "") + trimmed.substring(2);
    }
  }

  return agent;
}

// Agent 목록 가져오기
function getAgents() {
  const agentsDir = path.join(__dirname, "..", ".claude", "agents");

  if (!fs.existsSync(agentsDir)) {
    return [];
  }

  const files = fs.readdirSync(agentsDir).filter(f => f.endsWith(".md"));
  const agents = [];

  for (const file of files) {
    const content = fs.readFileSync(path.join(agentsDir, file), "utf-8");
    const agent = parseAgentFile(content, file);
    agents.push(agent);
  }

  return agents;
}

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
  const requestBody = {
    model,
    stream: false,
    messages: toRoleMessages(messages)
  };

  console.log(`🤖 Ollama API 호출: ${url}, 모델: ${model}, 메시지 수: ${messages.length}`);
  if (process.env.DEBUG) {
    console.log(`📤 요청 본문:`, JSON.stringify(requestBody, null, 2));
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120000); // 120s timeout

    const res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(requestBody),
      signal: controller.signal
    });

    clearTimeout(timeout);

    const responseText = await res.text();
    console.log(`📥 응답 상태: ${res.status}`);

    if (process.env.DEBUG) {
      console.log(`📥 응답 본문:`, responseText.substring(0, 500));
    }

    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseErr) {
      console.error(`❌ JSON 파싱 실패:`, parseErr.message);
      console.error(`원본 응답:`, responseText.substring(0, 200));
      throw new Error(`JSON 파싱 실패: ${parseErr.message}`);
    }

    if (!res.ok) throw new Error(data.error || `Ollama HTTP ${res.status}`);

    const result = data.message?.content || data.response || "";
    if (!result && process.env.DEBUG) {
      console.warn(`⚠️ content 필드 없음. 전체 응답:`, data);
    }

    console.log(`✅ Ollama 응답 성공 - 길이: ${result.length}자`);
    return result;
  } catch (err) {
    if (err.name === "AbortError") {
      const msg = `Ollama 연결 타임아웃: ${url} (30초 초과)`;
      console.error(`❌ ${msg}`);
      throw new Error(msg);
    }
    console.error(`❌ Ollama 오류:`, err.message);
    if (process.env.DEBUG) {
      console.error(err.stack);
    }
    throw new Error(`Ollama 연결 실패: ${err.message}`);
  }
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
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 30000); // 30s timeout

      try {
        const r = await fetch(url, { signal: controller.signal });
        clearTimeout(timeout);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
      } catch (err) {
        clearTimeout(timeout);
        if (err.name === "AbortError") {
          throw new Error(`연결 타임아웃 (10초 초과) - ${url}`);
        }
        throw new Error(`연결 실패: ${err.message}`);
      }
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

app.get("/api/agents", (_req, res) => {
  try {
    const agents = getAgents();
    res.json({ agents });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.listen(PORT, () => {
  console.log(`server running on http://localhost:${PORT}`);
});
