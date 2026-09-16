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
| the prompt-drift check | [`../koine_drift.py`](../koine_drift.py), [`drift.md`](drift.md) | anoieu and dokimasia, when each drops their copy |
| the branch-state reporter | [`../koine_branch.py`](../koine_branch.py), [`branch.md`](branch.md) | anoieu and dokimasia, when each drops their copy |
| **the postmortem protocol** | [`postmortem-protocol.md`](postmortem-protocol.md), [`../koine_postmortem.py`](../koine_postmortem.py) | **proposed**: a shape both keep today, offered here instead |
| the findings record | [`findings-record.md`](findings-record.md), [`../koine_findings.py`](../koine_findings.py) | anoieu, who asked for it in `D25`; dokimasia, whose registers it was checked against before it was built |
| the evidence that adoption is free | [`../tests/customers.py`](../tests/customers.py) | nobody, and it is the reason anybody should believe the other rows |

The bold row is bold because it is different in kind. The drift check and the
branch reporter are *code two repositories had written twice*; the postmortem
protocol is **a document other repositories would follow**, and koine has asked
for it rather than been given it. Until anoieu answers, the shape is still
theirs.

**The findings record is the other way round**, which is why it is not bold: it
is also a document other repositories would follow, and it was **asked for**, by
name, with the choice of format handed over explicitly. It is the first row here
that arrived that way.

### Why the modules are `koine_*.py` at the root, and not a package

The maintainer asked for this on 2026-09-16, and the reason they gave is the
first one: **a directory named `koine` inside a repository named `koine` reads
as a second thing**, and a reader opening the tree has to work out that it is
not one.

There is a second reason, and it is the one that would make this hard to undo.
A customer adopts koine by putting **the repository root** on `sys.path` — there
is no package and no install step, deliberately. Anything at that root is
therefore a name claimed inside somebody else's process, and `drift`, `branch`
and `findings` are names another project may well want. `koine_drift` cannot
collide with anything, and says whose it is at the point of use rather than at
the point of import.

So: **one module per piece, at the root, named `koine_<piece>.py`.** The examples
in the documents write `import koine_drift as drift`, which shows the real name
and keeps the call sites short.

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

