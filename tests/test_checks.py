import json
from pathlib import Path

from ghostkit.checks import check_json, check_readme, scan_for_secrets


def test_check_readme_flags_missing_heading_and_todo(tmp_path: Path) -> None:
 readme = tmp_path / "README.md"
 readme.write_text("Project notes\nTODO: add usage\n", encoding="utf-8")
 issues = check_readme(readme)
    assert "README is missing a top-level Markdown heading" in issues
    assert "README contains TODO markers" in issues


def test_check_readme_accepts_heading(tmp_path: Path) -> None:
 readme = tmp_path / "README.md"
 readme.write_text("# Project\n\nUseful docs.\n", encoding="utf-8")
    assert check_readme(readme) == []


def test_check_json_valid_and_invalid(tmp_path: Path) -> None:
 valid = tmp_path / "valid.json"
 valid.write_text(json.dumps({"ok": True}), encoding="utf-8")
 invalid = tmp_path / "invalid.json"
 invalid.write_text("{oops", encoding="utf-8")
    assert check_json(valid) == []
    assert check_json(invalid)[0].startswith("Invalid JSON in")


def test_check_json_missing_file(tmp_path: Path) -> None:
    assert check_json(tmp_path / "missing.json")[0].startswith("JSON file not found:")


def test_secret_scan_finds_common_token_pattern(tmp_path: Path) -> None:
 sample = tmp_path / "sample.txt"
 sample.write_text("token = 'ghp_" + "A" * 24 + "'\n", encoding="utf-8")
 findings = scan_for_secrets(tmp_path)
    assert len(findings) == 1
    assert "sample.txt" in findings[0]


def test_secret_scan_skips_virtual_environment(tmp_path: Path) -> None:
 ignored = tmp_path / ".venv"
 ignored.mkdir()
    (ignored / "secret.txt").write_text("ghp_" + "A" * 24, encoding="utf-8")
    assert scan_for_secrets(tmp_path) == []
