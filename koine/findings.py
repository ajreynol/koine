"""The findings record: one row per claim, written by more than one producer.

A tool here raises findings about somebody else's project and keeps a ledger of
them. Both customers keep one; both keep it as a markdown table; and in both of
them **the state of a row is a field nowhere** -- it is inferred from which file
or which table the row is in, and then qualified in prose. anoieu measured what
that costs, at `442bb67`: 39 open rows and 43 closed, seven distinct verdict
words separated from their reasons two different ways, five different phrasings
of a state in the notes column, and two regexes in `scripts/landing.py` that
parse a markdown cell back into data -- guarded by a test that fails if a
sentence is *reworded*, because a reworded marker drops a row from the audit
while leaving the debt owed.

This module is the record under that table. It holds what a row is, what a run
is, and the four operations a second producer makes necessary: read it, write it
back canonically, merge two of them, and say per id whether two producers agreed.

**It does not hold the ledger.** The rows stay in the customer's tree, under
their name, settled by them. Nothing here says what a finding is, when one may
be raised, what rank it carries or what closes it -- those differ because the
subjects differ, and they are the half koine has never had an opinion about.
[`docs/findings-record.md`](../docs/findings-record.md) is the definition, and
where the two disagree the document is right.

## Why the format is lines of JSON

Four constraints, and the fourth is the one that decides it.

1. **Two producers, one record.** A program and an agent write the same record
   against the same targets, and *did they agree* has to be answerable by id
   rather than by line of file. `agree` answers it.
2. **Appending is a merge.** Two runs, two machines, the same finding seen by
   both. The key is the id, which is **carried and never minted here**.
3. **Not-reported and not-scanned are different.** A row absent from a run means
   nothing until you know whether the run covered its file, so the record carries
   `Run`s as well as rows.
4. **It has to be readable in a browser with no clone.** One JSON object per
   line: github.com serves it as plain text, a diff reviews one row at a time,
   and a 528-character note with an em-dash in it survives without quoting
   games. A JSON array would make every append touch its neighbour; CSV would
   make the note the problem.

The generated markdown table stays what a reader is pointed at. `render` writes
one, and the customer harness demonstrates that rendering a real ledger back
from its record reproduces it exactly -- because a record that changes what
somebody in cvc5 sees when they open a page is one nobody should adopt.

## Calling it

    from koine import findings

    record = findings.read("docs/reports/findings.jsonl")
    problems = findings.check(record)

    both = findings.merge(record, findings.read(other))
    how  = findings.agree(record, other)          # per id: same, differs, absent

    findings.write(record, "docs/reports/findings.jsonl")
    print("\n".join(findings.render(record.findings, ANOIEU_COLUMNS)))

`report` prints and returns a count, the way `koine.drift.report` and
`koine.postmortem.report` do, so a customer's test runner calls all three alike.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "FIELDS", "COMPARED", "BY", "PROGRAM", "AGENT", "PERSON",
    "Finding", "Landing", "Target", "Run", "Record", "Problem",
    "Divergence", "Agreement", "Merge", "Column", "Table",
    "read", "parse", "write", "dumps", "check", "report",
    "merge", "agree", "landings", "render", "tables", "from_table",
    "split_verdict",
]

#: Who wrote a run. Three values, closed, and the only vocabulary this format
#: defines. A program and an agent are the two producers the record exists to
#: compare; a person is the third because both customers' closed ledgers are
#: written by hand at a review step, and a hand-written row that claimed to be a
#: program's output would make the comparison a lie.
PROGRAM, AGENT, PERSON = "program", "agent", "person"
BY = {
    PROGRAM: "a check ran and derived the row",
    AGENT: "an agent was asked the same question against the same targets",
    PERSON: "somebody wrote or ruled on the row by hand",
}

#: A row's fields, in the order a canonical line writes them. Everything except
#: `id` is optional, because the two customers' registers agree on less than
#: either would guess: dokimasia's rows mostly have no `where` and no `owner`,
#: anoieu's have no `rank` and no `kind`.
FIELDS = (
    "id",          # carried from the producer. Never minted here
    "owner",       # whose project the claim is about, by the ecosystem's ids
    "code",        # what produced it: a check id, a tool's name, `design note`
    "where",       # `path:line` inside the owner's tree, or nothing
    "what",        # the claim itself
    "state",       # the producer's own word for where the row stands
    "settled",     # whether the producer considers it ruled on
    "verdict",     # the reason behind `state`
    "notes",       # what the row carries that is not a reason for its state
    "rank",        # carried, never interpreted
    "kind",        # carried, never interpreted
    "run",         # the id of the run that last saw it
    "checked_at",  # the commit in somebody else's tree `state` was checked at
    "landing",     # a change promised but not seen to land
)

#: The fields two producers are compared on. `run` and `checked_at` are facts
#: about the run rather than about the finding, and `notes` is prose that two
#: producers will never write the same way -- comparing them would report a
#: divergence on every row and teach nobody anything.
COMPARED = ("owner", "code", "where", "what", "state", "settled", "verdict",
            "rank", "kind")

_ID_BAD = re.compile(r"\s")
#: The separator between a verdict word and its reason. Both spellings, because
#: anoieu's ledger carries 36 of the first and 7 of the second and neither is
#: wrong -- which is the whole argument for the word being a field.
_VERDICT_SPLIT = re.compile(r"\s+(?:—|--)\s+")


# -- the record --------------------------------------------------------------

@dataclass
class Landing:
    """A change a row was closed on, which has not been seen to land.

    anoieu writes this into a verdict cell as `awaiting landing: <project>
    <branch> <commit>` and reads it back out with a regex, and `tests/run.py`
    fails if the sentence is reworded. It is a `koine.branch.Query` with the
    quotes taken off; `landings` hands the whole record to that module.
    """
    project: str
    branch: str
    commit: str = ""

    def as_dict(self) -> Dict[str, str]:
        out = {"project": self.project, "branch": self.branch}
        if self.commit:
            out["commit"] = self.commit
        return out


@dataclass
class Finding:
    """One claim. A row, with its state as a field rather than as a file."""
    id: str
    owner: str = ""
    code: str = ""
    where: str = ""
    what: str = ""
    state: str = ""
    settled: bool = False
    verdict: str = ""
    notes: str = ""
    rank: str = ""
    kind: str = ""
    run: str = ""
    checked_at: str = ""
    landing: Optional[Landing] = None
    #: Whatever the producer carried that this format does not name. Kept, and
    #: written back, because a record that drops a column is a record that
    #: cannot be adopted without first losing something.
    extra: Dict[str, object] = field(default_factory=dict)
    line: int = 0

    @property
    def path(self) -> str:
        """The file part of `where`, or nothing."""
        return self.where.rsplit(":", 1)[0] if self.where else ""

    def get(self, name: str):
        if name in FIELDS:
            return getattr(self, name)
        return self.extra.get(name, "")

    def as_dict(self) -> Dict[str, object]:
        out: Dict[str, object] = {}
        for name in FIELDS:
            value = getattr(self, name)
            if name == "landing":
                if value is not None:
                    out[name] = value.as_dict()
            elif name == "settled":
                out[name] = bool(value)
            elif value not in ("", None):
                out[name] = value
        for key in sorted(self.extra):
            if key not in out:
                out[key] = self.extra[key]
        return out


@dataclass
class Target:
    """Something a run looked at: a project, optionally a subtree of it.

    `commit` is what it was at. It is here because a verdict is a claim about
    the world and can go stale: three rows sat closed as *fixed upstream* on a
    fix that never landed, for three months, and the commit the verdict was
    checked at had nowhere to live except a sentence.
    """
    project: str
    root: str = ""
    commit: str = ""

    def covers(self, owner: str, where: str = "") -> bool:
        if owner and self.project and owner != self.project:
            return False
        if not self.root:
            return True
        if not where:
            return False
        path = where.rsplit(":", 1)[0]
        return path == self.root or path.startswith(self.root.rstrip("/") + "/")

    def as_dict(self) -> Dict[str, str]:
        out = {"project": self.project}
        for name in ("root", "commit"):
            if getattr(self, name):
                out[name] = getattr(self, name)
        return out


@dataclass
class Run:
    """What was scanned, by whom, and when.

    Without this a row's absence says nothing: two people scan different targets
    and the difference is invisible. A run that names no target is refused by
    `check` for exactly that reason.
    """
    id: str
    by: str = PROGRAM
    producer: str = ""
    when: str = ""
    targets: List[Target] = field(default_factory=list)
    #: Which checks ran. Empty means *not stated*, never *none*.
    codes: List[str] = field(default_factory=list)
    line: int = 0

    def covers(self, owner: str, where: str = "") -> bool:
        return any(t.covers(owner, where) for t in self.targets)

    def as_dict(self) -> Dict[str, object]:
        out: Dict[str, object] = {"type": "run", "id": self.id, "by": self.by}
        if self.producer:
            out["producer"] = self.producer
        if self.when:
            out["when"] = self.when
        out["targets"] = [t.as_dict() for t in self.targets]
        if self.codes:
            out["codes"] = list(self.codes)
        return out


@dataclass
class Record:
    """Runs and rows, in the order the file carries them.

    **Order is the ledger's, not this module's.** Generation is additive at both
    customers -- a row is appended and never moved -- so writing the record back
    preserves it, and the sorted form is produced for comparison instead of
    being written to disk.
    """
    path: Optional[str] = None
    runs: List[Run] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)

    def __iter__(self):
        return iter(self.findings)

    def __len__(self):
        return len(self.findings)

    def by_id(self) -> Dict[str, Finding]:
        return {f.id: f for f in self.findings}

    def run(self, run_id: str) -> Optional[Run]:
        for r in self.runs:
            if r.id == run_id:
                return r
        return None

    def open(self) -> List[Finding]:
        return [f for f in self.findings if not f.settled]

    def settled(self) -> List[Finding]:
        return [f for f in self.findings if f.settled]

    def covers(self, owner: str, where: str = "") -> Optional[bool]:
        """Did any run look here? `None` when the record does not say.

        Three answers rather than two, and the third is the point of the field:
        a record with no runs cannot tell a clean file from an unscanned one,
        and reporting that as *covered* is the failure the audit exists to
        prevent.
        """
        if not self.runs:
            return None
        return any(r.covers(owner, where) for r in self.runs)

    def sorted(self) -> List[Finding]:
        """The comparison order: by id, and by nothing else.

        By id because it is the one field that survives an edit elsewhere in the
        file. Sorting by path would reorder the record every time somebody
        inserted a line in somebody else's tree.
        """
        return sorted(self.findings, key=lambda f: f.id)


@dataclass
class Problem:
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.where}: {self.message}"


# -- reading -----------------------------------------------------------------

def _landing(value) -> Optional[Landing]:
    if not value:
        return None
    if isinstance(value, str):                     # `project branch commit`
        parts = value.split()
        parts += [""] * (3 - len(parts))
        return Landing(parts[0], parts[1], parts[2])
    return Landing(str(value.get("project", "")), str(value.get("branch", "")),
                   str(value.get("commit", "")))


def _finding(obj: Dict[str, object], line: int = 0) -> Finding:
    known = {k: v for k, v in obj.items() if k in FIELDS}
    extra = {k: v for k, v in obj.items()
             if k not in FIELDS and k != "type"}
    out = Finding(id=str(known.get("id", "")), extra=extra, line=line)
    for name in FIELDS:
        if name in ("id", "landing", "settled") or name not in known:
            continue
        setattr(out, name, str(known[name]))
    out.settled = bool(known.get("settled", False))
    out.landing = _landing(known.get("landing"))
    return out


def _run(obj: Dict[str, object], line: int = 0) -> Run:
    targets = []
    for t in obj.get("targets") or []:
        if isinstance(t, str):
            targets.append(Target(t))
        else:
            targets.append(Target(str(t.get("project", "")),
                                  str(t.get("root", "")),
                                  str(t.get("commit", ""))))
    return Run(id=str(obj.get("id", "")), by=str(obj.get("by", PROGRAM)),
               producer=str(obj.get("producer", "")),
               when=str(obj.get("when", "")), targets=targets,
               codes=[str(c) for c in obj.get("codes") or []], line=line)


def parse(text: str, path: Optional[str] = None) -> Record:
    """Read a record. One JSON object per line; blanks and `#` lines ignored.

    A line that will not parse raises, rather than being skipped: a record that
    silently drops a row it could not read is worse than one that will not open.
    """
    record = Record(path=path)
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            obj = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"{path or 'the record'}:{n}: {exc}") from None
        if not isinstance(obj, dict):
            raise ValueError(f"{path or 'the record'}:{n}: not an object")
        if obj.get("type") == "run":
            record.runs.append(_run(obj, n))
        else:
            record.findings.append(_finding(obj, n))
    return record


def read(path: str) -> Record:
    with open(path, encoding="utf-8") as fh:
        return parse(fh.read(), path)


# -- writing -----------------------------------------------------------------

def dumps(record: Record, order: Optional[Sequence[Finding]] = None) -> str:
    """The canonical form: runs first, then rows, one object per line.

    Canonical means every producer writing the same record produces the same
    bytes -- fields in `FIELDS` order, unstated ones omitted, the producer's own
    columns after them in sorted order, no trailing whitespace, `\\n` endings.
    That is what makes *did the two agree* a question a diff can be asked.

    Runs come first so that somebody reading the raw file in a browser learns
    what was scanned before they read what was found.
    """
    lines = [json.dumps(r.as_dict(), ensure_ascii=False) for r in record.runs]
    rows = record.findings if order is None else order
    lines += [json.dumps(f.as_dict(), ensure_ascii=False) for f in rows]
    return "".join(line + "\n" for line in lines)


def write(record: Record, path: str, order: Optional[Sequence[Finding]] = None) -> int:
    """Write it, and return the number of rows written."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(dumps(record, order))
    return len(record.findings if order is None else order)


