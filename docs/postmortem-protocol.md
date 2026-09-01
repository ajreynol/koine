# The postmortem protocol

**A significant thing happened to a repository. What happened, who was involved,
how did it come out, and what did we learn?**

Four questions, one shape, and a program that can read the answers back. This
page is the definition; [`../koine/postmortem.py`](../koine/postmortem.py) is the
implementation, and where the two disagree this page is right.

koine has [volunteered to maintain this](discussion.md), which is a request
rather than a fact: today the shape lives in each repository's own log, and
anoieu's is the one dokimasia copied.

## Why it is not the log two repositories already keep

anoieu and dokimasia each keep a `postmortem.md`, and the shape is good. It is
also **about one kind of event** — a reply was worked — because that is the only
event the workflow that writes it knows about.

The evidence that this is too narrow is that **the two most instructive things
that have happened in this ecosystem are in neither log.**

- Three cvc5 rows sat closed as *fixed upstream*, on a fix that never landed,
  for three months. It is written up in the middle of
  `reporting-workflow.md` — a page about how to report findings — because there
  was nowhere else for it.
- anoieu's checker took dokimasia's CI red on its first outside run: twenty-two
  link failures, every one spurious, on a defect in the checker. It is written up
  in `coherence.md`, under *Defending the infrastructure*, as an argument.

Both are exactly *this happened, here is what we learned*. Both are prose inside
a document about something else, findable only by somebody who already knows they
are there. Neither is countable, neither is linked to the change it caused, and
neither will be read by the next person who is about to make the same mistake.

**The protocol is the same shape, asked of any significant event rather than only
of a round.** That is the whole of the generalisation.

## The entry

```text
## <date> — <what this was, in a phrase>

**Kind:** round | defect | retraction | debt | adoption

**Entities:** the repositories involved, by their ids

**Summary:** what happened, for somebody who works on none of them: no ids, no
counts, no procedure. Two sentences, 250 characters at most.

**Resolution:** how it came out, and what changed here as a result. Counts and
links belong in this field, not in the summary.

**Learned:** the general fact, stated so it applies to the next one rather than
to this one.

**Debt:** what was traded away on purpose; settles when <what discharges it>

### <an id, or a phrase for a group> — <what it was>

<What happened — only enough to make the resolution make sense.>

**Learned:** <the fact this part of it produced.>
```

Newest first. `Debt:` is optional and may repeat; every other field appears
exactly once, on the entry and never on a section beneath it. `Learned:` is the
one field a section may carry of its own, because a single event usually teaches
more than one thing and each deserves its own sentence.

### The fields

| field | what it is for | why it is required |
| --- | --- | --- |
| **Kind** | which of five things this was | a log you cannot filter is a log you re-read |
| **Entities** | who was involved, by the ids the ecosystem already uses for them | *who was involved* is the question with a registry behind it, and the one that makes an entry findable from the other end |
| **Summary** | what happened, to a stranger | it is the field people actually read; the limits are what keep it that |
| **Resolution** | how it came out | an entry with no outcome is a report of an alarm |
| **Learned** | the general fact | **the field that makes it a postmortem.** Without it this is a log |
| **Debt** | a shortcut taken on purpose, and what will notice | see below |

**`Learned:` is required at the entry, and this is the change that matters most.**
anoieu's template has it on the sections; dokimasia's copy dropped it, so a
dokimasia postmortem would record what happened and never what was learned. The
one field that distinguishes this record from a log did not survive being copied
once. That is the argument for holding the protocol in one place, made by the
protocol itself.

**`Entities:` supersedes `Tool:`, and does not replace it.** Both existing logs
write `Tool:`, meaning the project a finding was reported to. It is read as one
entity, so a log written before this page is read rather than rewritten in order
to be read. The generalisation is that an event has parties rather than a
subject: a checker taking somebody's build down involves two repositories and
neither is *the tool*.

