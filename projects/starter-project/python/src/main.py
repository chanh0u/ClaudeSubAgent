import logging
import os
import pathlib
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic 모델
class Message(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    provider: str
    config: Dict[str, Any]
    messages: List[Message]


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
            error_msg = e.response.json().get("error", {}).get("message", str(e))
            logger.error(f"❌ Claude API 에러 - {e.response.status_code}: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        except Exception as e:
            logger.error(f"❌ Claude API 예외 발생: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


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
            error_msg = e.response.json().get("error", {}).get("message", str(e))
            logger.error(f"❌ OpenAI API 에러 - {e.response.status_code}: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        except Exception as e:
            logger.error(f"❌ OpenAI API 예외 발생: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


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
            raise HTTPException(status_code=500, detail=f"Manus API error: {e.response.status_code}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Manus API 예외 발생: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


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
            except Exception as json_err:
                logger.error(f"❌ JSON 파싱 실패: {json_err}, 원본: {response_text[:200]}")
                raise HTTPException(status_code=500, detail=f"JSON 파싱 실패: {str(json_err)}")

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
            error_msg = f"연결 타임아웃 - {url} ({type(e).__name__})"
            logger.error(f"❌ {error_msg}")
            logger.error(f"   타임아웃 타입: {type(e)}")
            raise HTTPException(status_code=500, detail=error_msg)
        except httpx.ConnectError as e:
            error_msg = f"연결 실패 - {url}"
            logger.error(f"❌ {error_msg}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"{error_msg}: 서버에 연결할 수 없습니다")
        except httpx.HTTPStatusError as e:
            error_msg = e.response.text if e.response else str(e)
            logger.error(f"❌ Ollama API 에러 - {e.response.status_code}: {error_msg[:500]}")
            raise HTTPException(status_code=500, detail=f"Ollama HTTP {e.response.status_code}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ollama 예외 발생: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"스택 트레이스:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Ollama 오류: {str(e)}")


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
        raise HTTPException(status_code=500, detail=str(e))


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

        def handle_content_delta(text: str):
            chunk_count[0] += 1
            if chunk_count[0] % 10 == 1:  # 10개마다 로깅
                logger.debug(f"📨 [청크 #{chunk_count[0]}] 텍스트 수신: {len(text)}자")
            chunk = create_streaming_chunk(
                request_id, last_model[0], content=text, is_first=is_first[0]
            )
            is_first[0] = False
            asyncio.create_task(
                chunks_queue.put(f"data: {json.dumps(chunk)}\n\n")
            )

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
            asyncio.create_task(chunks_queue.put("DONE"))

        def handle_error(error: Exception):
            logger.error(f"❌ [Claude CLI 오류] {error}")
            error_chunk = {
                "error": {
                    "message": str(error),
                    "type": "server_error",
                    "code": None,
                }
            }
            asyncio.create_task(
                chunks_queue.put(f"data: {json.dumps(error_chunk)}\n\n")
            )
            asyncio.create_task(chunks_queue.put("DONE"))

        # Claude CLI 실행 (백그라운드)
        logger.info(f"⚙️ [Claude CLI 실행] 모델: {cli_input['model']}")
        asyncio.create_task(
            subprocess.start(
                prompt=cli_input["prompt"],
                model=cli_input["model"],
                session_id=cli_input.get("session_id"),
                on_content_delta=handle_content_delta,
                on_result=handle_result,
                on_error=handle_error,
            )
        )

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