# -- checking ----------------------------------------------------------------

def check(record: Record, require_runs: bool = False) -> List[Problem]:
    """What the record gets wrong.

    Nothing here is a judgement about a finding. Every rule is about whether the
    record can be *asked* something: an id that cannot be a key, a run that
    cannot answer what it covered, a state that is settled and does not say so.
    """
    problems: List[Problem] = []

    def bad(where, message):
        problems.append(Problem(where, message))

    name = record.path or "the record"
    seen_runs: Dict[str, Run] = {}
    for run in record.runs:
        where = f"{name}:{run.line}" if run.line else f"run {run.id!r}"
        if not run.id:
            bad(where, "a run with no id; nothing can refer to it")
        elif run.id in seen_runs:
            bad(where, f"run id {run.id!r} is used twice")
        else:
            seen_runs[run.id] = run
        if run.by not in BY:
            bad(where, f"by is {run.by!r}, not one of {', '.join(sorted(BY))}")
        if not run.targets:
            bad(where, "a run that names no target; a row's absence from it "
                       "cannot then be told from a file it never read")
        for target in run.targets:
            if not target.project:
                bad(where, "a target with no project")

    seen: Dict[str, Finding] = {}
    for f in record.findings:
        where = f"{name}:{f.line}" if f.line else f"{f.id!r}"
        if not f.id:
            bad(where, "a row with no id; the id is the merge key and is "
                       "carried from the producer, never minted here")
        elif _ID_BAD.search(f.id):
            bad(where, f"id {f.id!r} carries whitespace")
        elif f.id in seen:
            bad(where, f"id {f.id!r} is used twice; appending is a merge")
        else:
            seen[f.id] = f
        if not f.what:
            bad(where, "a row that does not say what it claims")
        if f.settled and not f.state:
            bad(where, "settled, and no **state**; a row whose state is "
                       "inferred from where it is filed is the defect this "
                       "record exists to remove")
        if f.landing is not None:
            if not f.landing.project or not f.landing.branch:
                bad(where, "a landing with no project or no branch; it has to "
                           "be answerable as a branch query")
            if not f.landing.commit:
                bad(where, "a landing with no commit; a promise nothing can "
                           "re-derive is the shape that went unnoticed for "
                           "three months")
        if f.run and record.runs and f.run not in seen_runs:
            bad(where, f"names run {f.run!r}, which this record does not carry")

    if require_runs and not record.runs:
        bad(name, "no runs; this record cannot tell a row nobody reported "
                  "from a file nobody scanned")
    return problems


