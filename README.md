# koine

A tool in the Eunoia ecosystem raises findings about projects that are not its
own: [anoieu](https://github.com/ajreynol/anoieu) reads somebody else's Eunoia
signature, [dokimasia](https://github.com/ajreynol/dokimasia) reads somebody
else's proof-production C++, and each has to get what it found to the people who
own it. The trip is always the same shape. A script runs in the project the
finding is about and leaves a question; somebody answers it in a file; a second
script runs back at home and reads the answer; and a check confirms that the
wording the scripts use still matches the document that defines it.

**koine is where that trip is defined and checked.** It is the shared half of
the reporting loop — the part that is identical no matter which tool is at one
end or which project is at the other.

Not *held once instead of once per tool*, which is how this page used to put it
and is wrong. **Redundancy is a feature; ambiguity about which copy is right is
the defect.** A protocol is read where somebody is working, not where it is
decided, so the copies should exist — a script still carries the prompt it sends,
and should. What makes a copy safe is that the document says which one is the
ground truth and something mechanical compares the rest to it. **koine's job is
to be the ground truth and the comparison, never to be the only copy**, and a
member holds its own copy and keeps working when this repository is unreachable.
[`docs/maintaining.md`](docs/maintaining.md) is the practice in full.

## The question it answers

*How does a finding get from the tool that raised it to the people it is about,
and an answer back, in a form both ends read the same way?*

That is a narrow, mechanical question, and it is the whole of the job. Two tools
in this ecosystem have now built the loop separately and arrived at the same
code for these parts — not similar code, the same code. They overlap in nothing
else: different inputs, different questions, no dependency in either direction.
The loop is the entire intersection, and koine exists because the second one had
to be written at all.

## Its two customers

**anoieu and dokimasia.** Not *tools in the ecosystem* — those two, by name,
today. anoieu reads `.eo` and `.eos` files and asks whether a signature and its
semantics agree; dokimasia reads cvc5's proof-production C++ and asks whether
the solver can reach a conclusion no proof step covers. Different subjects,
different questions, no shared line of code. Both run the same reporting loop,
and that is the only reason this repository has a subject at all.

**We supply the tooling; they run it and own what comes out.** koine does not
maintain anybody's report and does not hold anybody's ledger. A customer's
record stays in the customer's tree, under their name, settled by them, and what
counts as a finding or as an answer stays theirs to decide. This is the boundary
that makes koine cheap to depend on: adopting it costs a tool nothing it would
have to argue about later.

**They decide what gets built.** This repository takes its work from the two
tools that use it and invents nothing on its own. A feature neither has asked
for is a guess about somebody else's needs — likely wrong, and more expensive to
withdraw than it was to write. There is no third party whose hypothetical use
would justify guessing on their behalf.
[`docs/discussion.md`](docs/discussion.md) is where an ask arrives.

**One thing here was not asked for, and it is named rather than blended in.**
koine has volunteered to maintain the [postmortem
protocol](docs/postmortem-protocol.md) — a record neither customer requested and
anoieu explicitly declined to ask for. That is this repository inventing, against
the paragraph above it, and the case for the exception is put where it can be
refused: `D4` in the discussion file. If anoieu says no, the page becomes a
proposal into their document and the code stays available to whoever wants it.

It is the **one** exception, and the boundary below is what keeps it one. Two
larger asks have already been narrowed or withdrawn for crossing it.

**It is plumbing, and means to stay plumbing.** Small, fixed, and correct, with
no property a reader would notice except that nothing went wrong. A clever koine
would be a worse koine.

**It is a servant for the protocols nobody else wants to maintain**, and that is
the whole of its claim. koine does not own the documentation of how protocols
work in this ecosystem, and the higher-level ones are not available to it:
**membership and joining, the discussion protocol and its safety gate, the
inventory of who is in the ecosystem, the procedure by which a role changes
hands, and every position about what may be published.** Those are kanon's, which
took the ecosystem's governance over from anoieu on 2026-09-15, and not because of
seniority — they are the ones somebody is already maintaining, and the ones where
being wrong reaches people who did not sign up. What is left is
the low-level end: the shape of a reply, the shape of a postmortem entry, the
check that a script still says what its document says.

So the test for anything proposed here is **not *is this a protocol*** — it is
**is anybody else maintaining this, and would they want to.** The
[ground-truth principle](docs/maintaining.md) is true of every protocol anywhere,
which makes it tempting to conclude that koine should hold them; it does not
follow, and this repository has already been wrong about that once. A useful rule
and a narrow job are different things.

## The question it does not answer

*Whether the finding is any good.*

koine has no opinion on what is worth reporting, what makes a report correct,
or what settles one. Those belong to the tool that raised it, and they differ
because the subjects differ — the analyzer's questions are not the
scrutineer's. koine carries the envelope and never writes the letter.

The name invites a larger reading, so it is worth refusing in the open: koine
is not a shared standard for how members track issues, keep registers, or agree
on what counts as a problem. Those formats are still being discovered, and
fixing them now would fix them before anybody has evidence about which is
right. Nor does using koine enrol a repository in anything; a tool somebody
depends on is not thereby a member of this ecosystem.

**The findings record does not walk that back**, and the distinction is one a
reader should be able to check rather than take. It holds the shape of a *record*
— the fields a row is written in, so that two producers writing the same row
write the same bytes. It says nothing about what a finding is, when one may be
raised, what rank it carries or what closes it; `rank` and `kind` are carried
through and never read, and the vocabulary of states is the producer's.
[`docs/findings-record.md`](docs/findings-record.md) ends with the list of what
is not decided there, which is the part to hold it to.

## The open question

**The goal is that a reporting structure stays cheap to change.** A tool learns
what its record needs by keeping one: a field it did not know it wanted, a state
that turned out to be two, a view somebody actually has to read. That learning
is expensive today, because the ledger, the reply format and the scripts that
read them were each written once by hand and drift apart the moment any of them
moves. Making those changes cheap is the job.

**The hypothesis, which is open and may be wrong: a reporting record is better
kept in the tree than exported to an issue tracker.** Files under version
control have properties a tracker does not — the record is reviewed in a diff,
it is pinned to a commit, it arrives with a clone, and a program can decide
things about it with no network and no account. Against that, a tracker has what
files do not: notification, search across projects, a stable public URL, and a
way for somebody who will never clone the repository to reply.

This is a low-level technical question rather than a position, and it is the
first one this repository has. What would settle it is a customer running both
and saying which cost them less. If the answer is the tracker, koine is the tool
that should say so first.

**The findings record is the layer under both answers**, which is anoieu's
argument rather than ours and is the reason building one does not settle the
question: the row is the body of an issue, the id is the key, and an issue number
is one more column the format carries and does not read. What it changes is that
moving to a tracker would be a migration rather than a rewrite — which is also
what would let a customer run both and hand us the evidence.

## Running it

**One piece of the loop is built: the prompt-drift check.** A script that carries
a copy of a prompt still says what the document defining that prompt says it
says. It is the piece anoieu asked for first, on the ground that it is the one
guaranteed to rot — it exists to catch divergence, and it was two copies with
nothing watching either. [`docs/drift.md`](docs/drift.md) is the whole of it.

There is no package and no install step. A customer pins a commit, clones it, and
puts the directory on `sys.path` — the same mechanism this ecosystem already uses
to share a policy checker, and the reason adopting this costs one clone and
abandoning it costs restoring a file you already had.

```python
import sys; sys.path.insert(0, "/tmp/koine")
from koine import drift

failures = drift.report(SPEC)      # SPEC is data; docs/drift.md has both customers'
```

Both customers' specs are written out there verbatim, and
`python3 tests/customers.py ~/src/anoieu ~/src/dokimasia` runs them against the
real trees: they reproduce all four of anoieu's cases and all six of dokimasia's,
with no case, form or line of coverage lost. That is a claim worth being able to
re-run rather than take on our word, which is the only reason it is a script. What each would see
change on adopting it is listed in the same document, in full, because a shared
implementation that quietly alters somebody's behaviour is the thing this
repository exists to prevent.

`python3 tests/run.py` is koine's own suite. It needs no dependency, no network
and no customer checked out: everything runs against a miniature repository under
`tests/fixtures/`, and every part of the comparison is tested against a script
that has drifted as well as one that has not.

**The second piece is the postmortem protocol**, and it is offered rather than
owed: *a significant thing happened to this repository — what happened, who was
involved, how did it come out, and what did we learn?* Both customers keep a log
of that shape today and each checks it with its own copy of the same code; the
copies have already lost a field and diverged in behaviour.
[`docs/postmortem-protocol.md`](docs/postmortem-protocol.md) is the definition,
`koine/postmortem.py` reads a log, checks it at either of two levels, and derives
what the log knows — every lesson with the incident that produced it, and every
debt booked and not yet discharged. The same harness measures the adoption cost:
both customers' logs pass the lower level untouched.

**The third piece is the branch-state reporter**, and it is the cheapest of the
four to take: *what became of the branch a reply names* — landed, ahead, absent,
or a question that could not be put at all. It asks nothing of a customer, since
a caller that can name a checkout and a ref can call it, and it writes nothing
anywhere. [`docs/branch.md`](docs/branch.md) is the whole of it, including the
one place the two customers genuinely disagree — what a ref that is not in the
checkout means — which running both implementations against one repository is
what turned up.

**The fourth piece is the findings record**, and it is the first thing here
that a customer asked for in so many words rather than koine offering it. A
finding's row lives in a markdown table at both customers, and in both of them
the *state* of a row is a field nowhere — it is which file the row is filed in,
qualified in prose. anoieu's `D25` asks for a machine-readable record under that
table, written by more than one producer, and asks koine to choose the format
rather than inherit theirs. [`docs/findings-record.md`](docs/findings-record.md)
is the definition and says why it is lines of JSON;
[`koine/findings.py`](koine/findings.py) reads one, writes it canonically, merges
two of them with conflicts reported rather than resolved, and says per id whether
two producers agreed. The condition their topic sets is that the page a reader is
pointed at must not change, so the harness reads both of their real ledgers into
a record and renders them back: 39 rows and 43 rows, byte for byte.

**One of the four shared pieces is left** — the reply finder, asked for third.
It is not started, and it is the one to be careful with: it reads a file written
in a project that is not a member, and what it decides about that file feeds a
verdict about somebody's code.

## The name

κοινή — *koinē*, the common dialect. The Greek that spread after Alexander and
became the tongue people whose Greek differed used to understand each other. It
is here because what two tools running this loop actually share is not code but
a dialect they must both speak; the code is only what keeps them speaking it. It
was also the plain register rather than the literary one, which is the right
ambition for plumbing.

The objection, which belongs in the same paragraph as the claim: κοινή is a
word about communication in general, fastened to a tool about reporting in
particular, and a reader can fairly hear it as *the common one* — the drawer
where shared odds and ends go. That reading is wrong today and would become
right the moment this repository accepts its first piece of code that is merely
shared rather than spoken by both ends of a report. The name is a test as much
as a label, and it can be failed.

`koine` was reserved in the ecosystem's
[register of names](https://github.com/ajreynol/kanon/blob/main/tools/ynoia/names.md)
and approved on 2026-08-31 as proposal `P1`, awaiting a repository. This is the
repository. Taking the name commits this repository to the description written
there, or to changing it.

## How this repository is maintained

This repository is part of the **Eunoia ecosystem** and follows its shared
repository policy, kept by [kanon](https://github.com/ajreynol/kanon) in
[`docs/policy.md`](https://github.com/ajreynol/kanon/blob/main/docs/policy.md).
The program that decides it stays in
[anoieu](https://github.com/ajreynol/anoieu), and that is what CI here pins.

**Written by AI agents, under light human supervision.** A human directs the
work, decides what this repository is for, and reads what is published here;
nobody vets the internal design, and nothing here is carried into another
project without review.
