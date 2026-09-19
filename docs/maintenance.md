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

Run the same nine suites as [.github/workflows/koine.yml](../.github/workflows/koine.yml):

```bash
python3 tests/test_append_db.py
python3 tests/test_window.py
python3 tests/test_check_db.py
python3 tests/test_close_db.py
python3 tests/test_install_eo.py
python3 tests/test_eo_cmd.py
python3 tests/test_listen.py
python3 tests/test_register.py
python3 tests/test_git_status.py
python3 /path/to/anoieu/scripts/policy_check.py --policy-version 1 --root .
```

[The policy job](../.github/workflows/anoieu.yml) calls anoieu's shared workflow
at `main`, selecting **policy contract 1**. The contract fixes requirements and
severities while implementation fixes arrive automatically; there is no checker
pin to update. As checked on 2026-09-18 at anoieu `b5a7d4e`, the
[checker guide](https://github.com/ajreynol/anoieu/blob/main/docs/policy-checker.md)
defines this interface. The shared policy read for this maintenance pass is
kanon `d03447d`, on 2026-09-18.

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

These boundaries follow the policy and role register read at kanon `d03447d`
on 2026-09-18. `eo_init` and `eo_join` are maintained under R35; the other
commands and the four `koine_` programs are shared tooling under R16. **What joining
costs remains R4's.** Koine maintains the command that states the rule and does
not change that rule itself.

`eo_status` reads the register; it never writes it. Installing any `koine_`
program on PATH does not replace the lock-based locators used by pinned
consumers. Layout changes affecting consumers need a local notice before
those consumers are asked to change anything.

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

**Closure tooling was built on 2026-09-19.** `koine_window` resolves and
describes the window a closure run reads; `koine_close_db` starts an assistant
on the closure; `koine_check_db` establishes afterwards that the run added
closure fields and did nothing else; and `koine_append_db` now reports a record
the owner had closed and a later run found anyway. All four are mechanics. None
decides that a finding is fixed, and `koine_close_db` refuses to run without the
owner's `prompt.writes`, because a closure vocabulary is not koine's to guess.
[What is still not built](../bug_db_manager/README.md#what-is-still-not-built)
says what remains. D25 announced the tooling rename and the earlier assessment to
anoieu and dokimasia, and promised no cleanup or closure command; this goes
beyond that notice and the consumers have not been told.

**No consumer uses any of it yet.** anoieu and dokimasia pin koine at `8efe59c`,
which is before all of it, and both keep their own copy of the window machinery
inside `prompts/close_bug_db`. Metagraphe has no database yet and tachyon records
no koine pin. Adopting is each owner's to decide and to schedule; the ecosystem's
rule is that a pin only moves to a commit where this repository's CI is green, so
this wants pushing before any of them is asked.

**Three things want saying to the consumers when they are told.** anoieu's
`awaiting_landing` does not carry the `closed_` prefix, so it is named with
`--also` rather than renamed — the flag exists for that case and costs one line
of config. dokimasia's own launcher has neither the shallow-clone refusal nor the
diverged-branch warning that anoieu's grew, which is the concrete reason the
window is one program now. And a closure config's `baseline.command` is where
each owner's existing baseline logic goes; it is the one part of their launchers
that does not move here, because which field records a revision — and what to do
when two rows disagree — each of them has answered differently and correctly.

**The third customer is planned, not built.** Metagraphe, a child project in
tachyon at `tools/metagraphe/`, will keep a `rewrite_db/` of rewrite candidates:
a proposed `lhs -> rhs` with its side condition and the evidence that cvc5 does
not take the opportunity. That is not a defect, which is why these programs read
the envelope key a database uses rather than assuming one, take the noun for a
record from configuration, and require no field named `bug`. The tooling stays
called bug_db.

**No paper is planned for koine**, on the maintainer's instruction of
2026-09-18. This is koine's answer to anoieu-D14; it is not a judgment about
another tool's work.

Two proposed services remain unbuilt and require the maintainer to accept a new
maintenance obligation:

- A prompt-drift check that consumers fetch and run in **their own CI**. A
  verdict only in koine's CI cannot fail the consumer's change that causes drift.
- A shared pinned-checkout resolver taking a lock, an explicit override, and
  candidate directories. It must verify the exact revision and clean tracked
  files, reject an invalid override, and perform no network access or checkout
  mutation during analysis. Setup would be a separate operation.

These are the requests discussed in dokimasia-D6 and D12, read at `fe47f6c` on
2026-09-18, and answered here in D14 and D20. Consumers keep their adapters;
there is no promised replacement. No shared reporting-record checker or
postmortem protocol is offered by this tree.
