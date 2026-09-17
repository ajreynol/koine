#!/usr/bin/env python3
"""Reading the register, and never writing to it.

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
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "eo_cmd", "eo_status")

_spec = importlib.util.spec_from_loader(
    "eo_status", importlib.machinery.SourceFileLoader("eo_status", SCRIPT))
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


def holder(tmp, entries):
    """A directory that holds the register, and is therefore the one to read."""
    root = os.path.join(tmp, "office")
    os.makedirs(os.path.join(root, "scripts", "ecosystem"))
    with open(os.path.join(root, kr.REGISTER), "w") as handle:
        json.dump(entries, handle)
    return root


def test_only_where_the_register_is():
    """The register is read in the tree that holds it, or not at all.

    Not a sibling checkout and not a clone at a pin. Those are copies, and a
    copy of *who is in this ecosystem* is true as of whenever it was taken --
    printed with the authority of the real thing and nothing in the output
    saying which it was. An earlier version of this module went looking in
    three places; refusing is the whole point of the rewrite.
    """
    print("only where the register is")
    tmp = tempfile.mkdtemp()
    try:
        root = holder(tmp, {"x": {"status": "member", "url": "u"}})
        ok("a tree with the register holds it", kr.holds_register(root))

        elsewhere = os.path.join(tmp, "elsewhere")
        os.makedirs(elsewhere)
        ok("a tree without it does not", not kr.holds_register(elsewhere))

        # A sibling that *does* hold one must not rescue a run started elsewhere.
        try:
            kr.require(elsewhere)
            ok("reading elsewhere refuses", False)
        except SystemExit as exc:
            ok("reading elsewhere refuses", True)
            ok("and says where to stand", "Run it at the root" in str(exc))
            ok("and does not offer to go looking", "clone" not in str(exc).lower())
    finally:
        shutil.rmtree(tmp)


def test_reading_and_never_writing():
    print("reading, and never writing")
    tmp = tempfile.mkdtemp()
    try:
        root = holder(tmp, {
            "a": {"status": "member", "url": "https://x/a"},
            "b": {"status": "child", "parent": "a"},
            "footings": ["prose, not a tool"],
        })
        before = os.stat(os.path.join(root, kr.REGISTER)).st_mtime_ns
        data, provenance = kr.require(root)
        ok("a live read says so", provenance.startswith("live"))
        check("prose is not an entry", sorted(n for n, _ in kr.entries(data)), ["a", "b"])
        check("a well-formed register has no problems", kr.problems(data), [])
        check("the file was not written to",
              os.stat(os.path.join(root, kr.REGISTER)).st_mtime_ns, before)
        check("a missing checkouts.json is empty rather than fatal",
              kr.checkouts(root), {})
    finally:
        shutil.rmtree(tmp)


def test_what_check_reports():
    """Facts about the file, never opinions about who should hold what."""
    print("what --check reports")
    tmp = tempfile.mkdtemp()
    try:
        root = holder(tmp, {
            "a": {"status": "member", "url": "https://x/same"},
            "b": {"status": "member", "url": "https://x/same"},
            "c": {"status": "sovereign", "url": "https://x/c"},
            "d": {"status": "member"},
            "e": {"status": "child"},
        })
        bad = " | ".join(kr.problems(kr.require(root)[0]))
        ok("an undefined footing is named", "not one the policy defines" in bad)
        ok("a missing url is named", "no url" in bad)
        ok("a child with no parent is named", "records no parent" in bad)
        ok("two entries claiming one repository is named", "also claims" in bad)
        ok("but no opinion about who should hold what",
           "should" not in bad and "wrong footing" not in bad)
    finally:
        shutil.rmtree(tmp)


def test_against_the_real_register():
    """Read-only assertions against kanon beside this one, when it is there."""
    print("against the register beside this one, if it is there")
    beside = os.path.join(os.path.dirname(ROOT), "kanon")
    if not kr.holds_register(beside):
        print("  --   no register beside this one; skipped")
        return
    data, provenance = kr.require(beside)
    ok("reading the tree that holds it is live", "live" in provenance)
    ok("it reads", len(kr.entries(data)) > 5)
    footings = {e["status"] for _, e in kr.entries(data)}
    ok("every footing is one the policy defines", footings <= kr.FOOTINGS)
    ok("koine is in it", "koine" in dict(kr.entries(data)))


def main():
    for test in (test_only_where_the_register_is, test_reading_and_never_writing,
                 test_what_check_reports, test_against_the_real_register):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