def report(record: Record, require_runs: bool = False, out=None) -> int:
    """Print it and return the count, the way the other modules do."""
    import sys
    stream = sys.stdout if out is None else out
    problems = check(record, require_runs=require_runs)
    name = record.path or "the record"
    for problem in problems:
        print(f"FAIL {problem}", file=stream)
    if not problems:
        print(f"ok   {name}: {len(record.findings)} row(s), "
              f"{len(record.settled())} settled, {len(record.runs)} run(s)",
              file=stream)
    print(f"-- the findings record: {len(record.findings)} row(s), "
          f"{len(problems)} failure(s)", file=stream)
    return len(problems)


# -- appending, which is a merge ---------------------------------------------

@dataclass
class Merge:
    """The result of folding one record into another.

    `conflicts` is the part worth reading. A field both records state and state
    differently is **not resolved here**: the base keeps its value and the
    disagreement is handed back, because picking between two producers is a
    judgement and this module reads files.
    """
    record: Record
    added: List[str] = field(default_factory=list)
    updated: List[Tuple[str, str]] = field(default_factory=list)
    conflicts: List["Divergence"] = field(default_factory=list)

    @property
    def failures(self) -> int:
        return len(self.conflicts)

    def render(self) -> List[str]:
        lines = [f"-- merged: {len(self.added)} added, "
                 f"{len(self.updated)} field(s) filled, "
                 f"{len(self.conflicts)} conflict(s)"]
        for d in self.conflicts:
            lines.append("   " + str(d))
        return lines


