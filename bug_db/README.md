# bug_db

**Tooling for keeping a bug database.** A tool runs over somebody else's project
and dumps what it found *this time*; its database is everything it has ever
found. [`koine_append_db`](koine_append_db) is the trip between the two.

[anoieu](https://github.com/ajreynol/anoieu) and
[dokimasia](https://github.com/ajreynol/dokimasia) are the customers, checked on
2026-09-18. Each pins
a commit of this repository in its own `scripts/koine.lock` and calls this from
its own run; **that pin is the whole of the integration on either side.**
`scripts/install_eo` also puts this program on a person's PATH and that is a
different thing — PATH gives whatever the operator last installed, so a pinned
consumer keeps resolving through its lock.

```
bug_db/koine_append_db <new bugs> <bug database>
```

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

`bugs.json` now holds all four. This excerpt shows the two original entries,
with their original `first_seen` dates:

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
or by an `id` where the tool mints one. These identity forms are separate: an
explicit `id` never equals a `(tool, bug)` pair, even when the tool is named
`id`. Run the same dump twice and the second run adds nothing. Only `last_seen`
changes for an existing entry; its other fields stay as recorded.

That is the property that lets this be wired into a job instead of remembered.
Re-running is free, so a run that half-failed can simply be run again.

## Two runs at once

**A run holds an exclusive lock on the database while it reads, merges and
writes it.** *A bug is added once* is a claim about a file two tools append to,
and without a lock it holds only for runs that happen not to overlap: both read
the same database, both merge their own dump into what they read, and whichever
replaces last throws the others' bugs away. **Nothing reports that**, because
from inside every one of them everything worked.

[`tests/test_append_db.py`](../tests/test_append_db.py) checks that eight
concurrent writers preserve every accepted append, and that a later run
preserves the database after an interrupted write.

```console
$ koine_append_db run.json bugs.json --lock-timeout 60   # wait longer
$ koine_append_db run.json bugs.json --no-lock           # I have arranged this
```

The lock is `<database>.lock` beside the database, taken with `flock`, and the
kernel drops it when the process ends however it ends — so a killed run leaves a
stale file and never a stale lock. **The file is furniture rather than data**: it
is empty, it is not removed after a run (deleting it is how two runs end up
locking two different inodes and both proceeding), and it belongs wherever the
database is ignored or committed.

**A run that cannot take the lock within `--lock-timeout` seconds refuses and
writes nothing**, exiting `3` — a distinct code, because *somebody else is
writing* and *you gave me a bad dump* call for different things from whatever
wrapped the call. The dump is still there and re-running is free.

**`--no-lock` is the way past.** It is for a caller that already serialises its
own access to the database and would otherwise take the same lock twice, and it
is the way past on a platform with no `flock`, where a run refuses rather than
pretending to be serialised. A caller passing it owns the guarantee from there.

**A reading run — `--dry-run` — takes no lock and needs none.** The database is
replaced atomically, so a reader sees one whole version or another, never a
half-written one.

## What it will not do

- **It never changes an existing entry except for `last_seen`, and never removes one.** If a
  later run describes a known bug differently, that is printed as a conflict and
  the database keeps what it has. A record of what was found over time is worth
  having only if nothing quietly rewrites it, and deciding that the new wording
  is the better one is a person's call.
- **Nothing is written unless the whole dump is readable.** One malformed entry
  and the run writes nothing at all, so a half-applied dump is not a state the
  database can be in.
- **It writes the database and its lock file and nothing else**, fetches
  nothing, and needs no network. It reads two files and replaces one of them,
  and the replacement is atomic, so an interrupted run leaves the old database
  intact.

## The two files

They are the same shape, so a database can be fed back in as a dump:

```json
{"bugs": [{"bug": "...", "tool": "...", "description": "..."}]}
```

A bare JSON list is accepted as well, since that is what a tool's first dump
usually looks like. Every entry must be an object with either a nonempty `id`
or both `tool` and `bug`. `description` is useful but not required. **A tool may
carry any other fields it likes** — a path, a line, a rank, a URL. For a new
entry those fields are preserved, an existing `first_seen` is retained, and
`last_seen` is set to the run date. Missing `first_seen` uses the run date too.
For an existing entry, additional fields are not merged; conflicting values are
reported and kept as recorded.

## Running it

```console
$ python3 tests/test_append_db.py
```

No dependencies and no network. `--dry-run` says what would change and writes
nothing; `--date` records a run under a date other than today;
`--lock-timeout` and `--no-lock` are above.

**The executable is [`bug_db/koine_append_db`](koine_append_db).** The root
[`koine_append_db`](../koine_append_db) is a tombstone: it prints the executable's
location and exits non-zero. Consumers should probe and invoke the executable
inside `bug_db/`.

Also to a consumer's account: `bug_reports.writer` and any other caller that
already serialises its own access wants `--no-lock`, not a second lock.
