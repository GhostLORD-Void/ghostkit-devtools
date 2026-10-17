from __future__ import annotations

import argparse
from pathlib import Path

from ghostkit.checks import check_json, check_readme, scan_for_secrets


def build_parser() -> argparse.ArgumentParser:
 parser = argparse.ArgumentParser(
 prog="ghostkit",
 description="Lightweight repository hygiene checks for developers.",
    )
 parser.add_argument("path", nargs="?", default=".", help="Repository root (default: current directory)")
 parser.add_argument("--skip-secrets", action="store_true", help="Skip heuristic secret-pattern scanning")
    return parser


def main() -> int:
 args = build_parser().parse_args()
 root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}")
        return 2

 issues: list[str] = []
 readme = root / "README.md"
 issues.extend(check_readme(readme))
    for json_path in sorted(root.rglob("*.json")):
        if ".git" not in json_path.parts and ".venv" not in json_path.parts and "venv" not in json_path.parts:
 issues.extend(check_json(json_path))
    if not args.skip_secrets:
 issues.extend(scan_for_secrets(root))

    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        print(f"\nGhostKit found {len(issues)} issue(s).")
        return 1

    print(f"GhostKit checks passed for {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
