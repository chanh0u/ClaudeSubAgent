import logging
import os
import pathlib
import uuid
import subprocess
import shutil
import zipfile
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, Response
from pydantic import BaseModel, Field, field_validator

# Claude CLI 통합
from .claude_subprocess.claude_cli import ClaudeSubprocess, verify_claude
from .adapters.openai_to_cli import openai_to_cli
from .adapters.cli_to_openai import (
    cli_result_to_openai,
    create_streaming_chunk,
    create_done_chunk,
)

# 로깅 설정
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Claude Agent Platform API", version="1.0.0")

# CORS 설정 (환경변수 ALLOWED_ORIGINS로 오버라이드 가능, 콤마 구분)
_default_origins = "http://localhost:5173"
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def extract_http_error_message(exc: httpx.HTTPStatusError) -> str:
    """HTTP 에러 응답에서 안전하게 메시지 추출 (JSON이 아니어도 예외 미발생)"""
    try:
        body = exc.response.json()
        if isinstance(body, dict):
            error = body.get("error")
            if isinstance(error, dict):
                return error.get("message", str(exc))
            if isinstance(error, str):
                return error
        return str(exc)
    except ValueError:
        text = exc.response.text or ""
        return text[:200] if text else str(exc)


# Pydantic 모델
SUPPORTED_PROVIDERS = {"claude", "codex", "local", "manus"}


class Message(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    provider: str
    config: Dict[str, Any]
    messages: List[Message] = Field(..., min_length=1)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        return v.strip().lower()


class ConnectionTestRequest(BaseModel):
    provider: str
    config: Dict[str, Any]


class AgentProfile(BaseModel):
    id: str
    name: str
    specialty: str
    experience: str
    level: str
    techStack: List[str]
    role: str
    suitableProjects: str
    defaultConditions: str


# OpenAI 호환 API 모델
class OpenAIMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]


class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    stream: bool = False
    user: Optional[str] = None


class ProjectCreateRequest(BaseModel):
    requirements: str
    project_type: str
    features: List[str]
    agents: List[str]


class FileUpdateRequest(BaseModel):
    content: str


class FeedbackRequest(BaseModel):
    feedback: str
    file_path: Optional[str] = None


# 실행 중인 프로젝트 관리
running_projects: Dict[str, Dict[str, Any]] = {}


# Helper functions
def to_role_messages(messages: List[Message]) -> List[Dict[str, str]]:
    """메시지를 API 형식으로 변환"""
    return [
        {
            "role": "assistant" if msg.role == "assistant" else "user",
            "content": msg.text,
        }
        for msg in messages
    ]


