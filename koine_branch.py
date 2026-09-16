"""The branch-state reporter: what became of the branch a reply names.

A reply to a finding points at work rather than describing it -- a branch, or a
commit on one -- and the question the reporting tool then has to answer is the
same in every case: **has that work reached the project's default branch, or
not yet, or is it not here at all?** It is pure git, it is asked about a
checkout of somebody else's project, and both customers had written it before
this module existed.

They asked it about different things and printed different answers. anoieu asks
after a **commit**, read out of an `awaiting landing:` marker in a closed row,
because a row there closes on a promise that a change will land. dokimasia asks
after a **branch name**, the one its check script was told to work on, because
its reply is written on that branch. Underneath, the git is the same git, in
the same order, down to the list of names tried when a checkout does not say
what its default branch is.

So this asks the question and returns the answer. **It does not decide what the
answer means** -- whether a row may close, whether a debt is discharged, whether
somebody should be chased -- because that is what each tool keeps for itself.
koine carries the envelope and never writes the letter.

## The four states

A state is what the checkout supports saying, and no more:

    landed    the ref is an ancestor of the default branch. The work is in
    ahead     it exists and is not an ancestor: N commits the default does not have
    absent    the ref is not in this checkout at all
    unknown   the question could not be put -- not a repository, no default
              branch, git refused

**`unknown` is not `absent` and neither is a pass.** A checkout that could not
be reached is an unaudited row, not a clean one, and reporting it as anything
else is the failure the audit exists to prevent. That distinction is anoieu's,
learned the expensive way: three rows sat closed on a fix that never landed
because nothing re-derived them.

### Where the two customers genuinely disagree, and why the caller decides

A ref that is not in the checkout means **different things to the two of them**,
and running both implementations against one repository is what showed it.

anoieu holds a **commit**, read out of a ledger. A commit that is not there is
not news about the work -- it means this checkout is stale, or the branch was
rebased under it. anoieu calls that `unknown`, and is right to.

dokimasia holds a **branch name**, the one it asked somebody to work on. A
branch that is not there *is* news: nothing has been answered on it, or it was
answered somewhere else. dokimasia says exactly that, and is also right.

The same git command, two meanings, and **nothing in the repository can tell
them apart** -- which is precisely why this module must not choose. `Query`
carries `missing`, the caller's statement of what *not here* means for the thing
it is asking about. It defaults to `unknown`, the conservative reading: claiming
an answer that was never obtained is the failure this piece exists to prevent,
and a caller that knows better says so in one field.

## Finding the default branch

Both customers try the same names in the same order, and the order is the
interesting part rather than the list:

    refs/remotes/origin/HEAD    what the checkout itself says, if it says
    origin/main, origin/master  what a clone of a live project usually has
    main, master                what a checkout with no remote has

Asking the checkout first matters: a project whose default branch is neither
`main` nor `master` is answered correctly instead of plausibly, and a guess that
is usually right is the kind that fails quietly on the one project it is wrong
about.

## Calling it

Build `Query` values and hand them to `report`, which prints and returns the
number that could not be answered:

    import koine_branch as branch

    failures = branch.report([
        # a branch somebody was asked to work on: not here is an answer
        branch.Query(repo="/src/cvc5", ref="fix-proof-gap", label="i-4",
                     missing=branch.ABSENT),
        # a commit out of a ledger: not here means this checkout is stale
        branch.Query(repo="/src/ethos", ref="9a3f1c2", label="abc123def4567890"),
    ])

`run` returns the same records without printing, for a caller with its own
output -- which is what both customers have, since their reports do not look
alike and are not meant to. `ask` answers a single query.

Nothing here writes, anywhere, ever: every git command it runs is a read.

## What this asks of a customer

Nothing. There is no marker to adopt, no field to add and no file to move: a
caller that can name a checkout and a ref can call it. That is what makes this
the cheapest of the four pieces to take, and it is why it was asked for second.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

#: Long enough for a cold checkout on a slow disk, short enough that a hung git
#: is reported rather than waited on. anoieu's number, kept.
TIMEOUT = 30

#: How many commits to carry back when a ref is ahead. dokimasia's number; a
#: caller that wants none passes 0 and a caller that wants all of them passes -1.
LOG_LIMIT = 10

LANDED = "landed"
AHEAD = "ahead"
ABSENT = "absent"
UNKNOWN = "unknown"

#: Tried in order when the checkout does not say what its default branch is.
FALLBACKS = ("origin/main", "origin/master", "main", "master")


def git(repo: str, *args: str) -> tuple[int, str]:
    """Run one read-only git command. Returns its code and its output.

    Failure is a return value rather than an exception because every caller
    here has something to say about a failure and none of them should stop.
    """
    try:
        p = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True, text=True, timeout=TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)[:200]
    return p.returncode, (p.stdout or p.stderr).strip()


@dataclass(frozen=True)
class Query:
    """One question: what became of `ref` in the checkout at `repo`.

    `ref` may be a branch name or a commit; which one it is is worked out
    rather than declared, because anoieu holds commits and dokimasia holds
    branch names and neither should have to say so.

    `label` is whatever the caller calls this -- a finding id, a row id -- and
    is carried through untouched so a report can be read against the caller's
    own register. koine never interprets it.
    """
    repo: str
    ref: str
    label: str = ""
    log_limit: int = LOG_LIMIT
    #: What a ref that is not in the checkout means here -- `ABSENT` if the
    #: caller holds a branch name somebody was asked to work on, `UNKNOWN` if it
    #: holds a commit and a missing one means a stale checkout. The two
    #: customers differ, on purpose; see the module docstring.
    missing: str = UNKNOWN


@dataclass
class State:
    """What the checkout was able to say."""
    query: Query
    state: str = UNKNOWN
    base: str = ""              #: the default branch it was compared against
    where: str = ""             #: local / origin / local and origin / commit
    ahead: Optional[int] = None  #: commits the default branch does not have
    commits: List[str] = field(default_factory=list)
    detail: str = ""

    @property
    def answered(self) -> bool:
        """Whether the question was put at all. `absent` is an answer."""
        return self.state != UNKNOWN

    def line(self) -> str:
        """One line, the way a report prints it."""
        q = self.query
        left = f"{self.state:8} {q.label}" if q.label else f"{self.state:8}"
        return f"{left}  {q.ref}" + (f"  -- {self.detail}" if self.detail else "")


def default_branch(repo: str) -> str:
    """What a change in this checkout is supposed to land on.

    Asks the checkout before guessing; see the module docstring for why the
    order is the load-bearing part.
    """
    code, out = git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if code == 0 and out:
        return out
    for cand in FALLBACKS:
        if git(repo, "rev-parse", "--verify", "--quiet", cand)[0] == 0:
            return cand
    return ""


def _resolve(repo: str, ref: str) -> tuple[str, str]:
    """Locate `ref`: the rev to use, and where it was found.

    A local branch wins over the remote one of the same name, which is
    dokimasia's behaviour and the right one -- the local branch is what somebody
    working in that checkout is looking at.
    """
    local = git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{ref}")[0] == 0
    remote = git(repo, "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{ref}")[0] == 0
    if local and remote:
        return ref, "local and origin"
    if local:
        return ref, "local"
    if remote:
        return f"origin/{ref}", "origin"
    # Not a branch. anoieu's case: a bare commit out of a ledger marker.
    if git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] == 0:
        return ref, "commit"
    return "", ""


def ask(query: Query) -> State:
    """Put one question to one checkout."""
    st = State(query=query)
    repo = query.repo

    if not os.path.isdir(repo):
        st.detail = f"{repo} is not there"
        return st
    if git(repo, "rev-parse", "--is-inside-work-tree")[0] != 0:
        st.detail = f"{repo} is not a git repository"
        return st

    rev, where = _resolve(repo, query.ref)
    if not rev:
        st.state = query.missing
        st.detail = ("not in this checkout -- never pushed, or answered elsewhere"
                     if query.missing == ABSENT else
                     "not in this checkout -- fetch, or it was rewritten")
        return st
    st.where = where

    base = default_branch(repo)
    if not base:
        # Everything below needs something to compare against. Say so rather
        # than comparing against a guess.
        st.detail = "no default branch to compare against"
        return st
    st.base = base

    if git(repo, "merge-base", "--is-ancestor", rev, base)[0] == 0:
        st.state = LANDED
        st.detail = f"in {base}"
        return st

    st.state = AHEAD
    code, out = git(repo, "rev-list", "--count", f"{base}..{rev}")
    st.ahead = int(out) if code == 0 and out.isdigit() else None
    count = st.ahead if st.ahead is not None else "?"
    st.detail = f"{count} commit(s) {base} does not have"
    if query.log_limit:
        args = ["log", "--oneline", "--no-decorate"]
        if query.log_limit > 0:
            args.append(f"-{query.log_limit}")
        code, out = git(repo, *args, f"{base}..{rev}")
        if code == 0 and out:
            st.commits = out.splitlines()
    return st


@dataclass
class Report:
    """Every answer, and how many of them are not answers."""
    states: List[State] = field(default_factory=list)

    @property
    def failures(self) -> int:
        """The unanswered ones. Nothing else here is a failure.

        A branch that has not landed is news, not a defect -- the tool that
        asked decides what to do about it. A checkout that could not be reached
        is the one thing this module is entitled to call wrong, because it means
        the audit did not happen.
        """
        return sum(1 for s in self.states if not s.answered)

    def of(self, state: str) -> List[State]:
        return [s for s in self.states if s.state == state]

    def render(self) -> List[str]:
        lines = [f"-- {len(self.states)} ref(s), against the default branch"]
        if not self.states:
            lines.append("   nothing to ask about")
        for s in self.states:
            lines.append("   " + s.line())
            for c in s.commits:
                lines.append("                " + c)
        landed = self.of(LANDED)
        if landed:
            n = len(landed)
            lines.append(f"-- {n} {'has' if n == 1 else 'have'} landed")
        if self.failures:
            lines.append(f"-- {self.failures} could not be answered -- "
                         "that is an unaudited row, not a clean one")
        return lines


def run(queries: Sequence[Query]) -> Report:
    """Ask all of them. Prints nothing."""
    return Report(states=[ask(q) for q in queries])


def report(queries: Sequence[Query], out=None) -> int:
    """Ask, print, and return the number that could not be answered."""
    import sys
    stream = sys.stdout if out is None else out
    result = run(queries)
    for line in result.render():
        print(line, file=stream)
    return result.failures
