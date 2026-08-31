# koine

A tool in the Eunoia ecosystem raises findings about projects that are not its
own: [anoieu](https://github.com/ajreynol/anoieu) reads somebody else's Eunoia
signature, [dokimasia](https://github.com/ajreynol/dokimasia) reads somebody
else's proof-production C++, and each has to get what it found to the people who
own it. The trip is always the same shape. A script runs in the project the
finding is about and leaves a question; somebody answers it in a file; a second
script runs back at home and reads the answer; and a check confirms that the
wording the scripts use still matches the document that defines it.

**koine is that trip, held once instead of once per tool.** It is the shared
half of the reporting loop — the part that is identical no matter which tool is
at one end or which project is at the other.

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

**It is plumbing, and means to stay plumbing.** Small, fixed, and correct, with
no property a reader would notice except that nothing went wrong. A clever koine
would be a worse koine.

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

## Running it

Nothing runs. There is no code here yet — no command, no package, no interface —
and how a customer would fetch and call this has not been designed. Saying so is
more useful than a plan. What is here besides this page is the ecosystem's
apparatus: a documentation index, the channel in
[`docs/discussion.md`](docs/discussion.md), and the workflow that holds this
repository to the policy the note at the bottom claims it follows.

If that changes, it will arrive the way this ecosystem shares anything else: a
customer pins a commit and fetches it. That describes the mechanism, not a
release.

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
[register of names](https://github.com/ajreynol/anoieu/blob/main/tools/ynoia/names.md)
and approved on 2026-08-31 as proposal `P1`, awaiting a repository. This is the
repository. Taking the name commits this repository to the description written
there, or to changing it.

## How this repository is maintained

This repository is part of the **Eunoia ecosystem** and follows its shared
repository policy, kept by [anoieu](https://github.com/ajreynol/anoieu) in
[`docs/policy.md`](https://github.com/ajreynol/anoieu/blob/main/docs/policy.md).

**Written by AI agents, under light human supervision.** A human directs the
work, decides what this repository is for, and reads what is published here;
nobody vets the internal design, and nothing here is carried into another
project without review.
