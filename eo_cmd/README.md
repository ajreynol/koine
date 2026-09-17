# eo_cmd

**The commands a repository outside this ecosystem actually runs.** Each is meant
to be run *inside somebody else's tree* — the one being started, joined, tidied
or addressed — rather than from the repository that keeps the rule, which is why
they live with the tool whose job is shared machinery, and why
[`../scripts/install_eo_cmd`](../scripts/install_eo_cmd) exists to put them on a
person's path.

| command | what it does |
| --- | --- |
| [`eo_join`](eo_join) | join the Eunoia ecosystem, from inside the repository that is joining |
| [`eo_init`](eo_init) | start a tool: write a README saying what it is for, complying with nothing |
| [`eo_status`](eo_status) | who is in the ecosystem and on what footing. **Run only where the register is** |
| [`eo_respond`](eo_respond) | answer one topic another tool has addressed to you. Run in your own repository |
| [`eo_housekeeping`](eo_housekeeping) | bring a repository up to date: its documentation, the topics addressed to it, its own tooling, and CI |
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

[`commands.json`](commands.json) is what the installer reads, and it is where
each command says which of two things it is. **A `prompt` hands context to an
assistant, and every form of one takes `--show-prompt`**, which prints exactly
what it would hand one and does nothing else — read that before running it.
`eo_status` and `koine_append_db` are **programs**: they do the work themselves,
spend no turn, and have nothing to show.

## Installing them

```console
$ ../scripts/install_eo_cmd --prefix ~/bin   # install, and remember the directory
$ ../scripts/install_eo_cmd                  # later runs need no arguments
$ ../scripts/install_eo_cmd --status         # what is installed, and whether it is current
$ ../scripts/install_eo_cmd --init-clone     # put the ecosystem's repositories on this machine
$ ../scripts/install_eo_cmd --uninstall      # remove what it installed
```

**`--help` says why somebody would run it**, which is the question an option list
cannot answer: these commands are written to run inside *somebody else's*
repository and so are useless sitting in a checkout, and the ecosystem is a set
of sibling checkouts that has to get onto the disk before most of them are worth
much. Both jobs are named there; the second was invisible from the flags alone.

**Every run lists every command twice over** — once with the verb that applies
to it, and once with a line saying what it is for. A machine that is already up
to date therefore still answers *what are these*, which is when somebody is most
likely to be asking:

```console
$ ../scripts/install_eo_cmd --dry-run
-- would install 1, 1 already current, 1 skipped  ->  /home/you/bin
   skip eo_cmd/eo_join    /home/you/bin/eo_join     (already current)
   cp   eo_cmd/eo_status  /home/you/bin/eo_status   (new)
   skip eo_cmd/eo_init    /home/you/bin/eo_init     (exists and is not ours; --force replaces it)
-- what each one is for, from eo_cmd/commands.json:
   eo_join    join the Eunoia ecosystem, run inside the repository that is joining
   eo_status  who is in the Eunoia ecosystem and on what footing, as the register says it
   eo_init    start a tool: write a README saying what it is for, complying with nothing
-- a copy, not a move: the source keeps every file, and each one is written
   to a temporary file beside the target, made executable, and renamed over
   it, so an interrupted run leaves the old file in place
-- dry run: nothing was written, and /home/you/bin is unchanged
```

**That roster is the manifest's own text**, not a second description written
here: [`commands.json`](commands.json) is the ground truth, so a command whose
purpose moves says so on the next install rather than drifting quietly.

**The table at the top of this page is a copy of it, and something compares
them.** `test_the_readme_table_agrees_with_the_manifest` in
[`../tests/test_eo_cmd.py`](../tests/test_eo_cmd.py) decides that the same names
appear in both, that every executable in this directory is in the manifest, and
that each command is written up somewhere. **It answers the easy half only**: it
cannot tell whether a description is still true of what the command does. The
comparison was missing until 2026-09-17 and the copy had already drifted — this
page claimed every form takes `--show-prompt` after two programs arrived that
take no such thing.

A real run prints the same rows under `installed` rather than `would install`,
so the two are compared by reading them. **It never overwrites a file it did
not install** — that row is skipped and says so, and `--force` is a person's
decision because the file being replaced is theirs. The chosen directory is
remembered in `install_eo_cmd.local.json`, which the repository ignores.

**Cloning the ecosystem is not one of these commands.** It is
`../scripts/install_eo_cmd --init-clone [DIR]`, which reads the register the
president holds and clones what is missing beside it. A command for it would
have to be installed by the installer first, so putting the ecosystem on a
machine would depend on having already set up the thing that does it — the job
belongs where somebody already is. `--dry-run` prints the `git clone` lines and
runs none of them; a directory that already exists is reported and left alone.

**Each command is installed as one file**, so nothing here may import anything
from beside it in this tree. `eo_status` did for an afternoon on 2026-09-17 and
broke the moment somebody ran the installed copy; `tests/test_eo_cmd.py` now
runs every command from a directory with none of this tree in it.

## What koine may change here, and what it may not

