#!/usr/bin/env python3
"""Exercise installed cvc5 launchers with isolated checkouts and stub agents."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
COMMANDS = {
    "dokimasia": ("dokimasia", "dokimasia", []),
    "anoieu": ("anoieu", "anoieu", []),
    "emperia": ("empeiria", "paideia/tools/empeiria", ["12905"]),
    "anakrisis": ("anakrisis", "paideia/tools/anakrisis", ["12893"]),
}


class Cvc5Checks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="koine cvc5 ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.cwd = self.root / "work" / "cvc5"
        self.cwd.mkdir(parents=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.ecosystem = self.root / "ecosystem"
        self.env = dict(os.environ, HOME=str(self.home), ANOIEU_REPOS=str(self.ecosystem),
                        PATH=str(self.bin))
        for key in ("DOKIMASIA_ROOT", "ANOIEU_ROOT", "EMPEIRIA_ROOT",
                    "ANAKRISIS_ROOT", "PAIDEIA_ROOT", "GIT_DIR", "GIT_WORK_TREE"):
            self.env.pop(key, None)
        for name in ("python3", "git"):
            (self.bin / name).symlink_to(shutil.which(name))
        for suffix in COMMANDS:
            name = "eo_cvc5_check_" + suffix
            shutil.copy2(ROOT / "eo_cmd" / name, self.bin / name)
        for name in ("claude", "codex"):
            stub = self.bin / name
            stub.write_text("#!/usr/bin/env python3\nimport json, os, sys\n"
                            "print(json.dumps({'cwd': os.getcwd(), 'args': sys.argv[1:]}))\n")
            stub.chmod(0o755)

    def run_command(self, suffix, *args, cwd=None, env=None):
        return subprocess.run([str(self.bin / ("eo_cvc5_check_" + suffix)), *args],
                              cwd=cwd or self.cwd, env=env or self.env,
                              capture_output=True, text=True)

    def git(self, *args):
        return subprocess.run([str(self.bin / "git"), *args], cwd=self.cwd,
                              env=self.env, check=True, capture_output=True,
                              text=True).stdout

    def make_cvc5(self):
        self.git("init", "-q")
        (self.cwd / "configure.sh").touch()
        (self.cwd / "src/theory").mkdir(parents=True)
        (self.cwd / "existing.txt").write_text("already staged\n")
        self.git("add", "existing.txt")
        (self.cwd / "existing.txt").write_text("also has unstaged work\n")

    def make_tools(self):
        for _, relative, _ in COMMANDS.values():
            path = self.ecosystem / relative
            path.mkdir(parents=True, exist_ok=True)
            (path / "README.md").write_text("A fixture charter.\n")

    def snapshot(self):
        return (self.git("status", "--porcelain"), self.git("diff", "--cached"),
                self.git("diff"), self.git("symbolic-ref", "HEAD"))

    def test_previews_without_git_tools_or_agents(self):
        (self.bin / "git").unlink()
        (self.bin / "claude").unlink()
        (self.bin / "codex").unlink()
        for suffix, (tool, _, args) in COMMANDS.items():
            with self.subTest(command=suffix):
                result = self.run_command(suffix, *args, "--show-prompt")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("No checkout", result.stdout)
                self.assertIn(tool, result.stdout)
                self.assertIn("outside a cvc5 checkout", result.stdout)
                self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(list(self.cwd.iterdir()), [])

    def test_number_and_option_validation_before_launch(self):
        for suffix, (_, _, valid) in COMMANDS.items():
            invalid = [["--bogus"], ["--tool-root"], [*valid, "--push"]]
            if valid:
                invalid += [[], ["0"], ["-1"], ["1.5"], ["abc"], ["12", "13"],
                            ["1; touch injected"], ["１２"]]
            else:
                invalid += [["12"]]
            for args in invalid:
                with self.subTest(command=suffix, args=args):
                    result = self.run_command(suffix, *args, "--show-prompt")
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(result.stdout, "")
            help_result = self.run_command(suffix, "--help")
            self.assertEqual(help_result.returncode, 0, help_result.stderr)

    def test_real_runs_require_cvc5_and_a_charter(self):
        for suffix, (_, _, args) in COMMANDS.items():
            result = self.run_command(suffix, *args)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("cvc5 Git checkout", result.stderr)
        self.git("init", "-q")
        self.make_tools()
        for suffix, (_, _, args) in COMMANDS.items():
            result = self.run_command(suffix, *args)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(result.stdout, "")
        self.make_cvc5()
        for suffix, (_, _, args) in COMMANDS.items():
            result = self.run_command(suffix, *args, "--tool-root", str(self.root / "missing"))
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("charter", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_installed_agent_launch_matches_preview_and_preserves_checkout(self):
        self.make_cvc5()
        self.make_tools()
        before = self.snapshot()
        for suffix, (_, relative, args) in COMMANDS.items():
            preview = self.run_command(suffix, *args, "--show-prompt")
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertIn(str(self.ecosystem / relative / "README.md"), preview.stdout)
            for flags, prefix in (([], []), (["--print"], ["-p"]),
                                  (["--codex"], []), (["--codex", "--print"], ["exec"]),
                                  (["--codex", "--claude", "--print"], ["-p"])):
                with self.subTest(command=suffix, flags=flags):
                    result = self.run_command(suffix, *args, *flags, cwd=self.cwd / "src/theory")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    got = json.loads(result.stdout)
                    self.assertEqual(got["cwd"], str(self.cwd))
                    self.assertEqual(got["args"], [*prefix, preview.stdout])
        self.assertEqual(self.snapshot(), before)

    def test_explicit_and_environment_discovery_and_missing_agent(self):
        self.make_cvc5()
        self.make_tools()
        alternate = self.root / "a charter elsewhere"
        alternate.mkdir()
        (alternate / "README.md").touch()
        for suffix, (tool, relative, args) in COMMANDS.items():
            env = dict(self.env, **{tool.upper() + "_ROOT": str(alternate)})
            result = self.run_command(suffix, *args, "--show-prompt", env=env)
            self.assertIn(str(alternate / "README.md"), result.stdout)
            result = self.run_command(suffix, *args, "--tool-root", str(self.ecosystem / relative),
                                      "--show-prompt", env=env)
            self.assertIn(str(self.ecosystem / relative / "README.md"), result.stdout)
            env[tool.upper() + "_ROOT"] = str(self.root / "missing")
            self.assertEqual(self.run_command(suffix, *args, env=env).returncode, 2)
        env = dict(self.env, ANOIEU_REPOS="", PAIDEIA_ROOT=str(self.ecosystem / "paideia"))
        for suffix in ("emperia", "anakrisis"):
            _, relative, args = COMMANDS[suffix]
            result = self.run_command(suffix, *args, "--show-prompt", env=env)
            self.assertIn(str(self.ecosystem / relative / "README.md"), result.stdout)
        (self.bin / "codex").unlink()
        result = self.run_command("dokimasia", "--codex")
        self.assertEqual(result.returncode, 127, result.stderr)
        self.assertIn("codex is not on PATH", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_numbered_workflows_and_local_handoff(self):
        for suffix, (_, _, args) in COMMANDS.items():
            result = self.run_command(suffix, *args, "--show-prompt")
            prompt = " ".join(result.stdout.split())
            self.assertEqual(result.returncode, 0, result.stderr)
            if suffix == "anakrisis":
                self.assertIn("https://github.com/cvc5/cvc5/pull/12893", prompt)
                self.assertIn("merge-base", prompt)
                self.assertIn("Do not edit or stage cvc5", prompt)
                self.assertNotIn("**Leave the work staged", prompt)
            else:
                self.assertIn("**Leave the work staged and not committed**", prompt)
            if suffix == "emperia":
                self.assertIn("https://github.com/cvc5/cvc5/issues/12905", prompt)
            self.assertIn("Do not commit, push", prompt)


if __name__ == "__main__":
    unittest.main()
