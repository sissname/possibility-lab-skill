#!/usr/bin/env python3
"""Map idea payloads, dry-run registry writes, and write records through lark-cli."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from resolve_lark_cli import load_config, redacted_resolution, resolve_lark_cli


ZH_FIELDS = [
    "标题",
    "原始想法",
    "母题",
    "最推荐形态",
    "当前证据等级",
    "验证证据",
    "最小验证",
    "成功信号",
    "失败信号",
    "升级条件",
    "下一步",
    "状态",
    "价值类型",
    "标签",
]

EN_FIELDS = [
    "Title",
    "Raw idea",
    "Theme",
    "Recommended form",
    "Evidence level",
    "Evidence",
    "Smallest validation",
    "Success signal",
    "Failure signal",
    "Upgrade condition",
    "Next step",
    "Status",
    "Value type",
    "Tags",
]

EN_TO_ZH = dict(zip(EN_FIELDS, ZH_FIELDS, strict=True))
ZH_TO_EN = dict(zip(ZH_FIELDS, EN_FIELDS, strict=True))

ALIASES_TO_ZH = {
    **{field: field for field in ZH_FIELDS},
    **EN_TO_ZH,
    "title": "标题",
    "raw_idea": "原始想法",
    "raw idea": "原始想法",
    "idea": "原始想法",
    "theme": "母题",
    "motif": "母题",
    "recommended_form": "最推荐形态",
    "recommended form": "最推荐形态",
    "form": "最推荐形态",
    "evidence_level": "当前证据等级",
    "evidence level": "当前证据等级",
    "evidence": "验证证据",
    "smallest_validation": "最小验证",
    "smallest validation": "最小验证",
    "validation": "最小验证",
    "success_signal": "成功信号",
    "success signal": "成功信号",
    "failure_signal": "失败信号",
    "failure signal": "失败信号",
    "upgrade_condition": "升级条件",
    "upgrade condition": "升级条件",
    "next_step": "下一步",
    "next step": "下一步",
    "status": "状态",
    "value_type": "价值类型",
    "value type": "价值类型",
    "tags": "标签",
}

EVIDENCE_TO_ZH = {
    "L0 none": "L0 无证据",
    "L1 intuition": "L1 个人直觉",
    "L2 specific feedback": "L2 具体反馈",
    "L3 small experiment signal": "L3 小实验信号",
    "L4 strong demand signal": "L4 强需求信号",
    "L5 scalable evidence": "L5 可扩展证据",
}

STATUS_TO_ZH = {
    "inspiration": "灵感",
    "material": "素材",
    "experiment": "实验",
    "project candidate": "项目候选",
    "project": "项目",
    "archived": "归档",
    "archive": "归档",
}

VALUE_TO_ZH = {
    "culture": "文化",
    "education": "教育",
    "content": "内容",
    "tool": "工具",
    "business": "商业",
    "community": "社区",
    "system": "系统",
    "artwork": "作品",
    "work": "作品",
    "research": "研究",
}


def load_registry_config(config_path: str) -> dict[str, Any]:
    config = load_config(config_path)
    return {
        "base_token": os.environ.get("LARK_BASE_TOKEN") or config.get("base_token") or "",
        "table_id": os.environ.get("LARK_TABLE_ID") or config.get("table_id") or "",
        "identity": os.environ.get("LARK_IDENTITY") or config.get("identity") or "user",
        "field_locale": os.environ.get("LARK_FIELD_LOCALE") or config.get("field_locale") or "zh",
    }


def load_payload(path: str) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ("ideas", "records", "items"):
            if isinstance(data.get(key), list):
                items = data[key]
                break
        else:
            items = [data]
    else:
        raise ValueError("Payload must be a JSON object or array.")

    records: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        fields = item.get("fields") if isinstance(item.get("fields"), dict) else item
        records.append(fields)
    return records


def _normalize_key(key: str) -> str:
    return key.strip().replace("-", "_").lower()


def _map_value(field: str, value: Any, locale: str) -> Any:
    if locale != "zh" or not isinstance(value, str):
        return value
    cleaned = value.strip()
    lowered = cleaned.lower()
    if field == "当前证据等级":
        return EVIDENCE_TO_ZH.get(cleaned, EVIDENCE_TO_ZH.get(lowered, value))
    if field == "状态":
        return STATUS_TO_ZH.get(lowered, value)
    if field == "价值类型":
        return VALUE_TO_ZH.get(lowered, value)
    return value


def map_record_fields(record: dict[str, Any], locale: str) -> tuple[dict[str, Any], list[str]]:
    target_fields = set(ZH_FIELDS if locale == "zh" else EN_FIELDS)
    mapped: dict[str, Any] = {}
    dropped: list[str] = []

    for key, value in record.items():
        zh_field = ALIASES_TO_ZH.get(key) or ALIASES_TO_ZH.get(_normalize_key(key))
        if not zh_field:
            dropped.append(key)
            continue
        target = zh_field if locale == "zh" else ZH_TO_EN[zh_field]
        if target not in target_fields:
            dropped.append(key)
            continue
        mapped[target] = _map_value(zh_field, value, locale)

    return mapped, dropped


def build_batch_payload(records: list[dict[str, Any]], locale: str) -> tuple[dict[str, Any], list[str]]:
    batch_records = []
    dropped_fields: list[str] = []
    for record in records:
        mapped, dropped = map_record_fields(record, locale)
        dropped_fields.extend(dropped)
        if mapped:
            batch_records.append({"fields": mapped})
    return {"records": batch_records}, sorted(set(dropped_fields))


def _items_from_response(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if not isinstance(value, dict):
        return []
    for key in ("items", "records", "rows"):
        if isinstance(value.get(key), list):
            return value[key]
    data = value.get("data")
    if isinstance(data, (dict, list)):
        return _items_from_response(data)
    return []


def extract_field_names(response: Any) -> list[str]:
    names: list[str] = []
    for item in _items_from_response(response):
        if not isinstance(item, dict):
            continue
        name = item.get("field_name") or item.get("fieldName") or item.get("name") or item.get("title")
        if isinstance(name, str):
            names.append(name)
    return names


def extract_existing_titles(response: Any, locale: str) -> set[str]:
    title_field = "标题" if locale == "zh" else "Title"
    titles: set[str] = set()
    for item in _items_from_response(response):
        if not isinstance(item, dict):
            continue
        fields = item.get("fields") if isinstance(item.get("fields"), dict) else item
        title = fields.get(title_field) or fields.get("标题") or fields.get("Title") or fields.get("title")
        if isinstance(title, list) and title:
            title = title[0]
        if isinstance(title, dict):
            title = title.get("text") or title.get("value")
        if isinstance(title, str) and title.strip():
            titles.add(title.strip())
    return titles


def _run_json(command: list[str], args: list[str]) -> tuple[Any | None, str | None]:
    try:
        completed = subprocess.run(
            [*command, *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        return None, str(exc)

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        return None, message

    raw = completed.stdout.strip()
    if not raw:
        return {}, None
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as exc:
        return None, f"CLI returned non-JSON output: {exc}"


def _preflight(command: list[str], config: dict[str, Any], locale: str) -> tuple[set[str], list[str], list[str]]:
    errors: list[str] = []
    field_names: list[str] = []
    existing_titles: set[str] = set()

    common_args = [
        "--as",
        config["identity"],
        "--base-token",
        config["base_token"],
        "--table-id",
        config["table_id"],
        "--format",
        "json",
    ]

    fields_response, fields_error = _run_json(command, ["base", "+field-list", *common_args])
    if fields_error:
        errors.append(f"field-list failed: {fields_error}")
    else:
        field_names = extract_field_names(fields_response)

    records_response, records_error = _run_json(command, ["base", "+record-list", *common_args, "--limit", "200"])
    if records_error:
        errors.append(f"record-list failed: {records_error}")
    else:
        existing_titles = extract_existing_titles(records_response, locale)

    return existing_titles, field_names, errors


def _split_duplicates(batch_payload: dict[str, Any], existing_titles: set[str], locale: str) -> tuple[dict[str, Any], list[str], list[str]]:
    title_field = "标题" if locale == "zh" else "Title"
    seen = set(existing_titles)
    creatable = []
    created_titles: list[str] = []
    skipped: list[str] = []

    for record in batch_payload["records"]:
        fields = record["fields"]
        title = fields.get(title_field)
        if not isinstance(title, str) or not title.strip():
            skipped.append("<missing title>")
            continue
        normalized = title.strip()
        if normalized in seen:
            skipped.append(normalized)
            continue
        seen.add(normalized)
        creatable.append(record)
        created_titles.append(normalized)

    return {"records": creatable}, created_titles, skipped


def _missing_configuration(config: dict[str, Any], cli_resolution: dict[str, Any]) -> list[str]:
    missing = []
    if not cli_resolution.get("available"):
        missing.append("lark_cli")
    if not config.get("base_token"):
        missing.append("base_token")
    if not config.get("table_id"):
        missing.append("table_id")
    return missing


def _write_report(report: dict[str, Any], report_path: str | None) -> str:
    path = Path(report_path or "reports/possibility-lab-write-report.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return str(path)


def _write_records(command: list[str], config: dict[str, Any], batch_payload: dict[str, Any]) -> tuple[Any | None, str | None]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
        json.dump(batch_payload, handle, ensure_ascii=False)
        payload_path = handle.name

    try:
        return _run_json(
            command,
            [
                "base",
                "+record-batch-create",
                "--as",
                config["identity"],
                "--base-token",
                config["base_token"],
                "--table-id",
                config["table_id"],
                "--json",
                f"@{payload_path}",
                "--format",
                "json",
            ],
        )
    finally:
        Path(payload_path).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run and write idea records to a Lark/Feishu Base registry.")
    parser.add_argument("payload", help="JSON payload containing idea records")
    parser.add_argument("--config", default="config.local.json", help="Path to local config JSON")
    parser.add_argument("--field-locale", choices=("zh", "en"), help="Override field locale")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing records")
    parser.add_argument("--write-report", action="store_true", help="Write a JSON report")
    parser.add_argument("--report-path", help="Custom report path")
    args = parser.parse_args()

    config = load_registry_config(args.config)
    if args.field_locale:
        config["field_locale"] = args.field_locale
    locale = config["field_locale"]

    source_records = load_payload(args.payload)
    batch_payload, dropped_fields = build_batch_payload(source_records, locale)
    cli_resolution = resolve_lark_cli(args.config)
    missing = _missing_configuration(config, cli_resolution)

    preflight_errors: list[str] = []
    existing_titles: set[str] = set()
    field_names: list[str] = []
    if not missing:
        existing_titles, field_names, preflight_errors = _preflight(cli_resolution["command"], config, locale)

    creatable_payload, would_create, skipped_duplicates = _split_duplicates(batch_payload, existing_titles, locale)

    report: dict[str, Any] = {
        "dry_run": args.dry_run,
        "field_locale": locale,
        "cli": redacted_resolution(cli_resolution),
        "missing_configuration": missing,
        "errors": preflight_errors,
        "field_names_seen": field_names,
        "created": [],
        "would_create": would_create,
        "skipped_duplicates": skipped_duplicates,
        "dropped_fields": dropped_fields,
        "batch_payload": creatable_payload,
    }

    exit_code = 0
    if not args.dry_run:
        if missing or preflight_errors:
            report["errors"] = [*preflight_errors, "write skipped because configuration or preflight failed"]
            exit_code = 1
        elif creatable_payload["records"]:
            write_response, write_error = _write_records(cli_resolution["command"], config, creatable_payload)
            if write_error:
                report["errors"].append(f"record-batch-create failed: {write_error}")
                exit_code = 1
            else:
                report["created"] = would_create
                report["write_response"] = write_response
        else:
            report["errors"].append("write skipped because no non-duplicate titled records remain")
            exit_code = 1

    if args.write_report:
        report["report_path"] = _write_report(report, args.report_path)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