def merge(base: Record, incoming: Record) -> Merge:
    """Fold `incoming` into a copy of `base`, keyed on id.

    Four rules, and they are the ones both customers' generators already follow
    by hand:

    * a new id is **appended**, never inserted -- generation is additive, so a
      finding cannot vanish and a row's neighbours do not move;
    * a field `incoming` states and `base` leaves empty is **filled**;
    * a field both state, differently, is a **conflict**: `base` keeps its value
      and the divergence is reported;
    * nothing is ever removed, and `settled` never goes back to false here -- a
      reopen is somebody's decision, not a merge's.
    """
    out = Record(path=base.path, runs=list(base.runs),
                 findings=[_copy(f) for f in base.findings])
    have_run = {r.id for r in out.runs}
    for run in incoming.runs:
        if run.id not in have_run:
            out.runs.append(run)
            have_run.add(run.id)

    index = {f.id: f for f in out.findings}
    result = Merge(record=out)
    for new in incoming.findings:
        old = index.get(new.id)
        if old is None:
            copy = _copy(new)
            out.findings.append(copy)
            index[new.id] = copy
            result.added.append(new.id)
            continue
        for name in FIELDS:
            if name in ("id", "settled"):
                continue
            mine, theirs = getattr(old, name), getattr(new, name)
            if theirs in ("", None):
                continue
            if mine in ("", None):
                setattr(old, name, theirs)
                result.updated.append((new.id, name))
            elif mine != theirs:
                result.conflicts.append(
                    Divergence(new.id, name, _show(mine), _show(theirs)))
        for key, value in new.extra.items():
            if key not in old.extra:
                old.extra[key] = value
                result.updated.append((new.id, key))
            elif old.extra[key] != value:
                result.conflicts.append(
                    Divergence(new.id, key, _show(old.extra[key]), _show(value)))
        if new.settled and not old.settled:
            old.settled = True
            result.updated.append((new.id, "settled"))
        elif old.settled and not new.settled:
            result.conflicts.append(
                Divergence(new.id, "settled", "true", "false"))
    return result


