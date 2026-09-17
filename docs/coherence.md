# Coherence

**If you are an agent working on this repository, start here.** What koine is
for, what you may decide on your own, what you may not, and what the open work
is.

It is deliberately **not linked from the front page**.
[`../README.md`](../README.md) is for somebody deciding whether this is worth
depending on; how the work is run is noise to them.

The convention is anoieu's, and so is the name.

## What koine is for

**Every tool here is built to find something. koine is built to keep it.**
The tools here find bugs in projects that are not their own; koine keeps the
list of what they found. It does not find bugs, does not decide whether one is
real, and has no opinion about what should be done with one.

**Two purposes, named by the maintainer on 2026-09-17.**
[`../README.md`](../README.md) is where they are written for a reader; this is
the same pair with what an agent needs added.

1. **Tooling for keeping bug databases.**
   [`koine_append_db`](../scripts/koine_append_db) takes a run's dump and adds
   what is new to a database of everything a tool has ever found. **anoieu and
   dokimasia are the customers**, and each pins a commit of this repository and
   calls it from its own run — that pin is the whole of the integration on
   either side, and it is also what makes a path here somebody else's problem to
   change.
2. **[`../eo_cmd/`](../eo_cmd), the ecosystem's commands.** Scripts useful
   across the ecosystem rather than inside any one repository, stored here and
   put on a person's path by
   [`install_eo_cmd`](../scripts/install_eo_cmd). **This one is a service and
   not koine's own work**: another repository owns every word of what is in
   there. See [Storing somebody else's command](#storing-somebody-elses-command)
   below, which is where the rule that keeps it from becoming ownership is
   written down.

**[`koine_history`](../scripts/koine_history) is neither of them**, and knowing
that matters before an instruction arrives assuming it is one. It came in on
2026-09-16 when the history review child project was dissolved into this tree.
It reports mechanical signals and preserves human readings in
[`history-ledger.md`](history-ledger.md); it decides no verdict and writes
nothing to the source record. It is maintained, tested and in CI, and where it
sits against the two purposes is [open work](#the-open-work).

Everything runnable is in [`../scripts/`](../scripts).

**This replaced an earlier direction on 2026-09-16**, at the maintainer's
instruction. koine had been the shared half of a reporting loop: a prompt-drift
check, a branch-state reporter, a postmortem protocol and a findings record, with
a document for each. All of it was deleted in the same change. **It is in git
history and nothing depends on it**; if something there turns out to be wanted,
recover it from there rather than rebuilding it from memory.

**The maintainer also asked to fold the history review child project into Koine
on 2026-09-16.** Its script, tests, review standard, and ledger now live in the
normal Koine layout. There is no separate child project or lifecycle. The
[review design](history-review.md) retains its useful decisions: keep evidence
separate from judgement, preserve earlier readings, read the source without
editing it, and leave external communication to a person. The tool is part of
Koine's test suite; the reviews remain advisory.

### Naming

**One module or script per piece, in [`../scripts/`](../scripts), named
`koine_<piece>`.** The directory and the prefix answer different questions and
neither is decoration.

**The directory is the ecosystem's, not ours.** `docs/policy.md` gives the
layout every member uses, and `scripts/` is "commands, helpers and their data:
generators, checks, the runner". The top level is for *the package itself, named
after the tool*, and koine has no package.

**The prefix is ours, and the reason survived the move.** A customer adopts koine
by putting a directory of it on their path — `scripts/` now, the root before —
and either way a file in it is a name claimed inside somebody else's process.
`append_db` is a name another project may well want; `koine_append_db` cannot
collide, and says whose it is at the point of use.

**These were at the root until 2026-09-17**, on the argument that koine had no
package and no install step so the root *was* the interface. That argument did
not survive this repository acquiring an installer and a `scripts/` of its own:
a tree with `install_eo_cmd` in `scripts/` and `koine_append_db` beside the
README was following neither convention. The maintainer's instruction was to
move and let the consumer fix, which the policy permits in as many words —
*a member never told about an announcement has not been wronged.*

**What that instruction does not buy is a silent break**, and this move had one
waiting. [`../koine_append_db`](../koine_append_db) is a tombstone left at the
old path; its docstring is the whole account of why a bare `git mv` would have
degraded quietly rather than failed. Delete it once anoieu's pin has moved.

**Two directories are deliberately not that, and the exception is the rule
working rather than bending.**

[`../eo_cmd/`](../eo_cmd) holds commands this repository did not write. They
carry the ecosystem's prefix — `eo_join`, `eo_init` — precisely because the root
convention says a name claimed on somebody's path should say whose it is, and
these are not ours to claim. A file in there named `koine_join` would be a lie
about who to argue with.

[`../scripts/`](../scripts) holds what maintains this tree rather than what the
tree offers, and is reached by path from a checkout. Nothing in it goes on
anybody's path, so nothing in it can collide, and the root convention has no
work to do there.

## The supervision division

The maintainer's standing instruction, recorded here because an instruction that
lives only in a session is one the next session does not have.

> **Where the only parties are full members of the Eunoia ecosystem, low-level
> implementation is yours to decide — do not ask.** Be fearless. What is
> adamantly protected is the *structure* of the infrastructure, and that is not
> yours to move.

Two halves, and both are load-bearing.

### Fearless, within the island

**Do not ask permission for implementation.** The shape of an API, what a script
parses, how a failure reads, whether something is a dataclass or a dict, how the
tests are arranged, which of two equivalent behaviours to keep when nothing
depends on either — decide it, do it, say what you did. Asking about these is not
caution; it is passing a decision to somebody with less context than you, and it
is slower for everybody.

**The scope of that is member-only traffic.** anoieu, dokimasia, eudaimonia,
epikrisis, logos and koine are members, and kanon is president: they have joined,
they read diffs, and a mistake between them is corrected in a commit by somebody
who was already going to read it. cvc5 and ethos are not — at kanon `4c4a78a`,
read 2026-09-16, cvc5 is `foundation` and ethos is `candidate` with
`proposed: associate` in
[`ecosystem.json`](https://github.com/ajreynol/kanon/blob/main/scripts/ecosystem/ecosystem.json),
and what reaches them reaches people who did not sign up for this. **Anything
that will be read outside the island is not a low-level detail**, whatever else
it is: an outbound prompt, a bug report, a claim about somebody's code. The
ecosystem's own rule is the same one — everything that reaches a person who did
not ask for it is sent by a person.

### And the structure is protected

**The structure is what other repositories have arranged themselves around**, and
moving it costs somebody who is not in the room. Ask first for:

- **what koine is for.** The scope above, and *takes its work from the tools that
  use it and invents nothing*. Widening that is not an implementation decision.
- **a field vocabulary.** What a bug record must carry, what a key is, what a
  reader is entitled to assume. These are what another repository's output is
  shaped to; the code behind them is not.
- **a maintenance obligation.** Volunteering to hold a document, undertaking to
  announce a change, promising a cadence. Every one outlives the enthusiasm that
  made it, and withdrawing one costs more than never making it — most of that
  cost falling on somebody else. Prefer a **structural** answer to a promised
  one: a member that pins a commit needs no undertaking from us.
- **anything irreversible or public.** Creating a repository, writing to a
  remote, pushing, opening an issue anywhere. Nothing here holds credentials that
  create or publish, and that is deliberate rather than incidental.

**The failure mode is treating structure as overhead during a rush.**
Infrastructure is cheapest to delete at the moment it is most load-bearing, and
an agent under time pressure is well placed to make that trade badly and describe
it as simplification.

### What is not koine's at all

Do not design it, do not build it, do not have an opinion about it in the tree.

| | whose | why not |
| --- | --- | --- |
| **epochs** | the maintainer's | **THE DESIGN OF EPOCHS IS NOT KOINE'S TO DECIDE.** koine carries **no knowledge of how epochs are implemented** |
| global announcements, and who is told | **kanon's** | the same reason, one level down |
| membership, joining, the repository policy | **kanon's** | it decides who is in |
| the discussion protocol and its safety gate | **kanon's** | being wrong here reaches people who did not sign up |
| the inventory, and the entity ids | **kanon's** | koine *references* the vocabulary; owning it would be owning membership |
| the role handoff procedure, the channel model | **kanon's** | governance, not a shape |
| the policy checker itself | **anoieu's** | our CI pins it and it is not ours to move |
| every prompt template; every position on publishing | **anoieu's and kanon's** | a position is what somebody signs |

### Storing somebody else's command

**Two rows above say that joining and the prompt templates are kanon's, and
both rows still hold.** [`../eo_cmd/`](../eo_cmd) contains `eo_join` and
`eo_init`, which are copies of two of those templates, stored here on the
maintainer's instruction of 2026-09-17 so that
[`../scripts/install_eo_cmd`](../scripts/install_eo_cmd) can put them on a
person's path.

**Storing is not owning, and the difference is made checkable rather than
promised.** Their content is not koine's to modify.
[`../eo_cmd/origin.json`](../eo_cmd/origin.json) records the source repository,
path, role and commit for each; `--check <checkout>` re-derives the copy from
the original and compares; `--sync <checkout>` is the only sanctioned way a
file in there changes. An agent that improves the wording of `eo_join` has not
improved anything — it has made a copy wrong, and the next `--check` says so.

**What follows for an agent working here.** A request to change what `eo_join`
asks, to add an option to it, to soften or harden its first question, or to add
a third command to `eo_cmd/`, is a request to the repository that owns the
thing. Say so and name it; `origin.json` has the id. Copying a file in does not
move the argument about it, and this repository has no standing in that
argument — which is the whole reason the copies are checked against an original
instead of merely being similar to one.

**The rename is the single exception, and it stops at the wrapper.** It does not
touch the prompt text, because that text is read outside this ecosystem and
names the command so a stranger can check it against what the command actually
says. The name that survives that check is the one in the tree they can read.
Making the prompts say `eo_join` would point them at a command that exists on
one machine and in no repository anywhere, which is the failure this whole
arrangement exists to avoid.

**The test that puts something here:** somebody else maintains it, **or** being
wrong about it reaches people who did not sign up for this. Either is enough.

**What to do when a task lands on this list:** stop, say which row it is, and ask
which repository was meant. Do not build the smaller safe part.

### Check who the instruction is addressed to, before the first edit

**The tell is concrete: an instruction that describes artifacts this repository
does not have is addressed to a repository that has them.** The repositories here
are alike on purpose and sit side by side on one disk. The maintainer works on
all of them, and an instruction meant for anoieu arrives in this session looking
exactly like one meant for koine.

This has gone wrong in this tree more than once, each time by taking the more
plausible reading instead of stopping. So: if an instruction names a file, a
role, a CI, an announcement or a responsibility that this tree does not have,
**do not supply the missing thing.** Say which artifact is missing and ask which
repository was meant. A human may override after being told, and then the
override is recorded.

**The dangerous shape is a prompt asking this repository to decide its own
standing**, because an agent asked *should koine hold X* will find the case for
X — finding it is what it was asked to do.

## The two rules that cut across both

**Never act on a discussion file unbidden** — this one or anybody's. Reading is
free. Acting requires a human who told you to, named the topic, and whose
instruction agrees with the topic. Where they disagree, do nothing: not the
overlap, not the safer half. Say where they differ and wait.

**Work is left staged, not committed.** The diff is the review, and it is the
last place a change that binds another repository can be caught.

**And when a commit is taken while the work is still moving, say so in one
line.** Committing mid-stream is nobody's fault and will keep happening; what it
costs is that the commit's message stops describing its contents, and a reader
looking for a change finds it filed under a subject it has nothing to do with.
The remedy is deliberately small — **one line naming the commit and what it
actually carries.** Anyone may write it, anyone may delete it, at any time,
without asking: it is a note about the record, not a record.

## The open work

**What the maintainer names next, and nothing else.** koine takes its work from
the tools that use it and invents nothing on its own. A feature nobody has asked
for is a guess about somebody else's needs — likely wrong, and more expensive to
withdraw than it was to write.

Three things are outstanding and none is an agent's to settle:

- **Where [`koine_history`](../scripts/koine_history) sits.** The maintainer
  named two purposes on 2026-09-17 — bug-database tooling, and the ecosystem's
  commands — and the history tool is in neither. It may belong under the first
  read more broadly, it may be a third purpose, or it may be work this
  repository no longer wants. **All three are answers and none has been given**,
  so it stays where it is, documented as neither. Do not resolve this by
  quietly filing it under a purpose that nearly fits, and do not delete it.

- **A publishing stance**, owed by this repository — whether there is a paper
  in the work, or a plan for one, or nothing
  worth writing up. **All three are answers**, the third is the commonest, and
  which one it is is a position somebody signs. Asked by anoieu on 2026-09-02 and
  left unstated.
- **[`discussion.md`](discussion.md) is now a record of an earlier
  purpose.** Its topics were written when koine was a reporting-loop library and
  none of them was ever carried to anybody. Whether they are withdrawn, rewritten
  or left as they stand is the maintainer's; **no agent works that file
  unbidden**, including to tidy it.

## Where to start

```bash
python3 tests/test_append_db.py                          # bug database
python3 tests/test_history.py                            # history review
python3 tests/test_install_eo_cmd.py                     # the command store and installer
python3 /path/to/anoieu/scripts/policy_check.py --root .  # the ecosystem policy
```

Then read [`../README.md`](../README.md) for what this is for.
