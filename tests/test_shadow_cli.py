from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHADOW_MANAGER = REPO_ROOT / "tools" / "shadow_manager.py"
VERSION_MANAGER = REPO_ROOT / "tools" / "version_manager.py"


class ShadowCliSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name) / "shadows"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, script: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            [sys.executable, str(script), *args, "--base-dir", str(self.base_dir)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=merged_env,
            check=False,
        )

    def write_file(self, name: str, content: str) -> Path:
        path = Path(self.temp_dir.name) / name
        path.write_text(content, encoding="utf-8")
        return path

    def create_shadow(self, slug: str = "alice", name: str = "Alice", shadow_content: str = "# Alice\n\n🙂") -> subprocess.CompletedProcess[str]:
        shadow_path = self.write_file(f"{slug}_shadow.md", shadow_content)
        meta_path = self.write_file(
            f"{slug}_meta.json",
            json.dumps({"name": name, "profile": {"gender": "女", "rel_stage": "朋友"}}, ensure_ascii=False),
        )
        return self.run_cli(
            SHADOW_MANAGER,
            "--action", "create",
            "--slug", slug,
            "--name", name,
            "--meta", str(meta_path),
            "--shadow", str(shadow_path),
        )

    def test_create_refuses_to_overwrite_existing_shadow(self) -> None:
        first = self.create_shadow()
        self.assertEqual(first.returncode, 0, first.stderr)

        second = self.create_shadow()
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("影子已存在", second.stderr)

    def test_slugify_falls_back_to_codepoints_without_pypinyin(self) -> None:
        shadow_path = self.write_file("cn_shadow.md", "# 中文\n")
        meta_path = self.write_file(
            "cn_meta.json",
            json.dumps({"name": "李总"}, ensure_ascii=False),
        )

        created = self.run_cli(
            SHADOW_MANAGER,
            "--action", "create",
            "--name", "李总",
            "--meta", str(meta_path),
            "--shadow", str(shadow_path),
            env={"PYTHONPATH": ""},
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertTrue((self.base_dir / "u674eu603b").exists())

    def test_update_with_correction_creates_record_and_snapshot(self) -> None:
        created = self.create_shadow(shadow_content="# Alice\n\n## Correction 记录\n\n（暂无记录）\n")
        self.assertEqual(created.returncode, 0, created.stderr)

        patch_path = self.write_file("patch.md", "## Layer 2 补充\n- 新口头禅：行吧")
        updated = self.run_cli(
            SHADOW_MANAGER,
            "--action", "update",
            "--slug", "alice",
            "--shadow-patch", str(patch_path),
            "--correct-scene", "生气时",
            "--correct-wrong", "直接说我不想聊了",
            "--correct-right", "停止回复半天",
            "--message-count", "8",
        )
        self.assertEqual(updated.returncode, 0, updated.stderr)

        shadow_path = self.base_dir / "alice" / "shadow.md"
        meta_path = self.base_dir / "alice" / "meta.json"
        snapshot_shadow_path = self.base_dir / "alice" / "versions" / "v1" / "shadow.md"

        shadow_content = shadow_path.read_text(encoding="utf-8")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

        self.assertIn("[生气时] 错误：直接说我不想聊了；正确：停止回复半天", shadow_content)
        self.assertIn("## Layer 2 补充", shadow_content)
        self.assertTrue(snapshot_shadow_path.exists())
        self.assertEqual(meta["version"], "v2")
        self.assertEqual(meta["message_count"], 8)
        self.assertEqual(meta["corrections_count"], 1)

    def test_correct_action_requires_correction_payload(self) -> None:
        created = self.create_shadow()
        self.assertEqual(created.returncode, 0, created.stderr)

        result = self.run_cli(
            SHADOW_MANAGER,
            "--action", "correct",
            "--slug", "alice",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("correct 操作需要提供纠正内容", result.stderr)

    def test_rollback_restores_full_snapshot_including_knowledge_and_meta(self) -> None:
        created = self.create_shadow(slug="boss", name="李总", shadow_content="# V1\n")
        self.assertEqual(created.returncode, 0, created.stderr)

        chat_file = self.base_dir / "boss" / "knowledge" / "chats" / "sample.txt"
        chat_file.write_text("log-v1", encoding="utf-8")

        patch_v2 = self.write_file("patch_v2.md", "v2 update")
        updated_v2 = self.run_cli(
            SHADOW_MANAGER,
            "--action", "update",
            "--slug", "boss",
            "--shadow-patch", str(patch_v2),
            "--message-count", "1",
        )
        self.assertEqual(updated_v2.returncode, 0, updated_v2.stderr)

        chat_file.write_text("log-v2", encoding="utf-8")
        patch_v3 = self.write_file("patch_v3.md", "v3 update")
        updated_v3 = self.run_cli(
            SHADOW_MANAGER,
            "--action", "update",
            "--slug", "boss",
            "--shadow-patch", str(patch_v3),
            "--message-count", "1",
        )
        self.assertEqual(updated_v3.returncode, 0, updated_v3.stderr)

        rolled_back = self.run_cli(
            VERSION_MANAGER,
            "--action", "rollback",
            "--slug", "boss",
            "--version", "v1",
        )
        self.assertEqual(rolled_back.returncode, 0, rolled_back.stderr)

        shadow_content = (self.base_dir / "boss" / "shadow.md").read_text(encoding="utf-8")
        meta = json.loads((self.base_dir / "boss" / "meta.json").read_text(encoding="utf-8"))
        restored_chat = (self.base_dir / "boss" / "knowledge" / "chats" / "sample.txt").read_text(encoding="utf-8")

        self.assertEqual(shadow_content, "# V1\n")
        self.assertEqual(restored_chat, "log-v1")
        self.assertEqual(meta["version"], "v1_restored")
        self.assertEqual(meta["rollback_from"], "v3")

    def test_get_survives_ascii_stdout_with_unicode_shadow_content(self) -> None:
        created = self.create_shadow(slug="emoji", name="Emoji", shadow_content="# Emoji\n\n💼🙂\n")
        self.assertEqual(created.returncode, 0, created.stderr)

        result = self.run_cli(
            SHADOW_MANAGER,
            "--action", "get",
            "--slug", "emoji",
            env={"PYTHONIOENCODING": "ascii"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("=== Emoji (v1) ===", result.stdout)


if __name__ == "__main__":
    unittest.main()