**Ids come from the ecosystem's own list** —
[`tools/ecosystem.json`](https://github.com/ajreynol/anoieu/blob/main/tools/ecosystem.json),
which is what `docs/board.md` already uses for the same purpose. The checker
takes the registry as an argument and does not go looking for it, so nothing here
depends on anoieu's file existing.

### The kinds

Five, closed, and each with an incident behind it — because a rule with no
incident behind it is a preference, which is anoieu's own standard, applied here
to the vocabulary rather than to the rules.

| kind | what it is | the incident |
| --- | --- | --- |
| `round` | a reply from the project a finding was reported to was worked | ethos, nineteen rows, seven fixes and ten unsigned declines |
| `defect` | something here was wrong, and somebody else paid for it | anoieu's checker taking dokimasia's build red on twenty-two spurious link failures |
| `retraction` | we published something and withdrew it | dokimasia retracting a headline number |
| `adoption` | something was taken up, or dropped: a tool, a policy, a member | dokimasia declaring membership and wiring the check |
| `debt` | a shortcut was taken deliberately, and something was left to notice | closing a row before its change landed, in exchange for tempo |

A sixth — an audit reporting something — was considered and left out. Nothing has
happened under it yet, and inventing the category first is the failure this table
is arranged to prevent.

### Debt is a field, not a phrase in prose

This is the second change worth arguing for on its own.

anoieu books one debt today, and it books it as a **magic string inside free
text**: a row closed before its change landed ends its verdict with
`awaiting landing: <project> <branch> <commit>`, which `tools/landing.py` reads
back with a regex. `tests/run.py` then carries a check whose entire job is to
fail when somebody rewords a verdict into a marker the audit can no longer parse
— because that is how a row leaves the audit while still owing it.

That check is the right response to the arrangement and the arrangement is the
problem. **A debt is a thing the record has; it should be a field.** Then the
audit reads a field, rewording prose cannot silently discharge anything, and the
guard against rewording is not needed because there is nothing to reword.

The one rule: **a `Debt:` must carry a *settles when* clause**, in those words —
the same phrase the discussion protocol already requires of a topic, for the same
reason. A debt nothing discharges is a regret, and the checker refuses it.

## When an entry is owed

**A `round` gets one every time.** Both customers started from *write one when
something changed here*, both moved off it, and koine does not reopen a question
two repositories have independently settled: a round that changed nothing still
has reasoning about why it changed nothing, and the judgement call cost more than
the entry.

**Every other kind gets one when the answer to *what did we learn* is not empty.**
That is the threshold, and it is the same rule as the first one — rounds are
unconditional because their answer is never empty in practice, not because they
are special.

The failure this is arranged against is the one visible in both logs today: an
event significant enough to be argued about at length in a document, and not
significant enough for anybody to have opened the log.

## Two levels, so adoption is free on the first day

| level | what it checks | who it is for |
| --- | --- | --- |
| **`SHAPE`** | one field block per entry, no entry-level fields on the sections beneath, and the summary limits | what both customers already check, and nothing more |
| **`PROTOCOL`** | that, plus `Kind`, `Entities`, `Learned`, and a discharge condition on every `Debt` | this page |

**A customer at `SHAPE` deletes their copy of the check and changes no other
file.** That is not an aspiration; `tests/customers.py` runs it against both real
logs, and both keep `SHAPE` untouched. Moving anoieu's two entries to `PROTOCOL`
is four lines — a `Kind:` and a `Learned:` on each — and the harness prints
exactly which, so the migration is a list rather than a project.

Which level a repository runs, and when, is the repository's. koine ships a
definition and a checker; nothing here is binding on anybody, and a customer who
runs neither loses nothing they had.

## The one behaviour koine had to choose

The two copies of the shape check disagree about where a `Summary:` ends. anoieu
stops at a blank line; dokimasia reads on to the next field. It is the pair that
diverged in *behaviour* rather than in style, and koine cannot hold both.

**koine reads to the next field.** A field that ends at a blank line can be
overrun by pressing return and carrying on, which makes the limit advisory — and
the limit is the whole mechanism keeping a summary readable by somebody who works
on neither project. Under this reading both existing logs still pass, so the
choice costs nothing today; it closes an evasion that nobody has used yet.

## What the tooling does

```python
from koine import postmortem

log      = postmortem.read(path)          # wherever the log lives
problems = postmortem.check(log, level=postmortem.PROTOCOL, registry=ids)
failures = postmortem.report(log, level=postmortem.SHAPE)   # prints, returns a count
```

Two things beyond checking, and they are the reason a protocol is worth more than
a format.

**`lessons(log)`** returns every `Learned:` line with the entry and date that
produced it. anoieu maintains a *Standing rules this log has produced* table by
hand, whose own header says that a rule with no incident behind it is a
preference. Its log carries ten lessons; the table carries nine rules; at most
three of the ten are recognisable in a row of it, and two of the nine cite no
incident at all. **The table and the log are two records of one thing, kept
apart, already disagreeing.** Deriving one from the other is a one-line call.

**`open_debts(log)`** returns what has been booked and not written off, which is
the input `tools/landing.py` reads out of prose today.

**`scaffold(...)`** writes a blank entry with today's date and the fields.
The prompts that produce these entries run in sessions that have never read this
page; handing them the skeleton is cheaper than describing it, and it is the one
point where a protocol can be kept before the fact rather than audited after.

## Where the ground truth is

**This page.** [`../koine/postmortem.py`](../koine/postmortem.py) implements it and its
docstring says so; where the two disagree, this page is right and the module is
the defect.

**What carries a copy:** the module's docstring, and each customer's own log
preamble once one adopts. [`../tests/test_postmortem.py`](../tests/test_postmortem.py)
is what compares the implementation to the rules stated here, and
[`../tests/customers.py`](../tests/customers.py) compares it to real logs.

## What is not decided here

**Whether the log should be one file or several.** Both customers keep one per
repository. An ecosystem-wide log is a different object with different owners,
and nobody has asked for one.

**Whether an entry ever leaves the tree.** This is
[the open question in koine's front page](../README.md#the-open-question) and the
protocol does not prejudge it: a record a program can read with no network and no
account is what makes the tracker comparison possible to run at all.

**What a maintainer must sign.** An entry is written by whoever processed the
event, and nothing here says a person approves one. That is the customer's rule
to make, and both currently have it as part of *leave everything staged*.
