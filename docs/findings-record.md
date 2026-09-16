# The findings record

A tool here raises findings about somebody else's project and keeps a ledger of
them. Both customers keep one. In both, **the state of a row is a field
nowhere**: it is inferred from which file or which table the row is in, and then
qualified in prose. This is the record under that table — what a row is, what a
run is, and the four things a second producer makes necessary.

**It is not the ledger.** The rows stay in the customer's tree, under their
name, settled by them. Nothing here says what a finding is, when one may be
raised, what rank it carries, or what closes it. Those differ because the
subjects differ — the analyzer's questions are not the scrutineer's — and they
are the half koine has never had an opinion about.

**It was asked for.** anoieu's `D25`, opened 2026-09-16, asks for *a
machine-readable record of a finding, written by more than one producer, which
we can append to, diff, and render*, and asks koine to choose the format rather
than inherit theirs. That is why this exists and it is the whole of the warrant;
the postmortem protocol is still the one thing here that nobody asked for.

## Why it is not the register two repositories already keep

Because a register is a *page*, and this is what is under one. The distinction
is the same one `D25` draws and it is worth keeping in sight:

| | who holds it | where |
| --- | --- | --- |
| a findings **ledger** — which rows exist, what they claim | **the customer** | theirs, and staying theirs |
| what counts as a finding, what closes a row, what a rank means | **the customer** | theirs, and named below as not decided here |
| the **record format**, its reader and its writer | koine | this page |
| the **page a reader is pointed at** | the customer | generated; `render` writes one and does not choose its columns |

## What prose was costing, measured

At anoieu `442bb67`, and re-derived by `tests/customers.py` rather than quoted:

- **39 open rows and 43 closed**, in two markdown tables, with the state of a row
  given by which of the two files it is in.
- **Seven distinct verdict words** — `not audited` (17), `intentional` (14),
  `accepted and fixed` (7), `declined` (2), `withdrawn`, `fixed and landed`, and
  one re-coding — separated from their reasons **two different ways**, an em-dash
  in 36 rows and `--` in 7. Nothing can ask which word a row carries.
- **Five more states, in the notes column of the open ledger**: `Not closed:` in
  8 rows, `declined by` in 8, `Left open` in 4, `reopened —` in 3, `No longer
  derived` in 2. Every one is a state they use. None is one a program can ask
  about.
- **Two regexes in `scripts/landing.py`** that parse a markdown cell back into
  data, and a test in `tests/run.py` that fails if the sentence they read is
  *reworded* — because a reworded marker drops a row from the audit while leaving
  the debt owed. **That is a test about a sentence, guarding a field that should
  not have been a sentence.**

**One number in `D25` did not reproduce, and it is said here rather than back to
them**, because this page claims its figures are re-derived and a figure that
came out differently is exactly what that claim is for. The topic gives *the
longest row is 667 characters*; at the same commit, with the ledgers unchanged
since it, the longest **row** measures 689 and the longest **cell** 528. Nothing
turns on it — either reading says the same thing about prose in a table — and
which of the two was meant is theirs to say.

The failure those add up to is already booked: three cvc5 rows sat closed as
*fixed upstream*, on a fix that never landed, for three months, because nothing
re-derived a closed id and the commit a verdict was checked at had nowhere to
live except a sentence.

## The format is lines of JSON, and the fourth constraint is what decided it

One JSON object per line, `\n`-terminated, UTF-8. Runs first, then rows.

`D25` handed over four constraints. Three of them a good many formats meet; the
fourth is the one that picks:

| | what github.com does with it |
| --- | --- |
| `.csv`, `.tsv` | a searchable table in the blob view — and the longest cell in the ledger is **528 characters** of prose with an em-dash in it, which is where this stops being a good idea |
| `.json` | syntax-highlighted source, one long scroll, and every append touches its neighbour in the diff |
| `.jsonl` | plain text, **one row per line**: the cleanest thing a diff can be asked to review, and a long note survives without quoting games |
| `.md` | rendered, which is what is published today, and is not a record |

