# koine

**Maintains the shared tooling for the Eunoia ecosystem**

koine serves the tools of the Eunoia ecosystem by **taking responsibility** for
tooling that is either shared between them, or that an existing tool does not
want to maintain.

It finds nothing, settles nothing, and has no opinion about what anyone should
do with what it keeps. All three belong to the tool that raised the work, and
they stay there.

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

## What else is in this tree

**One directory per purpose**, each with a README that is the whole of its
subject: [`bug_db/`](bug_db) and [`eo_cmd/`](eo_cmd). [`scripts/`](scripts)
holds `install_eo_cmd`, which serves `eo_cmd/` without being a purpose of its
own, and [`tests/`](tests) drives both.

[`docs/`](docs/README.md) holds the maintenance entry point and
[`discussion.md`](docs/discussion.md), the channel to the rest of the
ecosystem. **No agent acts on the discussion file unbidden**
— the rule is at the top of it.

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
