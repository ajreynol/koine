"""The prompt-drift check: a script still says what its document says it says.

A tool that reports findings sends a prompt to whoever owns the file. The prompt
is defined in a document -- that is the version the far end was promised -- and a
script under `scripts/` carries a copy so nobody has to paste one. A copy that
has drifted is worse than no copy, because the drift is invisible from the side
that matters: somebody in the other project reading a prompt they were sent.

So the document is the definition, and this compares what each script actually
prints to it, in every form either can take.

Two things are compared and one is not. The whole of a prompt is compared, in
every form. The lines a script exists to fill in -- which rows, which branch --
are not, because filling them in is the point of the script.

## The shape a customer describes

A document writes both sides of an alternative with a marker line between them:

    Address every open row.
    -- or, for one row --
    Find the row whose id is ID, and address that row only.

Resolving the marker one way or the other gives the form a particular invocation
should print. Resolving rather than anchoring part way down is what lets the
comparison cover every line of a prompt; a check that starts matching at the
third paragraph will not notice a stale one above it.

## Calling it

Build a `Spec` and hand it to `report`, which prints and returns a failure count:

    import koine_drift as drift

    SPEC = drift.Spec(
        root=ROOT,
        document="docs/reports/reporting-workflow.md",
        prompts={"one": drift.Prompt("### Prompt one", "### Prompt two")},
        cases=[drift.Case(
            name="check_anoieu, one id",
            prompt="one",
            argv=["bash", "scripts/prompts/check_anoieu", "--show-prompt", "ID"],
            forms={"-- or, for the sweep form --": False},
            rules=[drift.sub("anoieu-ID", "BRANCH")],
        )],
    )

    failures = drift.report(SPEC)

`run` returns the same results without printing, for a caller that has its own
output. Neither writes anything anywhere.

## What this asks of a script

One thing: `--show-prompt` prints the prompt and exits, running nothing else and
reading nothing it does not have to. That is what makes the check cheap and what
makes it honest -- it compares the text a real invocation produces rather than a
second copy kept for testing.
"""

from __future__ import annotations

import difflib
import re
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

__all__ = [
    "Spec", "Prompt", "Case", "CaseResult", "Report",
    "Rule", "sub", "after", "drop_paragraphs",
    "body", "resolve", "spoken", "run", "report",
]

# How much of a failed script's own output is quoted back. Nothing depends on
# the number; it is here so the two customers stop having different ones.
ERROR_CHARS = 200

DOCUMENT = "document"
SCRIPT = "script"
BOTH = "both"


# -- the document ------------------------------------------------------------

def body(doc: str, start: str, end: str) -> str:
    """The fenced ```text block between two headings.

    `start` and `end` are literal text, found by search rather than parsed, so a
    customer names its headings however it writes them.
    """
    try:
        a = doc.index(start)
    except ValueError:
        raise LookupError(f"the document has no {start!r}") from None
    try:
        b = doc.index(end, a)
    except ValueError:
        raise LookupError(f"the document has no {end!r} after {start!r}") from None
    m = re.search(r"```text\n(.*?)\n```", doc[a:b], re.S)
    if not m:
        raise LookupError(f"no ```text block between {start!r} and {end!r}")
    return m.group(1)


def resolve(text: str, marker: str, alt: bool) -> str:
    """Keep one side of an alternatives block and drop the marker.

    The block is the run of lines before the marker back to the last blank line,
    the marker, and the run after it up to the next blank line. `alt` false keeps
    what is written above the marker, true keeps what is written below it.
    """
    lines = text.split("\n")
    try:
        i = next(k for k, l in enumerate(lines) if l.strip() == marker)
    except StopIteration:
        raise LookupError(f"the prompt has no marker line {marker!r}") from None
    a = max((k for k in range(i) if not lines[k].strip()), default=-1) + 1
    b = next((k for k in range(i + 1, len(lines)) if not lines[k].strip()), len(lines))
    keep = lines[i + 1:b] if alt else lines[a:i]
    return "\n".join(lines[:a] + keep + lines[b:])


# -- the script --------------------------------------------------------------

def spoken(argv: Sequence[str], cwd: str) -> str:
    """What a script prints under `--show-prompt`.

    A script that fails is not silently a script that printed nothing: the
    failure is returned as text so it lands in the diff, where somebody reads it.
    """
    try:
        got = subprocess.run(list(argv), cwd=cwd, capture_output=True, text=True)
    except OSError as exc:
        return f"!! {argv[0]}: {exc}"
    if got.returncode != 0:
        return f"!! {argv[0]}: {(got.stderr or got.stdout).strip()[:ERROR_CHARS]}"
    return got.stdout


# -- normalising -------------------------------------------------------------

@dataclass(frozen=True)
class Rule:
    """One canonicalisation, and which side of the comparison it applies to.

    `side` is `both` unless a customer means the asymmetry. Applying a rule to
    both sides says *these two spellings mean the same thing*, which is almost
    always what is meant and cannot hide a difference that is only on one side.
    """
    name: str
    fn: Callable[[str], str]
    side: str = BOTH

    def apply(self, text: str, side: str) -> str:
        return self.fn(text) if self.side in (BOTH, side) else text


