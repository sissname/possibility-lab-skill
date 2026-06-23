#!/usr/bin/env python3
"""Resolve the Lark CLI command without guessing multiple command names."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
from typing import Any


DEFAULT_CONFIG_PATH = "config.local.json"


def load_config(config_path: str | None = None) -> dict[str, Any]:
    path = Path(config_path or DEFAULT_CONFIG_PATH)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {path}")
    return data


def _command_from_path(path_value: str) -> list[str]:
    return [path_value]


def _command_from_string(command_value: str) -> list[str]:
    return shlex.split(command_value)


def _is_available(command: list[str]) -> bool:
    if not command:
        return False
    executable = command[0]
    if Path(executable).exists():
        return True
    return shutil.which(executable) is not None


def resolve_lark_cli(config_path: str | None = None) -> dict[str, Any]:
    config = load_config(config_path)
    candidates: list[tuple[str, list[str]]] = []

    if os.environ.get("LARK_CLI_PATH"):
        candidates.append(("env:LARK_CLI_PATH", _command_from_path(os.environ["LARK_CLI_PATH"])))
    if os.environ.get("LARK_CLI_COMMAND"):
        candidates.append(("env:LARK_CLI_COMMAND", _command_from_string(os.environ["LARK_CLI_COMMAND"])))
    if config.get("lark_cli_path"):
        candidates.append(("config:lark_cli_path", _command_from_path(str(config["lark_cli_path"]))))
    if config.get("lark_cli_command"):
        candidates.append(("config:lark_cli_command", _command_from_string(str(config["lark_cli_command"]))))

    default_cli = shutil.which("lark-cli")
    if default_cli:
        candidates.append(("path:lark-cli", [default_cli]))

    attempts = [{"source": source, "available": _is_available(command)} for source, command in candidates]
    for source, command in candidates:
        if _is_available(command):
            return {
                "available": True,
                "source": source,
                "command": command,
                "attempts": attempts,
            }

    return {
        "available": False,
        "source": None,
        "command": [],
        "attempts": attempts,
        "error": "No Lark CLI command resolved. Set LARK_CLI_PATH, LARK_CLI_COMMAND, or config.local.json.",
    }


def redacted_resolution(resolution: dict[str, Any]) -> dict[str, Any]:
    return {
        "available": resolution.get("available", False),
        "source": resolution.get("source"),
        "command": ["<resolved-lark-cli>"] if resolution.get("available") else [],
        "error": resolution.get("error"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the configured Lark CLI command.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to config.local.json")
    parser.add_argument("--show-command", action="store_true", help="Print the resolved command. May reveal a local path.")
    args = parser.parse_args()

    resolution = resolve_lark_cli(args.config)
    output = resolution if args.show_command else redacted_resolution(resolution)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if resolution.get("available") else 1


if __name__ == "__main__":
    raise SystemExit(main())
