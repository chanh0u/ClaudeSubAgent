#!/usr/bin/env python3
import sys
import json
import os
import re
import urllib.request
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webhook_config.json")


def load_config() -> dict:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def is_event_enabled(config: dict, event: str) -> bool:
    if not config.get("enabled", True):
        return False
    return config.get("events", {}).get(event, True)


def get_webhook_url(config: dict) -> str:
    return config.get("webhook_url") or os.environ.get("SLACK_WEBHOOK_URL", "")


# ── 텍스트 정규화 ──────────────────────────────────────────────
def normalize(text: str, max_len: int = 300) -> str:
    if not text:
        return ""
    text = re.sub(r"```[\s\S]*?```", "[코드 블록]", text)
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = re.sub(r"^\s*#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"https?://\S{60,}", "[URL]", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.strip()
    if len(text) > max_len:
        cut = text[:max_len].rsplit(". ", 1)[0]
        text = (cut if len(cut) > max_len // 2 else text[:max_len]).rstrip(".,;:") + " …"
    return text


# ── Slack Block Kit 전송 ───────────────────────────────────────
def send_slack(webhook_url: str, blocks: list, fallback: str = ""):
    if not webhook_url:
        return
    payload = json.dumps(
        {"text": fallback, "blocks": blocks}, ensure_ascii=False
    ).encode("utf-8", errors="replace")
    req = urllib.request.Request(
        webhook_url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def divider():
    return {"type": "divider"}


def section(text: str):
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def fields_block(*pairs):
    return {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*{label}*\n{value}"}
            for label, value in pairs
        ],
    }


# ── stdin 읽기 ─────────────────────────────────────────────────
def read_stdin() -> dict:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        return json.loads(raw)
    except Exception:
        return {}


def extract_last_message(data: dict) -> str:
    for msg in reversed(data.get("messages") or data.get("transcript") or []):
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
            return normalize(text)
    return ""


# ── 이벤트 핸들러 ──────────────────────────────────────────────
def handle_subagent_stop(data: dict, webhook_url: str):
    agent = data.get("agent_name") or data.get("subagent_name") or "Agent"
    session_id = (data.get("session_id", "") or "")[:8] or "—"
    project = os.path.basename(data.get("cwd", os.getcwd()))
    summary = extract_last_message(data)
    ts = datetime.now().strftime("%H:%M:%S")

    blocks = [
        section("🤖  *Agent 작업 완료*"),
        fields_block(
            ("Agent", agent),
            ("Project", project),
            ("Session", session_id),
            ("시각", ts),
        ),
    ]
    if summary:
        blocks += [divider(), section(f"*📋 작업 요약*\n{summary}")]
    blocks.append(divider())

    send_slack(webhook_url, blocks, fallback=f"[Agent 완료] {agent} — {summary or project}")


def handle_post_tool(data: dict, webhook_url: str, config: dict):
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    cwd = data.get("cwd", os.getcwd())
    project = os.path.basename(cwd)
    ts = datetime.now().strftime("%H:%M:%S")

    if tool_name in ("Edit", "Write") and is_event_enabled(config, "file_edit"):
        file_path = tool_input.get("file_path", "")
        rel_path = file_path.replace(cwd, "").replace("\\", "/").lstrip("/") or file_path
        blocks = [
            section("📝  *파일 수정*"),
            fields_block(
                ("파일", f"`{rel_path}`"),
                ("Project", project),
                ("Tool", tool_name),
                ("시각", ts),
            ),
            divider(),
        ]
        send_slack(webhook_url, blocks, fallback=f"[파일 수정] {rel_path}")

    elif tool_name == "Bash" and is_event_enabled(config, "git_commit"):
        cmd = str(tool_input.get("command", ""))
        if "git commit" not in cmd:
            return
        match = re.search(r'-m\s+["\'](.+?)["\']', cmd, re.DOTALL)
        commit_msg = normalize(match.group(1), max_len=120) if match else "—"
        blocks = [
            section("📦  *Git Commit*"),
            fields_block(("Project", project), ("시각", ts)),
            section(f"*커밋 메시지*\n```{commit_msg}```"),
            divider(),
        ]
        send_slack(webhook_url, blocks, fallback=f"[Git Commit] {commit_msg}")


# ── 진입점 ────────────────────────────────────────────────────
def main():
    event_type = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    data = read_stdin()
    config = load_config()
    webhook_url = get_webhook_url(config)

    if event_type == "subagent_stop" and is_event_enabled(config, "subagent_stop"):
        handle_subagent_stop(data, webhook_url)
    elif event_type == "post_tool":
        handle_post_tool(data, webhook_url, config)


if __name__ == "__main__":
    main()
