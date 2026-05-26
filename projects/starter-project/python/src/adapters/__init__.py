"""Adapters for converting between API formats"""

from .cli_to_openai import cli_result_to_openai, create_streaming_chunk, create_done_chunk
from .openai_to_cli import openai_to_cli

__all__ = [
    "cli_result_to_openai",
    "create_streaming_chunk",
    "create_done_chunk",
    "openai_to_cli",
]
