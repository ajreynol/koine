#!/usr/bin/env python3
"""Tests for koine_close_db.

    python3 tests/test_close_db.py

Everything runs against consumers built in a temporary directory: a config, a
database and the prompt sections their owner writes. Nothing launches an
assistant -- `--show-prompt` and `--dry-run` are what these read, and the whole
point of those flags is that they print the same thing on a machine with nothing
on it.

**The property that carries the weight is the line between koine and an owner.**
koine writes the mechanics: the window, the five steps of a closure assessment,
where the work is left, and the check afterwards. The owner writes what their
records are, what closes one, and what a closure is recorded as -- and koine
splices those in whole rather than paraphrasing them, because a paraphrase of
three projects' rules kept in a fourth repository is a copy with nothing keeping
it current.

**The second property is that none of it knows what the records are.** The
consumers here are a bug database and a rewrite database, and the prompt speaks
each owner's word throughout.
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
SCRIPT = os.path.join(ROOT, "bug_db_manager", "koine_close_db")

_spec = importlib.util.spec_from_loader(
    "koine_close_db",
    importlib.machinery.SourceFileLoader("koine_close_db", SCRIPT))
cls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cls)

FAILURES = []

CVC5 = {"url": "https://github.com/cvc5/cvc5.git", "ref": "main",
        "reads": "the rewriter and its regressions"}
ETHOS = {"url": "https://github.com/cvc5/ethos.git", "ref": "main"}


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


def said(text, phrase):
    """Whether the prompt says that, wherever the wrapping broke it.

    The prompt is wrapped at the end, and every paragraph carries a noun the
    owner chose, so where a sentence breaks depends on how long that noun is. A
    test matching raw text would be a test of one config's vocabulary.
    """
    return " ".join(phrase.split()) in " ".join(text.split())


class Consumer:
    """A config, a database, and the prompt sections an owner writes."""

    def __init__(self, records, key="bugs", config=None, inside="bug_db",
                 slots=None, named="bugs.json"):
        self.dir = tempfile.mkdtemp(prefix="koine-close-db-")
        self.db = os.path.join(inside, named)
        os.makedirs(os.path.join(self.dir, inside), exist_ok=True)
        os.makedirs(os.path.join(self.dir, "prompts"), exist_ok=True)
        self.write(self.db, json.dumps({key: records}, indent=2))
        if slots is None:
            slots = {"writes": "Add `closed_on` and `closed_why`."}
        for name, body in slots.items():
            self.write(os.path.join("prompts", name + ".md"), body)
        cfg = {"database": self.db, "projects": {"cvc5": CVC5},
               "prompt": {n: f"prompts/{n}.md" for n in slots}}
        cfg.update(config or {})
        self.config = os.path.join(self.dir, "closure.json")
        self.write("closure.json", json.dumps(cfg, indent=2))

    def write(self, name, body):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
            fh.write(body)

    def run(self, *extra):
        return subprocess.run([sys.executable, SCRIPT, "--config", self.config,
                               *extra], capture_output=True, text=True, timeout=60)

    def prompt(self, *extra):
        r = self.run("--show-prompt", "--since", "cvc5=aee8742",
                     "--date", "2026-10-01", *extra)
        if r.returncode:
            raise RuntimeError(r.stderr)
        return r.stdout


OPEN = [{"id": "A-1", "owner": "cvc5", "code": "EO1", "description": "one"},
        {"id": "A-2", "owner": "cvc5", "code": "EO1", "description": "two"},
        {"id": "A-3", "owner": "cvc5", "code": "DOC2", "description": "three"}]


def test_the_mechanics_are_koines():
    print("\nwhat every owner's prompt says, whoever they are:")
    c = Consumer(OPEN, config={"group": "code"})
    text = c.prompt()
    check("it says whose database and where",
          said(text, f"in the database of **{os.path.basename(c.dir)}**"), text)
    check("and how many are open", said(text, "holds 3 open records"), text)
    check("the window is there", said(text, "compare/aee8742...main"), text)
    for n, phrase in enumerate((
            "Read what the commit changed",
            "Name the records it could close, by id",
            "**Confirm the closure in the current source, not in the commit "
            "message.**",
            "**Absence closes nothing.**",
            "If you cannot tell, leave it open and say what would settle it."), 1):
        check(f"step {n} is stated", said(text, phrase), phrase)
    check("the grouping the owner chose is summarised",
          "DOC2 1, EO1 2" in text, text)
    check("the check afterwards is koine_check_db",
          "koine_check_db" in text and c.db in text, text)
    check("the work is left uncommitted",
          said(text, "**Commit nothing and push nothing.**"), text)
    check("and reaches nobody",
          said(text, "Open no pull request, file no issue, post no comment"), text)


def test_the_owners_sections_go_in_whole():
    print("\nwhat koine splices rather than writes:")
    about = "Metagraphe looks for rewrites cvc5 is **missing**, not defects."
    evidence = "A smaller expression is not a closure."
    writes = 'Add "closed_on": "{when}" and nothing else.\n\n    {"x": 1}'
    c = Consumer(OPEN, slots={"about": about, "evidence": evidence,
                              "writes": writes})
    text = c.prompt()
    check("the owner's `about` is there, as written", about in text, text)
    check("so is `evidence`", evidence in text, text)
    check("and `writes`", 'Add "closed_on": "2026-10-01" and nothing else.' in text,
          text)
    # These files carry JSON examples, so a `{` in one is not a placeholder and
    # substitution can never be `format`.
    check("a brace in the owner's text is left alone", '{"x": 1}' in text, text)
    check("and the date placeholder was filled", "{when}" not in text, text)


def test_a_closure_vocabulary_is_never_guessed():
    print("\nwhat koine refuses to invent:")
    c = Consumer(OPEN, slots={})
    r = c.run("--show-prompt", "--since", "cvc5=aee8742")
    check("with no `writes` section it refuses", r.returncode == 2)
    check("saying the vocabulary is the owner's",
          "koine will not guess a vocabulary" in r.stderr, r.stderr)


def test_a_baseline_is_the_owners_to_say():
    print("\nwhere the window starts:")
    c = Consumer(OPEN)
    r = c.run("--dry-run")
    check("without one, it refuses rather than picking a revision",
          r.returncode == 2, r.stdout)
    check("and says both ways to supply it",
          "--since" in r.stderr and "baseline.command" in r.stderr, r.stderr)

    # The owner's command, because which field records a revision -- and what to
    # do when two rows disagree -- is a decision each owner has made differently.
    c = Consumer(OPEN, config={"baseline": {"command": [
        "python3", "-c", "print('cvc5 abc1234 the newest archived run')"]}})
    r = c.run("--dry-run")
    check("a configured command answers it", r.returncode == 0, r.stderr)
    check("with the revision", "abc1234" in r.stdout, r.stdout)
    check("and the owner's own reason for it",
          "the newest archived run" in r.stdout, r.stdout)
    r = c.run("--dry-run", "--since", "cvc5=deadbee")
    check("and --since overrides it",
          "deadbee" in r.stdout and "abc1234" not in r.stdout, r.stdout)

    c = Consumer(OPEN, config={"baseline": {"command": ["false"]}})
    check("a baseline command that fails is refused, not worked around",
          c.run("--dry-run").returncode == 2)


def test_a_ruled_record_is_nobodys_question():
    print("\nwhat counts as open:")
    records = OPEN + [
        {"id": "A-4", "owner": "cvc5", "description": "four",
         "closed_on": "2026-09-19", "closed_why": "done"},
        {"id": "A-5", "owner": "cvc5", "description": "five",
         "awaiting_landing": {"project": "cvc5", "branch": "b", "commit": "c"}}]
    c = Consumer(records)
    check("an entry with a closed_ field is left out",
          said(c.prompt(), "holds 4 open records"), c.prompt())
    # The same `--also` the checker takes: an owner whose vocabulary predates
    # the prefix names the field once.
    c = Consumer(records, config={"also": ["awaiting_landing"]})
    text = c.prompt()
    check("and so is one in a vocabulary named by `also`",
          said(text, "holds 3 open records"), text)
    check("which is then passed to the check afterwards",
          "--also awaiting_landing" in text, text)


def test_a_project_with_nothing_open_is_named_out_loud():
    print("\ntelling a run that found nothing from a run that did not look:")
    c = Consumer(OPEN, config={"projects": {"cvc5": CVC5, "ethos": ETHOS}})
    text = c.prompt()
    check("the quiet project gets a heading of its own",
          "## ethos -- nothing open" in text, text)
    check("saying there is nothing for a commit of its to close",
          said(text, "there is nothing for a commit of its to close and no "
                     "window to read"), text)
    check("and that this is a complete result",
          said(text, "That is a complete result for ethos: do not go looking "
                     "for work there"), text)
    check("while the project with work gets a window",
          "## cvc5 -- 3 open records" in text and "compare/" in text, text)


def test_a_record_owned_by_two_projects_is_in_both_windows():
    print("\na claim about a disagreement between two projects:")
    c = Consumer([{"id": "A-1", "owner": "cvc5+ethos", "description": "they differ"}],
                 config={"projects": {"cvc5": CVC5, "ethos": ETHOS}})
    # Both need a baseline here, because both have the row open.
    text = c.prompt("--since", "ethos=1a2b3c4")
    # Filing it under one owner would put it in that window and leave the other
    # blind to it, and either side's change can resolve it.
    check("it is open for the first", "## cvc5 -- 1 open records" in text, text)
    check("and for the second", "## ethos -- 1 open records" in text, text)
    c = Consumer([{"id": "A-1", "owner": "logos", "description": "x"}])
    r = c.run("--dry-run", "--since", "cvc5=abc")
    check("and an owner the config does not name is refused",
          r.returncode == 2 and "does not name" in r.stderr, r.stderr)


def test_the_records_are_called_what_the_owner_calls_them():
    print("\na third customer, whose records are not defects:")
    c = Consumer([{"id": "M-1", "owner": "cvc5", "description": "str.len distributes"}],
                 key="rewrites",
                 inside=os.path.join("tools", "metagraphe", "rewrite_db"),
                 named="rewrites.json",
                 config={"tool": "metagraphe",
                         "records": {"one": "rewrite candidate",
                                     "many": "rewrite candidates",
                                     "collective": "rewrite database"}},
                 slots={"writes": "Add `closed_on`."})
    text = c.prompt()
    check("the prompt speaks the owner's word",
          said(text, "You are closing rewrite candidates in the rewrite "
                     "database of **metagraphe**"), text)
    check("throughout the steps koine wrote",
          said(text, "Name the rewrite candidates it could close, by id"), text)
    check("including the singular",
          said(text, "Re-read what the rewrite candidate names"), text)
    # koine's own prose never says bug. Two things in the page legitimately do:
    # whatever the owner wrote in their own sections, and the path to koine's
    # tooling, which is called bug_db whoever is using it.
    ours = [line for line in text.splitlines()
            if line and not line.startswith(" ") and "koine_check_db" not in line
            and "Add `closed_on`" not in line]
    check("and koine's own prose never says bug",
          not [line for line in ours if "bug" in line.lower()],
          "\n".join(line for line in ours if "bug" in line.lower()))
    check("the database is wherever the owner keeps it",
          "tools/metagraphe/rewrite_db/rewrites.json"
          in text.replace(os.sep, "/"),
          text)
    # koine's tooling is called bug_db; a consumer's database is its own.
    check("and its envelope key is read rather than assumed",
          said(text, "holds 1 open rewrite candidates"), text)


def test_a_paragraph_is_wrapped_and_a_command_is_not():
    print("\nwhat is re-wrapped and what is left alone:")
    c = Consumer(OPEN, config={"records": {
        "one": "extraordinarily long-winded record",
        "many": "extraordinarily long-winded records",
        "collective": "extraordinarily long-winded database"}})
    text = c.prompt()
    mine = [line for line in text.splitlines()
            if line and not line.startswith(" ") and "://" not in line]
    over = [line for line in mine if len(line) > cls.WIDTH]
    check("no paragraph koine wrote runs long, whatever the noun",
          all(len(line.split()) == 1 for line in over), "\n".join(over))
    check("the numbered steps keep their hanging indent",
          any(line.startswith("   ") and "extraordinarily" in line
              for line in text.splitlines()), text)


def test_it_starts_nothing_and_fetches_nothing():
    print("\nwhat a preview costs:")
    c = Consumer(OPEN, config={"baseline": {"command": [
        sys.executable, "-c", "print('cvc5 abc1234 a pin')"]}})
    # --show-prompt has to print the same text on a machine with nothing on it,
    # which is why a remote window is pointed at and never fetched. With an
    # empty PATH there is no `git`, no `gh` and no assistant to find.
    env = dict(os.environ, PATH="/nonexistent")
    r = subprocess.run([sys.executable, SCRIPT, "--config", c.config,
                        "--show-prompt"], capture_output=True, text=True,
                       env=env, timeout=60)
    check("it previews with nothing on the PATH", r.returncode == 0, r.stderr)
    check("and the window is still described",
          "compare/abc1234...main" in r.stdout, r.stdout)
    before = sorted(os.listdir(c.dir))
    c.run("--dry-run")
    c.prompt()
    check("and nothing was written beside the config",
          sorted(os.listdir(c.dir)) == before, str(sorted(os.listdir(c.dir))))


if __name__ == "__main__":
    for fn in (test_the_mechanics_are_koines,
               test_the_owners_sections_go_in_whole,
               test_a_closure_vocabulary_is_never_guessed,
               test_a_baseline_is_the_owners_to_say,
               test_a_ruled_record_is_nobodys_question,
               test_a_project_with_nothing_open_is_named_out_loud,
               test_a_record_owned_by_two_projects_is_in_both_windows,
               test_the_records_are_called_what_the_owner_calls_them,
               test_a_paragraph_is_wrapped_and_a_command_is_not,
               test_it_starts_nothing_and_fetches_nothing):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
