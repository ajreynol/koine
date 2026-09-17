# koine

**Every tool here is built to find something. koine is built to keep it.**

The tools in this ecosystem exist to find bugs in projects that are not their
own. [anoieu](https://github.com/ajreynol/anoieu) reads somebody else's Eunoia
signatures and asks whether a signature and its semantics agree;
[dokimasia](https://github.com/ajreynol/dokimasia) reads cvc5's proof-production
C++ and asks whether the solver can reach a conclusion no proof step covers.
Finding the bug is the work those tools were built for, and it is the part worth
their attention.

Then there is the other half, which nobody built a tool to do and everybody
needs done: keeping the list. Not losing the bug found in March. Not filing it
again in September under a new name. Not letting this week's run quietly
overwrite last week's record, or leaving two half-written files behind because a
job was interrupted. It is unglamorous, it is fiddly, it is the same in every
tool that has it, and it is exactly the kind of thing that gets written three
times badly because writing it once well was nobody's job.

**It is ours.** koine does not find bugs, does not decide whether a bug is real,
and has no opinion about what should be done with one. Those belong to the tool
that raised it, and they stay there. We keep the list, and we keep it properly,
so that nobody else has to think about it again.

**The same shape turned up again in the ecosystem's commands.** A script that
serves every repository here still belongs to whichever one wrote it, and none
of them is a natural place to put it on somebody's path. So they are kept here
and installed from here, and not one word of them changes on the way. Again the
interesting half stayed where it was, and the keeping came to us.

## What koine is for

Two things, and a reader who needs one of them can stop after it.

**1. Tooling for keeping bug databases.** A tool runs over somebody else's
project and dumps what it found *this time*; its database is everything it has
ever found. [`bug_db/koine_append_db`](bug_db/koine_append_db) is the trip
between the two, and it is the same trip in every tool that has one — which is
why it is written once here instead of three times badly elsewhere.
[anoieu](https://github.com/ajreynol/anoieu) and
[dokimasia](https://github.com/ajreynol/dokimasia) are the customers: each pins
a commit of this repository and calls it from its own run.
**[`bug_db/README.md`](bug_db/README.md) is the whole of it** — the worked
example, the one rule that makes it a database, and what it refuses to do.

**2. [`eo_cmd/`](eo_cmd), the ecosystem's commands.** Scripts that are useful
across the Eunoia ecosystem rather than inside any one repository, kept together
and put on a person's path by
[`scripts/install_eo_cmd`](scripts/install_eo_cmd). **koine keeps these and does
not write them** — the repository each one comes from is the authority for every
word of it, and the copies are held to that mechanically rather than by promise.
**[`eo_cmd/README.md`](eo_cmd/README.md) is the whole of it** — what is in
there, where each one came from, and how a copy is proved unmodified.

## Also here: reviewing the history record

**This is neither of the two above.** It came in on 2026-09-16 when the history
review child project was dissolved into this tree.

The Eunoia ecosystem keeps a term record — `docs/history.md`, in whichever
repository holds the office — saying what a term was for, what changed, what
went wrong, and what crosses to the next one. It is written by the people who
did the work, which is what makes it worth reading and also what makes it worth
reviewing: a record that quietly loses a failure is worse than no record.

[`scripts/koine_history`](scripts/koine_history) reads that file's history in a
Git checkout and reports, per change, what it touched, what it added and
removed, and which questions a reviewer should ask about it — a figure added
with nothing supporting it, failure language removed, an earlier term's section
edited. **It writes no verdict.** A person writes that into
[`docs/history-ledger.md`](docs/history-ledger.md), and `--append` adds rows for
changes that have none and never touches a row that does.

```console
$ scripts/koine_history /path/to/record-repository
$ scripts/koine_history /path/to/record-repository --append
```

It never writes to the record it reads, and it gates nothing.
[`docs/history-review.md`](docs/history-review.md) is the review standard, the
two axes it distinguishes, and the limits of its signals.

## What else is in this tree

**One directory per purpose**, each with a README that is the whole of its
subject: [`bug_db/`](bug_db) and [`eo_cmd/`](eo_cmd). [`scripts/`](scripts)
holds the programs that are not themselves a purpose — the installer that
serves `eo_cmd/`, and the history tool. [`tests/`](tests) drives all three.

[`docs/`](docs/README.md) holds the history review standard and ledger, the
maintenance entry point, and [`discussion.md`](docs/discussion.md), the channel
to the rest of the ecosystem. **No agent acts on the discussion file unbidden**
— the rule is at the top of it.

**An earlier version of this repository was a reporting-loop library** — a
prompt-drift check, a branch-state reporter, a postmortem protocol and a findings
record. It was deleted on 2026-09-16 when the repository was pointed at the job
described above. It is in git history, nothing depends on it, and it is mentioned
here only so that a reader who finds a reference to it knows where it went.

## The name

κοινή — *koinē*, the common dialect: the Greek that spread after Alexander and
became the tongue people whose Greek differed used to understand each other. It
was the plain register rather than the literary one, which is the right ambition
for a script that appends to a file.

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
