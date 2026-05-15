import React, { useMemo, useState, useEffect } from "react";

const API_BASE = "http://localhost:3001";

const projectTypeOptions = [
  { id: "web", label: "🌐 Web Application", desc: "React/Vue 기반 웹 서비스" },
  { id: "mobile", label: "📱 Mobile App", desc: "React Native/Flutter 앱" },
  { id: "api", label: "🔌 API Server", desc: "Backend Only API 서버" },
  { id: "fullstack", label: "🚀 Fullstack", desc: "Web + API 통합" },
  { id: "desktop", label: "💻 Desktop App", desc: "Electron 데스크톱 앱" },
  { id: "cli", label: "🔧 CLI Tool", desc: "커맨드라인 도구" },
  { id: "mcp", label: "🤖 MCP Server", desc: "Model Context Protocol 서버" }
];

const architectureFeatures = [
  { id: "realtime", label: "실시간 통신", desc: "WebSocket/SSE" },
  { id: "auth", label: "인증/권한 관리", desc: "로그인, JWT, OAuth" },
  { id: "database", label: "데이터베이스 집약적", desc: "복잡한 데이터 구조" },
  { id: "file", label: "파일 처리/업로드", desc: "이미지, 문서 처리" },
  { id: "external", label: "외부 API 연동", desc: "서드파티 API 통합" },
  { id: "ai", label: "AI/ML 기능", desc: "인공지능, 머신러닝" }
];

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
      { key: "endpoint", label: "엔드포인트", type: "text", placeholder: "http://llm.aicentro.ai.kr" },
      { key: "model", label: "모델", type: "text", placeholder: "qwen3:8b, qwen2.5-coder ..." }
    ],
    defaults: { endpoint: "http://llm.aicentro.ai.kr", model: "qwen3:8b" }
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

  const [projectType, setProjectType] = useState("fullstack");
  const [features, setFeatures] = useState([]);

  const [agents, setAgents] = useState([]);
  const [selectedAgents, setSelectedAgents] = useState([]);

  const [reviewed, setReviewed] = useState(false);
  const [approved, setApproved] = useState(false);
  const [status, setStatus] = useState("draft");

  const currentProvider = providers.find((p) => p.id === providerId);
  const currentConfig = configs[providerId];
  const providerStatus = connStatus[providerId] || "미연결";
  const isConnected = providerStatus === "연결됨";

  // Agent 목록 가져오기
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/agents`);
        const data = await res.json();
        setAgents(data.agents || []);
      } catch (e) {
        console.error("Failed to fetch agents:", e);
      }
    };
    fetchAgents();
  }, []);

  // 프로젝트 타입과 아키텍처 특성에 따라 추천 agent 자동 선택
  useEffect(() => {
    if (agents.length === 0) return;

    const recommended = [];

    // 1. 프로젝트 유형 기반 핵심 개발자 선택
    switch (projectType) {
      case "web":
        // Web Application → Frontend 필수
        const frontendWeb = agents.find(a => a.id === "frontend-developer");
        const backendWeb = agents.find(a => a.id === "backend-developer");
        if (frontendWeb) recommended.push(frontendWeb.id);
        if (backendWeb) recommended.push(backendWeb.id);
        break;

      case "mobile":
        // Mobile App → Frontend (모바일 개발도 Frontend 역할)
        const frontendMobile = agents.find(a => a.id === "frontend-developer");
        const backendMobile = agents.find(a => a.id === "backend-developer");
        if (frontendMobile) recommended.push(frontendMobile.id);
        if (backendMobile) recommended.push(backendMobile.id);
        break;

      case "api":
        // API Server → Backend Only
        const backendApi = agents.find(a => a.id === "backend-developer");
        if (backendApi) recommended.push(backendApi.id);
        break;

      case "fullstack":
        // Fullstack → Fullstack Developer
        const fullstack = agents.find(a => a.id === "fullstack-developer");
        if (fullstack) recommended.push(fullstack.id);
        break;

      case "desktop":
        // Desktop App → Frontend (Electron)
        const frontendDesktop = agents.find(a => a.id === "frontend-developer");
        const backendDesktop = agents.find(a => a.id === "backend-developer");
        if (frontendDesktop) recommended.push(frontendDesktop.id);
        if (backendDesktop) recommended.push(backendDesktop.id);
        break;

      case "cli":
      case "mcp":
        // CLI/MCP → Backend (서버 사이드 로직)
        const backendCli = agents.find(a => a.id === "backend-developer");
        if (backendCli) recommended.push(backendCli.id);
        break;
    }

    // 2. 아키텍처 특성 기반 전문가 추가
    if (features.includes("realtime")) {
      // 실시간 통신 → Backend Developer (이미 추가되어 있을 수 있음)
      const backend = agents.find(a => a.id === "backend-developer");
      if (backend && !recommended.includes(backend.id)) {
        recommended.push(backend.id);
      }
    }

    if (features.includes("auth")) {
      // 인증/권한 → Security Engineer
      const security = agents.find(a => a.id === "security-engineer");
      if (security) recommended.push(security.id);
    }

    if (features.includes("database")) {
      // 데이터베이스 집약적 → Database Engineer
      const db = agents.find(a => a.id === "database-engineer");
      if (db) recommended.push(db.id);
    }

    if (features.includes("file") || features.includes("external") || features.includes("ai")) {
      // 파일 처리, 외부 API, AI 기능 → Backend Developer (이미 추가되어 있을 수 있음)
      const backend = agents.find(a => a.id === "backend-developer");
      if (backend && !recommended.includes(backend.id)) {
        recommended.push(backend.id);
      }
    }

    // 3. 항상 추가되는 인력
    const devops = agents.find(a => a.id === "devops-engineer");
    const qa = agents.find(a => a.id === "qa-engineer");
    if (devops) recommended.push(devops.id);
    if (qa) recommended.push(qa.id);

    // 중복 제거
    setSelectedAgents([...new Set(recommended)]);
  }, [agents, projectType, features]);

  const summary = useMemo(() => {
    const projectTypeLabel = projectTypeOptions.find(p => p.id === projectType)?.label || projectType;
    const featuresLabel = features.length
      ? features.map(f => architectureFeatures.find(af => af.id === f)?.label).join(", ")
      : "(없음)";

    return {
      provider: `${currentProvider.label} (${providerStatus})`,
      requirements: requirements || "(요구사항 미정)",
      projectType: projectTypeLabel,
      features: featuresLabel,
      agents: selectedAgents.length
        ? agents
            .filter(a => selectedAgents.includes(a.id))
            .map(a => a.name)
            .join(", ")
        : "(미선택)"
    };
  }, [currentProvider, providerStatus, requirements, projectType, features, selectedAgents, agents]);

  const canReview = requirements.trim().length > 0 && selectedAgents.length > 0;

  const toggleAgent = (agentId) => {
    setSelectedAgents((prev) =>
      prev.includes(agentId) ? prev.filter((id) => id !== agentId) : [...prev, agentId]
    );
  };

  const isRecommended = (agent) => {
    // 프로젝트 유형 기반 추천
    if (projectType === "fullstack" && agent.id === "fullstack-developer") return true;
    if (
      (projectType === "web" || projectType === "mobile" || projectType === "desktop") &&
      agent.id === "frontend-developer"
    )
      return true;
    if (
      (projectType === "web" ||
        projectType === "mobile" ||
        projectType === "desktop" ||
        projectType === "api" ||
        projectType === "cli" ||
        projectType === "mcp") &&
      agent.id === "backend-developer"
    )
      return true;

    // 아키텍처 특성 기반 추천
    if (features.includes("auth") && agent.id === "security-engineer") return true;
    if (features.includes("database") && agent.id === "database-engineer") return true;

    // 항상 추천
    if (agent.id === "devops-engineer" || agent.id === "qa-engineer") return true;

    return false;
  };

  const getAvatarInitial = (name) => {
    if (!name) return "?";
    return name.charAt(0).toUpperCase();
  };

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
        <h2>3) 프로젝트 설정</h2>
        <p className="hint">
          프로젝트 유형과 필요한 기능을 선택하면 적합한 개발팀이 자동으로 추천됩니다.
        </p>

        <div className="formRow">
          <label>프로젝트 유형</label>
          <div className="projectTypeGrid">
            {projectTypeOptions.map((option) => (
              <div
                key={option.id}
                className={`projectTypeCard ${projectType === option.id ? "active" : ""}`}
                onClick={() => setProjectType(option.id)}
              >
                <div className="projectTypeLabel">{option.label}</div>
                <div className="projectTypeDesc">{option.desc}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="formRow" style={{ marginTop: "24px" }}>
          <label>아키텍처 특성 (다중 선택 가능)</label>
          <div className="featuresGrid">
            {architectureFeatures.map((feature) => (
              <label key={feature.id} className="featureCheckbox">
                <input
                  type="checkbox"
                  checked={features.includes(feature.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFeatures([...features, feature.id]);
                    } else {
                      setFeatures(features.filter((f) => f !== feature.id));
                    }
                  }}
                />
                <div className="featureContent">
                  <strong>{feature.label}</strong>
                  <span className="featureDesc">{feature.desc}</span>
                </div>
              </label>
            ))}
          </div>
        </div>
      </section>

      <section className="card">
        <h2>4) 개발팀 구성 (Agent 선택)</h2>
        <p className="hint">
          프로젝트 타입에 맞춰 추천 Agent가 자동 선택됩니다. 필요에 따라 추가/제거할 수 있습니다.
        </p>
        <div className="agentGrid">
          {agents.map((agent) => {
            const selected = selectedAgents.includes(agent.id);
            const recommended = isRecommended(agent);
            return (
              <div
                key={agent.id}
                className={`agentCard ${selected ? "selected" : ""} ${
                  recommended ? "recommended" : ""
                }`}
                onClick={() => toggleAgent(agent.id)}
              >
                <div className="agentCheckbox" />
                <div className="agentHeader">
                  <div className="agentAvatar">{getAvatarInitial(agent.name)}</div>
                  <div className="agentInfo">
                    <h3 className="agentName">{agent.name}</h3>
                    <span className="agentLevel">{agent.level}</span>
                  </div>
                </div>
                <p className="agentSpecialty">{agent.specialty}</p>
                <p className="agentRole">{agent.role}</p>
                {agent.techStack.length > 0 && (
                  <div className="agentTechStack">
                    {agent.techStack.slice(0, 3).map((tech, idx) => (
                      <span key={idx} className="techBadge">
                        {tech}
                      </span>
                    ))}
                    {agent.techStack.length > 3 && (
                      <span className="techBadge">+{agent.techStack.length - 3}</span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        {agents.length === 0 && (
          <p className="hint" style={{ textAlign: "center", marginTop: "20px" }}>
            Agent 프로필을 불러오는 중...
          </p>
        )}
      </section>

      <section className="card">
        <h2>5) 최종 요약 검토</h2>
        <pre className="summary">{`LLM: ${summary.provider}
요구사항: ${summary.requirements}
프로젝트 유형: ${summary.projectType}
아키텍처 특성: ${summary.features}
개발팀 (${selectedAgents.length}명): ${summary.agents}`}</pre>
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
        <h2>6) 서비스 시작</h2>
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