So: **JSONL for the record, and the markdown page stays the page.** The pairing
is the one `D25` guessed at; what it is not is a guess, because a line-oriented
record is what makes *did these two producers agree* a per-id question rather
than a per-line one.

The extension is not part of the definition. A customer who files it as `.json`
with one object per line has not broken anything; a customer who writes a JSON
array has, and `parse` will say so.

### Canonical form

Every producer writing the same record produces the same bytes. That is what
makes a diff between two of them evidence.

- One object per line; no trailing whitespace; `\n` endings; UTF-8, not escaped
  to ASCII.
- Keys in the order of the field table below, then whatever columns the producer
  carries that this format does not name, in sorted order.
- A field the row does not state is **omitted**, not written empty. `id` and
  `settled` are always written.
- **Row order is the ledger's**, not this format's. Generation is additive at
  both customers — a row is appended, never moved — so writing a record back
  preserves the order it arrived in. The comparison order is **by id and by
  nothing else**, produced by `Record.sorted()` and never written to disk:
  sorting by path would reorder the whole record every time somebody inserted a
  line in somebody else's tree.
- Blank lines and lines beginning `#` are ignored on read, so a record can carry
  a header for the person who opens it raw.

## The row

Every field except `id` is optional, and that is a result rather than a
courtesy: the two customers' registers agree on less than either would guess.

| field | what it is |
| --- | --- |
| `id` | the merge key. **Carried from the producer and never minted here** — anoieu's are a 16-hex fingerprint, dokimasia's are `i-*`, and they mean different things |
| `owner` | whose project the claim is about, by the ecosystem's entity ids. anoieu fills it on every row; dokimasia's subject is always cvc5 and the column does not exist |
| `code` | what produced the row: a check id (`EO0031`), a tool's name (`gates rule`), `design note` |
| `where` | `path:line` inside the owner's tree. Always present at anoieu; present on **1 of 51** dokimasia rows |
| `what` | the claim. The one field besides `id` that a row is refused without |
| `state` | **the producer's own word** for where the row stands |
| `settled` | whether the producer considers the row ruled on. A boolean, and the one thing that stops being a filename |
| `verdict` | the reason behind `state` |
| `notes` | what the row carries that is not a reason for its state |
| `rank` | **carried, never interpreted** |
| `kind` | **carried, never interpreted** |
| `run` | the id of the run that last saw this row |
| `checked_at` | the commit in somebody else's tree that `state` was checked at. This is the field the three-month failure did not have |
| `landing` | `{project, branch, commit}` — a change a row was closed on and which has not been seen to land |

**A column this format does not name is kept, and written back.** A migration
that drops a column is one nobody can be asked to run, so an unrecognised key is
carried through read, merge and write untouched.

### The state is a field; the vocabulary is not koine's

`state` is a **free string, chosen by the producer**. koine does not enumerate
the words, does not rank them, and does not decide when one may change. A row
closes on a maintainer's words and a commit, and that sentence is anoieu's; what
counts as *carry* is dokimasia's.

What is enforced is one thing, and it is mechanical: **a row that says it is
settled must say what its state is.** A row whose state is recoverable only from
which file it is filed in is the defect this record exists to remove, so the
checker refuses it. Nothing else about the word is checked.

`split_verdict` takes a cell like `not audited — the file is a copy of cvc5's`
and returns the word and the reason. Both separators are accepted and neither is
blessed; the point is that afterwards the word is a field and the spelling stops
mattering. **Which column holds a verdict is the caller's to say** — this splits
prose it is handed, it does not decide that a column holds one.

### `rank` and `kind` are carried and not read

