# Coherence

**If you are an agent working on this repository, start here.** This is the
maintenance entry point: what koine is responsible for, what you may decide on
your own, what you may not, and what the open work is.

It is deliberately **not linked from the front page**. [`../README.md`](../README.md)
is for somebody deciding whether this is worth depending on; how the work is run
is noise to them. It is linked from what a maintainer opens instead: the
documentation index, and the headers of the modules.

The convention is anoieu's, and so is the name.

## What this repository is responsible for

| what | where | who else it binds |
| --- | --- | --- |
| the prompt-drift check | [`../koine/drift.py`](../koine/drift.py), [`drift.md`](drift.md) | anoieu and dokimasia, when each drops their copy |
| **the postmortem protocol** | [`postmortem-protocol.md`](postmortem-protocol.md), [`../koine/postmortem.py`](../koine/postmortem.py) | **proposed**: a shape both keep today, offered here instead |
| the evidence that adoption is free | [`../tests/customers.py`](../tests/customers.py) | nobody, and it is the reason anybody should believe the other rows |

The second row is in bold because it is different in kind. The drift check is
*code two repositories had written twice*; the protocol is **a document other
repositories would follow**, and koine has asked for it rather than been given
it. Until anoieu answers, the shape is still theirs.

## The supervision division

The maintainer's standing instruction, recorded here because an instruction that
lives only in a session is one the next session does not have.

> **Where the only parties are full members of the Eunoia ecosystem, low-level
> implementation is yours to decide — do not ask.** Be fearless. What is
> adamantly protected is the *structure* of the infrastructure, and that is not
> yours to move.

Two halves, and both are load-bearing.

### Fearless, within the island

**Do not ask permission for implementation.** The API's shape, what a module
parses, how a failure reads, whether something is a dataclass or a dict, how the
tests are arranged, which of two equivalent behaviours to keep when nothing
depends on either — decide it, do it, say what you did. Asking about these is not
caution; it is passing a decision to somebody with less context than you, and it
is slower for everybody.

