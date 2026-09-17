# Maintenance

**If you are an agent working on this repository, start here.** What you may
decide alone, what you may not, and what is not this repository's at all.

[`../README.md`](../README.md) says what koine is for and is assumed read. This
page does not repeat it: everything here is something a reader of the front page
would still get wrong.

Deliberately not linked from the front page — how the work is run is noise to
somebody deciding whether this is worth depending on.

## Where to start

```bash
python3 tests/test_append_db.py                          # bug_db
python3 tests/test_install_eo_cmd.py                     # the installer
python3 tests/test_bump.py                               # eo_bump
python3 tests/test_register.py                           # reading the register
python3 tests/test_eo_cmd.py                             # eo_join and eo_init themselves
python3 /path/to/anoieu/scripts/policy_check.py --root .  # the ecosystem policy
```

Each directory's own README is the whole of its subject:
[`../bug_db/README.md`](../bug_db/README.md),
[`../eo_cmd/README.md`](../eo_cmd/README.md).

**Scripts are named `koine_<piece>`** where they go on somebody's path, because
a name claimed inside another person's process should say whose it is.
`../eo_cmd/` is the exception and the rule working: nothing in it is ours to
claim, so nothing in it carries our name.

## The supervision division

The maintainer's standing instruction, recorded here because an instruction that
lives only in a session is one the next session does not have.

> **Where the only parties are full members of the Eunoia ecosystem, low-level
> implementation is yours to decide — do not ask.** Be fearless. What is
> adamantly protected is the *structure* of the infrastructure, and that is not
> yours to move.

**Decide alone:** the shape of an API, what a script parses, how a failure
reads, how the tests are arranged, which of two equivalent behaviours to keep
when nothing depends on either. Asking about these passes a decision to somebody
with less context than you, and is slower for everybody.

**Ask first:** what this repository is *for*; a field vocabulary another
repository shapes its output to; a maintenance obligation, which outlives the
enthusiasm that made it; anything irreversible or public.

**The scope is member-only traffic.** Members read diffs, and a mistake between
them is corrected in a commit somebody was already going to read. **Anything
that will be read outside the island is not a low-level detail** whatever else
it is — an outbound prompt, a bug report, a claim about somebody's code.

## What is not koine's at all

Do not design it, do not build it, do not have an opinion about it in the tree.

| | whose | why not |
| --- | --- | --- |
| **epochs** | the maintainer's | **THE DESIGN OF EPOCHS IS NOT KOINE'S TO DECIDE.** koine carries **no knowledge of how epochs are implemented** |
| membership, joining, the repository policy | **kanon's** | it decides who is in |
| global announcements, and who is told | **kanon's** | the same reason, one level down |
| **the register itself** — the inventory, the footings, the entity ids | **kanon's** | a footing is a decision somebody made. koine keeps the programs that *read* it (`eo_cmd/eo_status`) and never writes to it, and reads it only in the tree that holds it; owning the file would be owning membership |
| the discussion protocol, the role handoff, the channel model | **kanon's** | governance, not a shape |
| the policy checker itself | **anoieu's** | our CI pins it and it is not ours to move |
| auditing how a repository's history changed | **epikrisis's** | the register describes it as *audits repository histories against evidence*; koine held a second implementation until 2026-09-17 and should not have |
| **what joining costs, and what a member is held to** | **kanon's** | `R4`. koine maintains `eo_join`, which *states* that rule, and has no standing to change it |
| `check_join_eo`, `global_audit`; every position on publishing | **anoieu's and kanon's** | a position is what somebody signs |

**The test that puts something here:** somebody else maintains it, **or** being
wrong about it reaches people who did not sign up for this. Either is enough.

**When a task lands on this list:** stop, say which row it is, and ask which
repository was meant. Do not build the smaller safe part.

**`eo_cmd/` is the edge of this list, and the edge moved.** Those two commands
were kanon's, stored here as copies nobody could edit, until kanon deleted its
pair on 2026-09-17 and `R35` was created to hold them. koine now writes them —
their text, their options, what they ask. **What it still may not touch is what
joining costs**, the row above: this repository maintains the program that
states the rule, and a change to the rule is argued in kanon and then written
here. [`../eo_cmd/README.md`](../eo_cmd/README.md) carries that line in full.

## Check who the instruction is addressed to, before the first edit

**The tell is concrete: an instruction describing artifacts this repository does
not have is addressed to a repository that has them.** These trees are alike on
purpose and sit side by side on one disk, and an instruction meant for anoieu
arrives here looking exactly like one meant for koine.

This has gone wrong more than once, each time by taking the more plausible
reading instead of stopping. If an instruction names a file, a role, a CI or a
responsibility this tree does not have, **do not supply the missing thing.** Say
what is missing and ask. A human may override after being told, and the override
is then recorded.

**The dangerous shape is a prompt asking this repository to decide its own
standing**, because an agent asked *should koine hold X* will find the case for
X — finding it is what it was asked to do.

## The two rules that cut across both

**Never act on a discussion file unbidden** — this one or anybody's. Reading is
free. Acting requires a human who told you to, named the topic, and whose
instruction agrees with the topic. Where they disagree, do nothing: not the
overlap, not the safer half. Say where they differ and wait.

**Work is left staged, not committed.** The diff is the review, and it is the
last place a change that binds another repository can be caught. If a commit is
taken mid-stream, say so in one line — the cost is that the message stops
describing its contents, and the remedy is a note about the record, which anyone
may write or delete without asking.

## The open work

**What the maintainer names next, and nothing else.** koine takes its work from
the tools that use it and invents nothing on its own. A feature nobody asked for
is a guess about somebody else's needs — likely wrong, and more expensive to
withdraw than it was to write.

- **A publishing stance**, owed by this repository — a paper, a plan for one, or
  nothing worth writing up. **All three are answers**, the third is the
  commonest, and which one it is is a position somebody signs. Asked by anoieu on
  2026-09-02 and left unstated.
- **[`discussion.md`](discussion.md) is a record of an earlier purpose.** Its
  topics were written when koine was a reporting-loop library and none was ever
  carried. Whether they are withdrawn, rewritten or left is the maintainer's;
  **no agent works that file unbidden**, including to tidy it.

## What was here before

koine has been pointed at a new job twice: it was a reporting-loop library until
2026-09-16, and held a history review tool until 2026-09-17. The history tool's
ledger — one day's readings of anoieu's record — went with it on 2026-09-17, and
is in git at `65d7b45` if anyone ever wants it handed to epikrisis, whose subject
it was. All of it is in git history, nothing depends on any of it, and none of it
should be rebuilt from memory.
