"""
Claude Code CLI Subprocess Manager

Claude CLI를 subprocess로 실행하고 JSON 스트리밍 출력을 파싱합니다.
"""

import asyncio
import inspect
import json
import logging
import os
import shutil
import subprocess
import sys
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)


def _resolve_claude_cmd(claude_bin: str) -> list:
    """Windows .cmd/.bat 파일을 subprocess로 실행하기 위해 cmd /c 래핑."""
    if sys.platform == "win32":
        resolved = shutil.which(claude_bin)
        if resolved and resolved.lower().endswith((".cmd", ".bat")):
            return ["cmd", "/c", resolved]
    return [claude_bin]


async def _call_callback(callback: Optional[Callable], *args, **kwargs):
    """콜백 함수 호출 (async/sync 모두 지원)"""
    if callback is None:
        return

    if inspect.iscoroutinefunction(callback):
        await callback(*args, **kwargs)
    else:
        callback(*args, **kwargs)

# OpenClaw 툴 맵핑 프롬프트
OPENCLAW_TOOL_MAPPING_PROMPT = """## Tool Name Mapping
You are running inside Claude Code CLI, not OpenClaw. The system prompt may reference OpenClaw tool names — map them to your actual tools:

### Direct tool replacements
- `exec` or `process` → use `Bash` (run shell commands)
- `read` → use `Read` (read file contents)
- `write` → use `Write` (write files)
- `edit` → use `Edit` (edit files)
- `grep` → use `Grep` (search file contents)
- `find` or `ls` → use `Glob` or `Bash(ls ...)`
- `web_search` → use `WebSearch`
- `web_fetch` → use `WebFetch`
- `image` → use `Read` (Claude Code can read images)

### OpenClaw CLI tools (use via Bash)
These OpenClaw tools are available through the `openclaw` CLI. Use `Bash` to run them:
- `memory_search` → `Bash(openclaw memory search "<query>")` — semantic search across memory files
- `memory_get` → `Read` on the memory file directly, OR `Bash(openclaw memory search "<query>")` for discovery
- `message` → `Bash(openclaw message send --to <target> "<text>")` — send messages to channels

### Skills
When a skill says to run a bash/python command, use the `Bash` tool directly.
Skills are located in the `skills/` directory relative to your working directory.
To use a skill: `Read` its SKILL.md file first, then follow the instructions using `Bash`.
"""


