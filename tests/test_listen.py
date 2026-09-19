#!/usr/bin/env python3
"""Discovery, coverage and read-only launches using temporary Git repositories.

    python3 tests/test_listen.py

Assistant stubs record argv; no real assistant or network is used. Summaries
are the assistant's judgement, while discovery and launch restrictions are
checked here against real checkouts, including an installed command.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMMAND = ROOT / "eo_cmd/eo_listen"


class ListenTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="koine listen ' ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith("GIT_")}
        self.env.update(HOME=str(self.home), ANOIEU_REPOS="", ANOIEU_REPOS_FILE="",
                        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        LC_ALL="C")
        self.here = self.repo(self.root / "near/current")

    def git(self, path, *args):
        return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-C", str(path), *args],
                              env=self.env, capture_output=True, text=True, check=True)

    def repo(self, path):
        path.mkdir(parents=True)
        self.git(path, "init", "-q", "-b", "feature")
        self.git(path, "config", "user.name", "Test")
        self.git(path, "config", "user.email", "test@example.invalid")
        (path / "README.md").write_text("# A tool\n", encoding="utf-8")
        self.commit(path)
        return path

    def commit(self, path):
        self.git(path, "add", "-A")
        self.git(path, "commit", "-qm", "fixture")

    def discussion(self, path):
        (path / "docs").mkdir(exist_ok=True)
        (path / "docs/discussion.md").write_text(
            "## D7 — An incoming question\n\n**To:** current, second\n"
            "**Kind:** question\n**Opened:** 2026-09-18\n"
            "**Settles when:** a decision is made\n\nWhat should we do?\n",
            encoding="utf-8")

    def office(self, entries):
        office = self.repo(self.here.parent / "office")
        register = office / "scripts/ecosystem/ecosystem.json"
        register.parent.mkdir(parents=True)
        data = {"office": {"status": "president"}, "current": {"status": "member"}, **entries}
        register.write_text(json.dumps(data), encoding="utf-8")
        return office

    def listen(self, *args, cwd=None, env=None, code=0, command=COMMAND):
        result = subprocess.run([str(command), *args], cwd=cwd or self.here,
                                env={**self.env, **(env or {})}, capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def snapshot(self, path):
        # Include .git/index, HEAD and refs, and untracked working files.
        return {str(p.relative_to(path)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in path.rglob("*") if p.is_file()}

    def stub_agents(self):
        bindir = self.root / "bin"
        bindir.mkdir()
        for name in ("claude", "codex"):
            path = bindir / name
            path.write_text(f"#!{sys.executable}\nimport json, os, sys\n"
                            "print(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()}))\n",
                            encoding="utf-8")
            path.chmod(0o755)
        self.env["PATH"] = str(bindir) + os.pathsep + self.env["PATH"]
        return bindir

    def test_discovery_and_coverage(self):
        sender = self.repo(self.here.parent / "sender")
        self.discussion(sender)
        self.commit(sender)
        revision = self.git(sender, "rev-parse", "HEAD").stdout.strip()
        (sender / "docs/discussion.md").write_text("Local draft\n", encoding="utf-8")
        duplicate = self.repo(self.root / "extra/sender")
        home_sender = self.repo(self.home / "home-sender")
        mapped = self.repo(self.root / "distant/mapped checkout")
        ignored = self.repo(self.here.parent / "unregistered")
        child = self.repo(self.here.parent / "child")
        office = self.office({
            "sender": {"status": "member"}, "home-sender": {"status": "associate"},
            "mapped": {"status": "member"}, "missing": {"status": "member"},
            "child": {"status": "child", "parent": "sender"},
        })
        (office / "scripts/repos.local").write_text(f"mapped {mapped}\nchild {sender}\n",
                                                    encoding="utf-8")
        subdir = self.here / "subdirectory"
        subdir.mkdir()
        text = self.listen("--show-prompt", cwd=subdir,
                           env={"ANOIEU_REPOS": str(duplicate.parent)}).stdout
        for path in (sender, duplicate, home_sender, mapped):
            self.assertIn(str(path), text)
        self.assertNotIn(str(ignored), text)
        self.assertNotIn(str(child), text)
        self.assertIn("discussion addressed to **current**", text)
        self.assertIn(revision + "; working tree: dirty", text)
        self.assertIn("Not checked out: missing", text)
        self.assertNotIn("Not checked out: child", text)
        self.assertIn("Discussion: no docs/discussion.md", text)
        self.assertIn(str(sender / "docs/discussion.md"), text)
        self.assertIn(str(office / "docs/policy.md"), text)

    def test_identity_from_map_and_remote(self):
        office = self.office({"sender": {"status": "member", "url": "https://example.invalid/org/sender"}})
        sender = self.repo(self.here.parent / "renamed")
        self.git(sender, "remote", "add", "origin", "git@example.invalid:org/sender.git")
        text = self.listen("--show-prompt").stdout
        self.assertIn(f"- sender: {sender}", text)
        renamed = self.here.with_name("renamed-current")
        self.here.rename(renamed)
        self.here = renamed
        (office / "scripts/repos.local").write_text(f"current {self.here}\n", encoding="utf-8")
        text = self.listen("--show-prompt").stdout
        self.assertIn("discussion addressed to **current**", text)

    def test_explicit_map_and_missing_path(self):
        self.office({"sender": {"status": "member"}, "missing": {"status": "member"}})
        sender = self.repo(self.root / "distant/renamed")
        mapping = self.root / "alternate map"
        mapping.write_text(f"sender {sender}\nmissing {self.root / 'absent'}\n", encoding="utf-8")
        text = self.listen("--show-prompt", env={"ANOIEU_REPOS_FILE": str(mapping)}).stdout
        self.assertIn(f"- sender: {sender}", text)
        self.assertIn("Mapped checkout unavailable: missing", text)
        self.assertIn("Not checked out: missing", text)

    def test_preview_without_register_or_git_repository(self):
        text = self.listen("--show-prompt").stdout
        self.assertIn("No register found", text)
        self.assertIn("coverage and missing repositories are unknown", text)
        self.assertIn("No other tool of this ecosystem is checked out", text)
        bare = self.home / "not-a-repository"
        bare.mkdir()
        self.listen("--show-prompt", cwd=bare)
        result = self.listen(cwd=bare, code=2)
        self.assertIn("not in a git repository", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_explicit_map_can_locate_the_register(self):
        office = self.office({"sender": {"status": "member"}, "missing": {"status": "member"}})
        distant = self.root / "distant"
        distant.mkdir()
        moved = distant / "office"
        office.rename(moved)
        sender = self.repo(distant / "sender")
        unrelated = self.repo(self.here.parent / "unregistered")
        mapping = self.root / "alternate map"
        mapping.write_text(f"office {moved}\nsender {sender}\n", encoding="utf-8")
        text = self.listen("--show-prompt", env={"ANOIEU_REPOS_FILE": str(mapping)}).stdout
        self.assertIn(f"Register: {moved / 'scripts/ecosystem/ecosystem.json'}", text)
        self.assertIn(f"- sender: {sender}", text)
        self.assertIn("Not checked out: missing", text)
        self.assertNotIn(str(unrelated), text)
        self.assertNotIn("No register found", text)

    def test_installed_launches_are_read_only_and_receive_exact_preview(self):
        sender = self.repo(self.here.parent / "sender")
        self.discussion(sender)
        self.office({"sender": {"status": "member"}})
        self.discussion(self.here)
        self.git(self.here, "add", "docs/discussion.md")
        (self.here / "README.md").write_text("Unstaged changes\n", encoding="utf-8")
        (self.here / "discussion-response.local.md").write_text("A draft\n", encoding="utf-8")
        bindir = self.stub_agents()
        installed = bindir / "eo_listen"
        shutil.copy2(COMMAND, installed)
        before = {p: self.snapshot(p) for p in (self.here, sender)}
        # A hostile inherited Git environment must not redirect observations.
        env = {"GIT_DIR": str(sender / ".git"), "GIT_WORK_TREE": str(sender)}
        preview = self.listen("--show-prompt", command=installed, env=env).stdout
        for agent in ("claude", "codex"):
            for printing in (False, True):
                with self.subTest(agent=agent, printing=printing):
                    flags = ["--" + agent] + (["--print"] if printing else [])
                    out = self.listen(*flags, command=installed, env=env)
                    call = json.loads(out.stdout)
                    self.assertEqual(call["cwd"], str(self.here))
                    self.assertEqual(call["argv"][-2:], ["--", preview])
                    if agent == "codex":
                        expected = ["--sandbox", "read-only", "--ask-for-approval", "never"]
                        if printing:
                            expected.append("exec")
                    else:
                        expected = ["--tools", "Read,Glob,Grep"]
                        if printing:
                            expected.append("--print")
                    self.assertEqual(call["argv"][:-2], expected)
        for path, snapshot in before.items():
            self.assertEqual(self.snapshot(path), snapshot)
        flat = " ".join(preview.split())
        self.assertIn("opening `To:` field", flat)
        self.assertIn("complete recipient name", flat)
        self.assertIn("discussion-response.local.md", flat)
        self.assertIn("distinguish a draft", flat)
        self.assertIn("Do not answer or implement", flat)
        self.assertIn("Do not fetch, pull, switch branches", flat)
        self.assertIn("including reports", flat)
        self.assertIn("unavailable sources are not evidence of an empty inbox", flat)

    def test_bad_register_refuses_before_assistant(self):
        self.stub_agents()
        office = self.office({})
        register = office / "scripts/ecosystem/ecosystem.json"
        for data in ("{broken", "[]", '{"current": {"status": "member"}}'):
            with self.subTest(data=data):
                register.write_text(data, encoding="utf-8")
                result = self.listen(code=2)
                self.assertEqual(result.stdout, "")
                self.assertIn("eo_listen:", result.stderr)


if __name__ == "__main__":
    unittest.main()
