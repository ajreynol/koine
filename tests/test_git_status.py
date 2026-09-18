#!/usr/bin/env python3
"""Read-only status and bounded discovery against real, temporary Git trees.

    python3 tests/test_git_status.py

No network or neighboring ecosystem checkouts are needed. Every write stays
inside a temporary directory, including the standalone installed command.
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMMAND = ROOT / "eo_cmd/eo_git_status"


class GitStatusTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="koine-status-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        home = self.root / "home"
        home.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith("GIT_")}
        self.env.update(HOME=str(home), ANOIEU_REPOS="", ANOIEU_REPOS_FILE="",
                        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        LC_ALL="C")
        self.here = self.repo(self.root / "near/current")

    def git(self, path, *args, check=True):
        return subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "-C", str(path), *args],
            env=self.env, capture_output=True, text=True, check=check)

    def repo(self, path, commit=True):
        path.mkdir(parents=True)
        self.git(path, "init", "-q", "-b", "main")
        self.git(path, "config", "user.name", "Test")
        self.git(path, "config", "user.email", "test@example.invalid")
        if commit:
            (path / "file").write_text("initial\n")
            self.commit(path)
        return path

    def commit(self, path):
        self.git(path, "add", "-A")
        self.git(path, "commit", "-qm", "fixture")

    def office(self, entries, mapping=None):
        path = self.repo(self.here.parent / "kanon")
        register = path / "scripts/ecosystem/ecosystem.json"
        register.parent.mkdir(parents=True)
        register.write_text(json.dumps(entries))
        if mapping is not None:
            (path / "scripts/repos.local").write_text(mapping)
        return path

    def status(self, *args, cwd=None, env=None, code=0, command=COMMAND):
        result = subprocess.run(
            [sys.executable, str(command), *map(str, args)],
            cwd=cwd or self.here, env={**self.env, **(env or {})},
            capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def rows(self, result):
        rows = [re.split(r" {2,}", line) for line in result.stdout.splitlines()]
        return {Path(row[-1]): row[:-1] for row in rows
                if len(row) == 8 and row[0] != "REPOSITORY"}

    def test_discovery_maps_worktrees_and_duplicate_names(self):
        sibling = self.repo(self.here.parent / "sibling")
        home = self.repo(self.root / "home/home-repo")
        environment = self.repo(self.root / "environment/env-repo")
        extra = self.repo(self.root / "extra/extra-repo")
        duplicate = self.repo(self.root / "extra/sibling")
        hidden = self.repo(self.root / "extra/nested/deep-repo")
        mapped = self.repo(self.root / "elsewhere/mapped checkout")
        linked = self.root / "elsewhere/linked"
        self.git(mapped, "worktree", "add", "-qb", "feature", str(linked))
        office = self.office({
            name: {"status": "member"} for name in
            ("current", "sibling", "mapped", "missing")
        }, f"# checkout locations\nmapped {mapped}\n")
        (self.root / "extra/alias").symlink_to(mapped, target_is_directory=True)
        subdir = self.here / "subdir"
        subdir.mkdir()
        result = self.status(self.root / "extra", cwd=subdir,
                             env={"ANOIEU_REPOS": str(environment.parent)})
        rows = self.rows(result)
        self.assertEqual(set(rows), {self.here, sibling, home, environment, extra,
                                     duplicate, mapped, linked, office})
        self.assertNotIn(hidden, rows)
        self.assertEqual(rows[mapped][0], "mapped")
        self.assertEqual(rows[linked][:2], ["mapped", "feature"])
        self.assertIn("Not found in the searched locations: missing\n", result.stdout)

    def test_register_matching_and_explicit_locations(self):
        renamed = self.repo(self.root / "elsewhere/renamed")
        self.git(renamed, "remote", "add", "upstream", "git@example.invalid:org/tool.git")
        by_directory = self.repo(self.here.parent / "DDTool")
        outside = self.repo(self.root / "outside/mapped")
        child = {"status": "child", "parent": "current"}
        entries = {
            "remote-match": {"status": "member", "url": "https://example.invalid/org/tool"},
            "directory-match": {"status": "foundation", "repo": "ddtool"},
            "mapped-id": {"status": "member"},
            "absent": {"status": "associate"}, "child": child,
            "_metadata": ["not a repository"],
        }
        office = self.office(entries)
        mapping = self.root / "custom.local"
        mapping.write_text("mapped-id ../../outside/mapped\n")
        subdir = renamed / "subdir"
        subdir.mkdir()
        result = self.status(subdir, "--president", office, "--repos-file", mapping)
        rows = self.rows(result)
        self.assertEqual(rows[renamed][0], "remote-match")
        self.assertEqual(rows[by_directory][0], "directory-match")
        self.assertEqual(rows[outside][0], "mapped-id")
        self.assertIn("Not found in the searched locations: absent\n", result.stdout)
        self.assertIn(f"Register: {office}/scripts/ecosystem/ecosystem.json", result.stdout)
        via_env = self.status(subdir, env={"ANOIEU_REPOS_FILE": str(mapping)})
        self.assertEqual(self.rows(via_env), rows)

    def test_counts_rename_untracked_directory_and_unborn(self):
        # In -z output a rename has a second filename field. It is not another
        # status record even when that filename starts with '? '.
        (self.here / "? original").write_text("rename me\n")
        self.commit(self.here)
        self.git(self.here, "mv", "? original", "renamed")
        (self.here / "file").write_text("unstaged\n")
        (self.here / "untracked").mkdir()
        for name in ("one", "two"):
            (self.here / "untracked" / name).write_text(name)
        unborn = self.repo(self.here.parent / "unborn", commit=False)
        rows = self.rows(self.status())
        self.assertEqual(rows[self.here][1:], ["main", "1", "1", "1", "0", "—"])
        self.assertEqual(rows[unborn][1], "main (unborn)")

    def test_ahead_behind_detached_and_missing_upstream(self):
        self.git(self.here, "checkout", "-qb", "topic")
        (self.here / "topic").write_text("topic\n")
        self.commit(self.here)
        self.git(self.here, "checkout", "-q", "main")
        (self.here / "main").write_text("main\n")
        self.commit(self.here)
        self.git(self.here, "checkout", "-q", "topic")
        self.git(self.here, "branch", "--set-upstream-to=main")
        self.assertEqual(self.rows(self.status())[self.here][-1], "main +1/-1")
        self.git(self.here, "branch", "-D", "main")
        self.assertEqual(self.rows(self.status())[self.here][-1], "main (counts unavailable)")
        self.git(self.here, "checkout", "-q", "--detach")
        oid = self.git(self.here, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(self.rows(self.status())[self.here][1], f"detached:{oid[:8]}")

    def test_conflicts_are_counted_separately(self):
        self.git(self.here, "checkout", "-qb", "other")
        (self.here / "file").write_text("other\n")
        self.commit(self.here)
        self.git(self.here, "checkout", "-q", "main")
        (self.here / "file").write_text("main\n")
        self.commit(self.here)
        merge = self.git(self.here, "merge", "other", check=False)
        self.assertEqual(merge.returncode, 1)
        row = self.rows(self.status())[self.here]
        self.assertEqual(row[2:6], ["0", "0", "0", "1"])

    def test_no_index_branch_hook_or_fetch_changes(self):
        # A same-content timestamp change invites an index refresh. A normal
        # status also invokes the configured fsmonitor; our command must not.
        file = self.here / "file"
        os.utime(file, ns=(file.stat().st_atime_ns, file.stat().st_mtime_ns + 2_000_000_000))
        hook = self.here / ".git/monitor"
        hook.write_text("#!/bin/sh\ntouch .git/monitor-ran\nexit 1\n")
        hook.chmod(0o755)
        self.git(self.here, "config", "core.fsmonitor", str(hook))
        self.git(self.here, "remote", "add", "origin", str(self.root / "nonexistent-remote"))
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in (self.here / ".git").rglob("*") if path.is_file()}
        # Inherited variables must not redirect status to a caller's index.
        self.status(env={"GIT_DIR": str(self.root / "absent"),
                         "GIT_INDEX_FILE": str(self.root / "absent-index")})
        after = {path: (path.read_bytes(), path.stat().st_mtime_ns)
                 for path in (self.here / ".git").rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_failed_checkout_does_not_hide_other_rows(self):
        broken = self.repo(self.here.parent / "broken")
        (broken / ".git/index").write_bytes(b"not a Git index")
        result = self.status(code=1)
        rows = self.rows(result)
        self.assertEqual(rows[broken][1], "ERROR")
        self.assertEqual(rows[self.here][1], "main")
        self.assertIn(str(broken), result.stderr)

    def test_invalid_configuration_is_refused(self):
        self.office({"current": {"status": "member"}})
        bad_map = self.root / "bad.local"
        bad_map.write_text("one-field\n")
        for args in (("--president", self.root / "absent"),
                     ("--repos-file", self.root / "absent"),
                     ("--repos-file", bad_map), (self.root / "absent",),
                     ("--show-prompt",)):
            with self.subTest(args=args):
                result = self.status(*args, code=2)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr)

    def test_standalone_copy_without_a_register_or_checkouts(self):
        command = self.root / "bin/eo_git_status"
        command.parent.mkdir()
        shutil.copy2(COMMAND, command)
        result = self.status(command=command)
        self.assertEqual(set(self.rows(result)), {self.here})
        self.assertIn("No register found; missing-repository coverage is unavailable.",
                      result.stdout)
        empty = self.root / "empty"
        empty.mkdir()
        result = self.status(command=command, cwd=empty)
        self.assertIn("No local checkouts found in the searched locations.", result.stdout)


if __name__ == "__main__":
    unittest.main()
