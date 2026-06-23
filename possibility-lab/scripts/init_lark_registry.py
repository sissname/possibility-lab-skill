#!/usr/bin/env python3
"""Create a safe setup plan and optional local config for an idea registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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


def build_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "lark_cli_path": args.lark_cli_path or "",
        "lark_cli_command": args.lark_cli_command or "lark-cli",
        "base_token": args.base_token or "",
        "table_id": args.table_id or "",
        "identity": args.identity,
        "field_locale": args.field_locale,
    }


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    fields = ZH_FIELDS if args.field_locale == "zh" else EN_FIELDS
    return {
        "dry_run": args.dry_run,
        "field_locale": args.field_locale,
        "config_target": args.config,
        "will_write_config": args.write_config,
        "config_template": build_config(args),
        "schema": {
            "table_name": args.table_name,
            "fields": fields,
            "evidence_levels": [
                "L0 无证据",
                "L1 个人直觉",
                "L2 具体反馈",
                "L3 小实验信号",
                "L4 强需求信号",
                "L5 可扩展证据",
            ],
            "statuses": ["灵感", "素材", "实验", "项目候选", "项目", "归档"],
            "value_types": ["文化", "教育", "内容", "工具", "商业", "社区", "系统", "作品", "研究"],
        },
        "note": "This script writes local config and schema guidance only. Create the Base/table in Lark/Feishu, then store its token and table id in config.local.json.",
    }


def write_config(path: str, config: dict[str, Any], force: bool) -> None:
    target = Path(path)
    if target.exists() and not force:
        raise FileExistsError(f"{target} already exists. Re-run with --force to overwrite.")
    with target.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a Lark/Feishu idea registry config and schema plan.")
    parser.add_argument("--dry-run", action="store_true", help="Print the setup plan without writing config")
    parser.add_argument("--write-config", action="store_true", help="Write config.local.json")
    parser.add_argument("--force", action="store_true", help="Overwrite existing config when writing")
    parser.add_argument("--config", default="config.local.json", help="Config path to write")
    parser.add_argument("--field-locale", choices=("zh", "en"), default="zh")
    parser.add_argument("--table-name", default="Ideas")
    parser.add_argument("--lark-cli-path", default="")
    parser.add_argument("--lark-cli-command", default="lark-cli")
    parser.add_argument("--base-token", default="")
    parser.add_argument("--table-id", default="")
    parser.add_argument("--identity", default="user")
    args = parser.parse_args()

    plan = build_plan(args)
    if args.write_config and not args.dry_run:
        write_config(args.config, plan["config_template"], args.force)
        plan["config_written"] = args.config

    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
