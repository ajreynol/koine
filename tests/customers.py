#!/usr/bin/env python3
"""The two customers' real files, run against koine's implementations.

    python3 tests/customers.py ~/src/anoieu ~/src/dokimasia
    python3 tests/customers.py --anoieu ~/src/anoieu

This is the evidence for the claim koine's documents make twice: that adopting a
piece costs a customer nothing on the first day. `docs/drift.md` says koine
reproduces the prompt check each repository already had, with no case, form or
line of coverage lost; `docs/postmortem-protocol.md` says a log that passed the
old shape check still passes `SHAPE`, and prints what moving to `PROTOCOL` would
cost; `docs/findings-record.md` says a ledger read into a record and rendered
back is the same page, byte for byte, and prints what the record would then be
able to ask that the table cannot. All three are claims that nobody can re-run
unless this exists.

It is **not** part of CI and nothing depends on it. It needs a checkout of
somebody else's repository, which `tests/run.py` deliberately does not, and it
fails when a customer moves their prompts -- which is their business, and is what
their own copy of this check is for until they drop it.

The specs below are the ones written out in `docs/drift.md`, and if the two
disagree the document is the one that is right.
"""

import collections
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import koine_branch as branch          # noqa: E402
import koine_drift as drift            # noqa: E402
import koine_findings as findings      # noqa: E402
import koine_postmortem as postmortem  # noqa: E402

SWEEP = "-- or, for the sweep form --"
BLOCKS = "-- or, for every block --"
POSTM = "-- or, with --no-postm --"


def anoieu(root):
    """Four cases, reproducing `prompts_agree()` in anoieu's `tests/run.py`."""
    two = [drift.after("TRIAGE: is an assistant"),
           drift.drop_paragraphs(["Working in the anoieu repository",
                                  "Process ", "Address "])]
    return drift.Spec(
        root=root,
        document="docs/reports/reporting-workflow.md",
        prompts={"one": drift.Prompt("### Prompt one", "### Prompt two"),
                 "two": drift.Prompt("### Prompt two", "### Prompt three")},
        cases=[
            drift.Case("prompts/check_anoieu, one id", "one",
                       ["bash", "prompts/check_anoieu", "--show-prompt", "ID"],
                       forms={SWEEP: False},
                       rules=[drift.sub("anoieu-ID", "BRANCH")]),
            drift.Case("prompts/check_anoieu, the sweep", "one",
                       ["bash", "prompts/check_anoieu", "--show-prompt"],
                       forms={SWEEP: True},
                       rules=[drift.sub("PROJECT", "anoieu"),
                              drift.sub("anoieu-findings", "BRANCH")]),
            drift.Case("prompts/process_anoieu", "two",
                       ["bash", "prompts/process_anoieu", "--show-prompt",
                        "--no-check", root],
                       forms={POSTM: False}, rules=two),
            drift.Case("prompts/process_anoieu --no-postm", "two",
                       ["bash", "prompts/process_anoieu", "--show-prompt",
                        "--no-check", "--no-postm", root],
                       forms={POSTM: True}, rules=two),
        ],
    )


def dokimasia(root):
    """Six cases, reproducing `test_prompts()` in dokimasia's `tests/test_workflow.py`."""
    read = [drift.after("Read it as two things.")]

    def two(name, argv, blocks, postm, rules=()):
        return drift.Case(name, "two", argv,
                          forms={BLOCKS: blocks, POSTM: postm}, rules=rules)

    return drift.Spec(
        root=root,
        document="docs/workflows.md",
        prompts={"one": drift.Prompt("## Prompt one", "## Prompt two"),
                 "two": drift.Prompt("## Prompt two", "### Keeping them in step")},
        cases=[
            drift.Case("scripts/prompts/check_dokimasia, one row", "one",
                       ["bash", "scripts/prompts/check_dokimasia", "--show-prompt", "ID"],
                       forms={SWEEP: False},
                       rules=[drift.sub("dokimasia-ID", "BRANCH")]),
            drift.Case("scripts/prompts/check_dokimasia, the sweep", "one",
                       ["bash", "scripts/prompts/check_dokimasia", "--show-prompt"],
                       forms={SWEEP: True},
                       rules=[drift.sub("dokimasia-findings", "BRANCH")]),
            two("scripts/prompts/process_dokimasia, one row",
                ["bash", "scripts/prompts/process_dokimasia", "--show-prompt",
                 "--link", "LINK", "ID"], False, False),
            two("scripts/prompts/process_dokimasia, every block",
                ["bash", "scripts/prompts/process_dokimasia", "--show-prompt",
                 "--link", "LINK"], True, False),
            two("scripts/prompts/process_dokimasia --no-postm",
                ["bash", "scripts/prompts/process_dokimasia", "--show-prompt", "--no-postm",
                 "--link", "LINK", "ID"], False, True),
            two("scripts/prompts/process_dokimasia, from a checkout",
                ["bash", "scripts/prompts/process_dokimasia", "--show-prompt", root, "ID"],
                False, False, rules=read),
        ],
    )


