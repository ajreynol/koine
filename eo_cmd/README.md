# eo_cmd

**The two commands a repository outside this ecosystem actually runs.** Both are
meant to be run *inside the tree being started or joined*, rather than from the
repository that keeps the rule — which is why they live with the tool whose job
is shared machinery, and why
[`../scripts/install_eo_cmd`](../scripts/install_eo_cmd) exists to put them on a
person's path.

| command | what it does |
| --- | --- |
| [`eo_join`](eo_join) | join the Eunoia ecosystem, from inside the repository that is joining |
| [`eo_init`](eo_init) | start a tool: write a README saying what it is for, complying with nothing |
| [`eo_bump`](eo_bump) | move a pinned dependency onto a commit whose CI is green, and refuse otherwise |
| [`eo_status`](eo_status) | who is in the ecosystem and on what footing. **Run only where the register is** |
| [`eo_process_discussion`](eo_process_discussion) | work the topics another tool has addressed to you. Run in your own repository |
| [`eo_install`](eo_install) | put the ecosystem on a machine, or say what is here |
| `koine_append_db` | add a run's new bugs to a database of every bug found. Installed from [`../bug_db/`](../bug_db), where it lives |

**Every installed command carries a prefix saying whose it is**, because the
name is claimed inside somebody else's process and on their PATH. `eo_` is the
ecosystem's — commands that run inside a tree that is not this one. `koine_` is
this repository's own work, installed under the name it already has: **one
program with two names is worse than a longer name.** `install_eo_cmd` refuses
anything else. A command does not have to *live* in this directory to be
installed out of it.

> **A pinned consumer must not take `koine_append_db` off PATH.** anoieu and
> dokimasia resolve it through their own `koine.lock` into a pinned checkout,
> and that pin is why an append-only database gets the same append semantics
> every run. PATH gives whatever the operator installed. Installing it here is
> for **a person at a terminal**, and it does not make those locators
> deletable.

[`commands.json`](commands.json) is what the installer reads.
**Read one before running it** — every form takes `--show-prompt`, which prints
exactly what it would hand an assistant and does nothing else.

## Installing them

```console
$ ../scripts/install_eo_cmd --prefix ~/bin   # install, and remember the directory
$ ../scripts/install_eo_cmd                  # later runs need no arguments
$ ../scripts/install_eo_cmd --status         # what is installed, and whether it is current
$ ../scripts/install_eo_cmd --uninstall      # remove what it installed
```

**`--dry-run` lists every command with the verb that applies to it**, so a run
on a machine that is already up to date still says what the command does —
which is when somebody is most likely to be asking:

```console
$ ../scripts/install_eo_cmd --dry-run
-- would install 1, 1 already current, 1 skipped  ->  /home/you/bin
   skip eo_cmd/eo_join    /home/you/bin/eo_join     (already current)
   cp   eo_cmd/eo_status  /home/you/bin/eo_status   (new)
   skip eo_cmd/eo_bump    /home/you/bin/eo_bump     (exists and is not ours; --force replaces it)
-- a copy, not a move: the source keeps every file, and each one is written
   to a temporary file beside the target, made executable, and renamed over
   it, so an interrupted run leaves the old file in place
-- dry run: nothing was written, and /home/you/bin is unchanged
```

A real run prints the same rows under `installed` rather than `would install`,
so the two are compared by reading them. **It never overwrites a file it did
not install** — that row is skipped and says so, and `--force` is a person's
decision because the file being replaced is theirs. The chosen directory is
remembered in `install_eo_cmd.local.json`, which the repository ignores.

**Each command is installed as one file**, so nothing here may import anything
from beside it in this tree. `eo_status` did for an afternoon on 2026-09-17 and
broke the moment somebody ran the installed copy; `tests/test_eo_cmd.py` now
runs every command from a directory with none of this tree in it.

## What koine may change here, and what it may not

