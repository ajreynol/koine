# bug_db_manager

**Tooling for owners to maintain their bug databases. Koine does not maintain
those databases.** Anoieu, dokimasia and tachyon's metagraphe own their records,
evidence, triage, cleanup, and close/reopen decisions. Koine maintains the
shared programs they invoke. [`koine_append_db`](koine_append_db) adds a run's findings to the
owner's persistent database; [`koine_window`](koine_window) resolves the window
of somebody else's history that a closure run reads;
[`koine_close_db`](koine_close_db) starts an assistant on the closure itself; and
[`koine_check_db`](koine_check_db) establishes afterwards that the run changed
only what it was allowed to.

**None of it knows what the records are.** A database of defects, a database of
static observations and a database of rewrite candidates are the same shape to
these programs: identities, a claim, and fields a closure adds. What the records
are *called* is the owner's, and an owner says so once -- in the envelope key
their database uses and in their closure config. koine's tooling is called
bug_db whoever is using it.

**Three customers, and all three pin this repository at `e4e4e2e`**, checked in
their trees on 2026-09-20: [anoieu](https://github.com/ajreynol/anoieu) at
`anoieu_analyzer/reporting/config/koine.lock`,
[dokimasia](https://github.com/ajreynol/dokimasia) at `scripts/koine.lock`, and
**metagraphe** — a child project in
[tachyon](https://github.com/ajreynol/tachyon), at `tools/metagraphe/` — at
`tools/metagraphe/rewrite_db/koine.lock`. Metagraphe's database is a `rewrite_db/`
holding rewrite candidates: a proposed `lhs -> rhs` with its side condition and
the evidence that cvc5 does not currently take the opportunity. That is not a
defect, and nothing here requires it to be one; its envelope key is `rewrites`.
Each calls these programs through its own lock, and resolving and enforcing that
pin is the consumer's responsibility.
`scripts/install_eo` also puts these programs on a person's PATH and that is a
different thing — PATH gives whatever the operator last installed, so a pinned
consumer keeps resolving through its lock.

```
bug_db_manager/koine_append_db <new bugs> <bug database>
bug_db_manager/koine_window --baseline <rev> --url <url> --ref <ref>
bug_db_manager/koine_close_db --config <closure.json>
bug_db_manager/koine_check_db <bug database>
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
$ bug_db_manager/koine_append_db run1.json bugs.json
-- 2 new bug(s), 0 already known, 0 conflict(s), 0 reopen candidate(s)
-- the database holds 2 bug(s) from 1 tool(s): anoieu 2
-- wrote bugs.json (created)
```

Months later anoieu runs again. It finds the first bug still there, one new one,
and dokimasia adds one of its own:

```console
$ bug_db_manager/koine_append_db run2.json bugs.json
-- 2 new bug(s), 1 already known, 0 conflict(s), 0 reopen candidate(s)
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

## A bug the owner closed, and this run found anyway

**It is reported, and nothing is done about it.** Closing a finding is the
owner's decision and so is reopening one. What a run can say is that the file
now contradicts itself: somebody ruled the claim false, and a later run saw it
again.

```console
$ koine_append_db run3.json bugs.json --date 2026-10-01
-- reopen candidate: id fbc033a960a2aaa5 was closed on 2026-09-19, and this run saw it again on 2026-10-01
-- 0 new bug(s), 2 already known, 0 conflict(s), 1 reopen candidate(s)
```

That contradiction is the only thing that surfaces a wrong closure, because **a
closed entry is one nothing re-derives**: a run does not re-check what somebody
has ruled on, so a closure made on a fix that never landed sits there being
believed. Both consumers' closure prompts already tell an assistant that the
contradiction is a feature and not something to tidy away. Until 2026-09-19
nothing implemented it — the sighting moved `last_seen`, the run printed *1
already known*, and the disagreement went into the file unmentioned.

**An entry is closed when it carries any field named `closed_*`.** That is the
convention its owners already keep — `closed_on`, `closed_commit`, `closed_why`,
`closed_verdict` — and reading the prefix rather than one name is what keeps this
out of deciding whose vocabulary is the right one. A `closed_` field koine has
never heard of still marks a ruling.

**The closure fields are not touched**, by this or by anything else here. The
entry keeps its verdict, its reasoning, its commit and its date; `last_seen`
moves, because it did see it again; and the count is printed even when it is
zero, because a run that looked and found no contradiction and a run with no
closed entry to contradict are different results.

## The window a closure run reads

**A record says what a check saw and when. Asking what became of it is a
different question, and it is asked of a window**: from the revision the open
rows were recorded at, to what that project ships today.
[`koine_window`](koine_window) resolves that window, and describes it to an
assistant.

```console
$ koine_window --baseline aee8742 --url https://github.com/cvc5/cvc5 --ref main --project cvc5
$ koine_window --baseline aee8742 --local ~/src/cvc5 --via=--use-local --project cvc5
$ koine_window --baseline aee8742 --local ~/src/cvc5 --json
```

Without `--local` the window is **pointed at and never fetched**: the prose says
where to read it and how, and the reading is the assistant's. That is what lets a
launcher's `--show-prompt` print the same text on a machine with no network as on
one with. It is also why `--json` reports `"commits": null` for a remote window
rather than an empty list — an empty list is a claim that nothing landed, and
this did not look.

**It was written twice before it was written here.** anoieu and dokimasia each
grew a closure launcher, and each grew its own copy of: find the commits after
the baseline, cut the listing and say how many were left out, print the `gh api`
recipes, warn that the compare view pages at 250. Two copies of one mechanism is
two places for a lesson to land in only one of them, and that is what happened —
see *The three ways a window lies*, below.

### The three ways a window lies

A window is the sentence *these commits are what happened after the baseline*,
and three things make that sentence false while leaving it looking fine. Each is
reported, in the facts and in the prose.

| | what it looks like | what it actually is |
| --- | --- | --- |
| **shallow clone** | an empty window | a fact about the clone, not the project. **Refused** |
| **diverged branch** | a list of commits | what a branch did since the *merge-base*; it may miss a fix on the branch the rows were measured on, and carry files the rows were never about |
| **parked checkout** | an empty window | what a pinned dependency tree is by construction. The refs that do carry the history are named |

Only the first is refused. A diverged window is still a window — it is just not a
history — and an empty one is a fact worth reporting; **whether a run should
start on either is the launcher's call, and the launcher is the owner's.** This
decides nothing.

The divergence warning is the concrete reason this is one program. anoieu learned
to make it, in a paragraph telling an assistant not to close a row because a
branch looks different from the one it was measured on. dokimasia, having no way
to hear about it, had neither the check nor the paragraph on either of its paths.

### What it will not do

- **It makes no network call, ever**, on any path. A remote window is a link and
  a set of recipes, and nothing here depends on what github says today.
- **It writes nothing and changes no checkout.** A local window is read with
  `git log`, `git rev-list` and `git merge-base`; no fetch, checkout or branch is
  among them, and [`tests/test_window.py`](../tests/test_window.py) checks that a
  run moves no ref and leaves no file.
- **It names no owner's command.** Where the prose says that re-measuring is a
  run and not a reading, `--remeasure` is how the owner's command gets named.
  Absent, the sentence stands without one, and koine invents nothing.
- **It re-wraps no command.** A paragraph is wrapped at the end, because every
  one of them carries something of variable length — a project's name, a path
  somebody chose, a sha — and a paragraph whose shape depends on how long a
  checkout path is is one nobody can edit. A commit list and a shell recipe are
  printed as written: a command that has been wrapped is not one.

## Closing a record

**Appending says what a run saw. Closing asks what became of it**, and it is a
different question asked of a different thing: not the owner's project, but a
window of the watched project's history. [`koine_close_db`](koine_close_db)
starts an assistant on it and [`koine_check_db`](koine_check_db) reads back what
that assistant wrote.

```console
$ koine_close_db --config tools/metagraphe/closure.json --dry-run
metagraphe: rewrite database at rewrite_db/rewrites.json
cvc5: 3 open rewrite candidates -- bitvectors 1, strings 2
  ref:      main
  baseline: aee8742 (from the 3 open candidates recorded at it)
  window:   https://github.com/cvc5/cvc5/compare/aee8742...main
            read by the assistant; this makes no network call
ethos: nothing open; no window to read
```

**A window is a window on one project, so an open record naming none has no
window** — and the run says so rather than leaving it out:

```console
$ koine_close_db --config tools/metagraphe/closure.json --dry-run
-- koine_close_db: 2 open rewrite candidates name no project this config watches,
   so no window covers them: M-7, M-11
```

That is not an error; a database may carry a row about something this owner does
not watch. What it cannot be is silent. `koine_check_db` reads the whole file
afterwards, so a run that described a smaller database would leave two counts and
nothing to say which of them to believe — and the prompt carries the same
sentence, because an assistant told the file holds fewer rows than it does is
being set up to tidy one.

### What is koine's here, and what is not

**koine owns the mechanics.** The window, which is `koine_window`. The
discipline of a closure assessment: commit-first, one commit at a time, confirm
in the current source rather than in the commit message, absence closes nothing,
leave it open if you cannot tell. Where the work is left, which is uncommitted,
in the owner's tree, reaching nobody. And the check afterwards.

**The owner owns every decision.** Which projects are watched and on which ref.
What the records are and what one is called. Where the baseline comes from --
koine will not go reading somebody's database for a revision field, because
which field that is, and what to do when two rows disagree, is a question each
owner has already answered differently. What evidence closes a record: a claim
about a file is confirmed by reading that file, a claim about a program's
behaviour is not, and which is which is not koine's to say. The closure
vocabulary. Whatever else gets written. The checks to run afterwards.

**So the prompt is assembled, not templated.** Three sections come from files
the owner writes and are spliced in whole: `about`, `evidence` and `writes`. A
launcher that flattened those into one shared wording would be a paraphrase of
three projects' rules kept in a fourth repository with nothing keeping it
current — and the paragraphs it would flatten are exactly the ones carrying what
each owner learned the hard way. koine points at them instead.

### The config

One file, in the owner's tree, naming what koine cannot know. Everything below
`database` and `projects` has a default.

```json
{
  "tool": "metagraphe",
  "database": "rewrite_db/rewrites.json",
  "records": {"one": "rewrite candidate", "many": "rewrite candidates",
              "collective": "rewrite database"},
  "group": "area",
  "projects": {
    "cvc5":  {"url": "https://github.com/cvc5/cvc5.git", "ref": "main",
              "reads": "the string and bit-vector rewriters and their regressions"},
    "ethos": {"url": "https://github.com/cvc5/ethos.git", "ref": "main"}
  },
  "baseline": {"command": ["python3", "scripts/closure_baseline.py"]},
  "prompt": {
    "about":    "prompts/closure/about.md",
    "evidence": "prompts/closure/evidence.md",
    "writes":   "prompts/closure/writes.md"
  },
  "checks": ["python3 tests/run.py"]
}
```

`baseline.command` runs in the owner's root and prints one
`<project> <rev> <why>` line per project; `--since NAME=REV` overrides it, and a
project with nothing open needs neither. A prompt section may be
`{"command": [...]}` instead of a path, for one that has to be computed from the
owner's own vocabulary. Placeholders — `{when}`, `{database}`, `{one}`, `{many}`
and the rest — are substituted by literal replacement and never by `format`,
because a `writes` section carries JSON examples and a `{` in one is not a field.

**`prompt.writes` has no default and the run refuses without it.** Where a
closure is recorded and in what words is the owner's, and koine will not guess a
vocabulary or a page shape.

### What a closure may do, and what it may not

`koine_check_db` compares the database against the version last committed —
which, because every launcher here leaves its work uncommitted, is exactly the
database before the assistant touched it.

| | |
| --- | --- |
| **may** | add `closed_*` fields to a record that carried none |
| **may not** | remove a record, add one, reorder them, change any field that is not a closure field, rewrite a closure already recorded, or rename the envelope key |

```console
$ koine_check_db bug_db/bugs.json
-- id fbc033a960a2aaa5 closed, adding `closed_commit`, `closed_on`, `closed_pr`, `closed_why`
-- changed: id 52912b69 `description` was 'rule takes 0 args' and is now 'rule takes 0 args (tidied)'
-- 82 record(s) at HEAD, 82 now; 1 closure(s), 1 unallowed change(s)
```

This is the gap that made it worth writing. The reason `koine_append_db` refuses
to rewrite an entry is that *a record of what was found over time is worth having
only if nothing quietly rewrites it* — and then closure arrives as an assistant
with the file open in a text editor, and the only thing between that and the
record is a person reading a long diff looking for the one hunk that is not what
they expected.

**`--also` names a closure field without the prefix**, for a vocabulary that
predates the convention: a verdict closing a finding before its fix reaches a
default branch owes an `awaiting_landing` saying where the change is.
**`--amended`** allows a recorded closure to be changed, which is a person
replacing a promise with the commit that kept it rather than a run making a
closure. **`--renamed`** allows the envelope key to change, which is a migration
and is above. All three are reported either way; the flag decides whether it
fails.

Run retroactively over anoieu's history on 2026-09-19, the commit that was a
closure run passed with 25 closures and no unallowed change, and the commit that
was a ledger migration did not — which is the right answer for both.

## What is still not built

**Nothing writes a closure, and nothing decides one.** An assistant does both,
and `koine_check_db` reads the result back. A writer is possible and is not
obviously wanted: the part an assistant is better at is authoring the reasoning,
and a program that took the write would have to take that with it.

**Two asks are on the table and neither is taken**, both made concrete by
consumers on 2026-09-19 rather than guessed at here. Each would be a new
maintenance obligation, which is the maintainer's to accept; `docs/discussion.md`
carries koine's answer to each and what it would cost.

| Asked by | What is wanted | Where it stands |
| --- | --- | --- |
| anoieu | **Was finding X covered by run B** — *covered and not reported*, *covered and reported*, or *not covered*, the last distinguishing an input that was not read from a check that was off from an identity that did not match. Today a finding absent from a dump and a finding nobody looked for are the same fact | Priced, not built. It needs a run record these programs do not keep, and the answer is only as good as the coverage the producer reports |
| dokimasia, tachyon | **Keep the original claim, its date and its corrections** when a later run under the same identity carries different text. Today the original is kept, `last_seen` moves, and the new wording is printed as a conflict and lost | Priced, not built. This is storage and so is koine's; what it changes is what a record *is*, which is why it is not a flag somebody adds on an afternoon |

The rest of what shared tooling could support, with what the owner would have to
supply for it:

| Owner supplies | Shared tooling could support |
| --- | --- |
| Run scope, source and analyzer versions, enabled checks, failures and skips | Store run evidence and establish whether an observation is comparable before assessing absence |
| Stable finding identities and explicit identity changes | Distinguish unmatched findings from closure candidates without silently merging records |
| Fresh fuzzer replay results and their evidence | Assess the replay without treating a stored export as a fresh observation |
| Reviewed corrections and close/reopen decisions under the owner's reporting policy | Record changes with their evidence and history, using locked, atomic writes and a preview |

Cleanup must preserve original findings, ids, dates, verdicts and evidence.
Incomplete or incomparable runs must leave closure unassessed. A retention or
archival decision belongs to the database owner as well.

**One shape is refused rather than unbuilt.** A second list in the envelope —
`{"bugs": [...], "runs": [...]}` — is not how a run record would arrive here,
because every program in this directory reads the envelope by finding the one
list in it and refuses a file with two. Whatever holds run evidence is a file
beside the database, which is where the two consumers that keep one already do.

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

### What the database calls its records

**The envelope key is read from the file and written back unchanged**, so a
consumer whose records are not defects is read and written like any other and the
counts a run prints speak that consumer's word: `-- 2 new rewrite(s)` over a
`{"rewrites": [...]}` database. **`--records KEY` names the key for a database
this run creates**; an existing one keeps its own and the flag is ignored, which
is why metagraphe's `rewrites.json` had to be re-keyed by hand.

**Renaming the key of an existing database is a person's edit, and it is
checked rather than performed.** Nothing here does it, because a program that
could rewrite the envelope could rewrite it by accident. What koine owes the
person who does it is the other half: `koine_check_db --renamed` establishes that
the rename is *all* that happened — every record, its order and its fields
compared as ever, the rename reported and not counted as a closure. Without the
flag it is an unallowed change, which is correct for a closure run and is the
wrong answer for a migration.

## Running it

```console
$ python3 tests/test_append_db.py
$ python3 tests/test_window.py
$ python3 tests/test_check_db.py
$ python3 tests/test_close_db.py
```

No dependencies and no network. `test_window.py` builds git repositories in a
temporary directory — a shallow clone, a diverged branch, a checkout parked at
its baseline — and reads a window out of each. `--dry-run` says what would change and writes
nothing; `--date` records a run under a date other than today;
`--records`, `--lock-timeout` and `--no-lock` are above.

**The executables are [`koine_append_db`](koine_append_db),
[`koine_window`](koine_window), [`koine_close_db`](koine_close_db) and
[`koine_check_db`](koine_check_db), all in `bug_db_manager/`.** The root
[`koine_append_db`](../koine_append_db) is a tombstone: it prints the executable's
location and exits non-zero. Consumers must probe and invoke
`bug_db_manager/koine_append_db`; there is no `bug_db/` compatibility directory.
The installed command remains `koine_append_db`, with the same arguments and
JSON format.

**The tombstone is still read, and taking it out is the maintainer's.** As
checked on 2026-09-20, both adapters name the root path — anoieu's in a
`BEFORE_MOVE` list, dokimasia's alongside the other retired spellings — and
neither runs it: each is deciding whether a directory it found is koine from
before the move, so that a consumer that cannot find this repository says which
of *wrong path* and *wrong commit* it hit. Dokimasia has said the tombstone may
go whenever koine's maintainer wants it out and is not asking for it. Removing it
would cost anoieu one of three signals in a diagnostic and no run anywhere.

Also to a consumer's account: dokimasia's `scripts/bug_reports.py` writer, and
any other caller that already serialises its own access, wants `--no-lock` rather
than a second lock.
