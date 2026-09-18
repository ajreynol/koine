# koine

**Maintains the shared tooling for the Eunoia ecosystem**

koine serves the tools of the Eunoia ecosystem by **taking responsibility** for
tooling that is either shared between them, or that an existing tool does not
want to maintain.

**Koine maintains the tooling, not the bug databases.** Anoieu and dokimasia
own and maintain their databases: their findings, evidence, triage, cleanup,
and closure decisions. Koine supplies the programs they use to do that work.

## What koine is for

Two things, and a reader who needs one of them can stop after it.

**1. Tooling for keeping bug databases.** A tool runs over somebody else's
project and dumps what it found *this time*; its database is everything it has
ever found. [`bug_db_manager/koine_append_db`](bug_db_manager/koine_append_db) is the trip
between the two, and it is the same trip in every tool that has one — which is
why it is written once here instead of three times badly elsewhere.
[anoieu](https://github.com/ajreynol/anoieu) and
[dokimasia](https://github.com/ajreynol/dokimasia) are the customers, checked on
2026-09-18: each records a koine dependency pin and calls the writer from its
own run. Their database files remain in their own repositories.
**[`bug_db_manager/README.md`](bug_db_manager/README.md) is the whole of it** — the worked
example, the one rule that makes it a database, what happens when two runs
arrive at once, and the evidence needed for future cleanup tooling.

**2. [`eo_cmd/`](eo_cmd), the commands that run inside somebody else's tree.**
`eo_init` starts a tool and `eo_join` joins it; `eo_status` says who is in this
ecosystem and on what footing; `eo_git_status` shows Git status across local
checkouts; `eo_child` starts a child project and `eo_topic`
opens one topic addressed to another tool; `eo_respond` answers one topic another
tool addressed to you; `eo_housekeeping` brings a repository up to date, and
`eo_brainstorm` looks for what it could do next, works through the list with
you, and changes nothing. These run where a person is working, with
`eo_git_status` also accepting directories to search. They live with the tool
whose job is shared machinery, and
[`scripts/install_eo`](scripts/install_eo) puts them on a person's path.
**koine maintains what they ask and has no standing to change what joining
costs** — that stays with the office.
**[`eo_cmd/README.md`](eo_cmd/README.md) is the whole of it** — one section per
command, and where the line between maintaining them and owning what they ask
falls.

## What else is in this tree

**One directory per purpose**, each with a README that is the whole of its
subject: [`bug_db_manager/`](bug_db_manager) and [`eo_cmd/`](eo_cmd). [`scripts/`](scripts)
holds `install_eo`, which serves `eo_cmd/` without being a purpose of its
own, and [`tests/`](tests) drives both.

[`docs/`](docs/README.md) holds the maintenance entry point and
[`discussion.md`](docs/discussion.md), the channel to the rest of the
ecosystem. **No agent acts on the discussion file unbidden**
— the rule is at the top of it.

No paper is planned for koine, on the maintainer's instruction of 2026-09-18.

## Running it

From this checkout:

```bash
python3 bug_db_manager/koine_append_db run.json bugs.json
scripts/install_eo --prefix ~/bin
eo_cmd/eo_housekeeping --show-prompt
eo_cmd/eo_git_status
```

The first command appends a JSON dump to a bug database. The installer puts the
shared commands on your PATH; the preview shows the work an assistant would be
asked to do. `eo_housekeeping` and `eo_respond` ensure `main` before pulling;
`--no-main` keeps the current branch. Their [command guide](eo_cmd/README.md)
describes the options and failure behavior. `eo_git_status` reads nearby
checkouts and linked worktrees without fetching; give it extra directories for
checkouts elsewhere.

## The name

κοινή — *koinē*, the common dialect: the Greek that spread after Alexander and
became the tongue people whose Greek differed used to understand each other. It
was the plain register rather than the literary one, which is the right ambition
for a script that appends to a file.

## Common questions

Mostly routing, because the commonest question about koine is which repository
the asker actually wants. These trees are alike on purpose and several sit side
by side on one disk.

- **Where is the repository policy, and what does joining cost?** Neither is
  koine's. Both are [kanon](https://github.com/ajreynol/kanon)'s, in
  `docs/policy.md`. koine maintains `eo_join`, which *states* that rule and
  cannot change it.
- **What decides whether my tree complies?** The policy checker, published by
  [anoieu](https://github.com/ajreynol/anoieu). koine follows its current
  implementation using policy contract 1.
- **Who is in this ecosystem, and on what footing?** The register, which kanon
  holds. [`eo_cmd/eo_status`](eo_cmd/eo_status) prints what it says and never
  writes to it — a footing is a decision somebody made, not one a program takes.
- **How do I start a tool, or join?** [`eo_cmd/`](eo_cmd/README.md) —
  `eo_init` and `eo_join`, run inside the tree being started or joined, and put
  on your path by [`scripts/install_eo`](scripts/install_eo).
- **Where do I report a bug you found in one of these tools?** Not here. A
  defect with a file and a line number is a finding, and anoieu keeps the
  reporting workflow that says how one is carried. Anything else goes in that
  tool's own `docs/discussion.md`.
- **Is this where the bug database itself lives?** No. koine keeps the program
  that appends to one. Anoieu and dokimasia maintain their own databases,
  including deciding what to close, reopen, correct, or retain.

## How this repository is maintained

This repository is part of the **Eunoia ecosystem** and follows its shared
repository policy, kept by [kanon](https://github.com/ajreynol/kanon) in
[`docs/policy.md`](https://github.com/ajreynol/kanon/blob/main/docs/policy.md).
The program that decides it stays in
[anoieu](https://github.com/ajreynol/anoieu). CI follows policy contract 1.

**Written by AI agents, under light human supervision.** A human directs the
work, decides what this repository is for, and reads what is published here;
nobody vets the internal design, and nothing here is carried into another
project without review.
