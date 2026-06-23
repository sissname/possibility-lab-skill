from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillStructureTests(unittest.TestCase):
    def test_skill_frontmatter_has_required_fields_only(self):
        skill = (ROOT / "possibility-lab" / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        frontmatter = skill.split("---", 2)[1]
        keys = [line.split(":", 1)[0] for line in frontmatter.splitlines() if ":" in line]
        self.assertEqual(keys, ["name", "description"])
        self.assertIn("name: possibility-lab", frontmatter)

    def test_openai_yaml_default_prompt_mentions_skill(self):
        metadata = (ROOT / "possibility-lab" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("display_name:", metadata)
        self.assertIn("$possibility-lab", metadata)

    def test_chinese_fields_are_not_mojibake(self):
        text_paths = [
            path
            for path in (ROOT / "possibility-lab").rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in {".md", ".py", ".yaml", ".yml", ".json"}
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in text_paths)
        self.assertIn("标题", combined)
        markers = [
            bytes.fromhex("e98f8de59bac").decode("utf-8"),
            bytes.fromhex("e98d98e786b7").decode("utf-8"),
            bytes.fromhex("e98eafe899abe7a1b6").decode("utf-8"),
        ]
        for marker in markers:
            self.assertNotIn(marker, combined)

    def test_private_markers_are_absent_from_text_files(self):
        text_suffixes = {".md", ".py", ".yaml", ".yml", ".json", ".sh", ".txt"}
        text_paths = [
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
            and "reports" not in path.parts
            and path.suffix in text_suffixes
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in text_paths)
        forbidden_literals = [
            "M" + "7OJ",
            "tbl" + "0",
            "aimwise" + "cd",
            "/Users/" + "sissname",
            "/Volumes/" + "1T",
            "gh" + "o_",
        ]
        for marker in forbidden_literals:
            self.assertNotIn(marker, combined)

        forbidden_patterns = [
            re.compile("sk-" + r"[A-Za-z0-9]"),
            re.compile("Bearer " + r"[A-Za-z0-9]"),
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(pattern.search(combined))


if __name__ == "__main__":
    unittest.main()
