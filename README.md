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

Three jobs, and none of them is finding a bug. Everything runnable is in
[`scripts/`](scripts): `koine_append_db` keeps the bug database, `koine_history`
supports review of the ecosystem's history record, and `install_eo_cmd` puts the
ecosystem's commands on a person's path.

## Keeping the bug database

```
scripts/koine_append_db <new bugs> <bug database>
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
$ scripts/koine_append_db run1.json bugs.json
-- 2 new bug(s), 0 already known, 0 conflict(s)
-- the database holds 2 bug(s) from 1 tool(s): anoieu 2
-- wrote bugs.json (created)
```

Months later anoieu runs again. It finds the first bug still there, one new one,
and dokimasia adds one of its own:

```console
$ scripts/koine_append_db run2.json bugs.json
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

No dependencies and no network. `--dry-run` says what would change and writes
nothing; `--date` records a run under a date other than today.

**The commands live in [`scripts/`](scripts)**, which is where the ecosystem's
policy says commands live. They were at this repository's root until
2026-09-17; a customer who put the root on their path wants `scripts/` on it
now, and [`koine_append_db`](koine_append_db) at the root is a tombstone that
says so and exits non-zero. It comes out once the one consumer that probes for
it has moved its pin.

## Reviewing the history record

```console
$ scripts/koine_history /path/to/record-repository
$ scripts/koine_history /path/to/record-repository --append
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
`python3 tests/test_history.py`; every test script here runs in Koine's CI.

## Installing the ecosystem's commands

```console
$ scripts/install_eo_cmd --prefix ~/bin   # install, and remember the directory
$ scripts/install_eo_cmd                  # later runs need no arguments
$ scripts/install_eo_cmd --status         # what is installed, and whether it is current
```

**`--dry-run` names every operation, both paths and nothing else**, so what will
happen is read rather than inferred:

```console
$ scripts/install_eo_cmd --dry-run
-- would install 2, 0 already current, 0 skipped  ->  /home/you/bin
   cp eo_cmd/eo_join  /home/you/bin/eo_join   (new)
   cp eo_cmd/eo_init  /home/you/bin/eo_init   (new)
-- a copy, not a move: eo_cmd/ keeps every file, and each one is written
   to a temporary file beside the target, made executable, and renamed over
   it, so an interrupted run leaves the old file in place
-- dry run: nothing was written, and /home/you/bin is unchanged
```

A real run prints the same lines under `installed` rather than `would install`,
so the two are compared by reading them. `--uninstall --dry-run` lists `rm` and
its path; `--sync --dry-run` lists each file it would write and where it reads
it from.

Some commands in this ecosystem are meant to be run **in a repository that is
not the one they live in** — the tree that is joining, the tree being started.
Reaching those by typing a path into somebody else's checkout is the wrong shape
for them, and nothing here put them anywhere better. `eo_cmd/` holds them, and
this installs them.

The chosen directory is remembered in `install_eo_cmd.local.json`, which the
repository ignores. **It never overwrites a file it did not install**: a name
already taken in the target directory is reported and skipped, and `--force` is
how a person overrides that, because the file being replaced is theirs.
`--uninstall` removes what it put there and leaves anything that has changed
since. `--dry-run` says what would happen and writes nothing.

Today there are two, and both are kanon's:

| installed as | copied from | what it does |
| --- | --- | --- |
| `eo_join` | [`prompts/join_eo`](https://github.com/ajreynol/kanon/blob/main/prompts/join_eo) | join the Eunoia ecosystem, run from inside the repository that is joining |
| `eo_init` | [`prompts/init_eo`](https://github.com/ajreynol/kanon/blob/main/prompts/init_eo) | start a tool: write a README saying what it is for, complying with nothing |

They carry the ecosystem's prefix rather than koine's, because they are not
koine's. Everything at this repository's root is named `koine_<piece>`; nothing
in `eo_cmd/` is, and that is the distinction the directory exists to draw.

### Their content is not koine's to modify

**koine stores these and installs them. It does not own a word of them.** kanon
does — they are part of its `R4`, the ecosystem's policy and joining it — and
kanon's copy is the authority for every line. A question about what `eo_join`
asks of a repository is a question for kanon, and an argument about whether it
should ask it is an argument to have there.

What this repository provides is the service: keeping the copies honest, and
putting them where a person can run them.

So the copies are held to a rule a program can check.
[`eo_cmd/origin.json`](eo_cmd/origin.json) records where each one came from and
at which commit, and a stored command must be its original with **one** change —
the command's own name, which differs here because the installed names are
prefixed:

```console
$ scripts/install_eo_cmd --check ../kanon
-- eo_join: is prompts/join_eo in /path/to/kanon, renamed and otherwise unchanged
-- eo_init: is prompts/init_eo in /path/to/kanon, renamed and otherwise unchanged
```

`--sync ../kanon` re-copies them, and is the only sanctioned way a file in
`eo_cmd/` changes. Editing one by hand is caught by `--check` and overwritten by
the next `--sync`, which is the intended outcome rather than a hazard: the store
is a copy, and a copy that has been improved locally is just a copy that is
wrong.

**The rename stops at the wrapper.** It is applied to each script's comments,
usage text, error messages and banner, and **not** to the prompt it hands an
assistant. That exception is the point of the rule rather than an edge of it.
Those prompts are read by somebody outside this ecosystem, in their own
repository, and they name the command so that a person handed one can check it
against what the command actually says. The name that survives that check is the
one in the tree they can read, which is kanon's. A local alias would name a
command that exists on one machine and in no repository anywhere.

## What else is in this tree

[`docs/`](docs/README.md) holds the history review standard and ledger, the
maintenance entry point, and [`discussion.md`](docs/discussion.md), the channel
to the rest of the ecosystem. [`eo_cmd/`](eo_cmd) is the store of other
repositories' commands described above, and [`scripts/`](scripts) holds what
maintains this tree rather than what it offers — today, the installer. **No agent acts on the discussion file unbidden**
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
