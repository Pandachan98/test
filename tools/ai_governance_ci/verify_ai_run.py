#!/usr/bin/env python3
"""Verify local AI run certificates and artifact hashes.

This module is dependency-free and can be used both as an importable verifier
and as a small CLI that mirrors the intended Git CI gate.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


DEFAULT_SECRET = "fjsk-local-trace-secret"
RUNS_FILE = "runs.json"
CERTIFICATES_FILE = "certificates.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json_file(path: Path) -> Tuple[Optional[Any], Optional[str]]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle), None
    except FileNotFoundError:
        return None, f"file does not exist: {path}"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path}: {exc}"
    except OSError as exc:
        return None, f"cannot read {path}: {exc}"


def _write_json_file(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _canonical_for_signature(record: Mapping[str, Any]) -> bytes:
    unsigned = {key: value for key, value in record.items() if key != "signature"}
    return json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign_record(record: Mapping[str, Any], secret: Optional[str] = None) -> str:
    secret_value = secret if secret is not None else os.environ.get("FJSK_TRACE_SECRET", DEFAULT_SECRET)
    return hmac.new(secret_value.encode("utf-8"), _canonical_for_signature(record), hashlib.sha256).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable_artifact_path(path_value: str, certificate_dir: Path) -> Optional[Path]:
    """Resolve local-workspace artifact paths after a workspace is copied into Git.

    Local demo certificates may store paths such as
    ``local_workspaces/STORY-001/<workspace>/output/demo_prd.md``. In a Git
    repository, teams often commit only the workspace contents, where
    ``trace/run_certificate.json`` and ``output/demo_prd.md`` are siblings. This
    fallback keeps the hash check strict while making the path portable.
    """

    normalized = _normalize_key(path_value)
    for marker in ("/output/", "output/"):
        index = normalized.rfind(marker)
        if index < 0:
            continue
        suffix = normalized[index + 1 :] if marker.startswith("/") else normalized[index:]
        candidate = (certificate_dir.parent / suffix).resolve()
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _resolve_path(path_value: str, repo_root: Path, certificate_dir: Optional[Path] = None) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        if path.exists():
            return path.resolve()
        if certificate_dir:
            portable = _portable_artifact_path(path_value, certificate_dir)
            if portable:
                return portable
        return path.resolve()
    resolved = (repo_root / path).resolve()
    if resolved.exists():
        return resolved
    if certificate_dir:
        portable = _portable_artifact_path(path_value, certificate_dir)
        if portable:
            return portable
    return resolved


def _normalize_key(path_value: str) -> str:
    return path_value.replace("\\", "/")


def _lookup_digest(path_value: str, artifact_sha256: Mapping[str, Any]) -> Optional[str]:
    value = artifact_sha256.get(path_value)
    if isinstance(value, str):
        return value
    normalized = _normalize_key(path_value)
    for key, candidate in artifact_sha256.items():
        if _normalize_key(str(key)) == normalized and isinstance(candidate, str):
            return candidate
    return None


def _artifact_ref_path(ref: Any) -> Optional[str]:
    if isinstance(ref, str):
        return ref
    if isinstance(ref, Mapping) and isinstance(ref.get("path"), str):
        return str(ref["path"])
    return None


def _artifact_ref_digest(ref: Any) -> Optional[str]:
    if isinstance(ref, Mapping) and isinstance(ref.get("sha256"), str):
        return str(ref["sha256"])
    return None


def _add_unique_artifact(
    artifacts: Dict[str, Dict[str, Any]],
    path_value: str,
    category: str,
    expected_sha256: Optional[str],
) -> None:
    entry = artifacts.setdefault(
        path_value,
        {
            "path": path_value,
            "categories": [],
            "expected_sha256": expected_sha256,
            "actual_sha256": None,
            "exists": False,
            "ok": False,
        },
    )
    if category not in entry["categories"]:
        entry["categories"].append(category)
    if expected_sha256 and not entry.get("expected_sha256"):
        entry["expected_sha256"] = expected_sha256


def _check_expected_field(
    certificate: Mapping[str, Any],
    field_name: str,
    expected_value: Optional[str],
    errors: List[str],
) -> None:
    if expected_value is None:
        return
    actual = certificate.get(field_name)
    if actual != expected_value:
        errors.append(f"{field_name} mismatch: expected {expected_value!r}, certificate has {actual!r}")


def _validate_artifact_list(
    certificate: Mapping[str, Any],
    field_name: str,
    artifact_sha256: Mapping[str, Any],
    artifacts: Dict[str, Dict[str, Any]],
    errors: List[str],
) -> None:
    refs = certificate.get(field_name)
    if refs is None:
        errors.append(f"certificate missing required field: {field_name}")
        return
    if not isinstance(refs, list):
        errors.append(f"{field_name} must be a list")
        return
    for index, ref in enumerate(refs):
        path_value = _artifact_ref_path(ref)
        if not path_value:
            errors.append(f"{field_name}[{index}] must be a path string or an object with a string path")
            continue
        ref_sha256 = _artifact_ref_digest(ref)
        mapped_sha256 = _lookup_digest(path_value, artifact_sha256)
        if ref_sha256 and mapped_sha256 and ref_sha256 != mapped_sha256:
            errors.append(f"sha256 conflict for {field_name}[{index}] path: {path_value}")
        expected_sha256 = ref_sha256 or mapped_sha256
        if not expected_sha256:
            errors.append(f"missing sha256 for {field_name}[{index}] path: {path_value}")
        _add_unique_artifact(artifacts, path_value, field_name, expected_sha256)


def _verify_trace_data(
    trace_data_dir: Path,
    certificate: Mapping[str, Any],
    errors: List[str],
    warnings: List[str],
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "trace_data_dir": str(trace_data_dir),
        "runs_checked": False,
        "certificates_checked": False,
    }
    run_id = certificate.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        warnings.append("trace-data-dir check skipped because certificate run_id is missing or invalid")
        return result

    runs_path = trace_data_dir / RUNS_FILE
    runs, runs_error = _read_json_file(runs_path)
    if runs_error:
        warnings.append(f"trace runs check skipped: {runs_error}")
    elif not isinstance(runs, Mapping):
        warnings.append(f"trace runs check skipped: {runs_path} is not a JSON object")
    else:
        result["runs_checked"] = True
        run_record = runs.get(run_id)
        if not isinstance(run_record, Mapping):
            errors.append(f"trace runs.json does not contain run_id {run_id!r}")
        else:
            result["run_found"] = True
            for field_name in ("task_id", "work_type", "skill_name", "skill_version"):
                if field_name in run_record and run_record.get(field_name) != certificate.get(field_name):
                    errors.append(
                        f"trace run {field_name} mismatch: runs.json has {run_record.get(field_name)!r}, "
                        f"certificate has {certificate.get(field_name)!r}"
                    )

    certificates_path = trace_data_dir / CERTIFICATES_FILE
    certificates, certificates_error = _read_json_file(certificates_path)
    if certificates_error:
        warnings.append(f"trace certificates check skipped: {certificates_error}")
    elif not isinstance(certificates, Mapping):
        warnings.append(f"trace certificates check skipped: {certificates_path} is not a JSON object")
    else:
        result["certificates_checked"] = True
        stored_certificate = certificates.get(run_id)
        if not isinstance(stored_certificate, Mapping):
            errors.append(f"trace certificates.json does not contain run_id {run_id!r}")
        else:
            result["certificate_found"] = True
            if _canonical_for_signature(stored_certificate) != _canonical_for_signature(certificate):
                errors.append("trace certificates.json record does not match the certificate file")
            if stored_certificate.get("signature") != certificate.get("signature"):
                errors.append("trace certificates.json signature does not match the certificate file")

    return result


def verify_run(
    certificate: str | os.PathLike[str],
    repo_root: str | os.PathLike[str] | None = None,
    expected_task_id: Optional[str] = None,
    expected_work_type: Optional[str] = None,
    expected_skill_name: Optional[str] = None,
    expected_skill_version: Optional[str] = None,
    trace_data_dir: str | os.PathLike[str] | None = None,
) -> Dict[str, Any]:
    """Verify a signed AI run certificate and referenced artifacts.

    Returns a report dictionary with ``ok``, ``errors``, ``warnings`` and
    ``checked_artifacts``. Expected verification failures are represented in the
    report instead of being raised.
    """

    resolved_repo_root = Path(repo_root).expanduser().resolve() if repo_root else Path.cwd().resolve()
    certificate_path = Path(certificate).expanduser()
    if not certificate_path.is_absolute():
        certificate_path = (resolved_repo_root / certificate_path).resolve()
    else:
        certificate_path = certificate_path.resolve()

    errors: List[str] = []
    warnings: List[str] = []
    checked_artifacts: Dict[str, Dict[str, Any]] = {}
    report: Dict[str, Any] = {
        "ok": False,
        "verified_at": _utc_now(),
        "certificate_path": str(certificate_path),
        "repo_root": str(resolved_repo_root),
        "errors": errors,
        "warnings": warnings,
        "checked_artifacts": [],
        "trace": {},
    }

    raw_certificate, read_error = _read_json_file(certificate_path)
    if read_error:
        errors.append(f"certificate check failed: {read_error}")
        return report
    if not isinstance(raw_certificate, Mapping):
        errors.append("certificate JSON must be an object")
        return report

    certificate_data = dict(raw_certificate)
    report["certificate"] = {
        "run_id": certificate_data.get("run_id"),
        "task_id": certificate_data.get("task_id"),
        "work_type": certificate_data.get("work_type"),
        "skill_name": certificate_data.get("skill_name"),
        "skill_version": certificate_data.get("skill_version"),
        "issued_at": certificate_data.get("issued_at"),
        "trace_server_id": certificate_data.get("trace_server_id"),
    }

    for field_name in (
        "run_id",
        "task_id",
        "work_type",
        "skill_name",
        "skill_version",
        "artifact_paths",
        "artifact_sha256",
        "skill_audit_artifacts",
        "usage_evaluation_artifacts",
        "issued_at",
        "trace_server_id",
        "signature",
    ):
        if field_name not in certificate_data:
            errors.append(f"certificate missing required field: {field_name}")

    signature = certificate_data.get("signature")
    if not isinstance(signature, str) or not signature:
        errors.append("certificate signature must be a non-empty string")
    else:
        expected_signature = _sign_record(certificate_data)
        report["signature"] = {
            "algorithm": "HMAC-SHA256",
            "valid": hmac.compare_digest(signature, expected_signature),
            "secret_source": "FJSK_TRACE_SECRET" if os.environ.get("FJSK_TRACE_SECRET") else "default",
        }
        if not hmac.compare_digest(signature, expected_signature):
            errors.append("certificate signature is invalid")

    _check_expected_field(certificate_data, "task_id", expected_task_id, errors)
    _check_expected_field(certificate_data, "work_type", expected_work_type, errors)
    _check_expected_field(certificate_data, "skill_name", expected_skill_name, errors)
    _check_expected_field(certificate_data, "skill_version", expected_skill_version, errors)

    artifact_sha256 = certificate_data.get("artifact_sha256")
    if not isinstance(artifact_sha256, Mapping):
        errors.append("artifact_sha256 must be a JSON object")
        artifact_sha256 = {}

    _validate_artifact_list(certificate_data, "artifact_paths", artifact_sha256, checked_artifacts, errors)
    _validate_artifact_list(certificate_data, "skill_audit_artifacts", artifact_sha256, checked_artifacts, errors)
    _validate_artifact_list(certificate_data, "usage_evaluation_artifacts", artifact_sha256, checked_artifacts, errors)

    for path_value, artifact in checked_artifacts.items():
        resolved_path = _resolve_path(path_value, resolved_repo_root, certificate_path.parent)
        artifact["resolved_path"] = str(resolved_path)
        artifact["exists"] = resolved_path.exists() and resolved_path.is_file()
        if not artifact["exists"]:
            errors.append(f"artifact does not exist: {path_value}")
            continue
        expected_sha256 = artifact.get("expected_sha256")
        if not expected_sha256:
            continue
        actual_sha256 = _sha256_file(resolved_path)
        artifact["actual_sha256"] = actual_sha256
        artifact["ok"] = actual_sha256 == expected_sha256
        if actual_sha256 != expected_sha256:
            errors.append(f"artifact sha256 mismatch: {path_value}")

    if trace_data_dir:
        report["trace"] = _verify_trace_data(Path(trace_data_dir).expanduser().resolve(), certificate_data, errors, warnings)

    report["checked_artifacts"] = sorted(checked_artifacts.values(), key=lambda item: item["path"])
    report["ok"] = not errors
    return report


def report_to_markdown(report: Mapping[str, Any]) -> str:
    status = "PASS" if report.get("ok") else "FAIL"
    lines = [
        f"# AI Run Verification Report",
        "",
        f"- Status: **{status}**",
        f"- Certificate: `{report.get('certificate_path')}`",
        f"- Repo root: `{report.get('repo_root')}`",
    ]
    certificate = report.get("certificate")
    if isinstance(certificate, Mapping):
        lines.extend(
            [
                f"- Run ID: `{certificate.get('run_id')}`",
                f"- Task: `{certificate.get('task_id')}`",
                f"- Work type: `{certificate.get('work_type')}`",
                f"- Skill: `{certificate.get('skill_name')}@{certificate.get('skill_version')}`",
            ]
        )

    errors = report.get("errors") if isinstance(report.get("errors"), list) else []
    warnings = report.get("warnings") if isinstance(report.get("warnings"), list) else []
    artifacts = report.get("checked_artifacts") if isinstance(report.get("checked_artifacts"), list) else []

    lines.extend(["", "## Errors"])
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings"])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")

    lines.extend(["", "## Artifacts"])
    if artifacts:
        lines.append("| Path | Categories | Exists | Hash OK |")
        lines.append("| --- | --- | --- | --- |")
        for artifact in artifacts:
            if not isinstance(artifact, Mapping):
                continue
            categories = ", ".join(str(item) for item in artifact.get("categories", []))
            lines.append(
                f"| `{artifact.get('path')}` | {categories} | {bool(artifact.get('exists'))} | "
                f"{bool(artifact.get('ok'))} |"
            )
    else:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def print_human_report(report: Mapping[str, Any]) -> None:
    status = "PASS" if report.get("ok") else "FAIL"
    print(f"AI run verification: {status}")
    certificate = report.get("certificate")
    if isinstance(certificate, Mapping):
        print(
            "Run: "
            f"{certificate.get('run_id')} | "
            f"{certificate.get('task_id')} | "
            f"{certificate.get('work_type')} | "
            f"{certificate.get('skill_name')}@{certificate.get('skill_version')}"
        )
    print(f"Certificate: {report.get('certificate_path')}")

    errors = report.get("errors") if isinstance(report.get("errors"), list) else []
    warnings = report.get("warnings") if isinstance(report.get("warnings"), list) else []
    artifacts = report.get("checked_artifacts") if isinstance(report.get("checked_artifacts"), list) else []
    print(f"Artifacts checked: {len(artifacts)}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify an AI run certificate and referenced artifacts")
    parser.add_argument("--certificate", required=True, help="Path to run_certificate.json")
    parser.add_argument("--repo-root", default=".", help="Repository root used to resolve relative artifact paths")
    parser.add_argument("--expected-task-id")
    parser.add_argument("--expected-work-type")
    parser.add_argument("--expected-skill-name")
    parser.add_argument("--expected-skill-version")
    parser.add_argument("--trace-data-dir", help="Optional trace_server data directory containing runs.json/certificates.json")
    parser.add_argument("--report-json", help="Optional path for the machine-readable verification report")
    parser.add_argument("--report-md", help="Optional path for the Markdown verification report")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = verify_run(
        certificate=args.certificate,
        repo_root=args.repo_root,
        expected_task_id=args.expected_task_id,
        expected_work_type=args.expected_work_type,
        expected_skill_name=args.expected_skill_name,
        expected_skill_version=args.expected_skill_version,
        trace_data_dir=args.trace_data_dir,
    )

    if args.report_json:
        _write_json_file(Path(args.report_json).expanduser().resolve(), report)
    if args.report_md:
        md_path = Path(args.report_md).expanduser().resolve()
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(report_to_markdown(report), encoding="utf-8")

    print_human_report(report)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