def normalize_chat_config(provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize frontend config keys to backend handler signatures."""
    normalized = dict(config or {})

    if "apiKey" in normalized and "api_key" not in normalized:
        normalized["api_key"] = normalized.pop("apiKey")

    if provider in {"claude", "codex", "manus"}:
        return {
            "api_key": normalized.get("api_key", ""),
            "model": normalized.get("model", ""),
        }
    if provider == "local":
        return {
            "endpoint": normalized.get("endpoint", ""),
            "model": normalized.get("model", ""),
        }
    return normalized


async def call_claude(api_key: str, model: str, messages: List[Message]) -> str:
    """Claude API 호출"""
    logger.info(f"🤖 Claude API 호출 시작 - 모델: {model}, 메시지 수: {len(messages)}")
    url = "https://api.anthropic.com/v1/messages"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                url,
                headers={
                    "content-type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": model,
                    "max_tokens": 1024,
                    "messages": to_role_messages(messages),
                },
            )
            response.raise_for_status()
            data = response.json()
            result = "".join(c.get("text", "") for c in data.get("content", []))
            logger.info(f"✅ Claude API 응답 성공 - 응답 길이: {len(result)}자")
            return result
        except httpx.HTTPStatusError as e:
            error_msg = extract_http_error_message(e)
            logger.error(f"❌ Claude API 에러 - {e.response.status_code}: {error_msg}")
            raise HTTPException(status_code=502, detail=f"Claude API 오류: {error_msg}")
        except httpx.RequestError as e:
            logger.error(f"❌ Claude API 연결 오류: {type(e).__name__}: {e}")
            raise HTTPException(status_code=502, detail="Claude API 연결에 실패했습니다.")


async def call_openai(api_key: str, model: str, messages: List[Message]) -> str:
    """OpenAI API 호출"""
    logger.info(f"🤖 OpenAI API 호출 시작 - 모델: {model}, 메시지 수: {len(messages)}")
    url = "https://api.openai.com/v1/chat/completions"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                url,
                headers={
                    "content-type": "application/json",
                    "authorization": f"Bearer {api_key}",
                },
                json={
                    "model": model,
                    "messages": to_role_messages(messages),
                },
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"✅ OpenAI API 응답 성공 - 응답 길이: {len(result)}자")
            return result
        except httpx.HTTPStatusError as e:
            error_msg = extract_http_error_message(e)
            logger.error(f"❌ OpenAI API 에러 - {e.response.status_code}: {error_msg}")
            raise HTTPException(status_code=502, detail=f"OpenAI API 오류: {error_msg}")
        except httpx.RequestError as e:
            logger.error(f"❌ OpenAI API 연결 오류: {type(e).__name__}: {e}")
            raise HTTPException(status_code=502, detail="OpenAI API 연결에 실패했습니다.")


async def call_manus(api_key: str, model: str, messages: List[Message]) -> str:
    """Manus API 호출 (Task 기반)"""
    logger.info(f"🤖 Manus API 호출 시작 - 모델: {model}, 메시지 수: {len(messages)}")

    # 메시지를 content로 변환 (마지막 사용자 메시지만 사용)
    user_content = messages[-1].text if messages else "Hello"

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            # 1. Task 생성
            logger.info(f"📤 Task 생성 중...")
            create_response = await client.post(
                "https://api.manus.ai/v2/task.create",
                headers={
                    "content-type": "application/json",
                    "x-manus-api-key": api_key,
                },
                json={
                    "message": {
                        "content": [{"type": "text", "text": user_content}]
                    },
                    "agent_profile": model,
                    "hide_in_task_list": True,
                },
            )
            create_response.raise_for_status()
            task_data = create_response.json()

            if not task_data.get("ok"):
                error = task_data.get("error", {})
                raise Exception(f"Task 생성 실패: {error.get('message', 'Unknown error')}")

            task_id = task_data.get("task_id")
            if not task_id:
                raise Exception(f"Task ID를 받지 못했습니다: {task_data}")

            logger.info(f"✅ Task 생성됨 - ID: {task_id}")

            # 2. Task 메시지 폴링 (최대 3분)
            import asyncio
            result_text = ""
            processed_message_ids = set()
            terminal_statuses = {"stopped", "completed", "done", "finished", "succeeded", "success"}
            for i in range(60):  # 60번 시도 (3초마다)
                await asyncio.sleep(3)
                logger.debug(f"📡 Task 메시지 확인 중... ({i+1}/60)")

                messages_response = await client.get(
                    "https://api.manus.ai/v2/task.listMessages",
                    headers={"x-manus-api-key": api_key},
                    params={"task_id": task_id, "verbose": False},
                )
                messages_response.raise_for_status()
                messages_data = messages_response.json()

                if not messages_data.get("ok"):
                    error = messages_data.get("error", {})
                    raise Exception(f"메시지 조회 실패: {error.get('message', 'Unknown error')}")

                messages_list = messages_data.get("messages", [])

                # 상태 확인 및 결과 추출
                for msg in messages_list:
                    msg_id = str(msg.get("id", ""))
                    if msg_id and msg_id in processed_message_ids:
                        continue
                    if msg_id:
                        processed_message_ids.add(msg_id)

                    event_type = msg.get("event_type")

                    # Assistant 메시지 수집
                    if event_type == "assistant_message":
                        content = msg.get("content", [])
                        for item in content:
                            if item.get("type") == "text":
                                text = item.get("text", "")
                                if text:
                                    result_text += text

                    # 상태 업데이트 확인
                    elif event_type == "status_update":
                        agent_status = str(msg.get("agent_status", "")).lower()
                        logger.debug(f"   상태: {agent_status}")

                        if agent_status in terminal_statuses:
                            logger.info(f"✅ Manus Task 완료 - 응답 길이: {len(result_text)}자")
                            return result_text if result_text else "작업이 완료되었습니다."

                        elif agent_status == "error":
                            error_content = msg.get("content", [])
                            error_msg = "Unknown error"
                            for item in error_content:
                                if item.get("type") == "text":
                                    error_msg = item.get("text", error_msg)
                            logger.error(f"❌ Manus Task 에러: {error_msg}")
                            raise Exception(f"Task error: {error_msg}")

                    # 에러 메시지
                    elif event_type == "error_message":
                        content = msg.get("content", [])
                        error_msg = "Unknown error"
                        for item in content:
                            if item.get("type") == "text":
                                error_msg = item.get("text", error_msg)
                        logger.error(f"❌ Manus Task 실패: {error_msg}")
                        raise Exception(f"Task failed: {error_msg}")

            # 타임아웃
            logger.error(f"⏱️ Manus Task 타임아웃 - ID: {task_id}")
            if result_text:
                logger.info(f"   부분 결과 반환: {len(result_text)}자")
                return result_text
            raise Exception(f"Task timeout after 3 minutes")

        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(f"❌ Manus API 에러 - {e.response.status_code}: {error_text[:500]}")
            raise HTTPException(status_code=502, detail=f"Manus API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"❌ Manus API 연결 오류: {type(e).__name__}: {e}")
            raise HTTPException(status_code=502, detail="Manus API 연결에 실패했습니다.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Manus API 처리 오류: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Manus 처리 오류: {str(e)}")


async def call_ollama(endpoint: str, model: str, messages: List[Message]) -> str:
    """Ollama API 호출"""
    logger.info(
        f"🤖 Ollama API 호출 시작 - 엔드포인트: {endpoint}, 모델: {model}, 메시지 수: {len(messages)}"
    )
    url = endpoint.rstrip("/") + "/api/chat"

    # 메시지 변환
    converted_messages = to_role_messages(messages)
    logger.info(f"📤 변환된 메시지 수: {len(converted_messages)}")
    logger.debug(f"📤 요청 메시지: {converted_messages}")

    request_body = {
        "model": model,
        "stream": False,
        "messages": converted_messages,
    }
    logger.debug(f"📤 요청 본문: {request_body}")

    # 타임아웃 설정: connect 5초, read/write 120초
    timeout_config = httpx.Timeout(
        connect=5.0,
        read=120.0,
        write=10.0,
        pool=5.0
    )

    logger.info(f"🌐 요청 URL: {url}")
    logger.info(f"⏱️ 타임아웃 설정: connect=5s, read=120s")

    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            logger.info("📡 HTTP POST 요청 전송 중...")

            response = await client.post(
                url,
                headers={"content-type": "application/json"},
                json=request_body,
            )

            logger.info(f"📥 응답 수신 완료 - 상태: {response.status_code}")

            # 응답 본문 로깅
            response_text = response.text
            logger.info(f"📥 응답 크기: {len(response_text)} bytes")
            logger.debug(f"📥 응답 본문 (raw): {response_text[:500]}...")

            response.raise_for_status()

            try:
                data = response.json()
                logger.debug(f"📥 응답 JSON: {data}")
            except ValueError as json_err:
                logger.error(f"❌ JSON 파싱 실패: {json_err}, 원본: {response_text[:200]}")
                raise HTTPException(status_code=502, detail="Ollama 응답을 파싱할 수 없습니다.")

            result = data.get("message", {}).get("content", "")

            if not result:
                logger.warning(f"⚠️ 응답에 content가 없음. 전체 응답: {data}")
                # 대체 경로 시도
                if "response" in data:
                    result = data.get("response", "")
                    logger.info(f"✅ 'response' 필드에서 내용 추출")

            logger.info(f"✅ Ollama API 응답 성공 - 응답 길이: {len(result)}자")
            return result
        except httpx.TimeoutException as e:
            logger.error(f"❌ Ollama 연결 타임아웃 - {url} ({type(e).__name__})")
            raise HTTPException(status_code=504, detail="Ollama 서버 응답 타임아웃")
        except httpx.ConnectError as e:
            logger.error(f"❌ Ollama 연결 실패 - {url}: {str(e)}")
            raise HTTPException(status_code=502, detail="Ollama 서버에 연결할 수 없습니다.")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Ollama API 에러 - {e.response.status_code}: {e.response.text[:500]}")
            raise HTTPException(status_code=502, detail=f"Ollama HTTP {e.response.status_code}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ollama 예외 발생: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
            raise HTTPException(status_code=502, detail="Ollama 처리 중 오류가 발생했습니다.")


def parse_agent_file(content: str, filename: str) -> AgentProfile:
    """Agent MD 파일 파싱"""
    lines = content.split("\n")
    agent = AgentProfile(
        id=filename.replace(".md", ""),
        name="",
        specialty="",
        experience="",
        level="",
        techStack=[],
        role="",
        suitableProjects="",
        defaultConditions="",
    )

    current_section = ""

    for line in lines:
        trimmed = line.strip()

        if trimmed.startswith("# "):
            agent.name = trimmed[2:]
        elif trimmed.startswith("## "):
            current_section = trimmed[3:]
        elif trimmed.startswith("- **이름**:"):
            agent.name = trimmed.split(":", 1)[1].strip()
        elif trimmed.startswith("- **전문분야**:"):
            agent.specialty = trimmed.split(":", 1)[1].strip()
        elif trimmed.startswith("- **경력**:"):
            agent.experience = trimmed.split(":", 1)[1].strip()
        elif trimmed.startswith("- **레벨**:"):
            agent.level = trimmed.split(":", 1)[1].strip()
        elif current_section == "기술 스택" and trimmed.startswith("- "):
            agent.techStack.append(trimmed[2:])
        elif current_section == "역할" and trimmed and not trimmed.startswith("#"):
            agent.role += (" " if agent.role else "") + trimmed
        elif current_section == "적합한 프로젝트" and trimmed.startswith("- "):
            agent.suitableProjects += (", " if agent.suitableProjects else "") + trimmed[2:]
        elif current_section == "기본 선택 조건" and trimmed.startswith("- "):
            agent.defaultConditions += (", " if agent.defaultConditions else "") + trimmed[2:]

    return agent


def get_agents() -> List[AgentProfile]:
    """Agent 목록 가져오기"""
    # python/src/main.py 기준으로 ../../.claude/agents 경로
    base_path = pathlib.Path(__file__).parent.parent.parent
    agents_dir = base_path / ".claude" / "agents"

    logger.info(f"📁 Agent 디렉토리 확인: {agents_dir}")

    if not agents_dir.exists():
        logger.warning(f"⚠️ Agent 디렉토리가 존재하지 않습니다: {agents_dir}")
        return []

    agents = []
    md_files = list(agents_dir.glob("*.md"))
    logger.info(f"📄 발견된 Agent 파일 수: {len(md_files)}")

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            agent = parse_agent_file(content, file_path.name)
            agents.append(agent)
            logger.info(f"  ✅ {file_path.name} → {agent.name} ({agent.level})")
        except Exception as e:
            logger.error(f"  ❌ {file_path.name} 파싱 실패: {str(e)}")

    return agents


def get_workspace_path() -> pathlib.Path:
    """Workspace 디렉토리 경로 반환"""
    base_path = pathlib.Path(__file__).parent.parent.parent
    workspace = base_path / "workspace"
    workspace.mkdir(exist_ok=True)
    return workspace


def get_project_path(project_id: str) -> pathlib.Path:
    """특정 프로젝트 디렉토리 경로 반환"""
    return get_workspace_path() / project_id


def get_file_tree(directory: pathlib.Path, prefix: str = "") -> List[Dict[str, Any]]:
    """디렉토리 트리 구조 반환"""
    tree = []
    try:
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        for item in items:
            # 숨김 파일, node_modules, venv 등 제외
            if item.name.startswith('.') or item.name in ['node_modules', 'venv', '__pycache__', 'dist', 'build']:
                continue

            rel_path = str(item.relative_to(get_workspace_path()))
            if item.is_dir():
                tree.append({
                    "name": item.name,
                    "type": "directory",
                    "path": rel_path,
                    "children": get_file_tree(item, prefix + "  ")
                })
            else:
                tree.append({
                    "name": item.name,
                    "type": "file",
                    "path": rel_path,
                    "size": item.stat().st_size
                })
    except Exception as e:
        logger.error(f"파일 트리 생성 실패: {str(e)}")
    return tree


def create_zip_archive(project_path: pathlib.Path) -> io.BytesIO:
    """프로젝트를 ZIP 파일로 압축"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                # 숨김 파일, node_modules 등 제외
                if any(part.startswith('.') or part in ['node_modules', 'venv', '__pycache__'] for part in file_path.parts):
                    continue
                arcname = file_path.relative_to(project_path)
                zip_file.write(file_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer


def find_available_port(start_port: int = 4000, max_port: int = 5000) -> Optional[int]:
    """사용 가능한 포트 찾기"""
    import socket
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return None


# API 엔드포인트
@app.get("/api/health")
async def health_check():
    """서버 헬스 체크"""
    logger.info("💚 Health check 요청")
    return {"ok": True, "timestamp": datetime.now().isoformat()}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """채팅 API"""
    logger.info(f"💬 채팅 요청 - Provider: {request.provider}, 메시지 수: {len(request.messages)}")
    logger.debug(f"📋 Config: {request.config}")

    if request.provider == "cursor":
        logger.warning("⚠️ Cursor provider 요청 - 미지원")
        raise HTTPException(status_code=501, detail="Cursor는 공개 채팅 API가 없어 현재 미지원입니다.")

    handlers = {
        "claude": call_claude,
        "codex": call_openai,
        "local": call_ollama,
        "manus": call_manus,
    }

    handler = handlers.get(request.provider)
    if not handler:
        logger.error(f"❌ 지원하지 않는 provider: {request.provider}")
        raise HTTPException(status_code=400, detail=f"지원하지 않는 provider: {request.provider}")

    try:
        normalized_config = normalize_chat_config(request.provider, request.config)
        text = await handler(**normalized_config, messages=request.messages)
        logger.info(f"✅ 채팅 응답 성공 - 응답 길이: {len(text)}자")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 채팅 처리 중 예외 발생: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="채팅 처리 중 내부 오류가 발생했습니다.")


@app.post("/api/connection-test")
async def connection_test(request: ConnectionTestRequest):
    """연결 테스트 API"""
    logger.info(f"🔌 연결 테스트 요청 - Provider: {request.provider}")

    try:
        if request.provider == "claude":
            logger.info("  → Claude API 테스트 중...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "content-type": "application/json",
                        "x-api-key": request.config.get("apiKey", ""),
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": request.config.get("model", "claude-opus-4-7"),
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "ping"}],
                    },
                )
                response.raise_for_status()

        elif request.provider == "codex":
            logger.info("  → OpenAI API 테스트 중...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"authorization": f"Bearer {request.config.get('apiKey', '')}"},
                )
                response.raise_for_status()

        elif request.provider == "local":
            endpoint = request.config.get("endpoint", "")
            url = endpoint.rstrip("/") + "/api/tags"
            logger.info(f"  → Ollama API 테스트 중... ({url})")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

        elif request.provider == "manus":
            logger.info("  → Manus API 테스트 중...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Manus는 task.list로 간단하게 연결 테스트
                response = await client.get(
                    "https://api.manus.ai/v2/task.list",
                    headers={
                        "x-manus-api-key": request.config.get('apiKey', ''),
                    },
                    params={
                        "limit": 1,  # 최소한의 데이터만 요청
                    },
                )
                response.raise_for_status()
                data = response.json()
                if not data.get("ok"):
                    error = data.get("error", {})
                    raise ValueError(f"Invalid response: {error.get('message', 'Unknown error')}")

        elif request.provider == "cursor":
            logger.warning("  → Cursor API 테스트 - 미지원")
            raise ValueError("Cursor 공개 API 미지원")

        else:
            logger.error(f"  → 지원하지 않는 provider: {request.provider}")
            raise ValueError(f"지원하지 않는 provider: {request.provider}")

        logger.info(f"  ✅ {request.provider} 연결 성공")
        return {"ok": True}

    except httpx.TimeoutException:
        error_msg = f"연결 타임아웃 (10초 초과)"
        logger.error(f"  ❌ {error_msg}")
        return {"ok": False, "error": error_msg}
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}"
        logger.error(f"  ❌ {error_msg}")
        return {"ok": False, "error": error_msg}
    except Exception as e:
        logger.error(f"  ❌ 연결 실패: {str(e)}")
        return {"ok": False, "error": str(e)}


