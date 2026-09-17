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

        check("--show reports and changes nothing", run(repo, "--show"),
              bump.ADOPT)
        check("and the pin is untouched", bump.read_pin(lock), "a" * 40)

        check("a red check refuses", run(repo, answer=(False, "red")),
              bump.REFUSED)
        check("and the pin stays", bump.read_pin(lock), "a" * 40)

        # Refused under its own code: somebody was asked and said no, and
        # nobody could be asked, are different facts to whatever wrapped this.
        check("an unknown check refuses too",
              run(repo, answer=(None, "no network")), bump.UNVERIFIED)
        check("and the pin stays", bump.read_pin(lock), "a" * 40)

        check("a dry run on green writes nothing",
              run(repo, "--dry-run", answer=(True, "green")), bump.ADOPT)
        check("and the pin stays", bump.read_pin(lock), "a" * 40)

        check("green moves it", run(repo, answer=(True, "green")),
              bump.ADOPT)
        check("to the upstream tip", bump.read_pin(lock), tip)
        ok("keeping the reason", "a reason" in open(lock).read())

        check("a second run has nothing to do",
              run(repo, answer=(True, "green")), bump.ADOPT)
    finally:
        shutil.rmtree(tmp)


def test_force_is_the_only_way_past():
    print("--force")
    tmp = tempfile.mkdtemp()
    try:
        repo, up, first, tip = sandbox(tmp, "a" * 40)
        lock = os.path.join(repo, "dep.lock")
        check("--force moves a red pin",
              run(repo, "--force", answer=(False, "red")), bump.ADOPT)
        check("and it moved", bump.read_pin(lock), tip)
    finally:
        shutil.rmtree(tmp)


def test_the_four_exit_codes():
    """*Asked and told no* and *could not ask* must not be the same number.

    The whole claim this command makes is that unknown is not green. A caller
    logging one number for both cannot act on the distinction, which puts it
    back where it was before the command existed.
    """
    print("what a run's exit code says")
    tmp = tempfile.mkdtemp()
    try:
        repo, up, first, tip = sandbox(tmp, "a" * 40)
        check("green is adopt", run(repo, "--check", answer=(True, "g")),
              bump.ADOPT)
        check("red is refused", run(repo, "--check", answer=(False, "r")),
              bump.REFUSED)
        check("unknown is its own code",
              run(repo, "--check", answer=(None, "no network")), bump.UNVERIFIED)
        ok("and they are three different numbers",
           len({bump.ADOPT, bump.REFUSED, bump.UNVERIFIED}) == 3)

        # An upstream that cannot be read is a thing nobody was asked about,
        # not a check that came back red.
        json.dump({"pin": {"file": "dep.lock"},
                   "upstream": {"url": "https://example.invalid/x",
                                "ref": "main"},
                   "green": {"workflow": "policy"}},
                  open(os.path.join(repo, "eo_bump.json"), "w"))
        check("an unreadable upstream is unverified, not refused",
              run(repo, "--check", answer=(True, "g")), bump.UNVERIFIED)
    finally:
        shutil.rmtree(tmp)

    print("no configuration")
    tmp = tempfile.mkdtemp()
    try:
        check("refuses with an exit code of its own", run(tmp),
              bump.CANNOT_RUN)
        ok("which is not one of the three answers about a commit",
           bump.CANNOT_RUN not in (bump.ADOPT, bump.REFUSED, bump.UNVERIFIED))
    finally:
        shutil.rmtree(tmp)


def test_a_json_lock():
    """A lock with a ref and a date beside the commit keeps them."""
    print("a lock that is JSON")
    tmp = tempfile.mkdtemp()
    try:
        up, first, tip = build_upstream(tmp)
        repo = os.path.join(tmp, "repo")
        os.makedirs(os.path.join(repo, "scripts"))
        lock = os.path.join(repo, "scripts", "deps.lock")
        json.dump({"_comment": "moved by a run, not by hand",
                   "anoieu": {"ref": "main", "commit": "a" * 40,
                              "date": "2026-01-01"}},
                  open(lock, "w"), indent=2)
        json.dump({"pin": {"file": "scripts/deps.lock", "json": "anoieu.commit",
                           "date": "anoieu.date"},
                   "upstream": {"url": "https://example.invalid/x", "ref": "main",
                                "local": up},
                   "green": {"workflow": "policy"}},
                  open(os.path.join(repo, "eo_bump.json"), "w"))

        check("the commit is read out of the named field",
              bump.read_pin(lock, "anoieu.commit"), "a" * 40)
        check("green moves it", run(repo, answer=(True, "green")), bump.ADOPT)
        after = json.load(open(lock))
        check("the field is moved", after["anoieu"]["commit"], tip)
        check("the ref beside it is untouched", after["anoieu"]["ref"], "main")
        check("the comment beside it is untouched", after["_comment"],
              "moved by a run, not by hand")
        ok("and the date is stamped", after["anoieu"]["date"] != "2026-01-01")

        bad = os.path.join(repo, "scripts", "empty.lock")
        json.dump({"anoieu": {"ref": "main"}}, open(bad, "w"))
        cfg = json.load(open(os.path.join(repo, "eo_bump.json")))
        cfg["pin"]["file"] = "scripts/empty.lock"
        json.dump(cfg, open(os.path.join(repo, "eo_bump.json"), "w"))
        check("a named field that is not there refuses rather than guessing",
              run(repo, answer=(True, "green")), bump.CANNOT_RUN)
    finally:
        shutil.rmtree(tmp)


def test_a_consumer_may_veto():
    """Green upstream and workable here are separate questions."""
    print("this repository's own check on the candidate")
    tmp = tempfile.mkdtemp()
    try:
        repo, up, first, tip = sandbox(tmp, "a" * 40)
        lock = os.path.join(repo, "dep.lock")
        probe = os.path.join(repo, "compat")
        open(probe, "w").write(
            "#!/bin/sh\necho \"$1\" > seen\n[ -f allow ] && exit 0\n"
            "echo 'the pinned checker fails on this tree' >&2\nexit 1\n")
        os.chmod(probe, 0o755)
        cfg = json.load(open(os.path.join(repo, "eo_bump.json")))
        cfg["verify"] = {"command": ["./compat", "{commit}"],
                         "what": "the pinned checker still passes here"}
        json.dump(cfg, open(os.path.join(repo, "eo_bump.json"), "w"))

        check("a veto refuses even on green",
              run(repo, answer=(True, "green")), bump.REFUSED)
        check("and the pin stays", bump.read_pin(lock), "a" * 40)
        check("the candidate commit is what it was asked about",
              open(os.path.join(repo, "seen")).read().strip(), tip)

        open(os.path.join(repo, "allow"), "w").write("")
        check("and it moves once the veto is lifted",
              run(repo, answer=(True, "green")), bump.ADOPT)
        check("to the upstream tip", bump.read_pin(lock), tip)
    finally:
        shutil.rmtree(tmp)


def main():
    for test in (test_reading_a_lock, test_the_refusal,
                 test_force_is_the_only_way_past, test_the_four_exit_codes,
                 test_a_json_lock, test_a_consumer_may_veto):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
