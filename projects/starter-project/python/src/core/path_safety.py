from pathlib import Path

from fastapi import HTTPException


def ensure_within_workspace(workspace: Path, requested_path: str) -> Path:
    file_path = workspace / requested_path
    try:
        file_path.resolve().relative_to(workspace.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.") from exc
    return file_path
