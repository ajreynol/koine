# The branch-state reporter

**What became of the branch a reply names.**

A reply to a finding points at work rather than describing it — a branch, or a
commit on one — and the reporting tool then has to ask the same question every
time: *has that work reached the project's default branch, or not yet, or is it
not here at all?* It is pure git, it is asked about a checkout of somebody
else's project, and **both customers had written it before this existed**. It is
the second of the four pieces, asked for in that order.

[`../koine_branch.py`](../koine_branch.py) is the whole of it.

## What it answers, and what it refuses to

Four states, and a state is only what a checkout can support saying:

| | what it means |
| --- | --- |
| `landed` | the ref is an ancestor of the default branch. The work is in |
| `ahead` | it exists and is not an ancestor — `N` commits the default does not have |
| `absent` | the ref is not in this checkout |
| `unknown` | the question could not be put — not a repository, no default branch, git refused |

**It does not decide what any of that means.** Whether a row may close, whether
a debt is discharged, whether somebody should be chased — those differ per tool
and stay with the tool. koine carries the envelope and never writes the letter.

**`unknown` is not a pass, and the report says so in those words.** A checkout
that could not be reached is an unaudited row, not a clean one. The distinction
is anoieu's and it was learned expensively: three rows sat closed on a fix that
never landed, for three months, because a closed id is one nothing re-derives.
So `report` returns *the number that could not be answered* — a branch that has
not landed is news rather than a defect, and is not counted.

## Finding the default branch

Both customers try the same names in the same order, and the order is the
load-bearing part rather than the list:

```
refs/remotes/origin/HEAD    what the checkout itself says, if it says
origin/main, origin/master  what a clone of a live project usually has
main, master                what a checkout with no remote has
```

Asking the checkout before guessing is what makes a project whose default branch
is neither `main` nor `master` answered correctly instead of plausibly. A guess
that is usually right is the kind that fails quietly on the one project it is
wrong about.

## The one place the two customers disagree

They ask about different things, and **a ref that is not in the checkout means
different things to them because of it.** Running both implementations against
one repository is what showed it; neither document said so.

| | holds | *not here* means | and they are right |
| --- | --- | --- | --- |
| **anoieu** | a **commit**, read out of an `awaiting landing:` marker in a closed row | this checkout is stale, or the branch was rebased under it | so it reports `unknown` |
| **dokimasia** | a **branch name**, the one its check script was told to work on | nothing has been answered on it, or it was answered somewhere else | so it reports that it is not here |

**Nothing in the repository can tell the two apart**, which is exactly why this
module must not choose. `Query.missing` is the caller's statement of what *not
here* means for the thing it is asking about.

It **defaults to `unknown`**, the conservative reading, because claiming an
answer that was never obtained is the failure this piece exists to prevent. A
caller holding a branch name says `missing=branch.ABSENT` in one field and gets
dokimasia's reading.

## Calling it

```python
import sys; sys.path.insert(0, "/tmp/koine")
import koine_branch as branch

failures = branch.report([
    # a branch somebody was asked to work on: not here is an answer
    branch.Query(repo="/src/cvc5", ref="fix-proof-gap", label="i-4",
                 missing=branch.ABSENT),
    # a commit out of a ledger: not here means this checkout is stale
    branch.Query(repo="/src/ethos", ref="9a3f1c2", label="abc123def4567890"),
])
```

`run` returns the same records without printing, which is what both customers
will want — their reports do not look alike and are not meant to. `ask` answers
a single query. `label` is whatever the caller calls the thing and is carried
through untouched, so a report can be read against the caller's own register;
koine never interprets it.

**Nothing here writes, anywhere.** Every git command it runs is a read.

## What it asks of a customer

**Nothing.** There is no marker to adopt, no field to add, no file to move: a
caller that can name a checkout and a ref can call it. That is what makes this
the cheapest of the four pieces to take, and it is most of why it was asked for
second.

## What each would see change on adopting it

Written out because a shared implementation that quietly alters somebody's
behaviour is the thing this repository exists to prevent.

**anoieu** would replace `base_of` and `ask` in
[`scripts/landing.py`](https://github.com/ajreynol/anoieu/blob/main/scripts/landing.py)
— about forty lines — and keep everything else: reading the ledger, the
`awaiting landing:` marker, the malformed-marker check, and the report. Their
three state names map onto koine's as `landed`, `not yet` → `ahead`, and
`unknown`, and with the default `missing` their verdicts are unchanged.

**dokimasia** would replace the `--status` block in
[`scripts/prompts/process_dokimasia`](https://github.com/ajreynol/dokimasia/blob/main/scripts/prompts/process_dokimasia)
— about thirty lines of shell — passing `missing=ABSENT`. Their output would
have to be printed from the records rather than by `echo`, which is the one real
cost here and is theirs to weigh: the `--status` block also prints the reply
file and `git status`, and neither of those is koine's.

**Neither is obliged to take it**, and the evidence for the claim above is
runnable rather than asserted: `tests/customers.py` puts the same four questions
to koine, to anoieu's real `landing.ask`, and to dokimasia's real `--status`,
and reports where they disagree. It builds its own git repository to ask about,
so it needs no network and no third project checked out.