#: name -> (spec builder, cases their own check had, their postmortem log)
CUSTOMERS = {
    "anoieu": (anoieu, 4, "docs/reports/postmortem.md"),
    "dokimasia": (dokimasia, 6, "docs/postmortem.md"),
}


def check_log(root, rel):
    """Their real postmortem log, at both levels.

    `SHAPE` failing is a failure here: it would mean adopting koine costs them an
    edit, which is the claim. `PROTOCOL` failing is not — it is the migration,
    and printing it is the point.
    """
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        print(f"  skip {rel} -- no log there")
        return 0
    log = postmortem.read(path)
    print(f"  {rel}: {len(log.entries)} entry(s), "
          f"{len(postmortem.lessons(log))} lesson(s), "
          f"{len(postmortem.open_debts(log))} open debt(s)")
    bad = postmortem.check(log, postmortem.SHAPE, require_entries=False)
    for problem in bad:
        print(f"  FAIL {problem}")
    if not bad:
        print("  ok   it keeps SHAPE untouched -- adopting the check costs no edit")
    todo = postmortem.check(log, postmortem.PROTOCOL, require_entries=False)
    if todo:
        print(f"  -- moving to PROTOCOL would take {len(todo)} edit(s):")
        for problem in todo:
            print(f"     {problem}")
    else:
        print("  ok   it already keeps PROTOCOL")
    return len(bad)


# -- the findings record ------------------------------------------------------

#: anoieu's two ledgers, and how their columns map onto the record's fields.
#: The mapping is **theirs** -- these are the headings on their page, and the
#: record is fitted to the ledger rather than the ledger to the record.
ANOIEU_LEDGERS = (
    # file, the last column's heading, whether rows there are ruled on
    ("docs/reports/open-findings.md", "notes", False),
    ("docs/reports/closed-findings.md", "verdict", True),
)

#: dokimasia's registers. Eight tables across two files, of which six are rows;
#: `issues.md` also carries a legend and a metrics table, which are not.
DOKIMASIA_REGISTERS = (
    # file, the table's headings, {field: heading}, defaults
    ("docs/issues.md", ("#", "what", "found by", "what would settle it"),
     {"id": "#", "what": "what", "code": "found by"}, {"rank": "2"}),
    ("docs/issues.md", ("#", "what", "found by"),
     {"id": "#", "what": "what", "code": "found by"}, {"rank": "3"}),
    ("docs/issues.md", ("#", "ask", "kind", "why", "where argued"),
     {"id": "#", "what": "ask", "kind": "kind"}, {}),
    ("docs/issues.md", ("#", "what"), {"id": "#", "what": "what"}, {}),
    ("docs/issues.md", ("#", "what we suspected", "what settled it"),
     {"id": "#", "what": "what we suspected", "verdict": "what settled it"},
     {"settled": True}),
    ("docs/issues.md", ("#", "what", "where"),
     {"id": "#", "what": "what", "where": "where"}, {}),
    ("docs/findings.md", ("#", "what", "kind", "rank", "state"),
     {"id": "#", "what": "what", "kind": "kind", "rank": "rank",
      "state": "state"}, {}),
    ("docs/findings.md", ("#", "what we claimed", "what was true"),
     {"id": "#", "what": "what we claimed", "verdict": "what was true"},
     {"settled": True, "state": "retracted"}),
)

_ROW = re.compile(r"^\|\s*`[0-9a-f]{16}`\s*\|")


def _table(text, headings):
    """The one table in a document with exactly these headings."""
    got = [t for t in findings.tables(text) if tuple(t.headings) == tuple(headings)]
    return got[0] if len(got) == 1 else None


def _anoieu_ledger(root, rel, last, settled):
    """One of their ledgers, read faithfully: every cell kept as it is written."""
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None, None, None
    text = open(path, encoding="utf-8").read()
    table = _table(text, ("id", "owner", "code", "where", "what", last))
    if table is None:
        return None, None, None
    rows = findings.from_table(
        table,
        {"id": "id", "owner": "owner", "code": "code", "where": "where",
         "what": "what", last: last},
        defaults={"settled": True} if settled else None)
    return rows, [l for l in text.splitlines() if _ROW.match(l)], last