def _copy(f: Finding) -> Finding:
    out = Finding(**{**{n: getattr(f, n) for n in FIELDS},
                     "extra": dict(f.extra), "line": f.line})
    if f.landing is not None:
        out.landing = Landing(f.landing.project, f.landing.branch,
                              f.landing.commit)
    return out


def _show(value) -> str:
    if isinstance(value, Landing):
        return f"{value.project} {value.branch} {value.commit}".strip()
    return str(value)


# -- did the two producers agree ---------------------------------------------

@dataclass
class Divergence:
    id: str
    field: str
    a: str
    b: str

    def __str__(self) -> str:
        return f"{self.id} {self.field}: {self.a!r} / {self.b!r}"


@dataclass
class Agreement:
    """Per id, and never per line of file.

    The two lists of absences are the reason `Run` exists. A row one producer
    has and the other does not is **two different results** -- the other one
    read the file and did not report it, or never read the file at all -- and
    until the record says which, the comparison is not evidence of anything.
    """
    same: List[str] = field(default_factory=list)
    differ: List[Divergence] = field(default_factory=list)
    not_reported_by_b: List[str] = field(default_factory=list)
    not_scanned_by_b: List[str] = field(default_factory=list)
    not_reported_by_a: List[str] = field(default_factory=list)
    not_scanned_by_a: List[str] = field(default_factory=list)

    @property
    def ids_that_differ(self) -> List[str]:
        out = []
        for d in self.differ:
            if d.id not in out:
                out.append(d.id)
        return out

    @property
    def undecidable(self) -> int:
        """Absences neither producer's runs can account for."""
        return len(self.not_scanned_by_a) + len(self.not_scanned_by_b)

    def render(self) -> List[str]:
        lines = [f"-- {len(self.same)} agreed, "
                 f"{len(self.ids_that_differ)} differ, "
                 f"{len(self.not_reported_by_b) + len(self.not_reported_by_a)} "
                 f"reported by one and not the other, "
                 f"{self.undecidable} outside what the other scanned"]
        for d in self.differ:
            lines.append("   " + str(d))
        for i in self.not_reported_by_b:
            lines.append(f"   {i}: a only -- b scanned it and did not report it")
        for i in self.not_scanned_by_b:
            lines.append(f"   {i}: a only -- b never scanned there")
        for i in self.not_reported_by_a:
            lines.append(f"   {i}: b only -- a scanned it and did not report it")
        for i in self.not_scanned_by_a:
            lines.append(f"   {i}: b only -- a never scanned there")
        return lines


