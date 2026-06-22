#!/usr/bin/env python3
"""Repository-level AI governance gate for GitHub Actions.

The scanner validates every ``run_certificate.json`` found in the repository
and fails when AI output directories are committed without a matching
``trace/run_certificate.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from verify_ai_run import report_to_markdown, verify_run


OUTPUT_MARKERS = {
    "demo_prd.md",
    "skill_audit_report.md",
    "skill_usage_evaluation.json",
}


def _is_inside_git(path: Path) -> bool:
    return ".git" in path.parts


def _find_certificates(repo_root: Path) -> list[Path]:
    return sorted(
        path
        for path in repo_root.rglob("run_certificate.json")
        if path.is_file() and not _is_inside_git(path)
    )


def _find_output_dirs(repo_root: Path) -> list[Path]:
    output_dirs: set[Path] = set()
    for marker in OUTPUT_MARKERS:
        for path in repo_root.rglob(marker):
            if path.is_file() and not _is_inside_git(path) and path.parent.name == "output":
                output_dirs.add(path.parent)
    return sorted(output_dirs)


def _certificate_for_output_dir(output_dir: Path) -> Path:
    return output_dir.parent / "trace" / "run_certificate.json"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _markdown_summary(results: list[dict[str, Any]], missing_certificate_errors: list[str]) -> str:
    lines = ["# AI Governance Repository Verification", ""]
    ok = not missing_certificate_errors and all(item["report"].get("ok") for item in results)
    lines.append(f"- Status: **{'PASS' if ok else 'FAIL'}**")
    lines.append(f"- Certificates checked: `{len(results)}`")
    lines.append("")

    if missing_certificate_errors:
        lines.append("## Missing Certificates")
        lines.extend(f"- {error}" for error in missing_certificate_errors)
        lines.append("")

    if not results:
        lines.append("## Certificates")
        lines.append("- No `run_certificate.json` files found. Nothing to verify.")
        return "\n".join(lines) + "\n"

    lines.append("## Certificates")
    lines.append("| Certificate | Status | Task | Run ID |")
    lines.append("| --- | --- | --- | --- |")
    for item in results:
        report = item["report"]
        certificate = report.get("certificate") if isinstance(report.get("certificate"), dict) else {}
        lines.append(
            "| `{}` | {} | `{}` | `{}` |".format(
                item["certificate"],
                "PASS" if report.get("ok") else "FAIL",
                certificate.get("task_id", "-"),
                certificate.get("run_id", "-"),
            )
        )

    failed = [item for item in results if not item["report"].get("ok")]
    if failed:
        lines.append("")
        lines.append("## Failures")
        for item in failed:
            report = item["report"]
            lines.append(f"### `{item['certificate']}`")
            for error in report.get("errors", []):
                lines.append(f"- {error}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify all AI governance certificates in a repository")
    parser.add_argument("--repo-root", default=".", help="Repository root to scan")
    parser.add_argument("--expected-skill-name", default="fjsk-ai-governance-demo-skill")
    parser.add_argument("--expected-skill-version", default="0.1.0-demo")
    parser.add_argument("--report-json", default="ai-governance-verifier-report.json")
    parser.add_argument("--report-md", default="ai-governance-verifier-report.md")
    parser.add_argument(
        "--require-certificate",
        action="store_true",
        help="Fail when no run_certificate.json files exist in the repository",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    certificates = _find_certificates(repo_root)
    output_dirs = _find_output_dirs(repo_root)

    certificate_set = {path.resolve() for path in certificates}
    missing_certificate_errors = [
        f"AI output directory has no sibling trace/run_certificate.json: {output_dir.relative_to(repo_root)}"
        for output_dir in output_dirs
        if _certificate_for_output_dir(output_dir).resolve() not in certificate_set
    ]

    results: list[dict[str, Any]] = []
    for certificate in certificates:
        report = verify_run(
            certificate=certificate,
            repo_root=repo_root,
            expected_skill_name=args.expected_skill_name,
            expected_skill_version=args.expected_skill_version,
        )
        results.append(
            {
                "certificate": certificate.relative_to(repo_root).as_posix(),
                "report": report,
            }
        )

    if args.require_certificate and not certificates:
        missing_certificate_errors.append("No run_certificate.json files found in repository")

    payload = {
        "ok": not missing_certificate_errors and all(item["report"].get("ok") for item in results),
        "repo_root": str(repo_root),
        "certificates_checked": len(results),
        "missing_certificate_errors": missing_certificate_errors,
        "results": results,
    }
    _write_json(Path(args.report_json), payload)
    Path(args.report_md).write_text(_markdown_summary(results, missing_certificate_errors), encoding="utf-8")

    print(f"AI governance certificates checked: {len(results)}")
    if missing_certificate_errors:
        print("Missing certificate errors:")
        for error in missing_certificate_errors:
            print(f"- {error}")
    for item in results:
        status = "PASS" if item["report"].get("ok") else "FAIL"
        print(f"{status}: {item['certificate']}")
        for error in item["report"].get("errors", []):
            print(f"- {error}")

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