def _columns(last):
    return [findings.Column("id", "id", code=True),
            findings.Column("owner", "owner"),
            findings.Column("code", "code"),
            findings.Column("where", "where", code=True),
            findings.Column("what", "what"),
            findings.Column(last, last)]


def _marker(root):
    """anoieu's own `awaiting landing:` regex, borrowed for the migration.

    Their parser is what converts their prose, once. After the conversion
    nothing needs it -- which is the argument for the field, and is why this
    imports theirs instead of koine growing a regex for somebody's sentence.
    """
    path = os.path.join(root, "scripts", "landing.py")
    if not os.path.isfile(path):
        return None, None
    spec = importlib.util.spec_from_file_location("_landing2", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MARKER, mod


def check_findings_anoieu(root):
    """anoieu's real ledgers, read into a record and rendered back.

    Two readings, and the pair is the whole of the evidence. The **faithful**
    one keeps every cell as it is written, and is what proves the claim their
    topic makes a condition: rendering the record back reproduces the page, so
    nobody in cvc5 sees anything change. The **typed** one splits the verdict
    word out of its reason and lifts the landing promise out of its sentence,
    and is the migration -- printing what it costs and what it buys is the point,
    exactly as the postmortem harness prints the move to `PROTOCOL`.
    """
    print("  the findings record, against their two ledgers:")
    record = findings.Record(path=os.path.join(root, "docs/reports"))
    failures = 0
    ledgers = []
    for rel, last, settled in ANOIEU_LEDGERS:
        rows, original, _ = _anoieu_ledger(root, rel, last, settled)
        if rows is None:
            print(f"  skip {rel} -- no such ledger, or its columns have moved")
            return 0
        rendered = findings.render(rows, _columns(last))[2:]
        if rendered != original:
            bad = next(i for i, (a, b) in enumerate(zip(rendered, original))
                       if a != b)
            print(f"  FAIL {rel}: rendering row {bad + 1} back does not "
                  f"reproduce it\n       got {rendered[bad][:110]}\n"
                  f"       was {original[bad][:110]}")
            failures += 1
        else:
            print(f"  ok   {rel}: {len(rows)} row(s) read and rendered back "
                  "byte for byte -- the page does not change")
        record.findings.extend(rows)
        ledgers.append((rel, last, rows))

    todo = findings.check(record)
    kinds = collections.Counter(
        "settled, and the state is which file the row is in"
        if "inferred from where it is filed" in p.message else p.message
        for p in todo)
    print(f"  -- reading them faithfully leaves {len(todo)} thing(s) the record "
          "cannot yet be asked:")
    for message, n in kinds.most_common():
        print(f"     {n} x {message}")

    # The typed reading: the word out of the verdict, the promise out of the
    # sentence. Nothing here decides what a verdict means -- `split_verdict`
    # takes the separator off, and their own regex takes the marker out.
    marker, mod = _marker(root)
    typed = findings.Record(path=record.path)
    words, spellings = collections.Counter(), collections.Counter()
    for rel, last, rows in ledgers:
        for row in rows:
            new = findings.Finding(**{n: getattr(row, n) for n in findings.FIELDS},
                                   extra=dict(row.extra), line=row.line)
            cell = getattr(row, last)
            if row.settled and cell:
                spellings["--" if re.search(r"\s--\s", cell) else "em dash"] += 1
                word, reason = findings.split_verdict(cell)
                new.state, new.verdict, new.notes = word, reason, ""
                words[word] += 1
                if marker is not None:
                    hit = marker.search(cell)
                    if hit:
                        new.landing = findings.Landing(*hit.group(
                            "project", "branch", "commit"))
            typed.findings.append(new)

    left = findings.check(typed)
    if left:
        print(f"  FAIL the typed reading still leaves {len(left)} problem(s)")
        for p in left[:4]:
            print(f"       {p}")
        failures += 1
    else:
        print(f"  ok   typed, it checks clean: {len(typed.settled())} settled "
              f"row(s) carry one of {len(words)} verdict word(s) as a field, "
              f"where the ledger spells the separator "
              f"{' and '.join(f'{n} {k}' for k, n in spellings.most_common())}")

    if mod is not None and hasattr(mod, "read_ledger"):
        theirs = [o.id for o in mod.read_ledger(
            os.path.join(root, "docs/reports/closed-findings.md"))]
        ours = [q.label for q in findings.landings(
            typed, {p: "." for p in {f.landing.project for f in typed.findings
                                     if f.landing}})]
        if sorted(theirs) == sorted(ours):
            print(f"  ok   the {len(ours)} outstanding landing(s) a typed field "
                  "finds are the ones their regex finds -- and a typed field "
                  "cannot be reworded out of the audit")
        else:
            print(f"  FAIL landings differ: theirs {sorted(theirs)}, "
                  f"ours {sorted(ours)}")
            failures += 1

    unscanned = sum(1 for f in record.findings
                    if record.covers(f.owner, f.where) is None)
    print(f"  -- and {unscanned} row(s) sit in a record with no run declared, "
          "so nothing there can yet tell a file nobody reported on from one "
          "nobody read")
    return failures


def check_findings_dokimasia(root):
    """dokimasia's registers, against the same record.

    This is the check their topic asked for **before** anything was built: the
    two customers' registers differ more than their two postmortem logs did, and
    a format written for one ledger is a guess about the other. What it finds is
    printed whether or not it is flattering -- a result is worth more than a
    schema that fits one customer.
    """
    print("  the findings record, against their registers:")
    record = findings.Record(path=os.path.join(root, "docs"))
    seen, missed = 0, []
    for rel, headings, mapping, defaults in DOKIMASIA_REGISTERS:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            missed.append((rel, headings))
            continue
        table = _table(open(path, encoding="utf-8").read(), headings)
        if table is None:
            missed.append((rel, headings))
            continue
        rows = findings.from_table(table, mapping, defaults=defaults)
        record.findings.extend(rows)
        seen += 1
    for rel, headings in missed:
        print(f"  -- {rel}: no table headed {' | '.join(headings)} any more; "
              "their register has moved and this map is stale")
    print(f"  ok   {len(record)} row(s) read out of {seen} register(s), "
          "against column names that are theirs and not ours")

    fields = {n: sum(1 for f in record if f.get(n))
              for n in ("owner", "code", "where", "what", "state", "rank",
                        "kind", "verdict")}
    print("  -- what their rows actually fill, out of "
          f"{len(record)}: "
          + ", ".join(f"{n} {c}" for n, c in fields.items() if c))
    print("     every one of those is optional in the record, which is the "
          "result rather than the design: `where` and `owner` are anoieu's "
          "and nearly absent here, `rank` and `kind` are theirs and absent "
          "there")

    todo = findings.check(record)
    kinds = collections.Counter(
        "an id with whitespace -- these rows have no id space, and an id is "
        "carried and never minted here" if "whitespace" in p.message
        else "settled, and the state is which table the row is in"
        if "inferred from where it is filed" in p.message else p.message
        for p in todo)
    print(f"  -- and {len(todo)} thing(s) the record cannot yet be asked:")
    for message, n in kinds.most_common():
        print(f"     {n} x {message}")
    return 0


#: name -> what its real records are worth checking against
RECORDS = {
    "anoieu": check_findings_anoieu,
    "dokimasia": check_findings_dokimasia,
}


def _git(repo, *args):
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, text=True)


