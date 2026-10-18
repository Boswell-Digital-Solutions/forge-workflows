"""Execute the actual YAML shell steps without building or publishing an app."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILES = ["tauri-ci-reusable.yml", "tauri-release-reusable.yml"]


def step(filename: str) -> str:
    text = (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
    text = text.split("- name: Check final Debian archives with required Lintian", 1)[1]
    lines = text.split("        run: |\n", 1)[1].splitlines()
    result = []
    for line in lines:
        if line.strip() and not line.startswith("          "):
            break
        result.append(line[10:] if line else "")
    return "\n".join(result)


class WorkflowBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tools = self.root / "tools"
        self.tools.mkdir()
        self.packages = self.root / "packages"
        self.packages.mkdir()
        (self.packages / "fixture package.deb").write_bytes(b"command fixture")
        self.tool = self.tools / "lintian"
        self.tool.write_text(
            "#!/bin/sh\n"
            '[ -z "${LINTIAN_SUPPRESS_TAGS:-}" ] || exit 9\n'
            'if [ "$1" = --version ]; then echo "Lintian fixture"; exit 0; fi\n'
            'echo "$*"\n'
            'case "$FIXTURE_MODE" in error) echo "E: fixture: rejected"; exit 2;; '
            'crash) exit 1;; warning) echo "W: fixture: review";; esac\n',
            encoding="utf-8",
        )
        self.tool.chmod(0o755)
        (self.tools / "sha256sum").symlink_to(shutil.which("sha256sum"))
        self.env = dict(
            os.environ,
            PATH=str(self.tools),
            DEB_DIR=str(self.packages),
            FIXTURE_MODE="pass",
            LINTIAN_SUPPRESS_TAGS="all",
        )

    def run_step(self, filename: str):
        return subprocess.run(
            ["/bin/bash", "-c", step(filename)],
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_success_and_warning_are_visible(self):
        for filename in FILES:
            for mode in ["pass", "warning"]:
                with self.subTest(filename=filename, mode=mode):
                    self.env["FIXTURE_MODE"] = mode
                    result = self.run_step(filename)
                    self.assertEqual(
                        result.returncode, 0, result.stdout + result.stderr
                    )
                    self.assertIn("--fail-on error", result.stdout)

    def test_error_and_tool_failure_block(self):
        for filename in FILES:
            for mode in ["error", "crash"]:
                with self.subTest(filename=filename, mode=mode):
                    self.env["FIXTURE_MODE"] = mode
                    self.assertNotEqual(self.run_step(filename).returncode, 0)

    def test_missing_tool_blocks(self):
        self.tool.unlink()
        for filename in FILES:
            result = self.run_step(filename)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Lintian is required", result.stderr)

    def test_empty_archive_directory_blocks(self):
        for package in self.packages.iterdir():
            package.unlink()
        for filename in FILES:
            self.assertNotEqual(self.run_step(filename).returncode, 0)

    def test_gate_is_after_build_and_before_any_upload(self):
        for filename in FILES:
            text = (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
            self.assertLess(
                text.index("run: cargo tauri build"),
                text.index("- name: Check final Debian"),
            )
            self.assertLess(
                text.index("- name: Check final Debian"), text.index("- name: Upload")
            )
            self.assertIn("            lintian\n", text)
        self.assertEqual(step(FILES[0]), step(FILES[1]))


if __name__ == "__main__":
    unittest.main()
