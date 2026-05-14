import React, { useMemo, useState } from "react";

const API_BASE = "http://localhost:3001";

const stackOptions = ["web", "backend", "db"];
const languageOptions = ["C", "C++", "Java", "Python"];
const directionOptions = ["신규", "고도화", "리팩토링", "POC"];
const domainOptions = ["금융", "유통", "공공", "B2B", "B2C"];

const providers = [
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
    desc: "Cursor API (cursor-agent)",
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
      { key: "endpoint", label: "엔드포인트", type: "text", placeholder: "http://localhost:11434" },
      { key: "model", label: "모델", type: "text", placeholder: "llama3, qwen2.5-coder ..." }
    ],
    defaults: { endpoint: "http://localhost:11434", model: "llama3" }
  }
];

const initialConfigs = providers.reduce((acc, p) => {
  acc[p.id] = { ...p.defaults };
  return acc;
}, {});

function toggle(arr, value) {
  return arr.includes(value) ? arr.filter((v) => v !== value) : [...arr, value];
}

function App() {
  const [providerId, setProviderId] = useState("claude");
  const [configs, setConfigs] = useState(initialConfigs);
  const [connStatus, setConnStatus] = useState({});

  const [messages, setMessages] = useState([
    { role: "assistant", text: "어떤 서비스를 만들고 싶은지 설명해 주세요." }
  ]);
  const [input, setInput] = useState("");
  const [requirements, setRequirements] = useState("");

  const [stacks, setStacks] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [direction, setDirection] = useState("신규");
  const [domain, setDomain] = useState("금융");

  const [reviewed, setReviewed] = useState(false);
  const [approved, setApproved] = useState(false);
  const [status, setStatus] = useState("draft");

  const currentProvider = providers.find((p) => p.id === providerId);
  const currentConfig = configs[providerId];
  const providerStatus = connStatus[providerId] || "미연결";
  const isConnected = providerStatus === "연결됨";

  const summary = useMemo(() => {
    return {
      provider: `${currentProvider.label} (${providerStatus})`,
      requirements: requirements || "(요구사항 미정)",
      stacks: stacks.length ? stacks.join(", ") : "(미선택)",
      languages: languages.length ? languages.join(", ") : "(미선택)",
      direction,
      domain
    };
  }, [currentProvider, providerStatus, requirements, stacks, languages, direction, domain]);

  const canReview =
    requirements.trim().length > 0 && stacks.length > 0 && languages.length > 0;

  const updateConfigField = (key, value) => {
    setConfigs((prev) => ({
      ...prev,
      [providerId]: { ...prev[providerId], [key]: value }
    }));
    setConnStatus((prev) => ({ ...prev, [providerId]: "변경됨" }));
  };

  const testConnection = async () => {
    const allFilled = currentProvider.fields.every((f) =>
      currentConfig[f.key]?.toString().trim()
    );
    if (!allFilled) {
      setConnStatus((prev) => ({ ...prev, [providerId]: "필드 누락" }));
      return;
    }
    setConnStatus((prev) => ({ ...prev, [providerId]: "확인 중..." }));
    try {
      const r = await fetch(`${API_BASE}/api/connection-test`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ provider: providerId, config: currentConfig })
      });
      const data = await r.json();
      setConnStatus((prev) => ({
        ...prev,
        [providerId]: data.ok ? "연결됨" : `실패: ${data.error || "unknown"}`
      }));
    } catch (e) {
      setConnStatus((prev) => ({
        ...prev,
        [providerId]: `실패: ${e.message}`
      }));
    }
  };

  const sendChat = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    const nextMessages = [...messages, { role: "user", text: userMsg }];
    setMessages(nextMessages);
    setInput("");
    setRequirements(`요구사항 초안: ${userMsg}`);
    setStatus("draft");
    setReviewed(false);
    setApproved(false);

    try {
      const r = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          provider: providerId,
          config: currentConfig,
          messages: nextMessages
        })
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || `HTTP ${r.status}`);
      setMessages((prev) => [...prev, { role: "assistant", text: data.text }]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `오류: ${e.message}` }
      ]);
    }
  };

  const createReview = () => {
    if (!canReview) return;
    setReviewed(true);
    setApproved(false);
    setStatus("ready_for_review");
  };

  const approve = () => {
    setApproved(true);
    setStatus("approved");
  };

  const requestRevision = () => {
    setApproved(false);
    setStatus("draft");
  };

  const startService = () => {
    if (!approved) return;
    setStatus("running");
    setTimeout(() => setStatus("packaged"), 1400);
  };

  return (
    <div className="page">
      <header className="hero card">
        <p className="eyebrow">Claude Agent Platform</p>
        <h1>대화형 요구사항 수집 + 승인 기반 POC 실행</h1>
        <p className="sub">
          LLM 대화로 요구사항을 만들고, 옵션 선택과 최종 검토 후 OK 승인 시점에만 코드를 생성합니다.
        </p>
      </header>

      <section className="card">
        <h2>1) LLM 연결</h2>
        <div className="providerTabs">
          {providers.map((p) => {
            const s = connStatus[p.id];
            const dotClass = s === "연결됨" ? "dot ok" : s ? "dot warn" : "dot";
            return (
              <button
                key={p.id}
                className={`providerTab ${providerId === p.id ? "active" : ""}`}
                onClick={() => setProviderId(p.id)}
              >
                <span className={dotClass} />
                {p.label}
              </button>
            );
          })}
        </div>

        <p className="hint">{currentProvider.desc}</p>

        <div className="providerForm">
          {currentProvider.fields.map((f) => (
            <div className="formRow" key={f.key}>
              <label>{f.label}</label>
              {f.type === "select" ? (
                <select
                  value={currentConfig[f.key]}
                  onChange={(e) => updateConfigField(f.key, e.target.value)}
                >
                  {f.options.map((opt) => (
                    <option key={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <input
                  type={f.type}
                  value={currentConfig[f.key]}
                  placeholder={f.placeholder}
                  onChange={(e) => updateConfigField(f.key, e.target.value)}
                />
              )}
            </div>
          ))}
        </div>

        <div className="actionRow">
          <button onClick={testConnection}>연결 확인</button>
          <span className={`statusBadge ${isConnected ? "ok" : "warn"}`}>
            상태: {providerStatus}
          </span>
        </div>
      </section>

      <section className="card">
        <h2>2) 요구사항 대화</h2>
        <p className="hint">
          현재 LLM: <strong>{currentProvider.label}</strong>
        </p>

        <div className="chatBox">
          {messages.map((m, idx) => (
            <div key={idx} className={`msg ${m.role}`}>
              <strong>{m.role === "assistant" ? "AI" : "USER"}</strong>
              <p>{m.text}</p>
            </div>
          ))}
        </div>

        <div className="inputRow">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="서비스 요구사항을 입력하세요"
          />
          <button onClick={sendChat}>대화 반영</button>
        </div>
      </section>

      <section className="card">
        <h2>3) 옵션 선택</h2>
        <div className="grid two">
          <div>
            <h3>기술 스택</h3>
            <div className="chips">
              {stackOptions.map((v) => (
                <button
                  key={v}
                  className={stacks.includes(v) ? "chip active" : "chip"}
                  onClick={() => setStacks((prev) => toggle(prev, v))}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>
          <div>
            <h3>프로그램 언어</h3>
            <div className="chips">
              {languageOptions.map((v) => (
                <button
                  key={v}
                  className={languages.includes(v) ? "chip active" : "chip"}
                  onClick={() => setLanguages((prev) => toggle(prev, v))}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="grid two">
          <div className="formRow">
            <label>프로젝트 방향</label>
            <select value={direction} onChange={(e) => setDirection(e.target.value)}>
              {directionOptions.map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </div>
          <div className="formRow">
            <label>영역</label>
            <select value={domain} onChange={(e) => setDomain(e.target.value)}>
              {domainOptions.map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>4) 최종 요약 검토</h2>
        <pre className="summary">{`LLM: ${summary.provider}
요구사항: ${summary.requirements}
기술 스택: ${summary.stacks}
언어: ${summary.languages}
방향: ${summary.direction}
영역: ${summary.domain}`}</pre>
        <div className="actionRow">
          <button onClick={createReview} disabled={!canReview}>
            요약본 생성
          </button>
          <button onClick={approve} disabled={!reviewed}>
            검토 완료 (OK)
          </button>
          <button className="ghost" onClick={requestRevision}>
            수정 요청
          </button>
        </div>
      </section>

      <section className="card">
        <h2>5) 서비스 시작</h2>
        <p>
          상태: <strong>{status}</strong>
        </p>
        <button onClick={startService} disabled={!approved || status === "running"}>
          서비스 시작 (POC 코드 작성)
        </button>
      </section>
    </div>
  );
}

export default App;
