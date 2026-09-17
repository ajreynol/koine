#!/usr/bin/env python3
"""eo_bump, against locks and repositories built here.

    python3 tests/test_bump.py

The property worth testing is the refusal. A pin that moves onto a commit
nobody checked is the failure this command exists to prevent, and the two ways
it happens are a red check and **a check whose state could not be established**.
The second is the subtle one: unknown is not green, and a command that treated
it as green would be worse than no command, because the lock would then read as
evidence it is not.

No network: the upstream is a git repository made in a temporary directory, and
the CI answer is stubbed.
"""

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "eo_cmd", "eo_bump")

_spec = importlib.util.spec_from_loader(
    "eo_bump", importlib.machinery.SourceFileLoader("eo_bump", SCRIPT))
bump = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bump)

FAILS = 0


def check(name, got, want):
    global FAILS
    if got == want:
        print(f"  ok   {name}")
        return
    FAILS += 1
    print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")


def ok(name, condition):
    check(name, bool(condition), True)


LOCK = """# why this pin is here, and a reason somebody wrote down
#
# a second comment line
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
"""


def test_reading_a_lock():
    print("reading and writing a lock")
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "dep.lock")
        open(path, "w").write(LOCK)
        check("the commit is the first non-comment line",
              bump.read_pin(path), "a" * 40)

        bump.write_pin(path, "b" * 40)
        after = open(path).read()
        check("the new commit is written", bump.read_pin(path), "b" * 40)
        ok("the reasoning is kept",
           "why this pin is here" in after and "a second comment" in after)
        check("and nothing else moved", after.count("\n"), LOCK.count("\n"))

        # A lock that is only comments still acquires a pin.
        bare = os.path.join(tmp, "bare.lock")
        open(bare, "w").write("# nothing pinned yet\n")
        bump.write_pin(bare, "c" * 40)
        check("a lock with no pin gains one", bump.read_pin(bare), "c" * 40)
        ok("keeping its comment", "nothing pinned yet" in open(bare).read())
    finally:
        shutil.rmtree(tmp)


def build_upstream(tmp):
    """A git repository with two commits, to stand in for the dependency."""
    up = os.path.join(tmp, "upstream")
    os.makedirs(up)
    run = lambda *a: subprocess.run(["git", "-C", up, *a], capture_output=True)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@example.invalid")
    run("config", "user.name", "t")
    for n in ("one", "two"):
        open(os.path.join(up, n), "w").write(n)
        run("add", "-A")
        run("commit", "-qm", n)
    first = subprocess.run(["git", "-C", up, "rev-list", "--max-parents=0", "HEAD"],
                           capture_output=True, text=True).stdout.strip()
    tip = subprocess.run(["git", "-C", up, "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    return up, first, tip


def sandbox(tmp, pin):
    up, first, tip = build_upstream(tmp)
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    open(os.path.join(repo, "dep.lock"), "w").write(f"# a reason\n{pin}\n")
    json.dump({"pin": {"file": "dep.lock"},
               "upstream": {"url": "https://example.invalid/x", "ref": "main",
                            "local": up},
               "green": {"workflow": "policy"}},
              open(os.path.join(repo, "eo_bump.json"), "w"))
    return repo, up, first, tip


def run(repo, *args, answer=None):
    """The command, with the CI answer stubbed to `answer`."""
    real = bump.green_at
    if answer is not None:
        bump.green_at = lambda *a, **k: answer
    argv = sys.argv
    sys.argv = ["eo_bump", "--root", repo, *args]
    try:
        return bump.main()
    finally:
        bump.green_at = real
        sys.argv = argv


def test_the_refusal():
    print("when the pin may move, and when it may not")
    tmp = tempfile.mkdtemp()
    try:
        repo, up, first, tip = sandbox(tmp, "a" * 40)
        lock = os.path.join(repo, "dep.lock")

        check("--show reports and changes nothing", run(repo, "--show"), 0)
        check("and the pin is untouched", bump.read_pin(lock), "a" * 40)

        check("a red check refuses", run(repo, answer=(False, "red")), 1)
        check("and the pin stays", bump.read_pin(lock), "a" * 40)

        check("an unknown check refuses", run(repo, answer=(None, "no network")), 1)
        check("and the pin stays", bump.read_pin(lock), "a" * 40)

        check("a dry run on green writes nothing",
              run(repo, "--dry-run", answer=(True, "green")), 0)
        check("and the pin stays", bump.read_pin(lock), "a" * 40)

        check("green moves it", run(repo, answer=(True, "green")), 0)
        check("to the upstream tip", bump.read_pin(lock), tip)
        ok("keeping the reason", "a reason" in open(lock).read())

        check("a second run has nothing to do", run(repo, answer=(True, "green")), 0)
    finally:
        shutil.rmtree(tmp)


def test_force_is_the_only_way_past():
    print("--force")
    tmp = tempfile.mkdtemp()
    try:
        repo, up, first, tip = sandbox(tmp, "a" * 40)
        lock = os.path.join(repo, "dep.lock")
        check("--force moves a red pin", run(repo, "--force", answer=(False, "red")), 0)
        check("and it moved", bump.read_pin(lock), tip)
    finally:
        shutil.rmtree(tmp)


def test_no_config():
    print("no configuration")
    tmp = tempfile.mkdtemp()
    try:
        check("refuses with an exit code of its own", run(tmp), 2)
    finally:
        shutil.rmtree(tmp)


def main():
    for test in (test_reading_a_lock, test_the_refusal,
                 test_force_is_the_only_way_past, test_no_config):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
