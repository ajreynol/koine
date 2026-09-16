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

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from koine import branch, drift, postmortem  # noqa: E402

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
        print()

    failures += check_branch(roots)

    print(f"-- the customers: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
