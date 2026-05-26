"""
Claude CLI 포맷을 OpenAI 포맷으로 변환
"""

import time
from typing import Dict, Any, List


def extract_text_from_content(content: List[Dict[str, Any]]) -> str:
    """
    Claude CLI content 블록에서 텍스트 추출

    Args:
        content: Claude content 블록 배열

    Returns:
        추출된 텍스트 (여러 블록은 \n\n으로 구분)
    """
    texts = []
    for block in content:
        if block.get("type") == "text":
            texts.append(block.get("text", ""))
    return "\n\n".join(texts)


def cli_result_to_openai(result: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    """
    Claude CLI 결과를 OpenAI 채팅 완성 응답으로 변환

    Args:
        result: Claude CLI 결과
            {
                "type": "result",
                "message": {
                    "model": "claude-sonnet-4-5",
                    "content": [{"type": "text", "text": "..."}],
                    ...
                },
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 200
                }
            }
        request_id: 요청 ID

    Returns:
        OpenAI 형식 응답
            {
                "id": "chatcmpl-...",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "claude-sonnet-4",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "..."
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 200,
                    "total_tokens": 300
                }
            }
    """
    message = result.get("message", {})
    content = extract_text_from_content(message.get("content", []))
    usage = result.get("usage", {})

    return {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": message.get("model", "claude-sonnet-4"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0)
            + usage.get("output_tokens", 0),
        },
    }


def create_streaming_chunk(
    request_id: str,
    model: str,
    content: str = "",
    finish_reason: str = None,
    is_first: bool = False,
) -> Dict[str, Any]:
    """
    OpenAI 스트리밍 청크 생성

    Args:
        request_id: 요청 ID
        model: 모델 ID
        content: 콘텐츠 텍스트
        finish_reason: 종료 이유 ("stop" 또는 None)
        is_first: 첫 번째 청크인지 여부

    Returns:
        OpenAI 스트리밍 청크
    """
    delta = {"content": content}
    if is_first:
        delta["role"] = "assistant"

    chunk = {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
    }

    return chunk


def create_done_chunk(
    request_id: str, model: str, usage: Dict[str, int] = None
) -> Dict[str, Any]:
    """
    OpenAI 스트리밍 종료 청크 생성

    Args:
        request_id: 요청 ID
        model: 모델 ID
        usage: 사용량 정보 (선택)

    Returns:
        종료 청크
    """
    chunk = {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }

    if usage:
        chunk["usage"] = {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0)
            + usage.get("output_tokens", 0),
        }

    return chunk