class ClaudeSubprocess:
    """Claude CLI subprocess 관리자"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_killed = False

    async def start(
        self,
        prompt: str,
        model: str = "sonnet",
        session_id: Optional[str] = None,
        cwd: Optional[str] = None,
        timeout: int = 900,
        on_message: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_content_delta: Optional[Callable[[str], None]] = None,
        on_result: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        """
        Claude CLI subprocess 시작

        Args:
            prompt: 사용자 프롬프트
            model: Claude 모델 (opus/sonnet/haiku)
            session_id: 세션 ID (선택)
            cwd: 작업 디렉토리 (선택)
            timeout: 타임아웃 (초)
            on_message: 메시지 콜백
            on_content_delta: 콘텐츠 델타 콜백 (스트리밍)
            on_result: 결과 콜백
            on_error: 에러 콜백
        """
        args = self._build_args(model, session_id)
        claude_bin = os.environ.get("CLAUDE_BIN", "claude")

        logger.info(f"🚀 [Claude CLI] 프로세스 시작")
        logger.info(f"   실행 파일: {claude_bin}")
        logger.info(f"   모델: {model}")
        logger.info(f"   세션 ID: {session_id or 'None'}")
        logger.info(f"   타임아웃: {timeout}초")
        logger.info(f"   작업 디렉토리: {cwd or os.getcwd()}")
        logger.debug(f"   전체 명령어: {claude_bin} {' '.join(args)}")
        logger.debug(f"   프롬프트 길이: {len(prompt)}자")

        try:
            # subprocess 시작 (Windows .cmd 파일 처리 포함)
            cmd = _resolve_claude_cmd(claude_bin) + args
            logger.info(f"⚙️ [subprocess] Popen 실행 중... 명령: {cmd[0]}")
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd or os.getcwd(),
                text=True,
                bufsize=1,
            )
            logger.info(f"✅ [subprocess] 프로세스 시작됨 (PID: {self.process.pid})")

            # 프롬프트를 stdin으로 전달
            if self.process.stdin:
                logger.info(f"📝 [stdin] 프롬프트 전송 중... ({len(prompt)}자)")
                self.process.stdin.write(prompt)
                self.process.stdin.close()
                logger.info(f"✅ [stdin] 프롬프트 전송 완료 및 stdin 닫힘")

            # stdout 스트림 처리
            logger.info(f"📡 [stdout] 스트림 처리 시작...")
            await self._process_stream(
                on_message=on_message,
                on_content_delta=on_content_delta,
                on_result=on_result,
                on_error=on_error,
                timeout=timeout,
            )

        except FileNotFoundError:
            error_msg = f"Claude CLI not found: {claude_bin}"
            logger.error(f"❌ [Claude CLI] {error_msg}")
            logger.error(f"   설치 방법: npm install -g @anthropic-ai/claude-code")
            error = Exception(
                "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )
            await _call_callback(on_error, error)
            raise error
        except Exception as e:
            logger.error(f"❌ [Claude CLI] 시작 실패: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await _call_callback(on_error, e)
            raise

    def _build_args(self, model: str, session_id: Optional[str]) -> list[str]:
        """CLI 인자 구성"""
        args = [
            "--print",  # Non-interactive mode
            "--dangerously-skip-permissions",  # Skip permission prompts
            "--output-format",
            "stream-json",  # JSON 스트리밍 출력
            "--verbose",  # stream-json에 필요
            "--include-partial-messages",  # 스트리밍 청크 활성화
            "--model",
            model,  # opus/sonnet/haiku
            "--no-session-persistence",  # 세션 저장 안 함
            "--append-system-prompt",
            OPENCLAW_TOOL_MAPPING_PROMPT,
        ]

        if session_id:
            args.extend(["--session-id", session_id])

        return args

    async def _process_stream(
        self,
        on_message: Optional[Callable],
        on_content_delta: Optional[Callable],
        on_result: Optional[Callable],
        on_error: Optional[Callable],
        timeout: int,
    ):
        """stdout 스트림 처리"""
        if not self.process or not self.process.stdout:
            logger.warning(f"⚠️ [stream] 프로세스 또는 stdout이 없음")
            return

        line_count = 0
        delta_count = 0
        message_types = {}

        try:
            # asyncio로 타임아웃 처리
            async def read_lines():
                loop = asyncio.get_event_loop()
                while True:
                    line = await loop.run_in_executor(
                        None, self.process.stdout.readline
                    )
                    if not line:
                        break
                    yield line.strip()

            async def process_stream_lines():
                nonlocal line_count, delta_count, message_types

                logger.info(f"📖 [stream] 스트림 읽기 시작 (타임아웃: {timeout}초)")
                async for line in read_lines():
                    if not line:
                        continue

                    line_count += 1
                    if line_count == 1:
                        logger.info(f"📨 [stream] 첫 번째 라인 수신")

                    try:
                        message = json.loads(line)
                        msg_type = message.get("type", "unknown")

                        # 메시지 타입 카운트
                        message_types[msg_type] = message_types.get(msg_type, 0) + 1

                        # 모든 메시지 콜백
                        if on_message:
                            on_message(message)

                        # 콘텐츠 델타 처리 (스트리밍)
                        if message.get("type") == "content_block_delta":
                            delta = message.get("event", {}).get("delta", {})
                            if delta.get("type") == "text_delta" and on_content_delta:
                                text = delta.get("text", "")
                                if text:
                                    delta_count += 1
                                    if delta_count == 1 or delta_count % 20 == 0:
                                        logger.debug(f"📨 [delta #{delta_count}] 텍스트: {len(text)}자")
                                    on_content_delta(text)

                        # 최종 결과 처리
                        elif message.get("type") == "result" and on_result:
                            logger.info(f"🎯 [result] 최종 결과 메시지 수신")
                            on_result(message)

                        # 기타 중요 메시지 타입 로깅
                        elif msg_type in ["message_start", "content_block_start", "content_block_stop", "message_stop"]:
                            logger.debug(f"📋 [message] 타입: {msg_type}")

                    except json.JSONDecodeError:
                        # JSON이 아닌 출력은 무시
                        logger.debug(f"⚠️ [stream] Non-JSON output: {line[:100]}")
                        continue

                logger.info(f"✅ [stream] 스트림 읽기 완료")
                logger.info(f"   총 라인 수: {line_count}")
                logger.info(f"   델타 청크 수: {delta_count}")
                logger.info(f"   메시지 타입별 카운트: {message_types}")

            # 전체 스트림 처리에 타임아웃 적용
            await asyncio.wait_for(process_stream_lines(), timeout=timeout)

        except asyncio.TimeoutError:
            error = Exception(f"Request timed out after {timeout}s")
            logger.error(f"⏱️ [timeout] {error}")
            logger.error(f"   처리된 라인 수: {line_count}")
            logger.error(f"   델타 청크 수: {delta_count}")
            await _call_callback(on_error, error)
            self.kill()
            raise error
        except Exception as e:
            logger.error(f"❌ [stream] 처리 오류: {e}")
            logger.error(f"   처리된 라인 수: {line_count}")
            import traceback
            logger.error(traceback.format_exc())
            await _call_callback(on_error, e)
            raise
        finally:
            # stderr 로그
            if self.process.stderr:
                stderr_output = self.process.stderr.read()
                if stderr_output:
                    logger.warning(f"⚠️ [stderr] {stderr_output[:500]}")
                else:
                    logger.debug(f"✅ [stderr] 출력 없음")

            # 프로세스 종료 대기
            if self.process:
                logger.debug(f"⏳ [process] 종료 대기 중...")
                self.process.wait()
                exit_code = self.process.returncode
                if exit_code == 0:
                    logger.info(f"✅ [process] 정상 종료 (exit code: {exit_code})")
                else:
                    logger.warning(f"⚠️ [process] 비정상 종료 (exit code: {exit_code})")

    def kill(self):
        """프로세스 종료"""
        if not self.is_killed and self.process:
            logger.debug(f"🛑 [kill] 프로세스 종료 시작 (PID: {self.process.pid})")
            self.is_killed = True
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                logger.debug(f"✅ [kill] 프로세스 정상 종료됨")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ [kill] 타임아웃 발생, 강제 종료 실행")
                self.process.kill()
                logger.debug(f"✅ [kill] 프로세스 강제 종료됨")

    def is_running(self) -> bool:
        """프로세스 실행 중인지 확인"""
        return (
            self.process is not None
            and not self.is_killed
            and self.process.poll() is None
        )


async def verify_claude() -> dict:
    """Claude CLI 설치 확인"""
    claude_bin = os.environ.get("CLAUDE_BIN", "claude")

    def _sync_verify() -> dict:
        try:
            cmd = _resolve_claude_cmd(claude_bin) + ["--version"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return {"ok": True, "version": result.stdout.strip()}
            return {"ok": False, "error": "Claude CLI returned non-zero exit code"}
        except FileNotFoundError:
            return {
                "ok": False,
                "error": "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code",
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Claude CLI version check timed out"}

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_verify)
