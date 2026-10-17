from __future__ import annotations

import json
import re
from pathlib import Path

SECRET_PATTERNS = (
 re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
 re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
 re.compile(r"AKIA[0-9A-Z]{16}"),
 re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def check_readme(path: Path) -> list[str]:
    """Return actionable issues found in a README file."""
 issues: list[str] = []
    if not path.exists():
        return [f"README not found: {path}"]
 content = path.read_text(encoding="utf-8")
    if not content.strip():
 issues.append("README is empty")
    elif not re.search(r"^#\s+\S", content, re.MULTILINE):
 issues.append("README is missing a top-level Markdown heading")
    if "TODO" in content:
 issues.append("README contains TODO markers")
    return issues


def check_json(path: Path) -> list[str]:
    """Validate a JSON file and return readable errors."""
    if not path.exists():
        return [f"JSON file not found: {path}"]
    try:
 json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"Invalid JSON in {path}: {exc}"]
    return []


def scan_for_secrets(root: Path, *, max_bytes: int = 1_000_000) -> list[str]:
    """Heuristically scan text files for common secret formats.

    This is a lightweight hygiene check, not a replacement for a dedicated
    secret scanner. Files larger than max_bytes and unreadable files are skipped.
    """
 findings: list[str] = []
 ignored_parts = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    for path in root.rglob("*"):
        if not path.is_file() or ignored_parts.intersection(path.parts):
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
 text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
 findings.append(f"Possible secret pattern in {path}")
                break
    return findings