koine maintains these under **`R35`** in
[kanon's `docs/roles.md`](https://github.com/ajreynol/kanon/blob/main/docs/roles.md):
their text, their options, and what they ask an assistant to do.

**What joining costs, and what a member is held to, is `R4` and stays with the
office.** This repository maintains the program that states the rule and **has
no standing to change the rule.** `eo_join` is two hundred lines of argument
about whose front page a declaration is; that argument is a position, and the
tool doing the drafting is not the one that holds it. A change to what `eo_join`
*asks of a repository* is a change to be argued in kanon, and then written here.

**They were kanon's until 2026-09-17**, as `prompts/join_eo` and
`prompts/init_eo`, and were stored here as copies nobody was allowed to edit.
kanon then deleted its pair and `R35` was created to hold them. The machinery
that policed the copies — a `--sync` and a `--check` that re-derived each file
from kanon's original — was removed with the arrangement it enforced.

## eo_join

```console
$ eo_join                       # join, and say so on the front page
$ eo_join --associate        # the associate footing, on the maintenance page
$ eo_join --soft                # the maintenance note only, joining nothing
$ eo_join --soft --affiliated   # the same, naming this ecosystem, held to nothing
```

**The answer to *should we join* is often no.** A tool with conventions of its
own, or maintainers who have agreed to none of this, is worse off adopting a
policy it did not choose — which is what `--soft` is for. Every form opens by
asking whether the repository is the runner's alone to speak for, because a
declaration on a shared tree is not one maintainer's to make, and commit access
is capability rather than voice.

### The four forms, and how they differ

**`eo_join`** declares membership on the README, adds the pinned `anoieu /
policy` workflow, and runs the checker.

**`eo_join --associate`** takes the **`associate`** footing. The repository
holds itself to the policy on its own `docs/maintenance.md`, adds no front-page
declaration, and **owes this ecosystem nothing.** Both halves matter and the
second is the one a reader gets wrong: an associate is not a quieter member. The
obligation is self-imposed and answered to by the repository alone; the check
runs and prints a result, and that result is **a measurement rather than a
shortfall** — a failure is nobody's fault and counts toward nothing. The marker
is read strictly all the same, which is not a contradiction: strictness is the
difference between a claim somebody can check and a word.

**`eo_join --soft`** adds the maintenance note and stops: no membership, no
workflow, no checker, and the note names no other project at all.

**`eo_join --soft --affiliated`** is the same note naming this ecosystem as one
the repository works with, and saying it is **not** held to the policy. On a tree
we do not own that is a second thing to ask agreement for, not a gentler version
of the first.

## eo_install

```console
$ eo_install --status    # what is here, what is missing
$ eo_install --dry-run   # the clone commands, run nothing
$ eo_install             # clone what is not here yet
```

Run it anywhere. Checkouts go beside the register's tree when you are standing
in it and otherwise into the working directory; `--into DIR` says where
instead, and **every run names the directory it chose before cloning
anything.**

**The dry run prints exactly what a real run executes**, live rather than
commented out, so reading it is a review and pasting it does the same thing.
The only command that installs anything is `git clone <url> <dir>` — no branch
flags, nothing through a shell. **A directory that already exists is reported
and never touched**, because a checkout is somebody's working tree and the cost
of being wrong about that is theirs. Children arrive inside their parent and
outsiders are never cloned: we do not put other people's projects on a disk on
their behalf.

## eo_process_discussion

```console
$ eo_process_discussion kanon        # read only: what have they addressed to us?
$ eo_process_discussion kanon D14    # work that one topic
```

Run it at the root of **your** repository, naming the one whose discussion file
may address you. Their tree is read and never written; anything this changes is
changed in your tree and left staged.

**Naming a topic is what authorises acting on it**, and the command implements
that rather than restating it: with no id the prompt is read-only and forbids
changing a file or drafting a reply. With an id it works that topic, and first
checks what the human asked against what the topic says — where they disagree
it stops and says where, rather than taking the more plausible reading or doing
the smaller safe part.

This was kanon's `prompts/process_discussion`, written around kanon by name.
**Nothing about the job is the office's** — every member has a discussion file
and can be addressed in one — so "us" is worked out from the checkout you are
standing in rather than written into the text.

## eo_status

```console
$ eo_status              # the table, by footing
$ eo_status --check      # what is structurally wrong with the register
$ eo_status --children   # include child projects, which are not repositories
```

**In the president's tree it reads the live register.** Anywhere else it is an
**offline** command: the register is baked into the file when
`install_eo_cmd` copies it, and a run says which commit and date that snapshot
came from. Re-installing refreshes it.

```console
$ eo_status --check          # from anywhere
-- offline: a snapshot taken at install time, from kanon at a7bd2b7, on 2026-09-17
--   re-install to refresh it, or run in the president's tree for the live register
```

**Being out of date is fine; not saying so is not.** Live beats snapshot beats
refusal, in that order and never silently — and there is no third place it will
look. A register found somewhere unnamed is a claim about who is in this
ecosystem with no way to say how current it is.

**Why baked in rather than fetched.** Going to look — a sibling checkout, a
clone at a pin — would find *a* register with no way to say how current it is.
Baking it in at install time makes the provenance a property of the file: the
snapshot and the sentence describing it are written together, so no run can
report one without the other.

**It never writes.** A footing is a decision somebody made and no program takes
one; `--check` reports facts about the file — a footing the policy does not
define, an entry with no url, a child with no parent, two entries claiming one
repository — and never an opinion about who should hold what.

## eo_init

```console
$ eo_init new                    # a repository with nothing in it yet
$ eo_init from-child <path>      # work that already exists as a child project
```

The mode is required rather than defaulted: the wrong one produces a confident
README about the wrong thing, and nothing downstream catches it. **It complies
with nothing, deliberately.** A new tool with a clear purpose and no policy is
worth more than a compliant one with nothing to say, and knowing what you are
building is what makes the rest decidable later.