def _rev(repo):
    return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def _fixture(root):
    """A checkout with a landed branch, an unlanded one, and a name for neither.

    Built rather than committed: what is being compared is what git says, and a
    git repository cannot be committed inside one without becoming a submodule.
    """
    repo = os.path.join(root, "project")
    os.makedirs(repo)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
    open(os.path.join(repo, "one"), "w").write("1")
    _git(repo, "add", "one"); _git(repo, "commit", "-q", "-m", "one")
    first = _rev(repo)
    _git(repo, "checkout", "-q", "-b", "merged")
    open(os.path.join(repo, "two"), "w").write("2")
    _git(repo, "add", "two"); _git(repo, "commit", "-q", "-m", "two")
    merged = _rev(repo)
    _git(repo, "checkout", "-q", "main"); _git(repo, "merge", "-q", "--ff-only", "merged")
    _git(repo, "checkout", "-q", "-b", "pending", first)
    open(os.path.join(repo, "three"), "w").write("3")
    _git(repo, "add", "three"); _git(repo, "commit", "-q", "-m", "three")
    pending = _rev(repo)
    _git(repo, "checkout", "-q", "main")
    return repo, merged, pending


def _anoieu_says(root, repo, commit):
    """anoieu's real `landing.ask`, on our fixture. Their vocabulary, unchanged."""
    path = os.path.join(root, "scripts", "landing.py")
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location("_landing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    item = mod.Outstanding("id", "project", "branch", commit)
    mod.ask(item, repo)
    return item.state


def _dokimasia_says(root, repo, ref):
    """dokimasia's real `--status`, on our fixture. Read back off their output."""
    script = os.path.join(root, "scripts", "prompts", "process_dokimasia")
    if not os.path.isfile(script):
        return None
    p = subprocess.run(["bash", script, "--status", "--branch", ref, repo],
                       capture_output=True, text=True, timeout=60)
    text = p.stdout
    if "merged into" in text:
        return "landed"
    if "does not have" in text:
        return "ahead"
    if "is not here" in text:
        return "absent"
    return "unknown"


def check_branch(roots):
    """Both customers' branch-state code, and koine's, asked the same questions.

    This is the piece's version of the claim the other two make: the answers are
    theirs, not ours. Their two implementations disagree in one place on purpose
    -- what a ref that is not in the checkout means -- and `Query.missing` is how
    a caller says which reading it wants. Both readings are checked here.
    """
    print("the branch-state reporter, against both customers' own code:")
    root = tempfile.mkdtemp(prefix="koine-customers-")
    failures = 0
    try:
        repo, merged, pending = _fixture(root)
        # `None` means the customer does not ask that question, and is not
        # consulted about it. The last two cases are exactly that: a missing
        # commit is anoieu's question and a missing branch is dokimasia's, which
        # is the disagreement `Query.missing` exists to carry.
        cases = [
            # name, ref, commit, koine, missing, anoieu, dokimasia
            ("a landed branch", "merged", merged,
             branch.LANDED, branch.UNKNOWN, "landed", "landed"),
            ("an unlanded branch", "pending", pending,
             branch.AHEAD, branch.UNKNOWN, "not yet", "ahead"),
            ("a commit that is not here", "0" * 40, "0" * 40,
             branch.UNKNOWN, branch.UNKNOWN, "unknown", None),
            ("a branch that is not here", "never-pushed", None,
             branch.ABSENT, branch.ABSENT, None, "absent"),
        ]
        for name, ref, commit, want, missing, want_a, want_d in cases:
            got = branch.ask(branch.Query(repo=repo, ref=ref, missing=missing)).state
            if got != want:
                print(f"  FAIL {name}: koine says {got!r}, expected {want!r}")
                failures += 1
                continue
            agreed = []
            if want_a is not None and "anoieu" in roots:
                said = _anoieu_says(roots["anoieu"], repo, commit)
                if said is not None:
                    if said != want_a:
                        print(f"  FAIL {name}: anoieu says {said!r}, koine says {got!r}")
                        failures += 1
                        continue
                    agreed.append("anoieu")
            if want_d is not None and "dokimasia" in roots:
                said = _dokimasia_says(roots["dokimasia"], repo, ref)
                if said is not None:
                    if said != want_d:
                        print(f"  FAIL {name}: dokimasia says {said!r}, koine says {got!r}")
                        failures += 1
                        continue
                    agreed.append("dokimasia")
            who = " and ".join(agreed) if agreed else "nobody else asks this"
            print(f"  ok   {name} -- {got}, and so says {who}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print()
    return failures


def main(argv):
    roots, positional = {}, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and a[2:] in CUSTOMERS:
            roots[a[2:]] = argv[i + 1]
            i += 2
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            positional.append(a)
            i += 1
    for name, root in zip(CUSTOMERS, positional):
        roots.setdefault(name, root)

    if not roots:
        print(__doc__.strip().split("\n\n")[1])
        print("\nnothing to check: name a checkout of anoieu, of dokimasia, or of both.")
        return 0

    failures = 0
    for name, (build, expected, log_rel) in CUSTOMERS.items():
        root = roots.get(name)
        if root is None:
            print(f"skip {name} -- no checkout given\n")
            continue
        root = os.path.abspath(os.path.expanduser(root))
        if not os.path.isdir(root):
            print(f"FAIL {name} -- {root} is not a directory\n")
            failures += 1
            continue
        print(f"{name}, at {root}:")
        result = drift.run(build(root))
        for line in result.render():
            print(f"  {line}")
        if len(result.cases) != expected:
            print(f"  FAIL {len(result.cases)} case(s), expected {expected} -- "
                  "this spec no longer covers what their own check covered")
            failures += 1
        failures += result.failures
        failures += check_log(root, log_rel)
        failures += RECORDS[name](root)
        print()

    failures += check_branch(roots)

    print(f"-- the customers: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