**The scope of that is member-only traffic.** anoieu, dokimasia, eudaimonia and
koine are members: they have joined, they read diffs, and a mistake between them
is corrected in a commit by somebody who was already going to read it. cvc5,
ethos and logos are not — they are `served` and `candidate` in
[`ecosystem.json`](https://github.com/ajreynol/anoieu/blob/main/tools/ecosystem.json),
and what reaches them reaches people who did not sign up for this. **Anything
that will be read outside the island is not a low-level detail**, whatever else
it is: an outbound prompt, a finding, a claim about somebody's code. The
ecosystem's own rule is the same one — everything that reaches a person who did
not ask for it is sent by a person.

### And the structure is protected

**The structure is what other repositories have arranged themselves around**, and
moving it costs somebody who is not in the room. Ask first for:

- **what koine is for.** The two-customer scope, and *takes its work from its
  customers and invents nothing*. That boundary is the whole reason this is cheap
  to depend on, and widening it is not an implementation decision — it is what
  [`discussion.md`](discussion.md)'s `D3` and `D4` are both about.
- **a protocol.** The reply format, the field vocabulary, what a level means,
  what a checker refuses. These are what a member's tree is shaped to; the code
  behind them is not.
- **a maintenance obligation.** Volunteering to hold a document, undertaking to
  announce a change, promising a cadence. Every one outlives the enthusiasm that
  made it, and withdrawing one costs more than never making it — most of that
  cost falling on somebody else. Prefer a **structural** answer to a promised
  one: a member that pins a commit needs no undertaking from us.
- **anything irreversible or public.** Creating a repository, writing to a
  remote, pushing, opening an issue anywhere. Nothing here holds credentials that
  create or publish, and that is deliberate rather than incidental.

**Reporting a defect in another member's tooling is not structure**, and is not
asked for. It is member-only traffic about a program we run or reimplement, and
the precedent is dokimasia's — their first outside run of anoieu's checker found
a defect in the checker and came through the discussion channel. What the first
one *did* move is the line [`discussion.md`](discussion.md) draws between a
finding and a topic; that line is now written down in its preamble rather than
left as an inference, which is the part that needed doing.

**The failure mode is treating structure as overhead during a rush.**
Infrastructure is cheapest to delete at the moment it is most load-bearing, and
an agent under time pressure is well placed to make that trade badly and describe
it as simplification.

### Three lists: what is ours, what is not, and what nobody can settle yet

**Look the thing up before building it.** Every protocol in this ecosystem is on
one of these lists, and the list says what to do — not what to weigh.

#### 1. Ours. Decide it and build it, without asking.

| | state |
| --- | --- |
| the prompt-drift check | built, `R16` |
| the branch-state reporter | asked for by both customers, not started |
| the reply finder | asked for by both customers, not started |
| the postmortem entry shape | built; offered in `D4` |

**The test that puts something here:** two tools already write it, no role holds
it, and it is a **shape** rather than a decision. All three, or it is not on this
list.

#### 2. Not ours. Do not design it, do not build it, do not have an opinion in the tree.

| | whose | why not |
| --- | --- | --- |
| **epochs** | the maintainer's | **THE DESIGN OF EPOCHS IS NOT KOINE'S TO DECIDE.** It is a high-level protocol; koine holds low-level ones and carries **no knowledge of how epochs are implemented** |
| global announcements, and who is told | `R4` | the same reason, one level down |
| membership, joining, the repository policy | `R4` | it decides who is in |
| the discussion protocol and its safety gate | `R4` | being wrong here reaches people who did not sign up |
| the inventory, and the entity ids | `R6` | koine *references* the vocabulary; owning it would be owning membership |
| the channel model — who has a wire at all | unowned, anoieu's to claim | a membership rule wearing a format's clothes |
| the role handoff procedure | unowned, anoieu's to claim | governance, not a shape |
| every prompt template; every position on publishing | `R1` | a position is what somebody signs |

**The test that puts something here:** somebody else maintains it, **or** being
wrong about it reaches people who did not sign up for this. Either is enough.

**What to do when a task lands on this list:** stop, say which row it is, and ask
which repository was meant. Do not build the smaller safe part.

#### 3. Undecided. Stop and name the topic that would settle it.

| question | what would settle it |
| --- | --- |
| does koine hold the postmortem shape at all | `D4`, unanswered |
| does `R26` exist | `D8`, unanswered |
| is our reading of anoieu's practice right | `D9`, unanswered |
| should a record live in the tree or in a tracker | a customer running both and saying which cost less — the open question on the front page |
| where the line between a format and a governance rule falls | judgement; we put the channel model on the wrong side once and were corrected |
| what a protocol owes a member that has stopped pinning | nobody has been on an old commit long enough to find out |

**What to do:** say which row, and that it is unsettled. An undecided question
answered by an agent is a decision nobody made.

### Check who the instruction is addressed to, before the first edit

**This has gone wrong twice in one day, both times the same way**, and the rule
that would have caught it already existed — scoped to discussion files, where it
is the protocol's one safety rule:

> Where the instruction and the topic disagree, **nothing happens**. Not the
> overlap, not the smaller safe part, not the more plausible of the two
> readings. Stop, say exactly where they differ, and wait. *These two are the
> only independent accounts of what somebody wants, and when they disagree at
> least one is wrong — proceeding means picking which, and an agent picking is
> how a misunderstanding acquires a commit.*

**It generalises past discussion files, and that is the part that was missed.**
The two independent accounts are not only *instruction and topic*. They are also
**the instruction and the tree you are standing in.** The maintainer works on
every repository in this ecosystem, and an instruction meant for anoieu arrives
in this session looking exactly like one meant for koine.

**The tell is concrete: an instruction that describes artifacts this repository
does not have is addressed to a repository that has them.** The ones missed:

| what was said | what koine actually had |
| --- | --- |
| *our CI must pass for an epoch deployment to be valid; **downstream tools** must refuse* | koine **is** a downstream tool. "Our" was somebody else |
| *the epoch announcement* | koine has never made one |
| *`epochs.md` is the actual log* | koine had no such file; anoieu already did |
| *an experience report about the epoch deployment* | the deployment is not koine's |

Every one of those said *our* and *the*, meaning a repository that was not this
one, and each was resolved by taking the more plausible reading instead of
stopping.

**And it happened a second time after the first was corrected.** That is the
worse half: the first correction was the evidence, and it was treated as a
one-off rather than as a pattern with a rule already written for it.

**So, before acting on an instruction:** if it names a file, a role, a CI, an
announcement or a responsibility that this tree does not have, **do not supply
the missing thing.** Say which artifact is missing and ask which repository was
meant. A human may override after being told, and then the override is recorded.

### The two rules that cut across both

**Never act on a discussion file unbidden** — this one or anybody's. Reading is
free. Acting requires a human who told you to, named the topic, and whose
instruction agrees with the topic. Where they disagree, do nothing: not the
overlap, not the safer half. Say where they differ and wait.

**Work is left staged, not committed.** The diff is the review, and it is the
last place a change that binds another repository can be caught.

## What coherence means here

**The record, the documents and the tree do not disagree.** koine's particular
version of that failure is narrow and worth naming, because this repository is
made almost entirely of copies of other people's shapes:

- a spec written out in a document that no longer matches the one in
  [`../tests/customers.py`](../tests/customers.py);
- a claim that adoption is free, made after the customer moved;
- a protocol document describing a field the checker does not enforce, or the
  reverse.

The first two are why the customer harness exists and is runnable by a reader.
The third has no guard yet, and is the first thing to build if this grows a
third piece.

## The open work

**Two of the four shared pieces are not built.** The inventory is in
[`drift.md`](drift.md#what-is-not-here): the **branch-state reporter** — what
became of the branch a reply names, which is pure git and identical in both — and
the **reply finder**, which locates and splits a reply file in somebody else's
checkout. Both were asked for, in that order. Neither is started.

**The reply finder is the one to be careful with.** It reads a file written in a
project that is not a member, and what it decides about that file feeds a verdict
about somebody's code. By the division above it is not a low-level detail.

**The protocol has no adopter.** It is checked against both customers' logs and
neither has been asked to run it. Until one does, everything on
[`postmortem-protocol.md`](postmortem-protocol.md) is a design nobody has tested
against a second opinion.

**A second role is proposed and nothing for it is to be built.** `D8` asks
anoieu to record `R26` — *the low-level communication protocols of the reporting
loop* — beside `R16`: three shapes that two tools both write and no role holds.
**koine wants that role**, and `D8` says so plainly rather than hedging; what it
declines to ask for is listed there and in [`maintaining.md`](maintaining.md). **No reply has
come back on any topic in this file**, so nothing in it is agreed.

**The scope test is the working rule, and it is not the one to reach for first.**
Ask **is anybody else maintaining this, and would they want to** — not *is this a
protocol*. koine is a servant for the protocols nobody else wants to maintain;
membership, joining, the discussion protocol and its gate, the inventory and the
entity ids, the channel model and the role handoff procedure are **not
available**, and [`maintaining.md`](maintaining.md) tables them. This repository
has already over-reached twice: `D7` asked for five documents and was withdrawn,
and `D8` asked to be *maintainer of the communication protocols of the Eunoia
ecosystem* before being cut back the same day. **The ground-truth principle is
true of every protocol anywhere, and that is not a reason for koine to hold
them.**

Until `D8` is answered, **write no parser for `board.md` or `roles.md`**, and add
no second `Kind:` vocabulary beside the one in `koine/postmortem.py`. What *is*
open to build meanwhile is the branch-state reporter and then the reply finder —
pieces two and three of the four-piece inventory both customers already asked
for, needing nothing from `D8`.

**And if `R26` is granted, the clause that matters is `Not this role:`.** koine
holds the shape of a message; anoieu keeps every constraint on whether it may be
sent — the STOP gate, *nothing crosses a repository boundary automatically*,
*touch no issue tracker*. A grant without that clause is worse than no grant, and
`D8` says so to them in those words.

**Nothing generates anything yet.** `lessons()` and `open_debts()` return records
and no document is written from them, so anoieu's standing-rules table is still
maintained by hand beside a log that already disagrees with it. Writing that
table is the obvious next piece and has not been asked for.

## Where to start

Run everything first; it takes seconds and needs nothing.

```bash
python3 tests/run.py                                    # the drift check
python3 tests/test_postmortem.py                        # the protocol
python3 tests/customers.py ~/src/anoieu ~/src/dokimasia  # both, against real trees
python3 /path/to/anoieu/tools/policy_check.py --root .   # the ecosystem policy
```

Then read [`../README.md`](../README.md) for what this is for, and
[`discussion.md`](discussion.md) for what is open with whom — without acting on
it.