koine maintains these under **`R35`** in
[kanon's `docs/roles.md`](https://github.com/ajreynol/kanon/blob/main/docs/roles.md):
their text, their options, and what they ask an assistant to do.

**`R35` is written as two commands and this directory holds more, and nothing
compares the two statements.** The role names `eo_init` and `eo_join`; the table
above is longer. Which of them the role is meant to cover is the office's to say
and is not settled by this page listing them — recorded here because a register
and a copy that disagree, with nothing that runs between them, is the thing the
policy asks somebody to notice.

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

## eo_respond

```console
$ eo_respond kanon D14    # answer that one topic
```

Run it at the root of **your** repository, naming the tool whose discussion file
carries the topic. Their tree is read and never written; anything this changes is
changed in your tree and left staged.

**The topic is required, and that is the gate.** The ecosystem's one
build-failing rule is that an agent answers a topic only where a human
instructed it and **named which topic** — and this refuses in argv rather than
asking a prompt to behave, which is strictly stronger than any wording. For *what
has anybody addressed to us*, which names nothing, run
[`eo_housekeeping`](eo_housekeeping): it sweeps every checkout at once and costs
no turn per tool.

**What this does that housekeeping cannot: the disagreement check.** There are
two independent accounts of what somebody wants — the human's instruction and the
topic itself — and where they differ at least one is wrong. A housekeeping run has
only the topic, so it can only take the topic at its word; this has both, and
stops and says where they differ rather than reconciling them or doing the
smaller safe part. **That is the whole of why both commands exist**, and it is
why the gated one is what a contested or expensive topic gets.

Two paragraphs, in the same shape as `eo_housekeeping`: pointers first — the
president, whose tree holds `docs/policy.md` and so what a topic is and what a
reply owes — then the job. The reply is drafted in `discussion-response.local.md`,
unstaged, by the `*.local.md` convention for a document deliberately not
committed.

## eo_housekeeping

```console
$ eo_housekeeping             # bring the repository up to date, and stage it
$ eo_housekeeping --report    # say what it would do, changing nothing
```

Run it at the root of the repository being tidied. **Two paragraphs.** The first
is nothing but pointers: what the ecosystem is, **who the president is** and so
where `docs/policy.md` and `docs/vision.md` are, this repository's own README and
`docs/`, the checker, and the other tools checked out on this machine. The second
is the goal — documentation made true of the tree, the topics other tools
addressed to us answered, bugs in our own tooling fixed, a topic opened in
`docs/discussion.md` for anything needing somebody else, and **CI green as the
final step.**

**The president is looked up, never written down.** The register names who holds
the office and lives in the office's tree, so finding the file is finding the
president — and the prompt keeps naming the right one after the office moves. The
same pass yields the register's list of names, which the neighbour list is
filtered to: a checkout the register does not name is somebody's working copy, and
offering it as a tool to answer is how a topic gets read out of the wrong tree.

**Why it points rather than restates, which is the whole design.** A prompt that
paraphrased the policy would be a copy of somebody else's rules, installed on a
stranger's PATH, with nothing keeping it current — the thing the policy's *Copies*
section is about, and the thing this command is sent to find. It would also
silently narrow the job to whatever the paraphrase happened to name. The first cut
of this file did exactly that, at 1,749 words; `tests/test_eo_cmd.py` now holds it
under five hundred and to two paragraphs.

> **The discussion work runs under a standing override.** Every discussion file
> opens with the ecosystem's one build-failing rule: a topic is answered only
> where a human instructed it and **named the topic**. A command run on a habit
> names none, so a run of this overrides that rule rather than satisfying it, on
> the maintainer's standing instruction — recorded in
> [`../docs/maintenance.md`](../docs/maintenance.md), which is where the policy's
> escape hatch says an override belongs. **The prompt says so in as many words**,
> and that is not ceremony: an assistant that reads the banner without it stops
> there and is right to.
>
> What survives the override: a run answers only what names it, **writes in no
> tree but its own**, and **sends nothing anywhere** — so what it produces is a
> diff somebody reads before anybody else hears from us. It does not extend to
> [`eo_respond`](eo_respond), which keeps the gate.

**The finished prompt is refilled to one width before it is sent**, being
assembled from fragments each wrapped at whatever width it was written at.

## eo_status

```console
$ eo_status              # the table, by footing
$ eo_status --check      # what is structurally wrong with the register
$ eo_status --children   # include child projects, which are not repositories
```

**It reads the register and prints what it says — that is the whole of it.**
It runs no checker against anybody, reads no correspondence, and looks at no
commits. Those go further than reading: they check the register *against the
world*, and being wrong about them is being wrong about somebody else's tree.
The president keeps `eo_status_audit` for that, and the line between the two is
the word audit.

**In the president's tree it reads the live register.** Anywhere else it is an
**offline** command: the register is baked into the file when
`install_eo_cmd` copies it, and a run says which commit and date that snapshot
came from. Re-installing refreshes it.

```console
$ eo_status --check          # from anywhere
-- offline: a snapshot taken at install time, from kanon at a7bd2b7, on 2026-09-17
--   re-install to refresh it, or run in the president's tree for the live register
```

Because every column comes out of the register, **the offline table is exactly
as complete as the live one** — only its age differs.

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