@app.get("/api/agents")
async def get_agents_list():
    """Agent 목록 API"""
    logger.info("👥 Agent 목록 요청")
    try:
        agents = get_agents()
        logger.info(f"✅ Agent 목록 반환 - {len(agents)}개")
        return {"agents": agents}
    except Exception as e:
        logger.error(f"❌ Agent 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OpenAI 호환 API 엔드포인트 (Claude CLI Proxy)
# ============================================================================


@app.get("/v1/models")
async def openai_models():
    """OpenAI 호환 - 사용 가능한 모델 목록"""
    logger.info("📋 OpenAI 모델 목록 요청")
    model_ids = [
        "claude-opus-4",
        "claude-opus-4-6",
        "claude-sonnet-4",
        "claude-sonnet-4-5",
        "claude-sonnet-4-6",
        "claude-haiku-4",
        "claude-haiku-4-5",
    ]
    now = int(datetime.now().timestamp())
    return {
        "object": "list",
        "data": [
            {"id": model_id, "object": "model", "owned_by": "anthropic", "created": now}
            for model_id in model_ids
        ],
    }


@app.post("/v1/chat/completions")
async def openai_chat_completions(request: OpenAIChatRequest):
    """OpenAI 호환 - 채팅 완성 (스트리밍/논스트리밍)"""
    request_id = str(uuid.uuid4()).replace("-", "")[:24]
    logger.info("=" * 80)
    logger.info(f"💬 [요청 시작] Request ID: {request_id}")
    logger.info(f"   모델: {request.model}")
    logger.info(f"   스트리밍: {request.stream}")
    logger.info(f"   메시지 수: {len(request.messages)}")
    if request.messages:
        logger.info(f"   첫 메시지 역할: {request.messages[0].role}")
        first_content = str(request.messages[0].content)[:100]
        logger.info(f"   첫 메시지 내용: {first_content}...")

    # 요청 검증
    if not request.messages or len(request.messages) == 0:
        logger.error("❌ [요청 검증 실패] 메시지가 비어있음")
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": "messages is required and must be a non-empty array",
                    "type": "invalid_request_error",
                    "code": "invalid_messages",
                }
            },
        )

    # OpenAI → CLI 변환
    logger.info(f"🔄 [변환 시작] OpenAI 형식 → Claude CLI 형식")
    cli_input = openai_to_cli(request.dict())
    logger.info(f"   CLI 모델: {cli_input['model']}")
    logger.info(f"   프롬프트 길이: {len(cli_input['prompt'])}자")
    logger.debug(f"   프롬프트 미리보기: {cli_input['prompt'][:200]}...")

    if request.stream:
        # 스트리밍 응답
        logger.info(f"📡 [스트리밍 모드] 응답 시작")
        return StreamingResponse(
            stream_chat_response(cli_input, request_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Request-Id": request_id,
            },
        )
    else:
        # 논스트리밍 응답
        logger.info(f"📦 [논스트리밍 모드] 응답 대기 중")
        return await non_streaming_chat_response(cli_input, request_id)