**The scope of that is member-only traffic.** anoieu, dokimasia, eudaimonia,
epikrisis, logos and koine are members, and kanon is president: they have joined,
they read diffs, and a mistake between them is corrected in a commit by somebody
who was already going to read it. cvc5 and ethos are not — at kanon `4c4a78a`,
read 2026-09-16, cvc5 is `foundation` and ethos is `candidate` with
`proposed: associate` in
[`ecosystem.json`](https://github.com/ajreynol/kanon/blob/main/scripts/ecosystem/ecosystem.json),
and what reaches them reaches people who did not sign up for this. **Anything
that will be read outside the island is not a low-level detail**, whatever else
it is: an outbound prompt, a finding, a claim about somebody's code. The
ecosystem's own rule is the same one — everything that reaches a person who did
not ask for it is sent by a person.

**The island grew since the last refresh, and that loosens rather than tightens.**
logos and epikrisis are members now, where this page had logos outside; kanon is
new and is president. Nothing that was inside has moved out, so no traffic this
page previously treated as internal has become external.

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
| the branch-state reporter | built, `R16` |
| the reply finder | asked for by both customers, not started |
| the postmortem entry shape | built; offered in `D4` |
| the findings record | built; asked for in anoieu's `D25`, 2026-09-16 |

**The test that puts something here:** two tools already write it, no role holds
it, and it is a **shape** rather than a decision. All three, or it is not on this
list.

#### 2. Not ours. Do not design it, do not build it, do not have an opinion in the tree.

| | whose | why not |
| --- | --- | --- |
| **epochs** | the maintainer's | **THE DESIGN OF EPOCHS IS NOT KOINE'S TO DECIDE.** It is a high-level protocol; koine holds low-level ones and carries **no knowledge of how epochs are implemented** |
| global announcements, and who is told | `R4`, **kanon's** | the same reason, one level down |
| membership, joining, the repository policy | `R4`, **kanon's** | it decides who is in |
| the discussion protocol and its safety gate | `R4`, **kanon's** | being wrong here reaches people who did not sign up |
| the inventory, and the entity ids | `R6`, **kanon's** | koine *references* the vocabulary; owning it would be owning membership |
| the channel model — who has a wire at all | unowned, kanon's to claim | a membership rule wearing a format's clothes |
| the role handoff procedure | **kanon's, and claimed** — the procedure and the role register are theirs since the handoff | governance, not a shape |
| the policy checker itself | `R31`, **anoieu's** | it stayed behind when the documents moved, and our CI pins it |
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
| does the record's format suit a second ledger | partly answered by running it: dokimasia's registers read into it, and the one place it does not fit is their retraction table, which has no id space. `D25` settles when they say so |
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
line.** The convention was read off anoieu's `coherence.md` at anoieu `12c2015`
on 2026-09-01; that page is kanon's now, and the convention went with it.
Committing mid-stream is nobody's fault and will keep
happening; what it costs is that the commit's message stops describing its
contents, and a reader looking for a change finds it filed under a subject it
has nothing to do with. The remedy is deliberately small — **one line naming the
commit and what it actually carries.** Anyone may write it, anyone may delete
it, at any time, without asking: it is a note about the record, not a record.

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
**The third still has no guard, and this repository has now grown its fourth
piece** — [`branch.md`](branch.md) describes four states and a default that
`koine_branch.py` implements, and nothing compares the two. That was named here
as the thing to build at exactly this point, and it has not been built; it is
recorded rather than quietly dropped. The findings record arrives with the same
gap in one place and without it in another: `tests/test_findings.py` fails on
every rule the document states, and `tests/customers.py` re-derives every number
the document quotes about the two real registers — but the field *table* on the
page and the `FIELDS` tuple in the module are still two copies with nothing
comparing them.

## The refresh, and what it found

**A member makes its copy of the shared arrangements current before relying on
them**, which is the ecosystem's protocol and not ours; what is ours is doing it
and writing down the date. Run **2026-09-16**, against checkouts of anoieu at
`442bb67`, dokimasia at `f9a5bd7` and kanon at `4c4a78a`.

**The governance moved to another repository, and that is the whole of this
refresh.** On 2026-09-15, in anoieu `ca58216` and kanon `7eb9973`, the shared
policy, the vision, the laws, the board, the role register, the inventory, the
installer and the joining prompts left anoieu for **kanon**, which is now
president. **anoieu kept the analyzer, the fuzzer, the findings system and the
policy checker** — and the checker moved within their tree, from
`tools/policy_check.py` to `scripts/policy_check.py`.

**Nothing about koine's job changed, and nothing this repository holds moved.**
`R16` is still ours and is now recorded in kanon's register. What changed is
**who to ask**, which is most of what this page is for.

**dokimasia has not moved since the last refresh.** Their tip is still `f9a5bd7`.

**The pin did not move, for the same reason as last time.** A member may only
bump to a commit where the checker's build was green, and **not being able to
find out is a refusal rather than a pass** — that check needs an API this tree
cannot reach. So the pin in
[`../.github/workflows/anoieu.yml`](../.github/workflows/anoieu.yml) stays at
`5668c20`, which costs nothing: this tree passes the policy check at anoieu's tip
as well, with `0` failures, so nothing here is waiting on the bump. **The pin and
the path are coupled now** — `tools/policy_check.py` is correct at `5668c20` and
wrong at the tip, so whoever moves the pin moves the path in the same commit. The
workflow says so beside the pin.

**What moved that touches this repository.**

| what | where it stands here |
| --- | --- |
| **the policy, and where we say we follow it** | kanon's `docs/policy.md`. The front page's maintenance note pointed at anoieu's copy, which no longer exists — corrected, and it now names kanon for the policy and anoieu for the program that decides it |
| **the inventory** | kanon's `scripts/ecosystem/ecosystem.json`. Two links here and in [`postmortem-protocol.md`](postmortem-protocol.md) followed the old path — corrected. The entity ids themselves did not change |
| **the register of names** | kanon's tree, under `ynoia`. The front page's link to it was dead — corrected |
| **the island got bigger** | logos and epikrisis are members; kanon is president. Nothing left the island, so nothing this page treated as internal is now external |
| **`R4` and `R6` changed hands** | both are kanon's. The *Not ours* table named anoieu — corrected. The ids are unchanged |
| **the checker acquired a role of its own** | `R31`, anoieu's, listed in the *Not ours* table because our CI pins it and it is not ours to move |
| **both customers' prompt scripts** | unmoved since the last refresh. `tests/customers.py` reproduces all four of anoieu's cases and all six of dokimasia's, `0` failures against both real trees |
| **a publishing stance is still owed** | by every member and by every child project in its tree. koine has not stated one — see the open work below |

**This section is a copy, and nothing compares it.** kanon's pages are the ground
truth; what is above is our reading of which of them reach us, written down
because a member that has not read them is complying with a version nobody
publishes any more. **Where their page and this one disagree, theirs is right.**

## The open work

**One answer is owed and it is not an agent's to give.** A publishing stance,
owed by this repository and by every child project in its tree — whether there is
a paper in the work, or a plan for one, or nothing worth writing up. **All three
are answers**, the third is the commonest, and which one it is is a position
somebody signs rather than a detail an agent settles. **Asked by anoieu on
2026-09-02 and left unstated**, which is where it stays until somebody states it.
The requirement itself is now kanon's page rather than anoieu's, and it moved
with the rest of the policy; the answer owed is the same one.

*Their correction of our reading of their practice was carried on 2026-09-02 and
is no longer outstanding — [`maintaining.md`](maintaining.md) marks what came
from them.*

**One of the four shared pieces is left.** The inventory is in
[`drift.md`](drift.md#what-is-not-here). The **branch-state reporter** was built
on 2026-09-16 — [`branch.md`](branch.md) — leaving the **reply finder**, which
locates and splits a reply file in somebody else's checkout.

**The findings record was built on 2026-09-16, on anoieu's `D25`.** It is the
first piece here a customer asked for in so many words, and `D25` hands koine the
choice of format explicitly. What was decided, and is an agent's to decide under
the division above: lines of JSON, the state of a row as a field with the
producer's own word in it, runs carried beside rows so an absence can be told
from an unread file, a merge that reports conflicts instead of resolving them,
and a per-id comparison of two producers.
[`findings-record.md`](findings-record.md) ends with what is *not* decided there
— what counts as a finding, what closes a row, what a rank means, the id scheme —
and that list is the part to hold a grant of this to.

**The check `D25` asked to have run first was run first**, and it is in the
document: 51 rows out of dokimasia's eight registers, against 82 of anoieu's, and
the two share `id`, `what`, `code`, `state` and `verdict` and nothing else
reliably. Every other field is optional because of that measurement rather than
by design. **`D25` is not thereby settled.** It settles when anoieu says the
format is theirs or is not, and saying so is a person carrying it — nothing here
replies to a topic.

**The reply finder is the one to be careful with.** It reads a file written in a
project that is not a member, and what it decides about that file feeds a verdict
about somebody's code. By the division above it is not a low-level detail.

**Building the branch reporter turned up something neither document said.** The
two customers disagree about what a ref that is not in the checkout means —
anoieu holds a commit and reads it as a stale checkout, dokimasia holds a branch
name and reads it as *nothing has been answered on it*. Both are right, nothing
in a repository tells them apart, and `Query.missing` carries the difference
rather than koine choosing. **Only running both implementations against one
repository showed it**, which is an argument for the customer harness doing that
for every piece rather than only for the ones with specs.

**The protocol has no adopter.** It is checked against both customers' logs and
neither has been asked to run it. Until one does, everything on
[`postmortem-protocol.md`](postmortem-protocol.md) is a design nobody has tested
against a second opinion.

**A second role is proposed and nothing for it is to be built.** `D8` asks for
`R26` — *the low-level communication protocols of the reporting loop* — beside
`R16`: three shapes that two tools both write and no role holds. **koine wants
that role**, and `D8` says so plainly rather than hedging; what it declines to
ask for is listed there and in [`maintaining.md`](maintaining.md). **One reply
has come back** — the answer to `D9`, recorded under that topic — **and `D8` is
not it**, so the role is still unagreed. Two topics ask something of us and
neither has been worked: a publishing stance, and a pin that may only move to a
commit where the checker's CI was green.

**`D8` is addressed to anoieu and the register it asks about is now kanon's.**
Their role page still says `R26` is deliberately unallocated because koine's
request is open, so the ask has not been lost — but the repository that would
grant it has changed since the topic was written. **Re-addressing a topic is
acting on the discussion file, which no agent does unbidden**, so this is left
for a person to redirect or restate.

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
no second `Kind:` vocabulary beside the one in `koine_postmortem.py`. What *is*
open to build meanwhile is the branch-state reporter and then the reply finder —
pieces two and three of the four-piece inventory both customers already asked
for, needing nothing from `D8`.

**And if `R26` is granted, the clause that matters is `Not this role:`.** koine
holds the shape of a message; the constraints on whether it may be sent are
somebody else's — the STOP gate, *nothing crosses a repository boundary
automatically*, *touch no issue tracker*, which sit in kanon's policy and vision
pages since the handoff. A grant without that clause is worse than no grant, and
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
python3 tests/test_findings.py                          # the findings record
python3 tests/test_branch.py                            # the branch reporter
python3 tests/customers.py ~/src/anoieu ~/src/dokimasia  # both, against real trees
python3 /path/to/anoieu/scripts/policy_check.py --root .  # the ecosystem policy
```

Then read [`../README.md`](../README.md) for what this is for, and
[`discussion.md`](discussion.md) for what is open with whom — without acting on
it.
