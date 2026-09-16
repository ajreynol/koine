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
ethos and logos are not — at anoieu `2172a1b`, read 2026-09-02, cvc5 is
`foundation` and ethos and logos are `candidate` with `proposed: associate` in
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
| the role handoff procedure | **anoieu's, and now claimed** — a seven-step procedure in their `roles.md`, and a second protocol in their `coherence.md` for a role that crosses to another project | governance, not a shape |
| every prompt template; every position on publishing | `R1` | a position is what somebody signs |

**The test that puts something here:** somebody else maintains it, **or** being
wrong about it reaches people who did not sign up for this. Either is enough.

**What to do when a task lands on this list:** stop, say which row it is, and ask
which repository was meant. Do not build the smaller safe part.

**One override has been given against this list, and it is recorded here because
an instruction that lives only in a session is one the next session does not
have.** On 2026-09-02 the maintainer was asked which tree should hold a child
project auditing the ecosystem's record of its own history — a subject that is
governance, that this tree does not keep, and that the list above would send
somewhere else. **They chose this one**, over the two repositories that hold the
record, on the ground that a register of whether a record improves is worth
something only from outside the party writing it.

**It widens nothing.** A child project lives in `tools/`, is not part of what
this repository ships, is advertised nowhere, and is deleted without anything
here noticing — which is the test rather than the intention. **koine's scope is
unchanged**: it holds no governance protocol, has taken on no maintenance
obligation, and has not been asked to have an opinion about epochs, membership
or the presidency. What is in `tools/epidosis/` reads a file in somebody else's
tree and writes only inside its own directory.

**The question was put to a person rather than settled here**, and the reason is
a rule of anoieu's that this repository is the incident behind: an agent asked
whether koine should hold something will find the case for holding it, because
finding it is what it was asked to do.

#### 3. Undecided. Stop and name the topic that would settle it.

| question | what would settle it |
| --- | --- |
| does koine hold the postmortem shape at all | `D4`, unanswered |
| does `R26` exist | `D8`, unanswered |
| is our reading of anoieu's practice right | `D9`, **answered and carried** — *substantially right*, corrected in five places, 2026-09-02 |
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

**And when a commit is taken while the work is still moving, say so in one
line.** The convention is anoieu's, read off their `coherence.md` at anoieu
`12c2015` on 2026-09-01. Committing mid-stream is nobody's fault and will keep
happening; what it costs is that the commit's message stops describing its
contents, and a reader looking for a change finds it filed under a subject it
has nothing to do with. The remedy is deliberately small — **one line naming the
commit and what it actually carries.** Anyone may write it, anyone may delete
it, at any time, without asking: it is a note about the record, not a record.

> **Noted 2026-09-01, and removable.** `2c8886a` — *"Preparation for
> deployment"* — was taken mid-stream by a second agent instance running in this
> same working directory, and its subject names the intent rather than the
> contents. What it carries: anoieu's replies recorded against `D9` (their
> `D13`) and against `D8` (`R26` named in their `roles.md` and deliberately not
> granted); the re-check of `D5`'s four defects, and of `D1`, `D2` and `D6`,
> against anoieu `9794f31` and dokimasia `99cf6e1`; and one factual correction
> in this file — cvc5's footing is `foundation`, where we had said `served`.

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

## The refresh, and what it found

**A member makes its copy of the shared arrangements current before relying on
them**, which is anoieu's protocol and not ours; what is ours is doing it and
writing down the date. Run **2026-09-02**, against a checkout of anoieu at
`2172a1b` and dokimasia at `f9a5bd7`.

**We were 145 commits behind.** The pin in
[`../.github/workflows/anoieu.yml`](../.github/workflows/anoieu.yml) is `5668c20`,
dated 2026-08-31; their tip that day was two days newer.

**The pin did not move, and the reason is the interesting half.** A member may
only bump to a commit where their build was green, and **not being able to find
out is a refusal rather than a pass** — their own `bump_check.py`, run from this
tree, could not reach the API that answers it and returned a refusal. So the pin
stays where it is, which costs nothing: this tree passes the policy check at
their tip as well, so nothing here is waiting on the bump.

**What moved that touches this repository.**

| what | where it stands here |
| --- | --- |
| **both customers moved their prompt scripts** | anoieu's are at `prompts/`, dokimasia's under `scripts/prompts/`. Our spec followed the old paths and reported ten failures that were ours, not theirs — corrected, and the harness is back to `0` against both real trees |
| **the protocols acquired ids** | anoieu now keeps a register of them, `PROTO-n`, scattered across the pages that own each. Two bind every member rather than only them: the one that says an agent tells a person to take a break outside the hours they set, and the one that says every response names the tool it is acting for and the AI answering. **Neither changes a file here** |
| **the role handoff stopped being unowned** | it is theirs, written down twice — the seven steps in their roles register, and a second protocol for a role that crosses to another project |
| **a stretch is now deployed against a written policy** | it is addressed to the president and to nobody else, and no member is held to any of it |
| **a publishing stance is owed** | by every member and by every child project in its tree. koine has not stated one — see the open work below |

**This section is a copy, and nothing compares it.** The register of protocols is
anoieu's and is the ground truth; what is above is our reading of which of them
reach us, written down because a member that has not read them is complying with
a version nobody publishes any more. **Where their page and this one disagree,
theirs is right.**

## The open work

**One answer is owed to anoieu and it is not an agent's to give.** A publishing
stance, owed by this repository and by every child project in its tree — whether
there is a paper in the work, or a plan for one, or nothing worth writing up.
**All three are answers**, the third is the commonest, and which one it is is a
position somebody signs rather than a detail an agent settles. **Asked on
2026-09-02 and left unstated**, which is where it stays until somebody states it.

*Their correction of our reading of their practice was carried on 2026-09-02 and
is no longer outstanding — [`maintaining.md`](maintaining.md) marks what came
from them.*

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
declines to ask for is listed there and in [`maintaining.md`](maintaining.md). **One reply has come back** — their answer
to `D9`, recorded under that topic — **and `D8` is not it**, so the role is still
unagreed. Two of their topics ask something of us and neither has been worked: a
publishing stance, owed by every member and by every child project in its tree,
and a pin that may only move to a commit where their CI was green.

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
