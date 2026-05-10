import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"
STARTER = ROOT / "llm-wiki" / "core" / "assets" / "starter-wiki"


def run_init(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def load_module():
    if not SCRIPT.exists():
        raise AssertionError(f"Missing initializer script: {SCRIPT}")
    spec = importlib.util.spec_from_file_location("init_llm_wiki", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestInitLlmWiki(unittest.TestCase):
    def test_init_creates_starter_wiki(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"

            result = run_init(target)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "WIKI_SCHEMA.md").is_file())
            self.assertTrue((target / "wiki_records" / "sources").is_dir())
            self.assertTrue((target / "wiki_pages" / "index.md").is_file())
            self.assertIn("created:", result.stdout)

    def test_init_skips_existing_files_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            target.mkdir()
            schema = target / "WIKI_SCHEMA.md"
            schema.write_text("local schema\n", encoding="utf-8")

            result = run_init(target)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(schema.read_text(encoding="utf-8"), "local schema\n")
            self.assertIn("skipped:", result.stdout)

    def test_force_overwrites_existing_starter_file_without_deleting_user_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            target.mkdir()
            schema = target / "WIKI_SCHEMA.md"
            schema.write_text("local schema\n", encoding="utf-8")
            personal = target / "personal.md"
            personal.write_text("private notes\n", encoding="utf-8")

            result = run_init("--force", target)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                schema.read_text(encoding="utf-8"),
                (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(personal.read_text(encoding="utf-8"), "private notes\n")
            self.assertIn("overwritten:", result.stdout)

    def test_directory_conflict_with_existing_file_returns_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            target.mkdir()
            raw = target / "raw"
            raw.write_text("user raw marker\n", encoding="utf-8")

            result = run_init(target)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("path type conflict", result.stderr)
            self.assertIn("raw", result.stderr)
            self.assertTrue(raw.is_file())
            self.assertEqual(raw.read_text(encoding="utf-8"), "user raw marker\n")

    def test_force_file_conflict_with_existing_directory_returns_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            schema = target / "WIKI_SCHEMA.md"
            schema.mkdir(parents=True)

            result = run_init("--force", target)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("path type conflict", result.stderr)
            self.assertIn("WIKI_SCHEMA.md", result.stderr)
            self.assertTrue(schema.is_dir())
            self.assertFalse((schema / "WIKI_SCHEMA.md").exists())

    def test_target_root_conflict_with_existing_file_returns_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            target.write_text("not a directory\n", encoding="utf-8")

            result = run_init(target)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("path type conflict", result.stderr)
            self.assertIn(str(target), result.stderr)
            self.assertTrue(target.is_file())
            self.assertEqual(target.read_text(encoding="utf-8"), "not a directory\n")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_force_rejects_symlinked_starter_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            target.mkdir()
            outside = Path(temp_dir) / "outside-schema.md"
            outside.write_text("outside schema\n", encoding="utf-8")
            schema = target / "WIKI_SCHEMA.md"
            os.symlink(outside, schema)

            result = run_init("--force", target)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr)
            self.assertTrue(schema.is_symlink())
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside schema\n")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_rejects_symlinked_starter_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            target.mkdir()
            outside_raw = Path(temp_dir) / "outside-raw"
            outside_raw.mkdir()
            raw = target / "raw"
            os.symlink(outside_raw, raw)

            result = run_init(target)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr)
            self.assertTrue(raw.is_symlink())
            self.assertFalse((outside_raw / ".gitkeep").exists())

    def test_missing_bundled_starter_wiki_returns_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module = load_module()
            module.starter_dir = lambda: Path(temp_dir) / "missing-starter"
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                exit_code = module.main([str(Path(temp_dir) / "wiki")])

            self.assertEqual(exit_code, 1)
            self.assertIn("starter wiki", stderr.getvalue())
            self.assertIn("missing-starter", stderr.getvalue())