def agree(a: Record, b: Record,
          fields: Sequence[str] = COMPARED) -> Agreement:
    """Compare two records row by row. Decides nothing about who is right."""
    left, right = a.by_id(), b.by_id()
    out = Agreement()
    for fid in sorted(set(left) | set(right)):
        one, two = left.get(fid), right.get(fid)
        if one is not None and two is not None:
            found = [Divergence(fid, name, _show(one.get(name)),
                                _show(two.get(name)))
                     for name in fields
                     if _show(one.get(name)) != _show(two.get(name))]
            if found:
                out.differ.extend(found)
            else:
                out.same.append(fid)
        elif two is None:
            covered = b.covers(one.owner, one.where)
            (out.not_reported_by_b if covered else out.not_scanned_by_b).append(fid)
        else:
            covered = a.covers(two.owner, two.where)
            (out.not_reported_by_a if covered else out.not_scanned_by_a).append(fid)
    return out


# -- what a landing is, in the other module's terms ---------------------------

def landings(record: Record, checkouts: Dict[str, str],
             missing: str = "unknown") -> List[object]:
    """Every outstanding landing, as `koine.branch.Query` values.

    This is the regex deleted. anoieu reads `awaiting landing: <project>
    <branch> <commit>` back out of a markdown cell and guards the *wording* of
    that sentence with a test; a typed field needs neither. `checkouts` maps a
    project id to where it is on this machine, which stays the caller's --
    nothing here knows where anybody's clone lives.
    """
    from koine import branch
    out = []
    for f in record.findings:
        if f.landing is None:
            continue
        repo = checkouts.get(f.landing.project)
        if repo is None:
            continue
        out.append(branch.Query(repo=repo, ref=f.landing.commit or f.landing.branch,
                                label=f.id, missing=missing))
    return out


# -- the markdown a reader is pointed at --------------------------------------

