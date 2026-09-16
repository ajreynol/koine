#!/usr/bin/env python3
"""The signals, against a record built here rather than described.

    python3 test_epidosis.py

It builds a small git repository in a temporary directory, changes the record
in the ways `axes.md` names, and asserts what comes back. No network, no
checkout of anybody's tree, nothing left behind.

**It is not in koine's test suite and must not be.** This directory is an island
in that tree: nothing there imports it, nothing there runs it, and deleting the
directory changes nothing about what koine does. Run it by hand.
"""

import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epidosis  # noqa: E402

FAILS = 0

BANNER = "# The history\n\n> Nothing here about an outside project is theirs.\n"
S0 = "\n## Stretch 0 — Before us\n\nIt was quiet.\n"
S1 = "\n## Stretch 1 — Initialization\n\nWe started.\n"
S2 = "\n## Stretch 2 — not started\n\nNothing yet.\n"


def check(name, got, want):
    global FAILS
    if got == want:
        print(f"  ok   {name}")
        return
    FAILS += 1
    print(f"  FAIL {name}\n       want: {want!r}\n       got:  {got!r}")


def git(repo, *args):
    subprocess.run(("git", "-C", repo) + args, check=True,
                   capture_output=True, text=True)


def commit(repo, text, message):
    path = os.path.join(repo, "docs", "history.md")
    open(path, "w").write(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


def build(tmp):
    repo = os.path.join(tmp, "record")
    os.makedirs(os.path.join(repo, "docs"))
    git_init = ("init", "-q", "-b", "main")
    subprocess.run(("git", "-C", repo) + git_init, check=True, capture_output=True)
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "test")

    # 1. the record arrives
    commit(repo, BANNER + S0 + S1 + S2, "the record")
    # 2. the open stretch grows, with a figure and no way to re-derive it
    commit(repo, BANNER + S0 + S1 + "\nWe took 41 commits.\n" + S2,
           "a bare figure")
    # 3. the open stretch grows, with the evidence beside it
    commit(repo, BANNER + S0 + S1 + "\nWe took 41 commits.\n"
           + "\nCI was red for 112 runs, see 2026-09-02 in the run history.\n" + S2,
           "a figure with its evidence")
    # 4. an earlier stretch is changed, silently
    commit(repo, BANNER + "\n## Stretch 0 — Before us\n\nIt was busy.\n" + S1
           + "\nWe took 41 commits.\n"
           + "\nCI was red for 112 runs, see 2026-09-02 in the run history.\n" + S2,
           "quietly rewriting the past")
    # 5. a failure is removed, and a footing line with it
    commit(repo, BANNER + "\n## Stretch 0 — Before us\n\nIt was busy.\n" + S1
           + "\nWe took 41 commits.\n" + S2,
           "tidying")
    return repo


def main():
    tmp = tempfile.mkdtemp(prefix="epidosis-")
    try:
        repo = build(tmp)
        items = epidosis.changes(repo)

        print("reading a record:")
        check("every change is read", len(items), 5)
        check("oldest first", items[0].subject, "the record")

        print("\nthe signals:")
        bare, evid, past, tidy = items[1], items[2], items[3], items[4]
        check("a figure is noticed", "figures added" in bare.signals, True)
        check("a bare figure is called out",
              "figures unsupported" in bare.signals, True)
        check("a figure with a date beside it is not",
              "figures unsupported" in evid.signals, False)
        check("the open stretch is not an earlier one",
              "earlier stretch" in bare.signals, False)
        check("an earlier stretch is", "earlier stretch" in past.signals, True)
        check("changing it with no evidence is named",
              "no demonstration" in past.signals, True)
        check("removed failure language is named",
              "failure language removed" in tidy.signals, True)
        check("the section is reported",
              any("Stretch 0" in s for s in past.sections), True)

        print("\nthe ledger is additive:")
        ledger = os.path.join(tmp, "ledger.md")
        open(ledger, "w").write("| change | date |\n| --- | --- |\n")
        check("rows are added", epidosis.append(items, "record", ledger), 5)
        with open(ledger) as fh:
            body = fh.read()
        hand = body.replace("| | |\n", "| epidosis | by hand |\n", 1)
        open(ledger, "w").write(hand)
        check("a second run adds nothing",
              epidosis.append(items, "record", ledger), 0)
        check("a written verdict survives",
              "by hand" in open(ledger).read(), True)
        commit(repo, open(os.path.join(repo, "docs", "history.md")).read()
               + "\nOne more line.\n", "later")
        check("a new change is added and the rest left alone",
              epidosis.append(epidosis.changes(repo), "record", ledger), 1)
        check("the hand-written row is still there",
              "by hand" in open(ledger).read(), True)

        print("\nit refuses what it cannot read:")
        check("a missing record reads as no changes",
              epidosis.changes(repo, "docs/nowhere.md"), [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nall checks passed" if not FAILS else f"\n{FAILS} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
