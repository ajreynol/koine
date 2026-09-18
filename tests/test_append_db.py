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
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "bug_db_manager", "koine_append_db")

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

    def start(self, dump, *extra, db=None):
        """A run left running, so two of them can be in flight at once."""
        return subprocess.Popen(
            [sys.executable, SCRIPT, dump, db or self.db, *extra],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


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


def test_an_id_cannot_collide_with_a_tool_and_bug():
    print("\nan explicit id and a tool named id with the same bug name:")
    explicit = {"id": "same", "tool": "anoieu", "bug": "first"}
    named = {"tool": "id", "bug": "same"}
    for entries in ([explicit, named], [named, explicit]):
        t = Tree()
        first = t.run(t.write("first.json", [entries[0]]), "--date", "2026-01-01")
        second = t.run(t.write("second.json", [entries[1]]), "--date", "2026-01-02")
        check("separate runs accept both identities",
              first.returncode == second.returncode == 0, second.stderr)
        check("the second identity is added rather than silently merged",
              len(t.bugs()) == 2 and "1 new bug(s), 0 already known" in second.stdout)
        check("the first identity is not marked seen by the second run",
              t.bugs()[0]["last_seen"] == "2026-01-01")
        replay = t.run(t.write("both.json", entries), "--date", "2026-01-03")
        check("a mixed dump replays both without a duplicate error",
              replay.returncode == 0 and "0 new bug(s), 2 already known" in replay.stdout,
              replay.stderr)


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


def test_two_runs_at_once_both_survive():
    """The property the lock exists for, and the one it is easiest to lose.

    *A bug is added once* is a claim about a file several tools append to.
    Without a lock each run reads the same database, merges its own dump into
    what it read, and whichever replaces last throws the others' bugs away --
    silently, because from inside every one of them everything worked.

    **Eight writers rather than two, because two was a bad test.** Measured
    against this script with the lock bypassed: two overlapping appends lost one
    in 2 trials out of 12, and eight lost one in 5 out of 6. A regression test
    that catches its own bug one run in six is not a test, and the number is
    here so the next person does not have to re-measure it to find that out.
    """
    print("\neight tools appending to one database at the same time:")
    t = Tree()
    t.run(t.write("first.json", RUN1), "--date", "2026-03-04")
    dumps = [t.write(f"n{i}.json", [{"bug": f"b-{i}", "tool": f"tool{i}",
                                     "description": "z"}])
             for i in range(8)]

    # Every run is held at the front of the queue by a third process sitting on
    # the lock, so all eight are certainly in flight before any may write.
    holder = subprocess.Popen(
        [sys.executable, "-c", textwrap.dedent(f"""
            import fcntl, sys, time
            h = open({t.db + ".lock"!r}, "a+")
            fcntl.flock(h.fileno(), fcntl.LOCK_EX)
            sys.stdout.write("held\\n"); sys.stdout.flush()
            time.sleep(0.8)
        """)], stdout=subprocess.PIPE, text=True)
    check("a third process can take the lock", holder.stdout.readline(), "held\n")

    runs = [t.start(dump, "--date", "2026-09-16") for dump in dumps]
    holder.wait()
    codes = [r.wait() for r in runs]

    check("every run succeeds", set(codes), {0})
    names = sorted(b["bug"] for b in t.bugs())
    check("and every accepted append survives",
          names, sorted(["DOC0011-202", "EO0031-17"] + [f"b-{i}" for i in range(8)]))
    check("each under its own tool", len({b["tool"] for b in t.bugs()}), 9)


def test_a_run_that_cannot_take_the_lock_refuses():
    print("\na database another run is holding:")
    t = Tree()
    t.run(t.write("first.json", RUN1), "--date", "2026-03-04")
    before = open(t.db, encoding="utf-8").read()
    holder = subprocess.Popen(
        [sys.executable, "-c", textwrap.dedent(f"""
            import fcntl, sys, time
            h = open({t.db + ".lock"!r}, "a+")
            fcntl.flock(h.fileno(), fcntl.LOCK_EX)
            sys.stdout.write("held\\n"); sys.stdout.flush()
            time.sleep(2.0)
        """)], stdout=subprocess.PIPE, text=True)
    holder.stdout.readline()
    try:
        r = t.run(t.write("b.json", [{"bug": "b-1", "tool": "anoieu",
                                      "description": "z"}]),
                  "--lock-timeout", "0.2")
        check("it refuses rather than waiting for ever", r.returncode == adb.BUSY,
              f"{r.returncode}: {r.stderr}")
        check("and says what it was waiting for",
              "is held by another run" in r.stderr, r.stderr)
        check("and the database is untouched",
              open(t.db, encoding="utf-8").read() == before)

        r = t.run(t.write("c.json", [{"bug": "c-1", "tool": "anoieu",
                                      "description": "z"}]), "--no-lock")
        check("--no-lock is the way past, for a caller holding its own",
              r.returncode == 0, r.stderr)

        r = t.run(t.write("e.json", [{"bug": "e-1", "tool": "anoieu",
                                      "description": "z"}]),
                  "--dry-run", "--lock-timeout", "0.2")
        check("and a reading run never waited in the first place",
              r.returncode == 0, r.stderr)
    finally:
        holder.wait()


def test_an_interrupted_write_leaves_a_readable_database():
    print("\na run killed between the write and the rename:")
    t = Tree()
    t.run(t.write("a.json", RUN1), "--date", "2026-03-04")
    before = open(t.db, encoding="utf-8").read()
    # What a killed run leaves behind: a temporary file named for its own
    # process. A fixed name would be taken for ever and the next run would
    # write over it.
    stale = f"{t.db}.writing.999999"
    open(stale, "w").write("half a fi")
    r = t.run(t.write("b.json", [{"bug": "b-1", "tool": "anoieu",
                                  "description": "z"}]), "--date", "2026-09-16")
    check("a later run is unaffected by the leftovers", r.returncode == 0, r.stderr)
    check("the database is whole and holds the new bug", len(t.bugs()) == 3)
    check("and the old rows are still what they were",
          before.count("EO0031-17") == 1 and t.bugs()[0]["bug"] == "EO0031-17")
    os.remove(stale)


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
    # `bugs.json.lock` is furniture rather than leftovers: `flock` needs a file
    # to hold, and deleting it after a run is how two runs end up locking two
    # different inodes and both proceeding. It is empty and carries no data.
    check("no leftover temporary file",
          sorted(os.listdir(t.dir)) == ["a.json", "bugs.json", "bugs.json.lock"],
          str(sorted(os.listdir(t.dir))))
    check("and the lock file holds nothing",
          os.path.getsize(t.db + ".lock") == 0)


if __name__ == "__main__":
    for fn in (test_a_first_run_creates_the_database,
               test_the_same_dump_twice_adds_nothing,
               test_a_later_run_adds_only_what_is_new,
               test_the_same_name_from_two_tools_is_two_bugs,
               test_an_id_wins_over_the_name,
               test_an_id_cannot_collide_with_a_tool_and_bug,
               test_nothing_already_in_is_rewritten,
               test_a_bad_dump_writes_nothing,
               test_dry_run_writes_nothing,
               test_a_database_is_also_a_dump,
               test_two_runs_at_once_both_survive,
               test_a_run_that_cannot_take_the_lock_refuses,
               test_an_interrupted_write_leaves_a_readable_database,
               test_the_file_it_writes):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
