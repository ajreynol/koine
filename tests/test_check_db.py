#!/usr/bin/env python3
"""Tests for koine_check_db.

    python3 tests/test_check_db.py

Everything runs against git repositories built in a temporary directory. A test
commits a database, edits it the way a closure run would or the way one should
not, and checks what is said about the difference.

**The property that carries the weight is one sentence.** A closure run may add
`closed_*` fields to an entry that had none, and may do nothing else at all. The
reason is `koine_append_db`'s: *a record of what was found over time is worth
having only if nothing quietly rewrites it* -- which the append side enforces by
refusing, and the closure side cannot, because closure is an assistant with the
file open. So it is checked afterwards instead.

**The second property is that none of this knows what the records are.** A
database of defects and a database of rewrite candidates are the same shape
here, and a consumer whose database is a `rewrite_db` several directories inside
somebody else's repository is checked like any other.
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
SCRIPT = os.path.join(ROOT, "bug_db_manager", "koine_check_db")

_spec = importlib.util.spec_from_loader(
    "koine_check_db",
    importlib.machinery.SourceFileLoader("koine_check_db", SCRIPT))
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)

FAILURES = []

RECORDS = [
    {"id": "A-1", "tool": "t", "bug": "one", "description": "the first claim",
     "first_seen": "2026-03-04", "last_seen": "2026-09-16"},
    {"id": "A-2", "tool": "t", "bug": "two", "description": "the second claim",
     "first_seen": "2026-03-04", "last_seen": "2026-09-16"},
    {"id": "A-3", "tool": "t", "bug": "three", "description": "the third claim",
     "first_seen": "2026-03-04", "last_seen": "2026-09-16"},
]

CLOSURE = {"closed_on": "2026-10-01", "closed_commit": "a" * 40,
           "closed_why": "the claim is no longer true of the file"}


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


class Owner:
    """A repository with a committed database, standing in for a consumer."""

    def __init__(self, inside="bug_db", key="bugs", records=None):
        self._temp = tempfile.TemporaryDirectory(prefix="koine-check-db-")
        self.dir = self._temp.name
        self.db = os.path.join(self.dir, inside, "bugs.json")
        os.makedirs(os.path.dirname(self.db), exist_ok=True)
        self.key = key
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "Test")
        self.put(records if records is not None else RECORDS)
        self.git("add", "-A")
        self.git("commit", "--quiet", "-m", "the database as recorded")

    def git(self, *args):
        p = subprocess.run(["git", "-C", self.dir, *args],
                           capture_output=True, text=True)
        if p.returncode:
            raise RuntimeError(f"git {' '.join(args)}: {p.stderr}")
        return p.stdout.strip()

    def put(self, records):
        with open(self.db, "w", encoding="utf-8") as fh:
            json.dump({self.key: records}, fh, indent=2)

    def get(self):
        with open(self.db, encoding="utf-8") as fh:
            return json.load(fh)[self.key]

    def run(self, *extra):
        return subprocess.run([sys.executable, SCRIPT, self.db, *extra],
                              capture_output=True, text=True, timeout=60)


def test_a_closure_is_what_it_is_allowed_to_be():
    print("\na closure run that did its job:")
    o = Owner()
    records = o.get()
    records[0].update(CLOSURE)
    records[2].update(CLOSURE)
    o.put(records)
    r = o.run()
    check("it passes", r.returncode == 0, r.stderr)
    check("and names each entry it closed and what was added",
          "id A-1 closed, adding `closed_commit`, `closed_on`, `closed_why`"
          in r.stdout, r.stdout)
    check("both of them", "id A-3 closed" in r.stdout, r.stdout)
    check("the one left open is not mentioned", "id A-2" not in r.stdout, r.stdout)
    check("and the counts are reported",
          "3 record(s) at HEAD, 3 now; 2 closure(s), 0 unallowed change(s)"
          in r.stdout, r.stdout)


def test_a_reworded_claim_is_caught():
    print("\nthe damage this exists to catch:")
    o = Owner()
    records = o.get()
    records[0].update(CLOSURE)
    # The whole point. An assistant tidying a claim while closing a different
    # entry changes what a future run is comparing against, and the diff that
    # would show it is long and mostly expected.
    records[1]["description"] = "the second claim, tidied"
    o.put(records)
    r = o.run()
    check("it fails", r.returncode == 1)
    check("naming the entry and the field",
          "id A-2 `description` was 'the second claim' and is now "
          "'the second claim, tidied'" in r.stderr, r.stderr)
    check("and the closure it did make is still reported",
          "id A-1 closed" in r.stdout, r.stdout)
    check("and says what to do", "Put back what changed" in r.stderr, r.stderr)


def test_an_entry_may_not_be_removed_added_or_reordered():
    print("\nthe three ways a database stops being the one that was recorded:")
    o = Owner()
    o.put([r for r in o.get() if r["id"] != "A-2"])
    r = o.run()
    check("a removed entry fails",
          r.returncode == 1 and "id A-2 is gone from the database" in r.stderr,
          r.stderr)
    check("and says a closure rules on a record rather than removing one",
          "it does not remove one" in r.stderr, r.stderr)

    o.put(o.get() + [{"id": "A-9", "description": "invented"}])
    r = o.run()
    check("an added entry fails", r.returncode == 1)
    # koine_append_db is the only thing that creates one, because an entry has
    # a first_seen and a closure run has no run to date it from.
    check("and says which program is allowed to add one",
          "koine_append_db is the only thing that adds a record" in r.stderr,
          r.stderr)

    o.git("checkout", "--", ".")
    records = o.get()
    records[0], records[2] = records[2], records[0]
    o.put(records)
    r = o.run()
    check("a reordering fails",
          r.returncode == 1 and "in a different order" in r.stderr, r.stderr)


def test_a_recorded_closure_is_not_a_closure_runs_to_change():
    print("\nan entry somebody had already ruled on:")
    o = Owner()
    records = o.get()
    records[0].update(CLOSURE)
    o.put(records)
    o.git("commit", "--quiet", "-am", "a closure")

    records = o.get()
    records[0]["closed_why"] = "a different reason"
    o.put(records)
    r = o.run()
    check("rewriting a recorded verdict fails", r.returncode == 1, r.stdout)
    check("naming what it was and what it became",
          "was already recorded as" in r.stderr, r.stderr)
    check("and pointing at the flag for the legitimate case",
          "--amended" in r.stderr, r.stderr)

    r = o.run("--amended")
    check("which allows it, for a person amending their own closure",
          r.returncode == 0, r.stderr)
    check("and still reports the change rather than hiding it",
          "a different reason" in r.stdout, r.stdout)

    records = o.get()
    del records[0]["closed_commit"]
    o.put(records)
    check("removing a recorded closure field fails too",
          o.run().returncode == 1)


def test_a_closure_field_without_the_prefix_is_named_not_guessed():
    print("\nan owner whose vocabulary predates the convention:")
    o = Owner()
    records = o.get()
    # A verdict that closes a finding before its fix reaches a default branch
    # owes a note saying where the change is. One consumer calls that field
    # `awaiting_landing`, and it does not carry the prefix.
    records[0].update(CLOSURE)
    records[0]["awaiting_landing"] = {"project": "p", "branch": "b", "commit": "c"}
    o.put(records)
    r = o.run()
    check("without being told, it is an unallowed change", r.returncode == 1)
    check("and the message says how to say otherwise",
          "Name it with --also" in r.stderr, r.stderr)
    r = o.run("--also", "awaiting_landing")
    check("named, it is part of the closure", r.returncode == 0, r.stderr)
    check("and is counted as one",
          "`awaiting_landing`" in r.stdout and "1 closure(s)" in r.stdout, r.stdout)


def test_it_knows_nothing_about_what_the_records_are():
    print("\na rewrite database, in a child project, inside somebody's repository:")
    # The third customer's shape: a `rewrite_db` several directories down, whose
    # records are proposed rewrites rather than defects.
    o = Owner(inside=os.path.join("tools", "metagraphe", "rewrite_db"),
              key="rewrites",
              records=[{"id": "M-1", "owner": "cvc5",
                        "description": "str.len of str.++ distributes",
                        "first_seen": "2026-09-19", "last_seen": "2026-09-19"},
                       {"id": "M-2", "owner": "cvc5",
                        "description": "bvand with a constant mask narrows",
                        "first_seen": "2026-09-19", "last_seen": "2026-09-19"}])
    records = o.get()
    records[0].update(CLOSURE)
    o.put(records)
    r = o.run()
    check("a closure in it passes", r.returncode == 0, r.stderr)
    check("and is reported by identity", "id M-1 closed" in r.stdout, r.stdout)
    records = o.get()
    records[1]["description"] = "reworded"
    o.put(records)
    check("and a reworded candidate is caught the same way",
          o.run().returncode == 1)


def test_the_envelope_key_is_not_a_closure():
    print("\nrenaming what the database says it holds:")
    o = Owner()
    records = o.get()
    with open(o.db, "w", encoding="utf-8") as fh:
        json.dump({"findings": records}, fh, indent=2)
    r = o.run()
    check("it is reported as a change to the file's shape",
          r.returncode == 1 and "not a closure" in r.stderr, r.stderr)
    check("and the way past is named rather than left to be guessed",
          "--renamed" in r.stderr, r.stderr)

    # A rename adds nothing and loses nothing, and koine_append_db will not do
    # it -- an existing database keeps its key -- so it is a person's edit. With
    # no way to say it was deliberate, a migration is a red run somebody has to
    # be told to ignore, which is the habit a check cannot afford to teach.
    r = o.run("--renamed")
    check("declared, the same migration passes",
          r.returncode == 0 and "a migration, and not a closure" in r.stdout,
          r.stdout + r.stderr)
    check("and is not counted as a closure",
          "0 closure(s), 0 unallowed change(s)" in r.stdout, r.stdout)

    # The flag permits the envelope and nothing else: what the records say is
    # still compared, which is the whole reason the check exists.
    with open(o.db, encoding="utf-8") as fh:
        records = json.load(fh)["findings"]
    records[0] = {**records[0], "description": "the first claim, tidied"}
    with open(o.db, "w", encoding="utf-8") as fh:
        json.dump({"findings": records}, fh, indent=2)
    r = o.run("--renamed")
    check("but a record reworded under cover of it still fails",
          r.returncode == 1 and "`description` was" in r.stderr, r.stderr)


def test_what_it_refuses_to_judge():
    print("\nwhat it will not compare:")
    o = Owner()
    with tempfile.TemporaryDirectory(prefix="koine-check-db-loose-") as loose:
        path = os.path.join(loose, "bugs.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"bugs": RECORDS}, fh)
        r = subprocess.run([sys.executable, SCRIPT, path], capture_output=True,
                           text=True)
        check("a database in no repository is refused", r.returncode == 1)
        check("and told why", "no committed version" in r.stderr
              or "not tracked" in r.stderr, r.stderr)

    untracked = os.path.join(o.dir, "bug_db", "other.json")
    with open(untracked, "w", encoding="utf-8") as fh:
        json.dump({"bugs": RECORDS}, fh)
    r = subprocess.run([sys.executable, SCRIPT, untracked], capture_output=True,
                       text=True)
    check("an untracked one is refused", r.returncode == 1)
    check("because nothing was recorded to compare it against",
          "nothing was recorded" in r.stderr, r.stderr)

    with open(o.db, "w", encoding="utf-8") as fh:
        fh.write("{not json")
    check("and unreadable JSON is refused rather than read as a change",
          o.run().returncode == 1)


def test_it_writes_nothing():
    print("\nwhat it leaves behind:")
    o = Owner()
    records = o.get()
    records[0].update(CLOSURE)
    o.put(records)
    before = o.git("status", "--porcelain=v1", "--untracked-files=all")
    head = o.git("rev-parse", "HEAD")
    o.run()
    o.run("--amended")
    check("the working tree is where it was",
          o.git("status", "--porcelain=v1", "--untracked-files=all") == before)
    check("and nothing was committed", o.git("rev-parse", "HEAD") == head)
    # Correcting a database is the owner's; a report naming the entry and the
    # field is what that takes.
    check("the closure it found is still only in the working tree",
          "closed_on" in open(o.db, encoding="utf-8").read())


if __name__ == "__main__":
    for fn in (test_a_closure_is_what_it_is_allowed_to_be,
               test_a_reworded_claim_is_caught,
               test_an_entry_may_not_be_removed_added_or_reordered,
               test_a_recorded_closure_is_not_a_closure_runs_to_change,
               test_a_closure_field_without_the_prefix_is_named_not_guessed,
               test_it_knows_nothing_about_what_the_records_are,
               test_the_envelope_key_is_not_a_closure,
               test_what_it_refuses_to_judge,
               test_it_writes_nothing):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
