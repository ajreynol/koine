#!/usr/bin/env python3
"""Exercise cvc5 and Eunoia launchers with isolated checkouts and stub agents."""

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


def command_name(suffix):
    return "eo_check_anoieu" if suffix == "anoieu" else "eo_cvc5_check_" + suffix


class Cvc5Checks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="koine checks ")
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
            name = command_name(suffix)
            shutil.copy2(ROOT / "eo_cmd" / name, self.bin / name)
        for name in ("claude", "codex"):
            stub = self.bin / name
            stub.write_text("#!/usr/bin/env python3\nimport json, os, sys\n"
                            "print(json.dumps({'cwd': os.getcwd(), 'args': sys.argv[1:]}))\n")
            stub.chmod(0o755)

    def run_command(self, suffix, *args, cwd=None, env=None):
        return subprocess.run([str(self.bin / command_name(suffix)), *args],
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
                self.assertNotIn("No checkout", result.stdout)
                self.assertNotIn("tool checkout", result.stdout)
                self.assertNotIn("--tool-root", result.stdout)
                if suffix == "emperia":
                    self.assertNotIn(tool, result.stdout)
                else:
                    self.assertIn("read-only GitHub access", result.stdout)
                    self.assertIn(tool, result.stdout)
                outside = "outside a Git checkout" if suffix == "anoieu" else "outside a cvc5 checkout"
                self.assertIn(outside, result.stdout)
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

    def test_real_runs_require_the_target_checkout_and_validate_explicit_tools(self):
        for suffix, (_, _, args) in COMMANDS.items():
            result = self.run_command(suffix, *args)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Git checkout", result.stderr)
        self.git("init", "-q")
        self.make_tools()
        for suffix, (_, _, args) in COMMANDS.items():
            if suffix == "anoieu":
                continue  # A generic Git checkout is a valid Anoieu target.
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
            for context in ([], ["--tool-root", str(self.ecosystem / relative)]):
                preview = self.run_command(suffix, *args, *context, "--show-prompt")
                self.assertEqual(preview.returncode, 0, preview.stderr)
                if context:
                    self.assertIn(str(self.ecosystem / relative / "README.md"), preview.stdout)
                else:
                    self.assertNotIn(str(self.ecosystem), preview.stdout)
                for flags, prefix in (([], []), (["--print"], ["-p"]),
                                      (["--codex"], []), (["--codex", "--print"], ["exec"]),
                                      (["--codex", "--claude", "--print"], ["-p"])):
                    with self.subTest(command=suffix, context=context, flags=flags):
                        result = self.run_command(suffix, *args, *context, *flags,
                                                  cwd=self.cwd / "src/theory")
                        self.assertEqual(result.returncode, 0, result.stderr)
                        got = json.loads(result.stdout)
                        self.assertEqual(got["cwd"], str(self.cwd))
                        self.assertEqual(got["args"], [*prefix, preview.stdout])
        self.assertEqual(self.snapshot(), before)

    def test_anoieu_runs_in_non_cvc5_targets(self):
        self.make_tools()
        for target in ("ethos", "logos", "another-signature-project"):
            with self.subTest(target=target):
                self.cwd = self.root / "work" / target
                definitions = self.cwd / "defs"
                definitions.mkdir(parents=True)
                self.git("init", "-q")
                (definitions / "Signature.eo").write_text("; fixture signature\n")
                self.git("add", "defs/Signature.eo")
                before = self.snapshot()
                preview = self.run_command("anoieu", "--show-prompt")
                self.assertEqual(preview.returncode, 0, preview.stderr)
                for flags, prefix in (([], []), (["--print"], ["-p"]),
                                      (["--codex"], []), (["--codex", "--print"], ["exec"])):
                    result = self.run_command("anoieu", *flags, cwd=definitions)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    launched = json.loads(result.stdout)
                    self.assertEqual(launched["cwd"], str(self.cwd))
                    self.assertEqual(launched["args"], [*prefix, preview.stdout])
                self.assertNotIn("cvc5", preview.stdout)
                self.assertIn("anoieu.json", preview.stdout)
                self.assertEqual(self.snapshot(), before)

    def test_explicit_tool_selection_and_missing_agent(self):
        self.make_cvc5()
        self.make_tools()
        alternate = self.root / "a charter elsewhere"
        alternate.mkdir()
        (alternate / "README.md").touch()
        for suffix, (tool, relative, args) in COMMANDS.items():
            env = dict(self.env, **{tool.upper() + "_ROOT": str(alternate)})
            result = self.run_command(suffix, *args, "--show-prompt", env=env)
            self.assertNotIn(str(alternate), result.stdout)
            result = self.run_command(suffix, *args, "--tool-root", str(self.ecosystem / relative),
                                      "--show-prompt", env=env)
            self.assertIn(str(self.ecosystem / relative / "README.md"), result.stdout)
            result = self.run_command(suffix, *args, "--tool-root", str(alternate), "--print")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(alternate / "README.md"), json.loads(result.stdout)["args"][-1])
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

    def test_emperia_runs_without_tool_context_by_default(self):
        self.make_cvc5()
        before = self.snapshot()
        preview = self.run_command("emperia", "12905", "--show-prompt")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        for reference in ("empeiria", "paideia", "charter", "triage.md", "ledger",
                          "tool checkout", "--tool-root"):
            self.assertNotIn(reference, preview.stdout)
        self.assertIn("https://github.com/cvc5/cvc5/issues/12905", preview.stdout)
        self.assertIn("test the reproducer before and after", preview.stdout)
        result = self.run_command("emperia", "12905", "--print")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["args"], ["-p", preview.stdout])
        self.assertNotIn("charter", result.stderr)

        # Existing checkouts and inherited discovery settings cannot opt a run in.
        self.make_tools()
        for search in (self.cwd.parent, self.home):
            path = search / "paideia/tools/empeiria"
            path.mkdir(parents=True)
            (path / "README.md").touch()
        for selected in (self.ecosystem / "paideia/tools/empeiria", self.root / "missing"):
            env = dict(self.env, EMPEIRIA_ROOT=str(selected),
                       PAIDEIA_ROOT=str(self.ecosystem / "paideia"))
            result = self.run_command("emperia", "12905", "--print", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["args"], ["-p", preview.stdout])
            self.assertNotIn("charter", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_emperia_tool_context_requires_explicit_opt_in(self):
        self.make_cvc5()
        self.make_tools()
        tool = self.ecosystem / "paideia/tools/empeiria"
        args = ["12905", "--tool-root", str(tool)]
        preview = self.run_command("emperia", *args, "--show-prompt")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        for relative in ("README.md", "docs/triage.md", "ledger/"):
            self.assertIn(f"{tool}/{relative}", preview.stdout)
        self.assertIn("without modifying", preview.stdout)
        result = self.run_command("emperia", *args, "--codex", "--print")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["args"], ["exec", preview.stdout])
        self.assertIn(str(tool / "README.md"), result.stderr)

    def test_all_checks_run_without_local_tools_and_ignore_discovery(self):
        self.make_cvc5()
        before = self.snapshot()
        previews = {}
        for suffix, (_, _, args) in COMMANDS.items():
            preview = self.run_command(suffix, *args, "--show-prompt")
            self.assertEqual(preview.returncode, 0, preview.stderr)
            previews[suffix] = preview.stdout
            result = self.run_command(suffix, *args, "--print")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["args"], ["-p", preview.stdout])
            self.assertNotIn("charter", result.stderr)

        self.make_tools()
        for search in (self.cwd.parent, self.home):
            for _, relative, _ in COMMANDS.values():
                path = search / relative
                path.mkdir(parents=True, exist_ok=True)
                (path / "README.md").touch()
        for exists in (True, False):
            env = dict(self.env, PAIDEIA_ROOT=str(self.ecosystem / "paideia"))
            for tool, relative, _ in COMMANDS.values():
                env[tool.upper() + "_ROOT"] = str(self.ecosystem / relative if exists
                                                 else self.root / "missing")
            for suffix, (_, _, args) in COMMANDS.items():
                with self.subTest(command=suffix, exists=exists):
                    result = self.run_command(suffix, *args, "--print", env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["args"], ["-p", previews[suffix]])
        self.assertEqual(self.snapshot(), before)

    def test_published_evidence_and_explicit_analyzer_workflows(self):
        self.make_tools()
        for suffix, analyzer in (("dokimasia", "scripts/dokimasia_analyzer"),
                                  ("anoieu", "anoieu_analyzer/usage.md"),
                                  ("anakrisis", "run_anakrisis 12893 --delta")):
            _, relative, args = COMMANDS[suffix]
            default = self.run_command(suffix, *args, "--show-prompt")
            local = self.run_command(suffix, *args, "--tool-root", str(self.ecosystem / relative),
                                     "--show-prompt")
            self.assertEqual(default.returncode, 0, default.stderr)
            self.assertEqual(local.returncode, 0, local.stderr)
            self.assertIn("https://github.com/ajreynol/", default.stdout)
            self.assertIn("source revision", default.stdout)
            self.assertNotIn(analyzer, default.stdout)
            self.assertNotIn("DOKIMASIA_ROOT", default.stdout)
            self.assertIn(analyzer, local.stdout)
            if suffix == "anakrisis":
                self.assertIn("published delta evidence", default.stdout)
                self.assertIn("SHAs match the verified PR", default.stdout)
                self.assertIn("stop the review", default.stdout)
                self.assertIn("analysis is not an empty delta", default.stdout)
                self.assertIn("analysis is not an empty delta", local.stdout)
            else:
                self.assertIn("bug_db/bugs.json", default.stdout)
                self.assertIn("reproducer" if suffix == "anoieu" else "concrete inputs",
                              default.stdout)


if __name__ == "__main__":
    unittest.main()