def sub(old: str, new: str, side: str = BOTH) -> Rule:
    """Two spellings of the same thing -- usually a branch name a script filled in."""
    return Rule(f"sub({old!r} -> {new!r})", lambda s: s.replace(old, new), side)


def after(marker: str, side: str = BOTH) -> Rule:
    """Keep the text from `marker` on.

    For the one case that is legitimate: an opening the document and the script
    word differently on purpose, where everything below it may not differ. Text
    with no `marker` in it is left alone rather than emptied, so a script that
    failed still shows its failure instead of vanishing into a match.
    """
    def cut(s: str) -> str:
        i = s.find(marker)
        return s if i < 0 else s[i:]
    return Rule(f"after({marker!r})", cut, side)


def drop_paragraphs(prefixes: Sequence[str], side: str = BOTH) -> Rule:
    """Drop blank-line-separated paragraphs starting with any of these.

    For the sentence each side words for the run it is doing.
    """
    keep = tuple(prefixes)

    def cut(s: str) -> str:
        return "\n\n".join(
            p for p in s.split("\n\n") if not p.lstrip().startswith(keep)
        )
    return Rule(f"drop_paragraphs({list(keep)})", cut, side)


# -- the spec ----------------------------------------------------------------

@dataclass(frozen=True)
class Prompt:
    """Where a prompt is in the document: the heading it is under, and the next one."""
    start: str
    end: str


@dataclass(frozen=True)
class Case:
    """One invocation of one script, and the form of the document it should print.

    `forms` maps each marker in the prompt to which side this invocation takes:
    false for what is written above the marker, true for below. Every marker in
    the prompt must appear, so adding an alternative to a document without saying
    which cases take which side is an error rather than a silent half-check.
    """
    name: str
    prompt: str
    argv: Sequence[str]
    forms: Dict[str, bool] = field(default_factory=dict)
    rules: Sequence[Rule] = ()


@dataclass(frozen=True)
class Spec:
    """A customer's whole drift check.

    `root` is the repository the scripts are run in and the document is read
    from. `document` is relative to it.
    """
    root: str
    document: str
    prompts: Dict[str, Prompt]
    cases: Sequence[Case]
    rules: Sequence[Rule] = ()


# -- running it --------------------------------------------------------------

@dataclass
class CaseResult:
    name: str
    ok: bool
    diff: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class Report:
    document: str
    cases: List[CaseResult]

    @property
    def failures(self) -> int:
        return sum(1 for c in self.cases if not c.ok)

    def render(self) -> List[str]:
        out: List[str] = []
        for c in self.cases:
            if c.ok:
                out.append(f"ok   {c.name} says what {self.document} says")
                continue
            if c.error is not None:
                out.append(f"FAIL {c.name}: {c.error}")
                continue
            out.append(f"FAIL {c.name} has drifted from {self.document}")
            out.extend(f"     {line}" for line in c.diff)
        out.append(f"-- the outbound prompts: {self.failures} failure(s) "
                   f"in {len(self.cases)} case(s)")
        return out


def _markers(text: str) -> List[str]:
    """Every alternatives marker in a prompt, in the order written.

    The convention is a line whose whole content is `-- ... --`; recognising them
    is what lets a case be told it has missed one.
    """
    return [l.strip() for l in text.split("\n")
            if re.fullmatch(r"--\s+\S.*\S\s+--", l.strip())]


def run(spec: Spec) -> Report:
    """Compare every case, reading and running but writing nothing."""
    import os

    doc_path = os.path.join(spec.root, spec.document)
    with open(doc_path, encoding="utf-8") as fh:
        doc = fh.read()

    results: List[CaseResult] = []
    for case in spec.cases:
        try:
            prompt = spec.prompts[case.prompt]
        except KeyError:
            results.append(CaseResult(case.name, False,
                                      error=f"no prompt named {case.prompt!r}"))
            continue
        try:
            want = body(doc, prompt.start, prompt.end)
            missing = [m for m in _markers(want) if m not in case.forms]
            if missing:
                raise LookupError(
                    "the prompt has alternatives this case does not choose "
                    "between: " + ", ".join(repr(m) for m in missing))
            for marker, alt in case.forms.items():
                want = resolve(want, marker, alt)
        except LookupError as exc:
            results.append(CaseResult(case.name, False, error=str(exc)))
            continue

        got = spoken(case.argv, spec.root)
        for rule in list(spec.rules) + list(case.rules):
            want = rule.apply(want, DOCUMENT)
            got = rule.apply(got, SCRIPT)

        want, got = want.strip(), got.strip()
        if want == got:
            results.append(CaseResult(case.name, True))
            continue
        diff = list(difflib.unified_diff(want.splitlines(), got.splitlines(),
                                         DOCUMENT, SCRIPT, lineterm=""))
        results.append(CaseResult(case.name, False, diff=diff))

    return Report(spec.document, results)


def report(spec: Spec, out=None) -> int:
    """Run it, print it the way both customers printed it, return the failures."""
    import sys
    stream = sys.stdout if out is None else out
    result = run(spec)
    for line in result.render():
        print(line, file=stream)
    return result.failures
