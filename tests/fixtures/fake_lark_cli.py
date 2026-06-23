#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


FIELDS = [
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


def _json_arg(args: list[str]) -> str | None:
    if "--json" not in args:
        return None
    value = args[args.index("--json") + 1]
    return value[1:] if value.startswith("@") else value


def main() -> int:
    args = sys.argv[1:]
    if args[:2] != ["base", "+field-list"] and args[:2] != ["base", "+record-list"] and args[:2] != ["base", "+record-batch-create"]:
        print(json.dumps({"error": "unsupported command", "args": args}, ensure_ascii=False), file=sys.stderr)
        return 2

    command = args[1]
    if command == "+field-list":
        print(json.dumps({"data": {"items": [{"field_name": name} for name in FIELDS]}}, ensure_ascii=False))
        return 0

    if command == "+record-list":
        print(json.dumps({"data": {"items": [{"fields": {"标题": "已有想法"}}]}}, ensure_ascii=False))
        return 0

    payload_path = _json_arg(args)
    payload = json.loads(Path(payload_path).read_text(encoding="utf-8")) if payload_path else {}
    print(json.dumps({"data": {"records": payload.get("records", [])}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
