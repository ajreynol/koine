# koine

**koine maintains the tooling that nobody else wants to maintain.**

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
so that nobody else has to think about it again. We also maintain a history
review tool: it lists changes and preserves reviewers' readings, with the
judgement left to the reviewer.

## What it does

Two scripts: `koine_append_db` keeps the bug database, and `koine_history`
supports review of the ecosystem's history record.

## Keeping the bug database

```
koine_append_db <new bugs> <bug database>
```

A tool runs and dumps what it found this time. The database is every bug it has
ever found. This puts the first into the second.

### A worked example

anoieu runs and writes `run1.json`:

```json
[
  {"bug": "EO0031-ArithExt-17", "tool": "anoieu",
   "description": "`@arith_vts_delta` is declared twice with the type Real"},
  {"bug": "DOC0011-Strings-202", "tool": "anoieu",
   "description": "program `$re_ac_merge` takes 3 arguments, docstring lists 5"}
]
```

There is no database yet, so one is made:

```console
$ koine_append_db run1.json bugs.json
-- 2 new bug(s), 0 already known, 0 conflict(s)
-- the database holds 2 bug(s) from 1 tool(s): anoieu 2
-- wrote bugs.json (created)
```

Months later anoieu runs again. It finds the first bug still there, one new one,
and dokimasia adds one of its own:

```console
$ koine_append_db run2.json bugs.json
-- 2 new bug(s), 1 already known, 0 conflict(s)
-- the database holds 4 bug(s) from 2 tool(s): anoieu 3, dokimasia 1
-- wrote bugs.json
```

`bugs.json` now holds all four, with the March bug still carrying March:

```json
{
  "bugs": [
    {
      "bug": "EO0031-ArithExt-17",
      "tool": "anoieu",
      "description": "`@arith_vts_delta` is declared twice with the type Real",
      "first_seen": "2026-03-04",
      "last_seen": "2026-09-16"
    },
    {
      "bug": "DOC0011-Strings-202",
      "tool": "anoieu",
      "description": "program `$re_ac_merge` takes 3 arguments, docstring lists 5",
      "first_seen": "2026-03-04",
      "last_seen": "2026-05-01"
    }
  ]
}
```

The second bug's `last_seen` is May because the September run did not mention
it. That is a fact worth having and the script records it; it does **not**
conclude that the bug was fixed, because a run that did not look and a run that
found nothing are not the same thing and nothing in these two files tells them
apart.

### The one rule that makes it a database

**A bug is added once.** It is identified by its `tool` and its `bug` together,
or by an `id` where the tool mints one. Run the same dump twice and the second
run adds nothing.

That is the property that lets this be wired into a job instead of remembered.
Re-running is free, so a run that half-failed can simply be run again.

### What it will not do

- **It never edits a bug already in the database, and never removes one.** If a
  later run describes a known bug differently, that is printed as a conflict and
  the database keeps what it has. A record of what was found over time is worth
  having only if nothing quietly rewrites it, and deciding that the new wording
  is the better one is a person's call.
- **Nothing is written unless the whole dump is readable.** One malformed entry
  and the run writes nothing at all, so a half-applied dump is not a state the
  database can be in.
- **It does not write anything anywhere else**, fetch anything, or need a
  network. It reads two files and replaces one of them, and the replacement is
  atomic, so an interrupted run leaves the old database intact.

### The two files

They are the same shape, so a database can be fed back in as a dump:

```json
{"bugs": [{"bug": "...", "tool": "...", "description": "..."}]}
```

A bare JSON list is accepted as well, since that is what a tool's first dump
usually looks like. `bug`, `tool` and `description` are what a bug is; **a tool
may carry any other fields it likes** — a path, a line, a rank, a URL — and they
are kept exactly as they arrive. koine adds `first_seen` and `last_seen` and
nothing else. There is no schema to agree on beyond the key.

### Running it

```console
$ python3 tests/test_append_db.py
```

No dependencies, no network, nothing to install. `--dry-run` says what would
change and writes nothing; `--date` records a run under a date other than today.

## Reviewing the history record

```console
$ ./koine_history /path/to/record-repository
$ ./koine_history /path/to/record-repository --append
```

`koine_history` reads changes to `docs/history.md` in a local Git checkout and
reports what each change touched, added, and removed, along with questions for a
reviewer. `--append` adds changes not yet recorded to
[`docs/history-ledger.md`](docs/history-ledger.md) in this Koine checkout. It
preserves every existing row and handwritten verdict. Without `--append`, it
only prints the report; it never writes to the source record.

The [review standard and design decisions](docs/history-review.md) distinguish
checkable meaning from technical progress. The script supplies signals, and a
reviewer supplies the judgement. This is advisory and does not gate a deployment.

Both tools keep earlier records, separate evidence from decisions, and work
locally without a network. The history tool also needs Git. Run its tests with
`python3 tests/test_history.py`; both test scripts run in Koine's CI.

## What else is in this tree

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
