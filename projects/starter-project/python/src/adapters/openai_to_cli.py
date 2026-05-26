"""
OpenAI 포맷을 Claude CLI 포맷으로 변환
"""

from typing import List, Dict, Any, Union

# 모델 맵핑
MODEL_MAP = {
    "claude-opus-4": "opus",
    "claude-opus-4-6": "opus",
    "claude-sonnet-4": "sonnet",
    "claude-sonnet-4-5": "sonnet",
    "claude-sonnet-4-6": "sonnet",
    "claude-haiku-4": "haiku",
    "claude-haiku-4-5": "haiku",
    "opus": "opus",
    "sonnet": "sonnet",
    "haiku": "haiku",
    "opus-max": "opus",
    "sonnet-max": "sonnet",
}


def extract_model(model: str) -> str:
    """
    OpenAI 모델 문자열에서 Claude 모델 alias 추출

    Args:
        model: OpenAI 모델 ID (예: "claude-sonnet-4", "claude-code-cli/opus")

    Returns:
        Claude CLI 모델 alias (opus/sonnet/haiku)
    """
    # 직접 매핑 확인
    if model in MODEL_MAP:
        return MODEL_MAP[model]

    # provider prefix 제거 후 재시도
    stripped = model.replace("claude-code-cli/", "").replace("claude-max/", "")
    if stripped in MODEL_MAP:
        return MODEL_MAP[stripped]

    # 기본값: opus
    return "opus"


def extract_text(content: Union[str, List[Dict[str, Any]]]) -> str:
    """
    콘텐츠에서 텍스트 추출

    OpenAI API는 content를 다음 형태로 허용:
    - 문자열: "Hello"
    - 콘텐츠 블록 배열: [{"type": "text", "text": "Hello"}]

    Args:
        content: 문자열 또는 콘텐츠 블록 배열

    Returns:
        추출된 텍스트
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []
        for block in content:
            if block.get("type") in ("text", "input_text"):
                texts.append(block.get("text", ""))
        return "\n".join(texts)

    return str(content or "")


def strip_openclaw_tooling(text: str) -> str:
    """
    OpenClaw 전용 툴링 섹션 제거

    OpenClaw의 시스템 프롬프트에는 Claude Code CLI에 없는 툴을 참조합니다.
    혼란을 방지하기 위해 해당 섹션을 제거합니다.

    Args:
        text: 원본 텍스트

    Returns:
        툴링 섹션이 제거된 텍스트
    """
    import re

    sections_to_strip = [
        "## Tooling",
        "## Tool Call Style",
        "## OpenClaw CLI Quick Reference",
        "## OpenClaw Self-Update",
    ]

    result = text
    for section in sections_to_strip:
        # 섹션 헤더부터 다음 ## 헤더까지 (또는 끝까지) 제거
        pattern = re.escape(section) + r"\n[\s\S]*?(?=\n## |$)"
        result = re.sub(pattern, "", result)

    # 과도한 빈 줄 정리
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def messages_to_prompt(messages: List[Dict[str, Any]]) -> str:
    """
    OpenAI 메시지 배열을 단일 프롬프트 문자열로 변환

    Claude Code CLI의 --print 모드는 대화가 아닌 단일 프롬프트를 기대합니다.
    컨텍스트를 보존하는 형식으로 메시지를 포맷팅합니다.

    Args:
        messages: OpenAI 메시지 배열

    Returns:
        포맷팅된 프롬프트 문자열
    """
    parts = []

    for msg in messages:
        text = extract_text(msg.get("content", ""))
        role = msg.get("role", "user")

        if role == "system":
            # 시스템 메시지는 컨텍스트 지시사항으로 변환
            # OpenClaw 툴링 섹션 제거
            parts.append(f"<system>\n{strip_openclaw_tooling(text)}\n</system>\n")
        elif role == "user":
            # 사용자 메시지는 메인 프롬프트
            parts.append(text)
        elif role == "assistant":
            # 이전 어시스턴트 응답 (컨텍스트용)
            parts.append(f"<previous_response>\n{text}\n</previous_response>\n")

    return "\n".join(parts).strip()


def openai_to_cli(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    OpenAI 채팅 요청을 CLI 입력 포맷으로 변환

    Args:
        request: OpenAI 채팅 요청
            {
                "model": "claude-sonnet-4",
                "messages": [...],
                "user": "session-id" (optional)
            }

    Returns:
        CLI 입력
            {
                "prompt": "...",
                "model": "sonnet",
                "session_id": "..." (optional)
            }
    """
    return {
        "prompt": messages_to_prompt(request.get("messages", [])),
        "model": extract_model(request.get("model", "sonnet")),
        "session_id": request.get("user"),  # OpenAI의 user 필드를 세션 매핑에 사용
    }
