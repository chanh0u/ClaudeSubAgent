import logging
import os
import pathlib
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    }

    handler = handlers.get(request.provider)
    if not handler:
        logger.error(f"❌ 지원하지 않는 provider: {request.provider}")
        raise HTTPException(status_code=400, detail=f"지원하지 않는 provider: {request.provider}")

    try:
        text = await handler(**request.config, messages=request.messages)
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


def main() -> None:
    """서버 시작"""
    port = int(os.environ.get("PORT", 3001))
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