import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "possibility-lab" / "scripts" / "write_ideas_to_lark.py"
sys.path.insert(0, str(SCRIPT.parent))

spec = importlib.util.spec_from_file_location("write_ideas_to_lark", SCRIPT)
writer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(writer)


class PayloadMappingTests(unittest.TestCase):
    def test_maps_english_payload_to_chinese_fields(self):
        mapped, dropped = writer.map_record_fields(
            {
                "Title": "Project evidence review assistant",
                "Raw idea": "Capture project evidence.",
                "Evidence level": "L1 intuition",
                "Status": "material",
                "Value type": "system",
                "Unknown": "drop me",
            },
            "zh",
        )

        self.assertEqual(mapped["标题"], "Project evidence review assistant")
        self.assertEqual(mapped["原始想法"], "Capture project evidence.")
        self.assertEqual(mapped["当前证据等级"], "L1 个人直觉")
        self.assertEqual(mapped["状态"], "素材")
        self.assertEqual(mapped["价值类型"], "系统")
        self.assertEqual(dropped, ["Unknown"])

    def test_extracts_titles_from_common_cli_shapes(self):
        for response in (
            {"data": {"items": [{"fields": {"标题": "A"}}]}},
            {"records": [{"fields": {"标题": "A"}}]},
            [{"fields": {"标题": "A"}}],
        ):
            self.assertEqual(writer.extract_existing_titles(response, "zh"), {"A"})

    def test_splits_duplicate_titles(self):
        payload = {"records": [{"fields": {"标题": "A"}}, {"fields": {"标题": "B"}}]}
        creatable, created, skipped = writer._split_duplicates(payload, {"A"}, "zh")

        self.assertEqual(created, ["B"])
        self.assertEqual(skipped, ["A"])
        self.assertEqual(creatable, {"records": [{"fields": {"标题": "B"}}]})


if __name__ == "__main__":
    unittest.main()
