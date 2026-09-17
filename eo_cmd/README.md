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
