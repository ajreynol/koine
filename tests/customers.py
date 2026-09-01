#!/usr/bin/env python3
"""The two customers' real files, run against koine's implementations.

    python3 tests/customers.py ~/src/anoieu ~/src/dokimasia
    python3 tests/customers.py --anoieu ~/src/anoieu

This is the evidence for the claim koine's documents make twice: that adopting a
piece costs a customer nothing on the first day. `docs/drift.md` says koine
reproduces the prompt check each repository already had, with no case, form or
line of coverage lost; `docs/postmortem-protocol.md` says a log that passed the
old shape check still passes `SHAPE`, and prints what moving to `PROTOCOL` would
cost. Both are claims that nobody can re-run unless this exists.

It is **not** part of CI and nothing depends on it. It needs a checkout of
somebody else's repository, which `tests/run.py` deliberately does not, and it
fails when a customer moves their prompts -- which is their business, and is what
their own copy of this check is for until they drop it.

The specs below are the ones written out in `docs/drift.md`, and if the two
disagree the document is the one that is right.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from koine import drift, postmortem  # noqa: E402

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
            drift.Case("scripts/check_anoieu, one id", "one",
                       ["bash", "scripts/prompts/check_anoieu", "--show-prompt", "ID"],
                       forms={SWEEP: False},
                       rules=[drift.sub("anoieu-ID", "BRANCH")]),
            drift.Case("scripts/check_anoieu, the sweep", "one",
                       ["bash", "scripts/prompts/check_anoieu", "--show-prompt"],
                       forms={SWEEP: True},
                       rules=[drift.sub("PROJECT", "anoieu"),
                              drift.sub("anoieu-findings", "BRANCH")]),
            drift.Case("scripts/process_anoieu", "two",
                       ["bash", "scripts/prompts/process_anoieu", "--show-prompt",
                        "--no-check", root],
                       forms={POSTM: False}, rules=two),
            drift.Case("scripts/process_anoieu --no-postm", "two",
                       ["bash", "scripts/prompts/process_anoieu", "--show-prompt",
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
            drift.Case("scripts/check_dokimasia, one row", "one",
                       ["bash", "scripts/check_dokimasia", "--show-prompt", "ID"],
                       forms={SWEEP: False},
                       rules=[drift.sub("dokimasia-ID", "BRANCH")]),
            drift.Case("scripts/check_dokimasia, the sweep", "one",
                       ["bash", "scripts/check_dokimasia", "--show-prompt"],
                       forms={SWEEP: True},
                       rules=[drift.sub("dokimasia-findings", "BRANCH")]),
            two("scripts/process_dokimasia, one row",
                ["bash", "scripts/process_dokimasia", "--show-prompt",
                 "--link", "LINK", "ID"], False, False),
            two("scripts/process_dokimasia, every block",
                ["bash", "scripts/process_dokimasia", "--show-prompt",
                 "--link", "LINK"], True, False),
            two("scripts/process_dokimasia --no-postm",
                ["bash", "scripts/process_dokimasia", "--show-prompt", "--no-postm",
                 "--link", "LINK", "ID"], False, True),
            two("scripts/process_dokimasia, from a checkout",
                ["bash", "scripts/process_dokimasia", "--show-prompt", root, "ID"],
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
        print()

    print(f"-- the customers: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
