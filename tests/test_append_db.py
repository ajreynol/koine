#!/usr/bin/env python3
"""Tests for koine_append_db.

    python3 tests/test_append_db.py

Everything runs in a temporary directory against files written inline, so the
test reads as a sequence of runs: here is what the tool dumped, here is what the
database then held.

Three properties carry the weight, and they are the three reasons this is a
database rather than a pile of dumps. **Running the same dump twice adds
nothing.** **Nothing already in the database is edited or removed.** And **a dump
with one bad entry writes nothing at all**, so there is no half-applied state.
"""

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "bug_db", "koine_append_db")

_spec = importlib.util.spec_from_loader(
    "koine_append_db",
    importlib.machinery.SourceFileLoader("koine_append_db", SCRIPT))
adb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adb)

FAILURES = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


class Tree:
    """A scratch directory, with the script pointed at files inside it."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="koine-append-db-")
        self.db = os.path.join(self.dir, "bugs.json")

    def write(self, name, data):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return path

    def run(self, dump, *extra, db=None):
        return subprocess.run(
            [sys.executable, SCRIPT, dump, db or self.db, *extra],
            capture_output=True, text=True, timeout=60)

    def bugs(self):
        with open(self.db, encoding="utf-8") as fh:
            return json.load(fh)["bugs"]


RUN1 = [{"bug": "EO0031-17", "tool": "anoieu", "description": "declared twice"},
        {"bug": "DOC0011-202", "tool": "anoieu", "description": "arity differs"}]


def test_a_first_run_creates_the_database():
    print("\na first run, with no database yet:")
    t = Tree()
    r = t.run(t.write("run1.json", RUN1), "--date", "2026-03-04")
    check("it succeeds", r.returncode == 0, r.stderr)
    check("and says it created the file", "(created)" in r.stdout, r.stdout)
    check("both bugs are in", len(t.bugs()) == 2)
    check("each carries the date it was first seen",
          all(b["first_seen"] == "2026-03-04" for b in t.bugs()))
    check("the tool's own fields are untouched",
          t.bugs()[0]["bug"] == "EO0031-17"
          and t.bugs()[0]["description"] == "declared twice")


def test_the_same_dump_twice_adds_nothing():
    print("\nthe same dump, run twice:")
    t = Tree()
    dump = t.write("run1.json", RUN1)
    t.run(dump, "--date", "2026-03-04")
    r = t.run(dump, "--date", "2026-05-01")
    check("the second run adds nothing", len(t.bugs()) == 2)
    check("and says so", "0 new bug(s), 2 already known" in r.stdout, r.stdout)
    check("first_seen does not move",
          all(b["first_seen"] == "2026-03-04" for b in t.bugs()))
    check("last_seen does",
          all(b["last_seen"] == "2026-05-01" for b in t.bugs()))


def test_a_later_run_adds_only_what_is_new():
    print("\na later run, overlapping the first:")
    t = Tree()
    t.run(t.write("run1.json", RUN1), "--date", "2026-03-04")
    later = [RUN1[0],
             {"bug": "EO0084-61", "tool": "anoieu", "description": "self-premise"},
             {"bug": "i-2", "tool": "dokimasia", "description": "safe mode",
              "rank": 2}]
    r = t.run(t.write("run2.json", later), "--date", "2026-09-16")
    check("two new, one known", "2 new bug(s), 1 already known" in r.stdout,
          r.stdout)
    check("the database holds four", len(t.bugs()) == 4)
    check("new bugs are appended at the end, in the order they arrived",
          [b["bug"] for b in t.bugs()]
          == ["EO0031-17", "DOC0011-202", "EO0084-61", "i-2"])
    check("a field this script does not know about is carried through",
          t.bugs()[3]["rank"] == 2)
    check("a bug the later run did not mention keeps its own last_seen",
          t.bugs()[1]["last_seen"] == "2026-03-04")
    check("and is not removed", t.bugs()[1]["bug"] == "DOC0011-202")
    check("two tools are counted separately",
          "anoieu 3, dokimasia 1" in r.stdout, r.stdout)


def test_the_same_name_from_two_tools_is_two_bugs():
    print("\nthe same bug name, from two different tools:")
    t = Tree()
    t.run(t.write("a.json", [{"bug": "i-2", "tool": "anoieu", "description": "x"}]),
          "--date", "2026-01-01")
    t.run(t.write("b.json", [{"bug": "i-2", "tool": "dokimasia", "description": "y"}]),
          "--date", "2026-01-02")
    check("both are kept", len(t.bugs()) == 2)
    check("because the tool is half of the key",
          {b["tool"] for b in t.bugs()} == {"anoieu", "dokimasia"})


def test_an_id_wins_over_the_name():
    print("\na tool that mints its own id:")
    t = Tree()
    first = [{"id": "deb8a1dbc6c6f079", "bug": "EO0031-17", "tool": "anoieu",
              "description": "declared twice"}]
    moved = [{"id": "deb8a1dbc6c6f079", "bug": "EO0031-19", "tool": "anoieu",
              "description": "declared twice"}]
    t.run(t.write("a.json", first), "--date", "2026-01-01")
    r = t.run(t.write("b.json", moved), "--date", "2026-02-01")
    check("the row moved and is still one bug", len(t.bugs()) == 1, r.stdout)
    check("the database keeps the name it was first given, and says so",
          t.bugs()[0]["bug"] == "EO0031-17"
          and "conflict" in r.stderr, r.stderr)


def test_nothing_already_in_is_rewritten():
    print("\na later run that describes a known bug differently:")
    t = Tree()
    t.run(t.write("a.json", RUN1), "--date", "2026-03-04")
    changed = [{"bug": "EO0031-17", "tool": "anoieu",
                "description": "REWORDED"}]
    r = t.run(t.write("b.json", changed), "--date", "2026-09-16")
    check("it succeeds", r.returncode == 0, r.stderr)
    check("the database keeps what it had",
          t.bugs()[0]["description"] == "declared twice")
    check("and the disagreement is printed rather than swallowed",
          "conflict" in r.stderr and "REWORDED" in r.stderr, r.stderr)
    check("it is counted", "1 conflict(s)" in r.stdout, r.stdout)


def test_a_bad_dump_writes_nothing():
    print("\na dump with one unreadable entry:")
    t = Tree()
    t.run(t.write("a.json", RUN1), "--date", "2026-03-04")
    before = open(t.db, encoding="utf-8").read()
    bad = [{"bug": "good", "tool": "anoieu", "description": "fine"},
           {"tool": "anoieu", "description": "no bug, and no id"}]
    r = t.run(t.write("b.json", bad), "--date", "2026-09-16")
    check("it refuses", r.returncode == 1, r.stdout)
    check("and says which entry", "bug 2" in r.stderr, r.stderr)
    check("the database is untouched -- not even the good entry",
          open(t.db, encoding="utf-8").read() == before)

    r = t.run(t.write("c.json", [{"bug": "x", "tool": "a", "description": "1"},
                                 {"bug": "x", "tool": "a", "description": "2"}]))
    check("a dump that names the same bug twice is refused",
          r.returncode == 1 and "the same bug as bug 1" in r.stderr, r.stderr)

    broken = os.path.join(t.dir, "broken.json")
    open(broken, "w").write("{not json")
    check("so is a file that is not JSON", t.run(broken).returncode == 1)
    notalist = t.write("d.json", {"findings": []})
    check("and so is JSON that is not a list of bugs",
          "expected a list of bugs" in t.run(notalist).stderr)


def test_dry_run_writes_nothing():
    print("\n--dry-run:")
    t = Tree()
    t.run(t.write("a.json", RUN1), "--date", "2026-03-04")
    before = open(t.db, encoding="utf-8").read()
    more = [{"bug": "new", "tool": "anoieu", "description": "z"}]
    r = t.run(t.write("b.json", more), "--dry-run", "--date", "2026-09-16")
    check("it succeeds", r.returncode == 0, r.stderr)
    check("it says what would have happened",
          "1 new bug(s)" in r.stdout and "would have gone from 2 to 3" in r.stdout,
          r.stdout)
    check("and the database is untouched",
          open(t.db, encoding="utf-8").read() == before)


def test_a_database_is_also_a_dump():
    print("\nthe database fed back in as a dump:")
    t = Tree()
    t.run(t.write("a.json", RUN1), "--date", "2026-03-04")
    second = os.path.join(t.dir, "other.json")
    r = t.run(t.db, db=second)
    check("it is read as a list of bugs", r.returncode == 0, r.stderr)
    with open(second, encoding="utf-8") as fh:
        check("and copies across intact", len(json.load(fh)["bugs"]) == 2)
    r = t.run(t.db, db=second)
    check("and doing it again adds nothing",
          "0 new bug(s), 2 already known" in r.stdout, r.stdout)


def test_the_file_it_writes():
    print("\nwhat the database looks like on disk:")
    t = Tree()
    t.run(t.write("a.json", [{"description": "d", "tool": "anoieu", "bug": "b",
                              "zz": 1}]), "--date", "2026-03-04")
    text = open(t.db, encoding="utf-8").read()
    check("it is indented, for a readable diff", '\n  "bugs": [' in text, text)
    check("it ends with a newline", text.endswith("}\n"))
    order = list(json.loads(text)["bugs"][0])
    check("known fields come first, in a fixed order, whatever the dump did",
          order == ["bug", "tool", "description", "first_seen", "last_seen", "zz"],
          str(order))
    check("no leftover temporary file",
          sorted(os.listdir(t.dir)) == ["a.json", "bugs.json"],
          str(sorted(os.listdir(t.dir))))


if __name__ == "__main__":
    for fn in (test_a_first_run_creates_the_database,
               test_the_same_dump_twice_adds_nothing,
               test_a_later_run_adds_only_what_is_new,
               test_the_same_name_from_two_tools_is_two_bugs,
               test_an_id_wins_over_the_name,
               test_nothing_already_in_is_rewritten,
               test_a_bad_dump_writes_nothing,
               test_dry_run_writes_nothing,
               test_a_database_is_also_a_dump,
               test_the_file_it_writes):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
