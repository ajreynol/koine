# The prompt-drift check

The first piece of the loop koine holds, and the one
[anoieu asked for first](https://github.com/ajreynol/anoieu/blob/main/docs/discussion.md).

A tool that reports a finding sends a prompt to whoever owns the file. The
prompt is defined in a document — that is the version the far end was promised —
and a script under `scripts/` carries a copy so nobody has to paste one. **A copy
that has drifted is worse than no copy**, because the drift is invisible from the
side that matters: somebody in the other project reading a prompt they were sent.

The check is the thing that makes the copy safe. It runs each script the way a
person would, takes what it prints, and compares it to the document.

## Why this piece and not another

Both customers wrote it, independently, and both copies had already diverged
before either was a week old. anoieu's is `prompts_agree()` in `tests/run.py`;
dokimasia's is `test_prompts()` in `tests/test_workflow.py`. The alternatives
resolver is line-for-line the same function in both. The runners are not: one
executes the script directly and truncates a failure at 160 characters, the other
prefixes `bash` and truncates at 200.

Nothing depends on either difference, which is exactly what makes it the right
first piece. This is the shape of drift on day one, in the one check whose whole
job is to notice drift, and nobody was watching either copy.

## What it asks of a script

One thing. **`--show-prompt` prints the prompt and exits**, running nothing else
and reading nothing it does not have to.

That is what makes the check honest: it compares the text a real invocation
produces, not a second copy kept for testing. Both customers already do this.

## What it compares, and what it does not

**The whole of a prompt, in every form it can take.** Not a paragraph of it. A
check anchored part way down a prompt will not notice a stale paragraph above
where it starts matching, which is a failure anoieu has actually had.

**Not the lines a script exists to fill in.** Which rows, which branch, which
checkout — filling those in is the point of the script. A customer says which
spans those are, and everything else is compared exactly.

### Alternatives

A prompt has forms, and the document writes both sides with a marker line
between them:

```text
Address every open row.
-- or, for one row --
Find the row whose id is ID, and address that row only.
```

The marker's block is the run of lines before it back to the last blank line, the
marker, and the run after it up to the next blank line. Resolving it one way or
the other gives the form a particular invocation should print — and resolving,
rather than skipping past, is what lets the comparison cover every line.

**Every marker in a prompt must be chosen for, in every case.** A document that
grows an alternative no case resolves is an error rather than a silent
half-check. This is the one behaviour neither copy had, and it is a consequence
of the interface rather than a feature: the copies wrote their `resolve()` calls
out by hand, where a missing one was visible in the code, and here they are data.

### Normalising

Three rules, which are all four normalisers across both copies reduced to their
primitives. Each applies to both sides unless told otherwise — applying it to
both says *these two spellings mean the same thing*, which is nearly always what
is meant and cannot hide a difference that is only on one side.

| rule | what it is for |
| --- | --- |
| `sub(old, new)` | two spellings of one thing, usually a branch name the script filled in |
| `after(marker)` | an opening the document and the script word differently on purpose, where everything below it may not differ |
| `drop_paragraphs(prefixes)` | the one sentence each side words for the run it is doing |

`after` leaves text that does not contain the marker alone, so a script that died
still shows its failure rather than vanishing into a match.

## Fetching it

The way this ecosystem already shares code: pin a commit, clone it, put it on
`sys.path`. koine is pure standard library, installs nothing, writes nothing, and
needs no network.

```yaml
      - name: koine, at the commit this repository pins
        env:
          KOINE_REV: 0000000        # a commit; there is no branch to track
        run: |
          git clone --quiet https://github.com/ajreynol/koine /tmp/koine
          git -C /tmp/koine checkout --quiet "$KOINE_REV"
```

```python
import sys
sys.path.insert(0, "/tmp/koine")
from koine import drift
```

There is no package, no install step and no second thing to pin. That is
deliberate: adoption costs a customer one clone and one `sys.path` line, and
abandoning it costs them restoring a file they already had.

## Calling it

A customer writes a spec — data, not code — and hands it to `report`, which
prints and returns a failure count.

```python
failures = drift.report(SPEC)        # prints; returns the count
result   = drift.run(SPEC)           # the same, structured, for your own output
```

`run` returns a `Report` with `.failures` and a `.cases` list of `CaseResult`,
each carrying `.ok`, `.diff` and `.error`. Neither writes anything anywhere.

### The two real specs live in the tests, not here

[`../tests/customers.py`](../tests/customers.py) holds anoieu's four cases and
dokimasia's six, and runs them against the real trees:

```bash
python3 tests/customers.py ~/src/anoieu ~/src/dokimasia
```

**The checkout must be in a directory named for the tool.** Both customers'
scripts take the repository name from `basename` of the path they are given and
interpolate it into the prompt, so a clone in a directory called anything else
reports drift that is not there. It is a property of their scripts rather than of
this check, and it is written down because the failure it produces looks exactly
like a real one.

They are **there and not written out here on purpose.** A spec copied into a
document is a second copy that drifts from the first, which is the failure this
whole page is about; and a spec in the tests is one a reader runs rather than
reads. That harness is not part of CI — it needs somebody else's checkout, and it
fails when a customer moves their prompts, which is their business.

What a spec looks like, in the small:

```python
SPEC = drift.Spec(
    root=ROOT,
    document="the/document/that/defines/the/prompts.md",
    prompts={"one": drift.Prompt("### Prompt one", "### Prompt two")},
    cases=[
        drift.Case(
            name="the script, in its one-row form",
            prompt="one",
            argv=["bash", "scripts/the_script", "--show-prompt", "ID"],
            forms={"-- or, for the sweep form --": False},
            rules=[drift.sub("tool-ID", "BRANCH")],
        ),
    ],
)
```

anoieu's differs from that in four ways and dokimasia's in five: a second prompt,
a second alternatives marker, and the `after`/`drop_paragraphs` rules for the
openings each words differently on purpose. Read them where they run.

## What changes for a customer who adopts it

Said in full, because a shared implementation that quietly changes somebody's
behaviour is the thing this repository is supposed to prevent.

**Both.** The wording of the printed lines is koine's now, not each customer's.
Whatever your test runner does with a failure count is unaffected.

**anoieu.** A failed script's own output is quoted back at 200 characters rather
than 160 — koine had to pick one of the two numbers and picked dokimasia's,
because nothing depends on it either way. `drop_paragraphs` strips leading
whitespace before matching every prefix, where `drop_scope` did so for only the
first of its three; no paragraph in the document is affected. And the
unchosen-marker error above is new.

**dokimasia.** `bash` is written into `argv` by the customer rather than prefixed
by the runner. The unchosen-marker error is new here too.

**Neither** loses a case, a form or a line of coverage: the two specs above were
run against the real trees and agree with what each repository's own check
already reported. **Last re-run 2026-09-02**, against anoieu `2172a1b` and
dokimasia `f9a5bd7`: ten cases, no failures, and each customer's own suite
reporting the same on its own side.

**Both customers have moved their prompts once since, and the specs followed
rather than the other way round.** anoieu's are at `prompts/` and dokimasia's
under `scripts/prompts/`; ours named the old paths, and for as long as they did
this harness reported ten failures that belonged to nobody. **A path in a spec is
a claim about somebody else's tree**, so it goes stale the way any other claim
about a tree does, and the harness cannot tell that kind of failure from a real
one — only re-running it against a fresh checkout can.

## What is not here

The
[inventory of what the two loops share](https://github.com/ajreynol/dokimasia/blob/main/docs/discussion.md)
is four pieces, not one. The other three are the **branch-state reporter** (what
became of the branch a reply names — pure git, and identical in both), the
**reply finder** (locating and splitting a reply file in somebody else's
checkout), and the **postmortem-shape check** (one field block per run, and a
summary short enough to stay one).

None of them is built, and the last of them has not been asked for. koine takes
its work from its customers and this piece is what was asked for first.