dokimasia ranks 1–3 and has kinds A–D; anoieu has neither. A shared format
should carry a rank it does not interpret, which is `D25`'s own sentence, and
the same goes for kind. Nothing here compares two ranks, orders them, or knows
that `1` is worse than `3`.

## The run, and why an absence needs one

**Not-reported and not-scanned are different, and today neither customer can
tell them apart.** Two producers scan different targets, and a row absent from
one of them means nothing until you know whether that run covered its file.

    {"type": "run", "id": "r1", "by": "program",
     "producer": "run_static_analysis", "when": "2026-09-16",
     "targets": [{"project": "cvc5", "root": "proofs/eo/cpc",
                  "commit": "40a4bb7e4"}],
     "codes": ["EO0031", "DOC0011"]}

`Record.covers(owner, where)` answers **three** ways, and the third is the point:
`True`, `False`, and `None` — *this record does not say*. A record with no runs
cannot tell a clean file from an unread one, and reporting that as covered is the
failure an audit exists to prevent. A run that names no target is refused for the
same reason.

`by` is the **one closed vocabulary this format defines**, and it has three
values:

| | |
| --- | --- |
| `program` | a check ran and derived the row |
| `agent` | an agent was asked the same question against the same targets |
| `person` | somebody wrote or ruled on the row by hand |

The first two are the two producers the record exists to compare. The third is
there because both customers' closed ledgers are written by hand at a review
step, and a hand-written row that claimed to be a program's output would make the
comparison a lie.

## Appending is a merge

Four rules, and they are what both generators already do by hand.

1. **A new id is appended, never inserted.** Generation stays additive: a
   finding cannot vanish without somebody saying why, and a row's neighbours do
   not move in the diff.
2. **A field the incoming row states, and the base leaves empty, is filled.**
3. **A field both state, differently, is a conflict.** The base keeps its value
   and the divergence is handed back. It is **not** resolved here — picking
   between two producers is a judgement, and this module reads files.
4. **Nothing is removed, and `settled` never goes back to false in a merge.** A
   reopen is somebody's decision. A merge that tried to make it would be
   deciding what closes a row, which is not koine's.

## Did the two producers agree

`agree(a, b)` compares **per id**, never per line of file, and returns four
things: the ids that match, the fields that differ, the rows one producer
reported and the other did not, and the rows that sit **outside what the other
one scanned**.

The last two are the reason `Run` exists at all. A row the agent has and the
program does not is two different results — the program read the file and did
not report it, or never read the file — and until the record says which, the
comparison is not evidence of anything.

`notes` is not compared, and `run` and `checked_at` are not: they are facts about
the run rather than about the finding, and prose is something two producers will
never write the same way. Comparing it would report a divergence on every row and
teach nobody anything.

## A landing is a branch query

`landing` carries `{project, branch, commit}`, and `landings(record, checkouts)`
hands the whole record to [`branch.md`](branch.md) as `Query` values. That is
`scripts/landing.py`'s two regexes deleted, and with them the test that fails
when a sentence is reworded — the audit now breaks when a *field* is missing,
which is a thing a person can be asked to fix rather than a thing they can
paraphrase past. `missing` defaults to `unknown`, which is the conservative
reading and the one anoieu holds.

Where anybody's clone lives stays the caller's: `checkouts` is handed in, and a
project with no checkout on this machine is skipped rather than guessed at.

## The page a reader is pointed at does not change

This is a condition rather than a nicety. `open-findings.md` is what another
project is pointed at, and if adopting a record changes what somebody in cvc5
sees when they open it, it will not be adopted.

`render` writes a markdown table from a record. It does not choose the columns,
their order, their headings or their quoting — those are the customer's page.
`tests/customers.py` reads both of anoieu's real ledgers into a record and
renders them back: **39 rows and 43 rows, byte for byte identical** to the
committed files. That claim is re-run rather than taken on trust, which is the
only reason the harness is a script.

## What the tooling does

