"""
API 호출 테스트 스크립트
http://localhost:3003/v1/chat/completions 엔드포인트 테스트
"""
import sys
import io
import requests
import json

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_chat_completions_non_streaming():
    """논스트리밍 모드 테스트"""
    url = "http://localhost:3003/v1/chat/completions"

    payload = {
        "model": "claude-sonnet-4",
        "messages": [
            {
                "role": "user",
                "content": "안녕하세요! 간단한 테스트 메시지입니다. '테스트 성공'이라고 답해주세요."
            }
        ],
        "stream": False
    }

    print("=" * 60)
    print("📡 논스트리밍 모드 테스트")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"요청 데이터:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print()

    try:
        response = requests.post(url, json=payload, timeout=60)

        print(f"응답 상태 코드: {response.status_code}")
        print()

        if response.status_code == 200:
            print("✅ 요청 성공!")
            print()
            print("응답 데이터:")
            result = response.json()
            print(json.dumps(result, ensure_ascii=False, indent=2))

            # 주요 정보 추출
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                print()
                print("=" * 60)
                print("📝 AI 응답 내용:")
                print("=" * 60)
                print(content)
                print()

            if "usage" in result:
                usage = result["usage"]
                print("📊 토큰 사용량:")
                print(f"  - 입력 토큰: {usage.get('prompt_tokens', 0)}")
                print(f"  - 출력 토큰: {usage.get('completion_tokens', 0)}")
                print(f"  - 총 토큰: {usage.get('total_tokens', 0)}")
        else:
            print(f"❌ 요청 실패!")
            print(f"응답 내용: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 연결 실패: 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: 서버 응답이 너무 느립니다.")
    except Exception as e:
        print(f"❌ 에러 발생: {type(e).__name__}: {str(e)}")


def test_chat_completions_streaming():
    """스트리밍 모드 테스트"""
    url = "http://localhost:3003/v1/chat/completions"

    payload = {
        "model": "claude-sonnet-4",
        "messages": [
            {
                "role": "user",
                "content": "1부터 5까지 세어주세요."
            }
        ],
        "stream": True
    }

    print()
    print("=" * 60)
    print("📡 스트리밍 모드 테스트")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"요청 데이터:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print()

    try:
        response = requests.post(url, json=payload, stream=True, timeout=60)

        print(f"응답 상태 코드: {response.status_code}")
        print()

        if response.status_code == 200:
            print("✅ 스트리밍 시작!")
            print()
            print("📝 AI 응답 (실시간):")
            print("-" * 60)

            full_content = ""
            chunk_count = 0

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')

                    # SSE 형식 파싱
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 'data: ' 제거

                        if data_str == '[DONE]':
                            print()
                            print("-" * 60)
                            print("🏁 스트리밍 완료!")
                            break

                        try:
                            chunk = json.loads(data_str)

                            # 에러 체크
                            if "error" in chunk:
                                print(f"\n❌ 에러: {chunk['error']}")
                                break

                            # 컨텐츠 델타 추출
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")

                                if content:
                                    print(content, end="", flush=True)
                                    full_content += content
                                    chunk_count += 1

                        except json.JSONDecodeError:
                            # :ok 같은 코멘트 무시
                            pass

            print()
            print()
            print(f"📊 총 {chunk_count}개 청크 수신")
            print(f"📏 전체 응답 길이: {len(full_content)}자")
        else:
            print(f"❌ 요청 실패!")
            print(f"응답 내용: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 연결 실패: 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: 서버 응답이 너무 느립니다.")
    except Exception as e:
        print(f"❌ 에러 발생: {type(e).__name__}: {str(e)}")


def test_health_check():
    """헬스 체크 테스트"""
    url = "http://localhost:3003/health"

    print()
    print("=" * 60)
    print("💚 헬스 체크 테스트")
    print("=" * 60)
    print(f"URL: {url}")
    print()

    try:
        response = requests.get(url, timeout=10)

        print(f"응답 상태 코드: {response.status_code}")

        if response.status_code == 200:
            print("✅ 서버 정상 작동 중!")
            print()
            print("응답 데이터:")
            result = response.json()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 헬스 체크 실패!")
            print(f"응답 내용: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 연결 실패: 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 에러 발생: {type(e).__name__}: {str(e)}")


if __name__ == "__main__":
    print()
    print("🚀 API 테스트 시작")
    print()

    # 1. 헬스 체크
    test_health_check()

    # 2. 논스트리밍 테스트
    test_chat_completions_non_streaming()

    # 3. 스트리밍 테스트
    test_chat_completions_streaming()

    print()
    print("=" * 60)
    print("✨ 모든 테스트 완료!")
    print("=" * 60)
    print()
