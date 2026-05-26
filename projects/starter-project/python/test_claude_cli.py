"""
Claude CLI 직접 테스트
"""
import subprocess
import sys

print("=" * 60)
print("Claude CLI 테스트")
print("=" * 60)

# 1. claude --version 테스트
print("\n1. claude --version 테스트")
try:
    result = subprocess.run(
        ["claude", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"   리턴 코드: {result.returncode}")
    print(f"   출력: {result.stdout.strip()}")
    if result.stderr:
        print(f"   에러: {result.stderr.strip()}")
except FileNotFoundError:
    print("   ❌ claude 명령을 찾을 수 없습니다.")
except Exception as e:
    print(f"   ❌ 에러: {e}")

# 2. 간단한 프롬프트 테스트
print("\n2. 간단한 프롬프트 테스트 (--print 모드)")
try:
    process = subprocess.Popen(
        [
            "claude",
            "--print",
            "--dangerously-skip-permissions",
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
            "--model", "sonnet",
            "--no-session-persistence"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(f"   프로세스 PID: {process.pid}")
    print(f"   프롬프트 전송 중...")

    stdout, stderr = process.communicate(input="안녕하세요! 간단히 '테스트 성공'이라고만 답해주세요.", timeout=30)

    print(f"   리턴 코드: {process.returncode}")
    print(f"   stdout 길이: {len(stdout)} bytes")

    if stdout:
        lines = stdout.strip().split('\n')
        print(f"   출력 라인 수: {len(lines)}")
        print(f"   첫 5줄:")
        for i, line in enumerate(lines[:5], 1):
            print(f"      {i}. {line[:100]}")

    if stderr:
        print(f"   stderr: {stderr[:200]}")

except subprocess.TimeoutExpired:
    print("   ❌ 타임아웃 (30초 초과)")
    process.kill()
except Exception as e:
    print(f"   ❌ 에러: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
