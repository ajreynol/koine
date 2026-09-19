#!/usr/bin/env python3
"""Topic selection, discovery and read-only output in temporary repositories.

    python3 tests/test_listen.py

No assistant or network is used. Installed copies run with only Python and
Git on PATH, and snapshots check that every repository stays unchanged.
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

    def discussion(self, path, text=None):
        (path / "docs").mkdir(exist_ok=True)
        (path / "docs/discussion.md").write_text(
            text if text is not None else
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

    def test_discovery_and_coverage(self):
        sender = self.repo(self.here.parent / "sender")
        self.discussion(sender)
        self.commit(sender)
        with (sender / "docs/discussion.md").open("a", encoding="utf-8") as file:
            file.write("\nLocal draft\n")
        duplicate = self.repo(self.root / "extra/sender")
        home_sender = self.repo(self.home / "home-sender")
        mapped = self.repo(self.root / "distant/mapped checkout")
        ignored = self.repo(self.here.parent / "unregistered")
        child = self.repo(self.here.parent / "child")
        for path in (duplicate, home_sender, mapped, ignored, child):
            self.discussion(path)
        office = self.office({
            "sender": {"status": "member"}, "home-sender": {"status": "associate"},
            "mapped": {"status": "member"}, "missing": {"status": "member"},
            "child": {"status": "child", "parent": "sender"},
        })
        (office / "scripts/repos.local").write_text(f"mapped {mapped}\nchild {sender}\n",
                                                    encoding="utf-8")
        subdir = self.here / "subdirectory"
        subdir.mkdir()
        out = self.listen(cwd=subdir, env={"ANOIEU_REPOS": str(duplicate.parent)})
        text = out.stdout
        for path in (sender, duplicate, home_sender, mapped):
            self.assertIn(str(path), text)
        self.assertNotIn(str(ignored), text)
        self.assertNotIn(str(child), text)
        self.assertIn("4 topic(s) addressed to current", out.stderr)
        self.assertIn("Local draft", text)
        self.assertIn("Not checked out: missing", out.stderr)
        self.assertNotIn("Not checked out: child", out.stderr)
        self.assertIn(f"No discussion file: {office / 'docs/discussion.md'}", out.stderr)
        self.assertIn(str(sender / "docs/discussion.md"), text)

    def test_identity_from_map_and_remote(self):
        office = self.office({"sender": {"status": "member", "url": "https://example.invalid/org/sender"}})
        sender = self.repo(self.here.parent / "renamed")
        self.discussion(sender)
        self.git(sender, "remote", "add", "origin", "git@example.invalid:org/sender.git")
        text = self.listen().stdout
        self.assertIn(f"# sender — {sender}", text)
        renamed = self.here.with_name("renamed-current")
        self.here.rename(renamed)
        self.here = renamed
        (office / "scripts/repos.local").write_text(f"current {self.here}\n", encoding="utf-8")
        out = self.listen()
        self.assertIn("## D7 — An incoming question", out.stdout)
        self.assertIn("1 topic(s) addressed to current", out.stderr)

    def test_explicit_map_and_missing_path(self):
        self.office({"sender": {"status": "member"}, "missing": {"status": "member"}})
        sender = self.repo(self.root / "distant/renamed")
        self.discussion(sender)
        mapping = self.root / "alternate map"
        mapping.write_text(f"sender {sender}\nmissing {self.root / 'absent'}\n", encoding="utf-8")
        out = self.listen(env={"ANOIEU_REPOS_FILE": str(mapping)})
        self.assertIn(f"# sender — {sender}", out.stdout)
        self.assertIn("Mapped checkout unavailable: missing", out.stderr)
        self.assertIn("Not checked out: missing", out.stderr)

    def test_without_register_or_git_repository(self):
        out = self.listen()
        self.assertIn("No topics addressed to current", out.stdout)
        self.assertIn("No register found", out.stderr)
        self.assertIn("coverage and missing repositories are unknown", out.stderr)
        self.assertIn("No other tool of this ecosystem is checked out", out.stderr)
        self.assertIn("read 0 discussion file(s)", out.stderr)
        self.discussion(self.repo(self.here.parent / "sender"))
        self.assertIn("## D7 — An incoming question", self.listen().stdout)
        bare = self.home / "not-a-repository"
        bare.mkdir()
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
        self.discussion(sender)
        unrelated = self.repo(self.here.parent / "unregistered")
        mapping = self.root / "alternate map"
        mapping.write_text(f"office {moved}\nsender {sender}\n", encoding="utf-8")
        out = self.listen(env={"ANOIEU_REPOS_FILE": str(mapping)})
        self.assertIn(f"Register: {moved / 'scripts/ecosystem/ecosystem.json'}", out.stderr)
        self.assertIn(f"# sender — {sender}", out.stdout)
        self.assertIn("Not checked out: missing", out.stderr)
        self.assertNotIn(str(unrelated), out.stdout)
        self.assertNotIn("No register found", out.stderr)

    def test_installed_program_needs_no_agent_and_changes_nothing(self):
        sender = self.repo(self.here.parent / "sender")
        self.discussion(sender)
        self.office({"sender": {"status": "member"}})
        self.discussion(self.here)
        self.git(self.here, "add", "docs/discussion.md")
        (self.here / "README.md").write_text("Unstaged changes\n", encoding="utf-8")
        (self.here / "discussion-response.local.md").write_text("A draft\n", encoding="utf-8")
        bindir = self.root / "bin"
        bindir.mkdir()
        (bindir / "python3").symlink_to(sys.executable)
        (bindir / "git").symlink_to(shutil.which("git"))
        self.env["PATH"] = str(bindir)
        installed = bindir / "eo_listen"
        shutil.copy2(COMMAND, installed)
        before = {p: self.snapshot(p) for p in (self.here, sender)}
        # A hostile inherited Git environment must not redirect observations.
        env = {"GIT_DIR": str(sender / ".git"), "GIT_WORK_TREE": str(sender)}
        out = self.listen(command=installed, env=env)
        topic = (sender / "docs/discussion.md").read_text(encoding="utf-8")
        self.assertEqual(out.stdout, f"# sender — {sender / 'docs/discussion.md'}:1\n\n{topic}")
        self.assertNotIn("A draft", out.stdout)
        self.assertNotIn(f"# current — {self.here}", out.stdout)
        self.assertEqual(self.listen(command=installed, env=env).stdout, out.stdout)
        for path, snapshot in before.items():
            self.assertEqual(self.snapshot(path), snapshot)

    def test_only_opening_recipients_select_complete_topics(self):
        sender = self.repo(self.here.parent / "sender")
        prefix = ("# Discussion\n\n> ## D90 — Quoted example\n> **To:** current\n\n"
                  "````markdown\n## D91 — Fenced example\n**To:** current\n"
                  "```\n## D92 — Still inside the longer fence\n**To:** current\n````\n\n"
                  "~~~markdown\n## D93 — Tilde example\n**To:** current\n~~~\n\n")
        first = ("## D7 — Keep the whole topic\n\n**To:** second, current\n"
                 "**Kind:** question\n**Opened:** 2026-09-18\n"
                 "**Settles when:** we agree\n\nThe original request.\n\n"
                 "### Replies\n\n**current, 2026-09-18.** Already answered.\n\n"
                 "```markdown\n## D94 — An example inside the topic\n**To:** other\n```\n")
        excluded = ("\n## Notes\nThis is not part of D7.\n\n"
                    "## D8 — A different recipient\n\n**To:** currently, not-current\n"
                    "\nThis mentions current.\n\n### Replies\n\n**To:** current\n\n"
                    "## D9 — Late address\n\nSome body text.\n**To:** current\n\n"
                    "## D10suffix — Not a topic ID\n\n**To:** current\n\n")
        second = "## D11 — Plain field\n\nTo: current\n\nA second request."
        source = prefix + first + excluded + second
        self.discussion(sender, source)
        out = self.listen()
        path = sender / "docs/discussion.md"
        first_line = source[:source.index(first)].count("\n") + 1
        second_line = source[:source.index(second)].count("\n") + 1
        self.assertEqual(out.stdout,
                         f"# sender — {path}:{first_line}\n\n{first}\n"
                         f"# sender — {path}:{second_line}\n\n{second}\n")
        self.assertIn("2 topic(s) addressed to current", out.stderr)

    def test_empty_results_and_read_failures(self):
        sender = self.repo(self.here.parent / "sender")
        self.discussion(sender, "## D1 — Not ours\n\n**To:** another\n")
        out = self.listen()
        self.assertEqual(out.stdout, "No topics addressed to current in the discussion files read.\n")
        self.assertIn("read 1 discussion file(s)", out.stderr)
        good = self.repo(self.here.parent / "good")
        self.discussion(good)
        (sender / "docs/discussion.md").write_bytes(b"\xff\xfe")
        out = self.listen(code=1)
        self.assertIn("Cannot read", out.stderr)
        self.assertIn(str(sender / "docs/discussion.md"), out.stderr)
        self.assertIn("## D7 — An incoming question", out.stdout)

    def test_prompt_options_are_not_supported(self):
        for flag in ("--show-prompt", "--print", "--codex", "--claude"):
            with self.subTest(flag=flag):
                out = self.listen(flag, code=2)
                self.assertIn("unrecognized arguments", out.stderr)
                self.assertEqual(out.stdout, "")

    def test_bad_register_refuses(self):
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
