# Maintenance

**Start here when maintaining koine, whether directly or with an assistant.**
Read the [front page](../README.md), then the shared
[policy](https://github.com/ajreynol/kanon/blob/main/docs/policy.md) and
[vision](https://github.com/ajreynol/kanon/blob/main/docs/vision.md). This page
covers local responsibilities and the decisions reserved for the maintainer.

## Where to start

Begin on `main` and pull with `git pull --ff-only`; stop if switching or pulling
fails. `eo_housekeeping --no-main` explicitly keeps the current branch.
Read [`bug_db/README.md`](../bug_db/README.md) and
[`eo_cmd/README.md`](../eo_cmd/README.md) for the two implementations.

Run the same four suites as [.github/workflows/koine.yml](../.github/workflows/koine.yml):

```bash
python3 tests/test_append_db.py
python3 tests/test_install_eo_cmd.py
python3 tests/test_eo_cmd.py
python3 tests/test_register.py
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
commands and `koine_append_db` are shared tooling under R16. **What joining
costs remains R4's.** Koine maintains the command that states the rule and does
not change that rule itself.

`eo_status` reads the register; it never writes it. Installing
`koine_append_db` on PATH does not replace the lock-based locators used by
pinned consumers. Layout changes affecting consumers need a local notice before
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

## The open work

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