@dataclass
class Column:
    """One column of a rendered table: its heading, its field, its quoting."""
    heading: str
    field: str
    code: bool = False          # wrap the cell in backticks

    def cell(self, f: Finding) -> str:
        value = f.get(self.field)
        if isinstance(value, bool):
            value = "yes" if value else ""
        text = "" if value is None else str(value)
        return f"`{text}`" if self.code and text else text


def render(rows: Iterable[Finding], columns: Sequence[Column]) -> List[str]:
    """A markdown table, in the record's order.

    The page a reader is pointed at should not change when a record arrives
    under it, so this renders rather than redesigns: the columns, their order
    and their quoting are the caller's, because they are the customer's page.
    """
    cols = list(columns)
    out = ["| " + " | ".join(c.heading for c in cols) + " |",
           "| " + " | ".join("---" for c in cols) + " |"]
    for f in rows:
        out.append("| " + " | ".join(c.cell(f) for c in cols) + " |")
    return out


# -- reading the table a customer already has ---------------------------------

@dataclass
class Table:
    """A markdown table found in a document: its headings and its cells."""
    headings: List[str]
    rows: List[List[str]] = field(default_factory=list)
    line: int = 0

    def column(self, heading: str) -> int:
        return self.headings.index(heading)


_DIVIDER = re.compile(r"^\|(?:\s*:?-{3,}:?\s*\|)+\s*$")


def _cells(line: str) -> List[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(text: str) -> List[Table]:
    """Every markdown table in a document, in order.

    A customer's register is a document with several tables in it, only some of
    which are rows -- dokimasia's `issues.md` carries six, one of them a legend.
    So this finds them all and the caller says which is which; guessing would be
    this module deciding what counts as a finding, which is not its to decide.
    """
    out: List[Table] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith("|") and _DIVIDER.match(lines[i + 1]):
            table = Table(headings=_cells(lines[i]), line=i + 1)
            width = len(table.headings)
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                cells = _cells(lines[i])
                if len(cells) == width:
                    table.rows.append(cells)
                i += 1
            out.append(table)
            continue
        i += 1
    return out


def split_verdict(cell: str) -> Tuple[str, str]:
    """A verdict cell, split into the word and the reason behind it.

    anoieu's closed ledger carries seven distinct verdict words separated from
    their reasons **two different ways**, 36 rows one way and 7 the other, and
    nothing can ask which word a row carries. Both spellings are accepted here
    and neither is blessed -- the point is that after this runs the word is a
    field and the separator stops mattering.

    **Which cell is a verdict is the caller's to say.** This splits prose it is
    handed; it does not decide that a column holds one.
    """
    parts = _VERDICT_SPLIT.split(cell.strip(), maxsplit=1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _unquote(cell: str) -> str:
    text = cell.strip()
    if len(text) > 1 and text.startswith("`") and text.endswith("`"):
        return text[1:-1]
    return text


def from_table(table: Table, mapping: Dict[str, str],
               defaults: Optional[Dict[str, object]] = None,
               keep_extra: bool = True,
               unquote: Sequence[str] = ("id", "where")) -> List[Finding]:
    """Rows out of a table a customer already keeps, by a column map.

    `mapping` is `{field: heading}` -- the customer's column names, not koine's,
    because the record is being fitted to the ledger rather than the other way
    round. A heading the mapping does not name is carried into `extra` under its
    own name, so nothing is lost on the way in: a migration that drops a column
    is one nobody can be asked to run.
    """
    out: List[Finding] = []
    index = {}
    for field_name, heading in mapping.items():
        if heading in table.headings:
            index[field_name] = table.headings.index(heading)
    named = set(index.values())
    for n, cells in enumerate(table.rows):
        f = Finding(id="")
        for field_name, col in index.items():
            value = cells[col]
            if field_name in unquote:
                value = _unquote(value)
            if field_name == "settled":
                setattr(f, field_name, bool(value))
            else:
                setattr(f, field_name, value)
        for key, value in (defaults or {}).items():
            if not getattr(f, key, None) and key in FIELDS:
                setattr(f, key, value)
        if keep_extra:
            for col, heading in enumerate(table.headings):
                if col not in named and heading and cells[col]:
                    f.extra[heading] = cells[col]
        f.line = table.line + 2 + n
        out.append(f)
    return out
