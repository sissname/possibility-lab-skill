from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRITER = ROOT / "possibility-lab" / "scripts" / "write_ideas_to_lark.py"
FAKE_CLI = ROOT / "tests" / "fixtures" / "fake_lark_cli.py"


class FakeLarkCliIntegrationTests(unittest.TestCase):
    def run_writer(self, payload_path: Path, *extra_args: str) -> dict:
        env = {
            **os.environ,
            "LARK_CLI_PATH": str(FAKE_CLI),
            "LARK_BASE_TOKEN": "test-base-token",
            "LARK_TABLE_ID": "test-table-id",
            "LARK_IDENTITY": "user",
            "LARK_FIELD_LOCALE": "zh",
        }
        completed = subprocess.run(
            [sys.executable, str(WRITER), str(payload_path), *extra_args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        return json.loads(completed.stdout)

    def test_dry_run_reports_duplicates_and_creatable_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            payload_path = Path(tmpdir) / "payload.json"
            payload_path.write_text(
                json.dumps(
                    [
                        {"标题": "已有想法", "原始想法": "Duplicate title"},
                        {"Title": "新想法", "Raw idea": "Create a new row", "Status": "material"},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report = self.run_writer(payload_path, "--dry-run")

        self.assertEqual(report["missing_configuration"], [])
        self.assertEqual(report["skipped_duplicates"], ["已有想法"])
        self.assertEqual(report["would_create"], ["新想法"])
        self.assertEqual(report["batch_payload"]["records"][0]["fields"]["状态"], "素材")

    def test_write_uses_fake_batch_create_and_reports_created_titles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            payload_path = Path(tmpdir) / "payload.json"
            payload_path.write_text(
                json.dumps([{"标题": "新想法", "原始想法": "Create a new row"}], ensure_ascii=False),
                encoding="utf-8",
            )

            report = self.run_writer(payload_path)

        self.assertEqual(report["errors"], [])
        self.assertEqual(report["created"], ["新想法"])
        self.assertEqual(report["write_response"]["data"]["records"][0]["fields"]["标题"], "新想法")


if __name__ == "__main__":
    unittest.main()