| | |
| --- | --- |
| `read` / `parse` | a record off disk or out of a string. A line that will not parse **raises**, rather than being skipped — a record that silently drops a row it could not read is worse than one that will not open |
| `write` / `dumps` | the canonical form |
| `check` | what the record gets wrong. Every rule is about whether the record can be *asked* something, never about whether a finding is any good |
| `report` | prints and returns a count, the way `drift.report` and `postmortem.report` do, so a test runner calls all three alike |
| `merge` | appending, with conflicts reported and not resolved |
| `agree` | per-id comparison of two producers, coverage-aware |
| `landings` | the outstanding promises, as `branch.Query` values |
| `render` | the generated markdown page |
| `tables` / `from_table` | the register a customer already keeps, read by a column map that is **theirs** |
| `split_verdict` | the word out of the prose, both separators accepted |

## What running it against both registers found

`D25` asked that this be checked **before** anything was built — only one
customer is asking, and a format written for one ledger is a guess about the
other. `python3 tests/customers.py` runs it against both real trees. What it
found, at anoieu `442bb67` and dokimasia `5d39f62`:

**They share less than either would guess, and it is the optionality that
carries it.** 51 rows read out of dokimasia's eight registers fill: `what` 51,
`rank` 24, `code` 23, `kind` 14, `verdict` 11, `state` 5, `where` **1**, `owner`
**0**. anoieu's 82 fill `owner`, `code`, `where` and `what` on every row and
`rank` and `kind` on none. **The intersection is `id`, `what`, `code`, `state`
and `verdict`** — and every other field has to be optional, which is a result of
running it rather than a decision.

**Both keep their state in prose, and both are refused by the same rule.** 43 of
anoieu's rows are settled by being in `closed-findings.md`; 7 of dokimasia's are
settled by being under `Settled`. Neither carries a word a program can read, and
the checker says so about both in the same sentence.

**dokimasia's retraction register has no id space**, and that is the one place
the record does not fit. Its four rows are keyed by phrases — *every published
number*, *`infer`/`inferid` baselines* — and `id` is carried and never minted
here, so koine cannot supply one. **A register of what a tool got wrong is worth
keeping and the format should leave room for it**; what it needs first is four
ids, and minting them is dokimasia's.

**Neither record can yet tell a row nobody reported from a file nobody read.**
82 rows and 51 rows, and no runs declared anywhere. That is the state of things
before this lands, stated so the first declared run is a visible improvement
rather than a formality.

## Where the ground truth is

**This page.** [`../koine_findings.py`](../koine_findings.py) implements it and
its docstring says so; where the two disagree, this page is right and the module
is the defect.

**What carries a copy:** the module's docstring, and each customer's own record
preamble once one adopts. [`../tests/test_findings.py`](../tests/test_findings.py)
is what compares the implementation to the rules stated here, and
[`../tests/customers.py`](../tests/customers.py) compares it to the two real
registers.

## What is not decided here

Named so that a grant of this can be a clean yes or a clean no.

| | whose |
| --- | --- |
| what counts as a finding, and what closes a row | the customer's. A row closes on a maintainer's words and a commit, and that sentence is not koine's to hold |
| severity, ranking, priority | the customer's. The record carries a rank and does not read it |
| the id scheme | the producer's. **Carry the id, do not mint it** |
| which register a row belongs in, and how many registers there are | the customer's |
| where the record file lives, and what it is called | the customer's |
| the local configuration naming where each project sits on a machine | anoieu's, machine-local, and never committed as a claim about anybody |
| the two producers — the analysis and the prompt that drives an agent | anoieu's and `R1`'s. **Only what they write is here** |
| filing anything anywhere | nothing crosses a repository boundary automatically, and a person posts |
| whether a record belongs in the tree or in an issue tracker | **open** — the question on koine's front page, which a customer running both is what would settle. A record is the layer under both answers: the row is the body of an issue, the id is the key, an issue number is one more column this format carries and does not read |
