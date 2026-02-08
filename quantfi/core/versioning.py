from __future__ import annotations

import subprocess

from quantfi.core.config import Settings, Versions


def detect_code_version() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
            .strip()[:16]
        )
    except Exception:
        return "unknown_code"


def build_versions(settings: Settings) -> Versions:
    return Versions(
        code_version=detect_code_version(),
        config_version=settings.config_version(),
    )
