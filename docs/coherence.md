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
anoieu to record `R26` — *the low-level formats of the reporting loop* — beside
`R16`: three shapes that two tools both write and no role holds. **No reply has
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
