# bug_db

**Tooling for keeping a bug database.** A tool runs over somebody else's project
and dumps what it found *this time*; its database is everything it has ever
found. [`koine_append_db`](koine_append_db) is the trip between the two.

[anoieu](https://github.com/ajreynol/anoieu) and
[dokimasia](https://github.com/ajreynol/dokimasia) are the customers. Each pins
a commit of this repository in its own `scripts/koine.lock` and calls this from
its own run; that pin is the whole of the integration on either side.

```
bug_db/koine_append_db <new bugs> <bug database>
```

A tool runs and dumps what it found this time. The database is every bug it has
ever found. This puts the first into the second.
## A worked example

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
$ bug_db/koine_append_db run1.json bugs.json
-- 2 new bug(s), 0 already known, 0 conflict(s)
-- the database holds 2 bug(s) from 1 tool(s): anoieu 2
-- wrote bugs.json (created)
```

Months later anoieu runs again. It finds the first bug still there, one new one,
and dokimasia adds one of its own:

```console
$ bug_db/koine_append_db run2.json bugs.json
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

## The one rule that makes it a database

**A bug is added once.** It is identified by its `tool` and its `bug` together,
or by an `id` where the tool mints one. Run the same dump twice and the second
run adds nothing.

That is the property that lets this be wired into a job instead of remembered.
Re-running is free, so a run that half-failed can simply be run again.

## What it will not do

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

## The two files

They are the same shape, so a database can be fed back in as a dump:

```json
{"bugs": [{"bug": "...", "tool": "...", "description": "..."}]}
```

A bare JSON list is accepted as well, since that is what a tool's first dump
usually looks like. `bug`, `tool` and `description` are what a bug is; **a tool
may carry any other fields it likes** — a path, a line, a rank, a URL — and they
are kept exactly as they arrive. koine adds `first_seen` and `last_seen` and
nothing else. There is no schema to agree on beyond the key.

## Running it

```console
$ python3 tests/test_append_db.py
```

No dependencies and no network. `--dry-run` says what would change and writes
nothing; `--date` records a run under a date other than today.

**The commands live in [`scripts/`](scripts)**, which is where the ecosystem's
policy says commands live. They were at this repository's root until
2026-09-17; a customer who put the root on their path wants `scripts/` on it
now, and [`koine_append_db`](koine_append_db) at the root is a tombstone that
says so and exits non-zero. It comes out once anoieu and dokimasia have moved
their pins.
