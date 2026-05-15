#!/usr/bin/env python3
"""Ollama API 테스트 스크립트"""

import httpx
import json
import sys

ENDPOINT = "http://llm.aicentro.ai.kr"
MODEL = "qwen3:8b"

def test_connection():
    """연결 테스트 - /api/tags"""
    print(f"1️⃣ 연결 테스트: {ENDPOINT}/api/tags")
    print("-" * 60)
    try:
        response = httpx.get(f"{ENDPOINT}/api/tags", timeout=10.0)
        print(f"✅ 상태 코드: {response.status_code}")
        print(f"📥 응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")
        return True
    except Exception as e:
        print(f"❌ 실패: {e}\n")
        return False

def test_chat_api():
    """채팅 API 테스트 - /api/chat"""
    print(f"2️⃣ 채팅 API 테스트: {ENDPOINT}/api/chat")
    print("-" * 60)

    request_body = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "user", "content": "안녕하세요"}
        ]
    }

    print(f"📤 요청 본문:\n{json.dumps(request_body, indent=2, ensure_ascii=False)}")

    try:
        print(f"\n⏱️ 요청 전송 중 (타임아웃: 120초)...")
        response = httpx.post(
            f"{ENDPOINT}/api/chat",
            json=request_body,
            timeout=120.0
        )
        print(f"✅ 상태 코드: {response.status_code}")
        print(f"📥 응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")
        return True
    except httpx.TimeoutException:
        print(f"❌ 타임아웃 (30초 초과)\n")
        return False
    except Exception as e:
        print(f"❌ 실패: {type(e).__name__}: {e}\n")
        return False

def test_generate_api():
    """생성 API 테스트 - /api/generate"""
    print(f"3️⃣ 생성 API 테스트: {ENDPOINT}/api/generate")
    print("-" * 60)

    request_body = {
        "model": MODEL,
        "prompt": "안녕하세요",
        "stream": False
    }

    print(f"📤 요청 본문:\n{json.dumps(request_body, indent=2, ensure_ascii=False)}")

    try:
        print(f"\n⏱️ 요청 전송 중 (타임아웃: 120초)...")
        response = httpx.post(
            f"{ENDPOINT}/api/generate",
            json=request_body,
            timeout=120.0
        )
        print(f"✅ 상태 코드: {response.status_code}")
        print(f"📥 응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")
        return True
    except httpx.TimeoutException:
        print(f"❌ 타임아웃 (30초 초과)\n")
        return False
    except Exception as e:
        print(f"❌ 실패: {type(e).__name__}: {e}\n")
        return False

def main():
    print("=" * 60)
    print("Ollama API 테스트")
    print("=" * 60)
    print(f"엔드포인트: {ENDPOINT}")
    print(f"모델: {MODEL}")
    print("=" * 60)
    print()

    results = []
    results.append(("연결 테스트", test_connection()))
    results.append(("채팅 API", test_chat_api()))
    results.append(("생성 API", test_generate_api()))

    print("=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    for name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{name}: {status}")

if __name__ == "__main__":
    main()
