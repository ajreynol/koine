# Maintenance

**Start here when maintaining koine, whether directly or with an assistant.**
Read the [front page](../README.md), then the shared
[policy](https://github.com/ajreynol/kanon/blob/main/docs/policy.md) and
[vision](https://github.com/ajreynol/kanon/blob/main/docs/vision.md). This page
covers local responsibilities and the decisions reserved for the maintainer.

## Where to start

Begin on `main` and pull with `git pull --ff-only`; stop if switching or pulling
fails. `eo_housekeeping --no-main` explicitly keeps the current branch.
Read [`bug_db_manager/README.md`](../bug_db_manager/README.md) and
[`eo_cmd/README.md`](../eo_cmd/README.md) for the two implementations.

Run the same ten suites as [.github/workflows/koine.yml](../.github/workflows/koine.yml):

```bash
python3 tests/test_append_db.py
python3 tests/test_window.py
python3 tests/test_check_db.py
python3 tests/test_close_db.py
python3 tests/test_install_eo.py
python3 tests/test_eo_cmd.py
python3 tests/test_cvc5_checks.py
python3 tests/test_listen.py
python3 tests/test_register.py
python3 tests/test_git_status.py
python3 /path/to/anoieu/scripts/policy_check.py --policy-version 1 --root .
```

[The policy job](../.github/workflows/anoieu.yml) calls anoieu's shared workflow
at `main`, selecting **policy contract 1**. The contract fixes requirements and
severities while implementation fixes arrive automatically; there is no checker
pin to update. As checked on 2026-09-20 at anoieu `0b6ec54`, which is that tree
committed and clean, the contract page is
[`policy_check/README.md`](https://github.com/ajreynol/anoieu/blob/main/policy_check/README.md)
and it defines this interface: anoieu keeps each document beside the thing it
describes, and `docs/` holds only that repository's own records. Its `D41`
publishes the was-to-is table for every path of theirs a link here could name.
**The invocation in the suite above will not move under us**: `scripts/policy_check.py`
with `--root` and `--policy-version` is named on that page as part of contract 1
and as the stable launcher for people, whatever the implementation beside it does.
The shared policy and role register read for this maintenance pass are kanon
`5152223`, on 2026-09-20, with `docs/laws.md` edited and not committed in that
tree.

Tests must work without neighboring ecosystem checkouts. The prompt suite
previews every advertised form with an empty home directory and no siblings;
optional checks against neighboring tools report their skips. A local pass
covers these commands, not a hosted workflow run. Inspect `gh run list` for the
current committed revision when network access is available; uncommitted work
has no hosted CI result.

None of this repository's documentation is generated. The command manifest is
the ground truth for the roster; the prompt suite compares the README's copy.

## The supervision division

The maintainer's standing instruction:

> **Where the only parties are full members of the Eunoia ecosystem, low-level
> implementation is yours to decide — do not ask.** Be fearless. What is
> adamantly protected is the *structure* of the infrastructure, and that is not
> yours to move.

Decide API mechanics, parsing, diagnostics, tests, and equivalent behavior
locally. Ask before changing this repository's purpose, a field vocabulary
other repositories consume, or a maintenance obligation. Public or irreversible
actions require the maintainer's instruction. Nothing is sent to another
project without that instruction.

## What is not koine's at all

**Anoieu, dokimasia and metagraphe maintain their own databases.** Koine
maintains `bug_db_manager/`, the tooling they call. Metagraphe's is a
`rewrite_db/` of rewrite candidates, in tachyon at `tools/metagraphe/`; the
tooling is called bug_db regardless and requires no record to be a defect. Data upkeep, evidence, triage,
corrections, cleanup and close/reopen decisions stay with each database owner.

| responsibility | whose |
| --- | --- |
| Epoch design and implementation | the maintainer's; koine carries no epoch machinery |
| Membership, joining requirements, policy, announcements, and the register | kanon's |
| Discussion protocol, role handoffs, and the channel model | kanon's |
| Policy checker implementation and reporting workflow | anoieu's |
| Repository-history audits | epikrisis's |
| The office's document checks | kanon's; they remain separate from register-reading commands |
| Working-window machinery | withdrawn; koine has no schedule to implement |

These boundaries follow the policy and role register read at kanon `5152223`
on 2026-09-20. `eo_init` and `eo_join` are maintained under R35; the other
commands and the four `koine_` programs are shared tooling under R16. **What joining
costs remains R4's.** Koine maintains the command that states the rule and does
not change that rule itself. R16's own list of commands names six of the eight
and not `eo_listen` or `eo_git_status`; both are in this repository's manifest and
in the register's tooling inventory, so the gap is in one paragraph of the
register and is recorded in `discussion.md` as a live request rather than fixed
here — the register is the office's page.

`eo_status` reads the register; it never writes it. Installing any `koine_`
program on PATH does not replace the lock-based locators used by pinned
consumers. Layout changes affecting consumers need a local notice before
those consumers are asked to change anything.

**The policy was reorganised on 2026-09-20, and two of its changes reached the
commands.** Kanon **retired mandatory child isolation** — a child may now be
imported, tested and shipped with its parent, and documented boundaries replace
the island rule — and **recommended `docs/brainstorm.md`** as the standing
register of exploratory ideas, on the same optional footing as this page and
`discussion.md`. `eo_child` had **paraphrased** the retired rule into its prompt
and so carried it past the retirement; `eo_brainstorm` now reads that register
before proposing anything and appends what survives. The general lesson is the one
`eo_housekeeping` was rewritten for and is worth keeping in front of the next
pass: **a prompt that restates somebody else's rule is a copy nothing keeps
current.** Where a command needs a rule, it names the section and sends the
assistant to read it.

## Check who the instruction is addressed to, before the first edit

If an instruction names a responsibility held elsewhere, identify the intended
repository and stop. Do not create a missing artifact to make the instruction
fit this tree. If no other intended repository can be named, do the work here.
A person may override a mismatch after it is explained.

An instruction asking koine to decide its own standing belongs with the person
who decides that standing. An agent can describe an interface it could support;
it cannot grant koine a role or declare its work publishable.

## The two rules that cut across both

**Discussion work needs a human instruction.** Reading is free; answering or
implementing a topic requires an instruction naming it and agreeing with it.
If they disagree, explain the mismatch and wait rather than reconciling them.

> **Overridden for `eo_housekeeping`, standing, by the maintainer on
> 2026-09-17.** A run
> answers topics whose `To:` names this repository without requiring the person
> to name each one. The prompt states that instruction explicitly. The override
> permits writing only in this tree and sending nothing anywhere.
>
> The recorded basis is that the response gate otherwise requires a named topic,
> while housekeeping discovers topics during the run. For it not to be needed,
> the human instruction would need to name the discovered topics
> before they are answered. It does not extend to `eo_respond`, whose topic
> argument remains required.

Keep live correspondence in [`discussion.md`](discussion.md), append dated
replies, and remove settled topics after recording lasting decisions where they
belong. A proposal in an old topic does not establish koine's current scope;
changes to scope remain the maintainer's decision. Allocate new IDs above the
highest ever used, including Git history.

**Work is left staged, not committed.** The diff is the review. If another
session commits or changes the tree during a run, report what moved and inspect
it before relying on the earlier reading.

> This is also the convention the `eo_cmd/` prompts state to an assistant, in
> the same words in every command that changes a tree. **`--push` is the one
> thing that changes it**: the person running the command asks for the work to
> be committed and pushed, and a run that was not asked does not commit.
> `eo_brainstorm` refuses the flag, and so does `eo_housekeeping --report`,
> because neither produces anything to push. See
> [`eo_cmd/README.md`](../eo_cmd/README.md#how-the-work-is-left).

## The open work

**The closure tooling is built and all three consumers use it.** `koine_window`
resolves and describes the window a closure run reads; `koine_close_db` starts an
assistant on the closure; `koine_check_db` establishes afterwards that the run
added closure fields and did nothing else; and `koine_append_db` reports a record
the owner had closed and a later run found anyway. All four are mechanics. None
decides that a finding is fixed, and `koine_close_db` refuses to run without the
owner's `prompt.writes`, because a closure vocabulary is not koine's to guess.
[What is still not built](../bug_db_manager/README.md#what-is-still-not-built)
says what remains, and who asked for it.

**Adoption, as read in each consumer's tree on 2026-09-20.** All three pin
`e4e4e2e`, **which is no longer this repository's tip**: `a5df029` landed after
it and nobody's pin has moved, which is the expected state rather than a lag to
chase. A pin moves when a consumer decides to move it, on evidence of green CI
at the commit it is moving to, and that decision is theirs. The evidence behind
the pin they hold is anoieu's: its lock records `e4e4e2e` verified against
remote `main` on 2026-09-19 with both koine jobs passing, and names the two
runs. That is their reading rather than one taken here — a local pass covers
these commands and not a hosted run. anoieu's launcher calls `koine_close_db`, `koine_window` and `koine_check_db`
through `anoieu_analyzer/reporting/config/koine.lock`, and builds its closure
config in memory with `also: ["awaiting_landing"]` and its own `baseline.command`
— the two things this page expected it to need. dokimasia's calls the same three
through `scripts/koine.lock`, so the shallow-clone refusal and the
diverged-branch warning it never had are now the same code anoieu's uses, which
was the argument for making the window one program. Metagraphe pins it at
`tools/metagraphe/rewrite_db/koine.lock` and files through a thin adapter,
`tools/metagraphe/scripts/koine_db.py`.

**Nobody's copy of the window machinery is left.** Where each consumer's own
baseline logic stays is `baseline.command`, which is the one part that does not
move here: which field records a revision, and what to do when two rows disagree,
each owner has answered differently and correctly.

**The third customer's records are not defects and never were.** Metagraphe's
`rewrite_db/` holds rewrite candidates — a proposed `lhs -> rhs` with its side
condition and the evidence that cvc5 does not take the opportunity. That is why
these programs read the envelope key a database uses rather than assuming one,
take the noun for a record from configuration, and require no field named `bug`.
Its database is keyed `rewrites`; the tooling stays called bug_db.

**No paper is planned for koine**, on the maintainer's instruction of
2026-09-18. This is koine's answer to anoieu's request for one; it is not a
judgment about another tool's work.

**koine keeps no `docs/brainstorm.md`, and the reason is that the ideas are
already somewhere.** The shared policy recommends that register for exploratory
ideas worth retaining, and this repository's are not loose: the four unbuilt
services below are each priced in a live topic and summarised here, which is the
document that governs whether koine takes a maintenance obligation on. A second
home for them would be a copy, and the policy asks for pages somebody intends to
maintain. `eo_brainstorm` opens one where a repository has ideas and no register;
if a pass here ever produces ideas that are koine's own rather than a consumer's
request, that is when this changes.

**Four proposed services are unbuilt, and each needs the maintainer to accept a
new maintenance obligation.** The first two were koine's own answers to
dokimasia; the last two are what the consumers asked for on 2026-09-19, once
koine had asked them to make any follow-up concrete. Every one of them is priced
in [discussion.md](discussion.md) and none is promised.

- A prompt-drift check that consumers fetch and run in **their own CI**. A
  verdict only in koine's CI cannot fail the consumer's change that causes drift.
- A shared pinned-checkout resolver taking a lock, an explicit override, and
  candidate directories. It must verify the exact revision and clean tracked
  files, reject an invalid override, and perform no network access or checkout
  mutation during analysis. Setup would be a separate operation.
- A **coverage query**, asked for by anoieu: given two runs, whether a finding
  was *covered and not reported*, *covered and reported*, or *not covered*. It
  needs a run record these programs do not keep, and no part of it may become a
  verdict — *covered and not reported* is evidence for a person.
- **Correction history**, asked for by dokimasia and by tachyon independently:
  keeping the original claim, its date and its corrections when a later run under
  the same identity carries different text. Today the original is kept and the
  new wording is printed as a conflict and lost. This is storage and so is
  koine's, which is why it is the one of the four a maintainer is most likely to
  want; it also changes what a record is, so it is not an afternoon's flag.

Consumers keep their adapters; there is no promised replacement. No shared
reporting-record checker is offered by this tree, and no postmortem protocol —
anoieu retired the postmortem log and its shape checks on 2026-09-19, so there is
no longer a shape for anyone to hold.
