import { useMemo, useState } from "react";

const stackOptions = ["web", "backend", "db"];
const languageOptions = ["C", "C++", "Java", "Python"];
const directionOptions = ["신규", "고도화", "리팩토링", "POC"];
const domainOptions = ["금융", "유통", "공공", "B2B", "B2C"];

const assistantPrompts = {
  internal: "내부 LLM이 요구사항을 정리합니다.",
  external: "외부 LLM(환경변수 기반)로 요구사항을 정리합니다."
};

function toggle(arr, value) {
  return arr.includes(value) ? arr.filter((v) => v !== value) : [...arr, value];
}

function App() {
  const [llmMode, setLlmMode] = useState("internal");
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

  const summary = useMemo(() => {
    return {
      llmMode,
      requirements: requirements || "(요구사항 미정)",
      stacks: stacks.length ? stacks.join(", ") : "(미선택)",
      languages: languages.length ? languages.join(", ") : "(미선택)",
      direction,
      domain
    };
  }, [llmMode, requirements, stacks, languages, direction, domain]);

  const canReview = requirements.trim().length > 0 && stacks.length > 0 && languages.length > 0;

  const sendChat = () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);

    const synthesized = `요구사항 초안: ${userMsg}`;
    setRequirements(synthesized);

    const assistant = `${assistantPrompts[llmMode]}\n핵심 요구를 초안으로 정리했습니다.`;
    setMessages((prev) => [...prev, { role: "assistant", text: assistant }]);
    setInput("");
    setStatus("draft");
    setReviewed(false);
    setApproved(false);
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
        <p className="sub">LLM 대화로 요구사항을 만들고, 옵션 선택과 최종 검토 후 OK 승인 시점에만 코드를 생성합니다.</p>
      </header>

      <section className="card">
        <h2>1) 요구사항 대화</h2>
        <div className="modeRow">
          <label><input type="radio" checked={llmMode === "internal"} onChange={() => setLlmMode("internal")} /> 내부 LLM</label>
          <label><input type="radio" checked={llmMode === "external"} onChange={() => setLlmMode("external")} /> 외부 LLM (ENV)</label>
        </div>

        <div className="chatBox">
          {messages.map((m, idx) => (
            <div key={idx} className={`msg ${m.role}`}>
              <strong>{m.role === "assistant" ? "AI" : "USER"}</strong>
              <p>{m.text}</p>
            </div>
          ))}
        </div>

        <div className="inputRow">
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="서비스 요구사항을 입력하세요" />
          <button onClick={sendChat}>대화 반영</button>
        </div>
      </section>

      <section className="card">
        <h2>2) 옵션 선택</h2>
        <div className="grid two">
          <div>
            <h3>기술 스택</h3>
            <div className="chips">{stackOptions.map((v) => <button key={v} className={stacks.includes(v) ? "chip active" : "chip"} onClick={() => setStacks((prev) => toggle(prev, v))}>{v}</button>)}</div>
          </div>
          <div>
            <h3>프로그램 언어</h3>
            <div className="chips">{languageOptions.map((v) => <button key={v} className={languages.includes(v) ? "chip active" : "chip"} onClick={() => setLanguages((prev) => toggle(prev, v))}>{v}</button>)}</div>
          </div>
        </div>
        <div className="grid two">
          <div className="formRow">
            <label>프로젝트 방향</label>
            <select value={direction} onChange={(e) => setDirection(e.target.value)}>{directionOptions.map((v) => <option key={v}>{v}</option>)}</select>
          </div>
          <div className="formRow">
            <label>영역</label>
            <select value={domain} onChange={(e) => setDomain(e.target.value)}>{domainOptions.map((v) => <option key={v}>{v}</option>)}</select>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>3) 최종 요약 검토</h2>
        <pre className="summary">{`LLM 모드: ${summary.llmMode}\n요구사항: ${summary.requirements}\n기술 스택: ${summary.stacks}\n언어: ${summary.languages}\n방향: ${summary.direction}\n영역: ${summary.domain}`}</pre>
        <div className="actionRow">
          <button onClick={createReview} disabled={!canReview}>요약본 생성</button>
          <button onClick={approve} disabled={!reviewed}>검토 완료 (OK)</button>
          <button className="ghost" onClick={requestRevision}>수정 요청</button>
        </div>
      </section>

      <section className="card">
        <h2>4) 서비스 시작</h2>
        <p>상태: <strong>{status}</strong></p>
        <button onClick={startService} disabled={!approved || status === "running"}>서비스 시작 (POC 코드 작성)</button>
      </section>
    </div>
  );
}

export default App;