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
    "heuresis": ("heuresis", "tachyon/tools/heuresis", ["9"]),
    "elaphros": ("elaphros", "tachyon/tools/elaphros", ["3"]),
    "metagraphe": ("metagraphe", "tachyon/tools/metagraphe", ["25"]),
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
        """What a preview prints is what that same run hands an agent.

        `--show-prompt` is compared against the launch of the *same* invocation,
        which means the flags that select the agent go into both. They used to be
        dropped from the preview, because no prompt depended on which agent got
        it -- until heuresis, whose branch name carries the agent, so that two
        agents sent at one research direction do not write to one name. A preview
        taken without `--codex` is a preview of a different run.
        """
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
                        selection = [flag for flag in flags if flag != "--print"]
                        same = (preview if not selection else
                                self.run_command(suffix, *args, *context, *selection,
                                                 "--show-prompt"))
                        self.assertEqual(same.returncode, 0, same.stderr)
                        result = self.run_command(suffix, *args, *context, *flags,
                                                  cwd=self.cwd / "src/theory")
                        self.assertEqual(result.returncode, 0, result.stderr)
                        got = json.loads(result.stdout)
                        self.assertEqual(got["cwd"], str(self.cwd))
                        self.assertEqual(got["args"], [*prefix, same.stdout])
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

    def test_heuresis_argues_before_it_writes_and_claims_no_measurement(self):
        """The one check whose product is a new approach, and what stops it
        being an old one renamed.

        A direction with a register of branches behind it is exactly where a
        plausible-looking approach is most likely to be something already tried
        and measured, so the prompt asks for that inventory *before* any code and
        refuses an approach whose difference cannot be stated against a named
        branch or option. And a run that builds one binary must not report a
        speedup: the number belongs to a whole-set run on the register's own
        host, and a claim made here would enter that register as evidence it is
        not.
        """
        self.make_cvc5()
        before = self.snapshot()
        preview = self.run_command("heuresis", "9", "--show-prompt")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        flat = " ".join(preview.stdout.split())
        for asked in (
                "tools/heuresis/docs/directions.md",
                "Record the source revision",
                "**Brainstorm before writing any code, and say the result in "
                "your response**",
                "is a variant rather than a new approach",
                "**Make no performance claim.**",
                "**Check the tree before anything else and stop on any of three**",
                "this checkout is not on `main`",
                "a tracked file has staged or unstaged changes",
                "not the current tip of cvc5's own `main`",
                "**Untracked files are none of the three**",
                "leave untracked files that were here before you where they are",
                "Leave heuresis's own documents alone",
                "**Leave the work staged and not committed**",
                "create branch `ai-heuresis-r9-claude` from the current HEAD"):
            self.assertIn(asked, flat)
        # Written 9 or R9, it is the same direction; the register writes R9.
        self.assertEqual(self.run_command("heuresis", "R9", "--show-prompt").stdout,
                         preview.stdout)
        self.assertIn("direction R9", flat)
        # The agent that wrote it is in the branch name, so two agents on one
        # direction do not collide.
        codex = self.run_command("heuresis", "9", "--codex", "--show-prompt")
        self.assertIn("create branch `ai-heuresis-r9-codex` from", " ".join(codex.stdout.split()))
        self.assertNotIn("claude", codex.stdout)
        # A cvc5 checkout that has been built once has untracked output in it,
        # so a gate that counted those would stop on every real checkout it was
        # pointed at: the three are about the branch, the tracked tree and the
        # revision. None of them is cleared by the agent, and the sweeps that
        # would clear one by taking somebody's work with it are asked for
        # nowhere.
        for never in ("git add -A", "git add .", "git clean", "git stash",
                      "git pull", "git reset"):
            self.assertNotIn(never, flat)
        # This fixture has both staged and unstaged changes in it, and the run
        # still launches: the gate is in the prompt, checked by the agent that
        # can also read upstream, rather than guessed at by a launcher that
        # fetches nothing.
        launched = self.run_command("heuresis", "9", "--print")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        self.assertEqual(json.loads(launched.stdout)["args"], ["-p", preview.stdout])
        self.assertIn("R9 on ai-heuresis-r9-claude", launched.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_heuresis_takes_the_first_free_branch_name(self):
        """A name already taken is not free, wherever the ref lives.

        The fork is where these branches end up, so a remote-tracking ref counts
        too: discovering the collision after the work is done costs a rename of
        the one thing the register cites. The launcher reads refs and picks; it
        creates nothing, and the prompt still carries the rule for a ref that
        arrives after the pick.
        """
        self.make_cvc5()
        self.git("-c", "user.email=t@example.invalid", "-c", "user.name=A Fixture",
                 "commit", "-q", "-m", "a base commit")
        for ref, expected, then in (
                (None, "claude", ("claude2", "claude3")),
                ("refs/heads/ai-heuresis-r9-claude", "claude2", ("claude3", "claude4")),
                ("refs/remotes/origin/ai-heuresis-r9-claude2", "claude3",
                 ("claude4", "claude5")),
                ("refs/heads/ai-heuresis-r9-claude4", "claude3", ("claude5", "claude6"))):
            if ref is not None:
                self.git("update-ref", ref, "HEAD")
            with self.subTest(taken=ref):
                result = self.run_command("heuresis", "9", "--show-prompt")
                self.assertEqual(result.returncode, 0, result.stderr)
                flat = " ".join(result.stdout.split())
                self.assertIn(f"create branch `ai-heuresis-r9-{expected}` from", flat)
                self.assertIn(f"`ai-heuresis-r9-{then[0]}`, then "
                              f"`ai-heuresis-r9-{then[1]}`", flat)
        # Reading refs is all it does: no branch was created, switched or moved.
        self.assertEqual(self.git("symbolic-ref", "HEAD").strip(), "refs/heads/" + self.git(
            "rev-parse", "--abbrev-ref", "HEAD").strip())
        self.assertNotIn("ai-heuresis-r9-claude3", self.git("for-each-ref", "--format=%(refname)"))

    def test_elaphros_keeps_the_proof_it_is_making_cheaper(self):
        """Heuresis's shape, with the one thing a proof-overhead approach can
        cheat on refused out loud.

        A proof with more trusted steps is cheaper to produce and is not the
        same proof; the register refuses it as a proposal, so the prompt refuses
        it as an approach and asks for the emitted proof to be checked and
        compared with the default's.
        """
        self.make_cvc5()
        before = self.snapshot()
        preview = self.run_command("elaphros", "3", "--show-prompt")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        flat = " ".join(preview.stdout.split())
        for asked in (
                "tools/elaphros/docs/directions.md",
                "direction E3 of elaphros's register",
                "**Brainstorm before writing any code, and say the result in "
                "your response**",
                "is a variant rather than a new approach",
                "**An approach that saves its time by weakening the proof is not "
                "an approach here**",
                "check the proof it emits",
                "**Make no performance claim.**",
                "Leave elaphros's own documents alone",
                "**Leave the work staged and not committed**",
                "create branch `ai-elaphros-e3-claude` from the current HEAD"):
            self.assertIn(asked, flat)
        self.assertNotIn("heuresis", preview.stdout)
        self.assertEqual(self.run_command("elaphros", "E3", "--show-prompt").stdout,
                         preview.stdout)
        # A heuresis direction is not an elaphros one.
        self.assertEqual(self.run_command("elaphros", "R3", "--show-prompt").returncode, 2)
        codex = self.run_command("elaphros", "3", "--codex", "--show-prompt")
        self.assertIn("create branch `ai-elaphros-e3-codex` from", " ".join(codex.stdout.split()))
        launched = self.run_command("elaphros", "3", "--print")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        self.assertEqual(json.loads(launched.stdout)["args"], ["-p", preview.stdout])
        self.assertIn("E3 on ai-elaphros-e3-claude", launched.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_metagraphe_rechecks_the_record_before_implementing_it(self):
        """A filed candidate was observed on an older cvc5, so availability and
        validity are established again before any code, and the run implements
        the record's schemas rather than inventing an approach.

        The other refusals are the ones a rewrite invites: a condition only
        known during search is not a rewrite, and a rule that adds a trusted
        step to proofs has moved a cost rather than removed one.
        """
        self.make_cvc5()
        before = self.snapshot()
        preview = self.run_command("metagraphe", "25", "--show-prompt")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        flat = " ".join(preview.stdout.split())
        for asked in (
                "tools/metagraphe/rewrite_db/rewrites.json",
                "Implement candidate M-25 of metagraphe's rewrite database",
                "record `metagraphe:M-25` whole",
                "**Establish before writing any code, and say the result in your "
                "response**",
                "reproduce the record's own availability command at this HEAD",
                "is not a rewrite and stops that schema",
                "proof production gains no trusted step",
                "Implement the record's schemas and nothing else",
                "**Make no performance claim.**",
                "Leave metagraphe's own documents alone",
                "**Leave the work staged and not committed**",
                "create branch `ai-metagraphe-m25-claude` from the current HEAD"):
            self.assertIn(asked, flat)
        self.assertNotIn("direction", preview.stdout)
        for spelled in ("M25", "M-25", "m-25"):
            with self.subTest(spelled=spelled):
                self.assertEqual(self.run_command("metagraphe", spelled,
                                                  "--show-prompt").stdout, preview.stdout)
        for wrong in ("M--25", "R25", "M0"):
            with self.subTest(wrong=wrong):
                self.assertEqual(self.run_command("metagraphe", wrong,
                                                  "--show-prompt").returncode, 2)
        codex = self.run_command("metagraphe", "25", "--codex", "--show-prompt")
        self.assertIn("create branch `ai-metagraphe-m25-codex` from",
                      " ".join(codex.stdout.split()))
        launched = self.run_command("metagraphe", "25", "--print")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        self.assertEqual(json.loads(launched.stdout)["args"], ["-p", preview.stdout])
        self.assertIn("M-25 on ai-metagraphe-m25-claude", launched.stderr)
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
