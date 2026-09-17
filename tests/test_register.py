#!/usr/bin/env python3
"""Finding kanon's register, and never writing to it.

    python3 tests/test_register.py

kanon keeps the register and koine keeps the programs that read it, so the
property worth testing is the boundary: that a directory is only accepted as
kanon when it actually holds the register, that what comes back says which
checkout and which commit it came from, and that nothing here writes.

The locator is tested against directories built here. The live checkout beside
this one is used only for the read-only assertions, and skipped when absent.
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
SCRIPT = os.path.join(ROOT, "scripts", "koine_register.py")

_spec = importlib.util.spec_from_loader(
    "koine_register", importlib.machinery.SourceFileLoader("koine_register", SCRIPT))
kr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kr)

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


def fake_kanon(tmp, entries):
    """A directory that is kanon, because it holds the register."""
    root = os.path.join(tmp, "kanon")
    os.makedirs(os.path.join(root, "scripts", "ecosystem"))
    with open(os.path.join(root, kr.REGISTER), "w") as handle:
        json.dump(entries, handle)
    return root


def test_what_counts_as_kanon():
    print("what counts as kanon")
    tmp = tempfile.mkdtemp()
    try:
        ok("a directory with the register is kanon",
           kr._is_kanon(fake_kanon(tmp, {})))
        empty = os.path.join(tmp, "empty")
        os.makedirs(empty)
        ok("a directory without it is not, whatever it is called",
           not kr._is_kanon(empty))
        ok("and neither is nothing at all", not kr._is_kanon(""))
    finally:
        shutil.rmtree(tmp)


def test_the_pin():
    print("the pin")
    commit = kr.pinned()
    ok("kanon.lock names a commit", len(commit) >= 7)
    ok("and it is not a branch name", all(c in "0123456789abcdef" for c in commit))


def test_env_wins_and_nothing_is_written():
    print("$KANON, and that reading is all this does")
    tmp = tempfile.mkdtemp()
    try:
        root = fake_kanon(tmp, {"x": {"status": "member"}, "note": "not a dict"})
        before = os.stat(os.path.join(root, kr.REGISTER)).st_mtime_ns
        os.environ["KANON"] = root
        try:
            check("$KANON is used", kr.find(clone=False), root)
            data, note = kr.register(clone=False)
            check("the register is read", data["x"]["status"], "member")
            ok("the note says where it came from", root in note)
            check("entries without a status are not footings",
                  kr.members(clone=False), {"x": "member"})
            check("a missing checkouts.json is empty rather than fatal",
                  kr.checkouts(clone=False), {})
        finally:
            del os.environ["KANON"]
        after = os.stat(os.path.join(root, kr.REGISTER)).st_mtime_ns
        check("the register was not written to", after, before)
    finally:
        shutil.rmtree(tmp)


def test_refuses_rather_than_guessing():
    print("when kanon is not here")
    tmp = tempfile.mkdtemp()
    try:
        os.environ["KANON"] = os.path.join(tmp, "nothing")
        real_clone, kr.CLONE = kr.CLONE, os.path.join(tmp, "deps", "kanon")
        real_root = kr.ROOT
        kr.ROOT = os.path.join(tmp, "koine")
        try:
            try:
                kr.find(clone=False)
                ok("it refuses rather than guessing", False)
            except SystemExit as exc:
                ok("it refuses rather than guessing", True)
                ok("and says what would fix it", "$KANON" in str(exc))
        finally:
            kr.CLONE, kr.ROOT = real_clone, real_root
            del os.environ["KANON"]
    finally:
        shutil.rmtree(tmp)


def test_against_the_real_checkout():
    """Read-only assertions against kanon beside this one, when it is there."""
    print("against the checkout beside this one, if it is there")
    beside = os.path.join(os.path.dirname(ROOT), "kanon")
    if not kr._is_kanon(beside):
        print("  --   no kanon checkout beside this one; skipped")
        return
    data, note = kr.register(clone=False)
    ok("the register reads", isinstance(data, dict) and len(data) > 5)
    ok("the note names the checkout", beside in note)
    footings = set(kr.members(clone=False).values())
    ok("every footing is one the policy defines",
       footings <= {"member", "associate", "candidate", "foundation",
                    "president", "child", "outsider"})


def main():
    for test in (test_what_counts_as_kanon, test_the_pin,
                 test_env_wins_and_nothing_is_written,
                 test_refuses_rather_than_guessing,
                 test_against_the_real_checkout):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