async def stream_chat_response(cli_input: Dict[str, Any], request_id: str):
    """스트리밍 채팅 응답 생성기"""
    import json
    import asyncio

    logger.info(f"🚀 [스트리밍 시작] Request ID: {request_id}")
    subprocess = ClaudeSubprocess()
    is_first = [True]  # list를 사용하여 클로저 문제 해결
    last_model = ["claude-sonnet-4"]
    result_data = [None]
    chunks_queue = asyncio.Queue()
    chunk_count = [0]

    # SSE 연결 확인 코멘트
    yield ":ok\n\n"

    try:

        # put_nowait는 순서를 보장하고, unbounded 큐이므로 블로킹되지 않는다.
        # create_task 방식은 fire-and-forget이라 청크 순서/유실 위험이 있어 사용하지 않는다.
        def handle_content_delta(text: str):
            chunk_count[0] += 1
            if chunk_count[0] % 10 == 1:  # 10개마다 로깅
                logger.debug(f"📨 [청크 #{chunk_count[0]}] 텍스트 수신: {len(text)}자")
            chunk = create_streaming_chunk(
                request_id, last_model[0], content=text, is_first=is_first[0]
            )
            is_first[0] = False
            chunks_queue.put_nowait(f"data: {json.dumps(chunk)}\n\n")

        def handle_result(result: Dict[str, Any]):
            result_data[0] = result
            usage = result.get("usage", {})
            logger.info(f"✅ [최종 결과 수신]")
            logger.info(f"   모델: {result.get('message', {}).get('model', 'unknown')}")
            logger.info(f"   입력 토큰: {usage.get('input_tokens', 0)}")
            logger.info(f"   출력 토큰: {usage.get('output_tokens', 0)}")
            logger.info(f"   총 청크 수: {chunk_count[0]}")
            if result.get("message"):
                last_model[0] = result["message"].get("model", last_model[0])
            chunks_queue.put_nowait("DONE")

        def handle_error(error: Exception):
            logger.error(f"❌ [Claude CLI 오류] {error}")
            error_chunk = {
                "error": {
                    "message": str(error),
                    "type": "server_error",
                    "code": None,
                }
            }
            chunks_queue.put_nowait(f"data: {json.dumps(error_chunk)}\n\n")
            chunks_queue.put_nowait("DONE")

        # Claude CLI 실행 (백그라운드). start()가 콜백 밖에서 예외로 죽더라도
        # 소비 루프가 영원히 멈추지 않도록 항상 "DONE"을 큐에 넣는다.
        async def run_subprocess():
            try:
                await subprocess.start(
                    prompt=cli_input["prompt"],
                    model=cli_input["model"],
                    session_id=cli_input.get("session_id"),
                    on_content_delta=handle_content_delta,
                    on_result=handle_result,
                    on_error=handle_error,
                )
            except Exception as exc:
                logger.error(f"❌ [Claude CLI 백그라운드 실패] {exc}")
            finally:
                chunks_queue.put_nowait("DONE")

        logger.info(f"⚙️ [Claude CLI 실행] 모델: {cli_input['model']}")
        asyncio.create_task(run_subprocess())

        # 큐에서 청크 읽어서 yield
        logger.debug(f"📬 [큐 대기] 스트림 청크 수신 대기 중...")
        while True:
            chunk = await chunks_queue.get()
            if chunk == "DONE":
                logger.info(f"🏁 [스트리밍 완료] Request ID: {request_id}")
                break
            yield chunk

        # 최종 done 청크
        if result_data[0]:
            usage = result_data[0].get("usage")
            done_chunk = create_done_chunk(request_id, last_model[0], usage)
            yield f"data: {json.dumps(done_chunk)}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"❌ [스트리밍 에러] {e}")
        import traceback
        logger.error(traceback.format_exc())
        error_chunk = {
            "error": {"message": str(e), "type": "server_error", "code": None}
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    finally:
        logger.info(f"🛑 [Claude CLI 종료] Request ID: {request_id}")
        subprocess.kill()


async def non_streaming_chat_response(
    cli_input: Dict[str, Any], request_id: str
) -> Dict[str, Any]:
    """논스트리밍 채팅 응답"""
    logger.info(f"🚀 [논스트리밍 시작] Request ID: {request_id}")
    subprocess = ClaudeSubprocess()
    result_data = None

    async def handle_result(result: Dict[str, Any]):
        nonlocal result_data
        result_data = result
        usage = result.get("usage", {})
        logger.info(f"✅ [최종 결과 수신]")
        logger.info(f"   모델: {result.get('message', {}).get('model', 'unknown')}")
        logger.info(f"   입력 토큰: {usage.get('input_tokens', 0)}")
        logger.info(f"   출력 토큰: {usage.get('output_tokens', 0)}")

    async def handle_error(error: Exception):
        logger.error(f"❌ [Claude CLI 오류] {error}")
        raise HTTPException(status_code=500, detail=str(error))

    try:
        # Claude CLI 실행
        logger.info(f"⚙️ [Claude CLI 실행] 모델: {cli_input['model']}")
        await subprocess.start(
            prompt=cli_input["prompt"],
            model=cli_input["model"],
            session_id=cli_input.get("session_id"),
            on_result=handle_result,
            on_error=handle_error,
        )

        if result_data:
            logger.info(f"🔄 [응답 변환] CLI 형식 → OpenAI 형식")
            openai_response = cli_result_to_openai(result_data, request_id)
            logger.info(f"🏁 [논스트리밍 완료] Request ID: {request_id}")
            return openai_response
        else:
            logger.error(f"❌ [응답 없음] Claude CLI가 응답 없이 종료됨")
            raise HTTPException(
                status_code=500, detail="Claude CLI exited without response"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [논스트리밍 에러] {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        logger.info(f"🛑 [Claude CLI 종료] Request ID: {request_id}")
        subprocess.kill()


@app.get("/health")
async def health_check_openai():
    """OpenAI 호환 - 헬스 체크"""
    logger.info("💚 Health check (OpenAI 호환)")
    claude_status = await verify_claude()
    return {
        "status": "ok" if claude_status["ok"] else "error",
        "provider": "claude-code-cli",
        "timestamp": datetime.now().isoformat(),
        "claude_cli": claude_status,
    }


# ============================================================================
# 프로젝트 관리 API
# ============================================================================

async def generate_code_with_claude_cli(
    requirements: str,
    project_type: str,
    features: List[str],
    file_type: str,  # "html" or "python"
    model: str = "claude-sonnet-4"
) -> str:
    """Claude CLI를 사용하여 고품질 코드 생성"""

    features_text = ", ".join(features) if features else "기본 기능"

    # Simplified prompts for Claude CLI
    prompts = {
        "html": f"""Create a complete, production-ready HTML web application for this requirement:

{requirements}

Project type: {project_type}
Features: {features_text}

Requirements:
- Single HTML file with inline CSS and JavaScript
- Modern, responsive design with gradient backgrounds
- Full functionality implementation (not just UI mockup)
- Use localStorage for data persistence
- Include form validation and error handling
- Smooth animations and transitions
- No code comments
- Output ONLY the HTML code without markdown code blocks

Generate the complete HTML code now:""",

        "python": f"""Create a complete, production-ready FastAPI backend for this requirement:

{requirements}

Project type: {project_type}
Features: {features_text}

Requirements:
- FastAPI framework with CORS middleware
- Pydantic models for validation
- RESTful API endpoints (GET, POST, PUT, DELETE)
- In-memory data storage with UUID keys
- Proper error handling with HTTPException
- Health check endpoint at /
- Run with uvicorn on port 8000
- No code comments
- Output ONLY the Python code without markdown code blocks

Generate the complete Python code now:"""
    }

    prompt = prompts.get(file_type, f"Generate {file_type} code")

    try:
        logger.info(f"🤖 Claude CLI로 {file_type} 코드 생성 중...")
        subprocess_client = ClaudeSubprocess()
        result_data = None

        async def handle_result(result: Dict[str, Any]):
            nonlocal result_data
            result_data = result

        # Claude CLI 실행
        await subprocess_client.start(
            prompt=prompt,
            model=model,
            on_result=handle_result,
        )

        if result_data and result_data.get("message"):
            content_blocks = result_data["message"].get("content", [])
            code = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    code += block.get("text", "")

            # 코드 블록 마커 제거
            code = code.strip()
            if "```" in code:
                parts = code.split("```")
                for part in parts:
                    cleaned = part.strip()
                    # 언어 지시자 제거
                    if cleaned and not cleaned.split('\n')[0].strip() in ["html", "python", "javascript", "css"]:
                        code = cleaned
                        break
                    elif cleaned and '\n' in cleaned:
                        # 첫 줄이 언어 지시자인 경우
                        lines = cleaned.split('\n')
                        if lines[0].strip() in ["html", "python", "javascript", "css"]:
                            code = '\n'.join(lines[1:])
                        else:
                            code = cleaned
                        break

            logger.info(f"✅ Claude CLI 코드 생성 완료 - {len(code)} 자")
            return code
        else:
            logger.error("❌ Claude CLI에서 응답을 받지 못했습니다.")
            return f"<!-- Error: No response from Claude CLI -->"

    except Exception as e:
        logger.error(f"❌ Claude CLI 코드 생성 실패: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return f"<!-- Error: {str(e)} -->"


@app.post("/api/project/create")
async def create_project(request: ProjectCreateRequest):
    """실제 LLM을 사용한 프로젝트 생성"""
    logger.info(f"📦 프로젝트 생성 요청 - 타입: {request.project_type}")
    logger.info(f"   요구사항: {request.requirements[:100]}...")

    project_id = f"project-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    project_path = get_project_path(project_id)
    project_path.mkdir(parents=True, exist_ok=True)

    # README 생성
    (project_path / "README.md").write_text(
        f"# {request.project_type.upper()} Project\n\n"
        f"## 요구사항\n{request.requirements}\n\n"
        f"## 기능\n{chr(10).join('- ' + f for f in request.features)}\n\n"
        f"## 개발팀\n{chr(10).join('- ' + a for a in request.agents)}\n\n"
        f"## 실행 방법\n\n"
        f"### Frontend\n"
        f"```bash\n"
        f"cd frontend\n"
        f"python -m http.server 8000\n"
        f"```\n\n"
        f"브라우저에서 http://localhost:8000 접속\n",
        encoding="utf-8"
    )

    # Claude CLI를 사용하여 고품질 코드 생성
    # 모델 선택: sonnet-4 (빠르고 고품질) 또는 opus-4 (최고 품질)
    model = "claude-sonnet-4"

    # 프로젝트 타입에 따라 실제 코드 생성
    if request.project_type in ["web", "fullstack"]:
        logger.info("🎨 Claude CLI로 Frontend 코드 생성 중...")
        frontend_path = project_path / "frontend"
        frontend_path.mkdir(exist_ok=True)

        # Claude CLI로 HTML 생성
        html_code = await generate_code_with_claude_cli(
            request.requirements, request.project_type, request.features, "html", model
        )

        if html_code and not html_code.startswith("<!--"):
            (frontend_path / "index.html").write_text(html_code, encoding="utf-8")
            logger.info("✅ Frontend HTML 생성 완료")
        else:
            logger.error("❌ Frontend HTML 생성 실패")
            raise HTTPException(status_code=500, detail="Frontend 코드 생성 실패")

    if request.project_type in ["api", "fullstack"]:
        logger.info("⚙️ Claude CLI로 Backend 코드 생성 중...")
        backend_path = project_path / "backend"
        backend_path.mkdir(exist_ok=True)

        # Claude CLI로 Python 백엔드 생성
        python_code = await generate_code_with_claude_cli(
            request.requirements, request.project_type, request.features, "python", model
        )

        if python_code and not python_code.startswith("<!--"):
            (backend_path / "main.py").write_text(python_code, encoding="utf-8")
            (backend_path / "requirements.txt").write_text(
                "fastapi>=0.104.0\nuvicorn>=0.24.0\npython-multipart>=0.0.6\n",
                encoding="utf-8"
            )
            logger.info("✅ Backend 코드 생성 완료")
        else:
            logger.error("❌ Backend 코드 생성 실패")
            raise HTTPException(status_code=500, detail="Backend 코드 생성 실패")

    logger.info(f"✅ 프로젝트 생성 완료 - ID: {project_id}")
    return {
        "project_id": project_id,
        "path": str(project_path),
        "message": "프로젝트가 생성되었습니다."
    }


@app.get("/api/project/{project_id}/files")
async def get_project_files(project_id: str):
    """프로젝트 파일 트리 조회"""
    logger.info(f"📁 파일 트리 조회 - 프로젝트: {project_id}")
    project_path = get_project_path(project_id)

    if not project_path.exists():
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    tree = get_file_tree(project_path)
    return {"project_id": project_id, "tree": tree}


@app.get("/api/project/{project_id}/file")
async def get_project_file(project_id: str, path: str):
    """특정 파일 내용 조회"""
    logger.info(f"📄 파일 조회 - {project_id}/{path}")
    workspace = get_workspace_path()
    file_path = workspace / path

    # 보안: workspace 외부 접근 방지
    try:
        file_path.resolve().relative_to(workspace.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="디렉토리는 조회할 수 없습니다.")

    try:
        content = file_path.read_text(encoding="utf-8")
        return {
            "path": path,
            "content": content,
            "size": file_path.stat().st_size
        }
    except UnicodeDecodeError:
        # 바이너리 파일
        return {
            "path": path,
            "content": None,
            "binary": True,
            "size": file_path.stat().st_size
        }


@app.post("/api/project/{project_id}/file")
async def update_project_file(project_id: str, path: str, request: FileUpdateRequest):
    """파일 내용 수정"""
    logger.info(f"✏️ 파일 수정 - {project_id}/{path}")
    workspace = get_workspace_path()
    file_path = workspace / path

    # 보안: workspace 외부 접근 방지
    try:
        file_path.resolve().relative_to(workspace.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    try:
        file_path.write_text(request.content, encoding="utf-8")
        logger.info(f"✅ 파일 수정 완료 - {path}")
        return {"message": "파일이 수정되었습니다.", "path": path}
    except Exception as e:
        logger.error(f"❌ 파일 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 수정 실패: {str(e)}")


@app.post("/api/project/{project_id}/feedback")
async def submit_feedback(project_id: str, request: FeedbackRequest):
    """피드백 기반 코드 수정"""
    logger.info(f"💬 피드백 수신 - 프로젝트: {project_id}")
    logger.info(f"   피드백: {request.feedback[:100]}...")

    project_path = get_project_path(project_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    workspace = get_workspace_path()
    modified_files = []

    # 특정 파일에 대한 피드백인 경우
    if request.file_path:
        file_path = workspace / request.file_path

        # 보안: workspace 외부 접근 방지
        try:
            file_path.resolve().relative_to(workspace.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

        try:
            # 기존 코드 읽기
            original_code = file_path.read_text(encoding="utf-8")

            # 파일 확장자로 타입 결정
            file_ext = file_path.suffix.lower()
            file_type_map = {
                ".html": "html",
                ".htm": "html",
                ".py": "python",
                ".js": "javascript",
                ".css": "css",
                ".json": "json"
            }
            file_type = file_type_map.get(file_ext, "text")

            # Claude CLI로 코드 수정
            logger.info(f"🤖 Claude CLI를 사용하여 코드 수정 중...")

            prompt = f"""Modify the following {file_type} code based on the user's feedback.

Original code:
```{file_type}
{original_code}
```

User feedback:
{request.feedback}

Requirements:
- Apply the requested changes accurately
- Preserve all existing functionality
- No code comments
- Output ONLY the modified code without markdown code blocks

Generate the complete modified code now:"""

            subprocess_client = ClaudeSubprocess()
            result_data = None

            async def handle_result(result: Dict[str, Any]):
                nonlocal result_data
                result_data = result

            # Claude CLI 실행
            await subprocess_client.start(
                prompt=prompt,
                model="claude-sonnet-4",
                on_result=handle_result,
            )

            if result_data and result_data.get("message"):
                content_blocks = result_data["message"].get("content", [])
                modified_code = ""
                for block in content_blocks:
                    if block.get("type") == "text":
                        modified_code += block.get("text", "")

                # 코드 블록 제거
                modified_code = modified_code.strip()
                if "```" in modified_code:
                    parts = modified_code.split("```")
                    for part in parts:
                        cleaned = part.strip()
                        if cleaned and '\n' in cleaned:
                            lines = cleaned.split('\n')
                            if lines[0].strip() in ["html", "python", "javascript", "css", "json"]:
                                modified_code = '\n'.join(lines[1:])
                            else:
                                modified_code = cleaned
                            break
            else:
                raise HTTPException(status_code=500, detail="Claude CLI에서 응답을 받지 못했습니다.")

            # 파일 저장
            file_path.write_text(modified_code, encoding="utf-8")
            modified_files.append(request.file_path)
            logger.info(f"✅ 파일 수정 완료: {request.file_path}")

        except Exception as e:
            logger.error(f"❌ 파일 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail=f"파일 수정 실패: {str(e)}")

    return {
        "message": "피드백이 반영되었습니다.",
        "modified_files": modified_files
    }


@app.get("/api/project/{project_id}/download")
async def download_project(project_id: str):
    """프로젝트 ZIP 다운로드"""
    logger.info(f"📦 프로젝트 다운로드 - {project_id}")
    project_path = get_project_path(project_id)

    if not project_path.exists():
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        zip_buffer = create_zip_archive(project_path)
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={project_id}.zip"
            }
        )
    except Exception as e:
        logger.error(f"❌ ZIP 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ZIP 생성 실패: {str(e)}")


@app.post("/api/project/{project_id}/start")
async def start_project(project_id: str, background_tasks: BackgroundTasks):
    """프로젝트 실행 (개발 서버 시작)"""
    logger.info(f"🚀 프로젝트 실행 요청 - {project_id}")
    project_path = get_project_path(project_id)

    if not project_path.exists():
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    # 이미 실행 중인지 확인
    if project_id in running_projects:
        return {
            "message": "프로젝트가 이미 실행 중입니다.",
            "url": running_projects[project_id]["url"]
        }

    # 사용 가능한 포트 찾기
    port = find_available_port()
    if not port:
        raise HTTPException(status_code=500, detail="사용 가능한 포트가 없습니다.")

    # 간단한 HTTP 서버 시작 (실제로는 프로젝트 타입에 따라 다르게 처리)
    try:
        # Python의 내장 HTTP 서버 사용
        frontend_path = project_path / "frontend"
        if frontend_path.exists():
            serve_dir = frontend_path
        else:
            serve_dir = project_path

        process = subprocess.Popen(
            ["python", "-m", "http.server", str(port)],
            cwd=serve_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        url = f"http://localhost:{port}"
        running_projects[project_id] = {
            "process": process,
            "port": port,
            "url": url,
            "path": str(project_path)
        }

        logger.info(f"✅ 프로젝트 실행됨 - {url}")
        return {
            "message": "프로젝트가 실행되었습니다.",
            "url": url,
            "port": port
        }
    except Exception as e:
        logger.error(f"❌ 프로젝트 실행 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로젝트 실행 실패: {str(e)}")


@app.post("/api/project/{project_id}/stop")
async def stop_project(project_id: str):
    """프로젝트 중지"""
    logger.info(f"⏹️ 프로젝트 중지 요청 - {project_id}")

    if project_id not in running_projects:
        raise HTTPException(status_code=404, detail="실행 중인 프로젝트를 찾을 수 없습니다.")

    try:
        process = running_projects[project_id]["process"]
        process.terminate()
        process.wait(timeout=5)
        del running_projects[project_id]
        logger.info(f"✅ 프로젝트 중지됨 - {project_id}")
        return {"message": "프로젝트가 중지되었습니다."}
    except Exception as e:
        logger.error(f"❌ 프로젝트 중지 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로젝트 중지 실패: {str(e)}")


@app.get("/api/projects")
async def list_projects():
    """프로젝트 목록 조회"""
    logger.info("📋 프로젝트 목록 조회")
    workspace = get_workspace_path()

    projects = []
    for item in workspace.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            is_running = item.name in running_projects
            projects.append({
                "id": item.name,
                "name": item.name,
                "path": str(item),
                "created": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                "running": is_running,
                "url": running_projects[item.name]["url"] if is_running else None
            })

    return {"projects": projects}


def main() -> None:
    """서버 시작"""
    port = int(os.environ.get("PORT", 3003))
    logger.info("=" * 60)
    logger.info("🚀 Claude Agent Platform API Server 시작")
    logger.info(f"📡 서버 주소: http://localhost:{port}")
    logger.info(f"📚 API 문서: http://localhost:{port}/docs")
    logger.info(f"🕐 시작 시간: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
