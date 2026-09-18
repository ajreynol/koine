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
| [`eo_topic`](eo_topic) | open one topic addressed to another tool. **Asks you what you want to say**; sends nothing |
| [`eo_child`](eo_child) | start a child project, `tools/<name>/`. Naming it is what starts it |
| [`eo_respond`](eo_respond) | answer one topic another tool has addressed to you. Run in your own repository |
| [`eo_brainstorm`](eo_brainstorm) | look for what a repository could do next, against what cvc5 and the other tools do now, then work through the list with you. **Changes nothing** |
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

**A preview prints on a machine with nothing on it**, which is the only way that
sentence means anything: the reader it is addressed to has not cloned this
ecosystem, so a preview that refused until the other checkouts were beside it
would refuse exactly them. `eo_respond --show-prompt` did refuse until
2026-09-18, and the same gap made this repository's own suite green here and red
in CI for eight pushes — every check that previews a command reads a checkout
that is a sibling on the machine these are written on and nowhere on a runner.
`test_every_form_previews_on_a_machine_with_nothing_on_it` runs every advertised
form again with `$HOME` and `$ANOIEU_REPOS` pointed at an empty directory.

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
likely to be asking.

**The second list goes last, and a finished install introduces it.** The
bookkeeping — what was copied where, which directory was remembered — answers
the question the script has about the run; the person who ran it is asking
whether they are set up and what to type, so that is what the run ends on:

```console
$ ../scripts/install_eo_cmd --prefix ~/bin
-- installed 1, 1 already current, 1 skipped  ->  /home/you/bin
   skip eo_cmd/eo_join    /home/you/bin/eo_join     (already current)
   cp   eo_cmd/eo_status  /home/you/bin/eo_status   (new)
   skip eo_cmd/eo_init    /home/you/bin/eo_init     (exists and is not ours; --force replaces it)
-- a copy, not a move: the source keeps every file, and each one is written
   to a temporary file beside the target, made executable, and renamed over
   it, so an interrupted run leaves the old file in place
-- remembered /home/you/bin in install_eo_cmd.local.json
-- You are now ready to use the Eunoia ecosystem. For a quick start, here is
   a list of possible commands, to run in the root of repos:
   eo_join    join the Eunoia ecosystem, run inside the repository that is joining
   eo_status  who is in the Eunoia ecosystem and on what footing, as the register says it
   eo_init    start a tool: write a README saying what it is for, complying with nothing
-- every one of them takes --help, which says what it does and what forms it takes
```

**It says *ready* only where that is true.** A dry run wrote nothing, and an
install into a directory that is not on your PATH leaves you files whose names
you cannot yet type; both print the same roster under a heading that promises
nothing, immediately below the line saying which of the two happened.

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

koine maintains all of these — their text, their options, and what they ask an
assistant to do — **under two roles, and the line is where the command runs.**
[kanon's `docs/roles.md`](https://github.com/ajreynol/kanon/blob/main/docs/roles.md)
files `eo_init` and `eo_join` under **`R35`**, because those two are the only
ones that run inside a repository being started or joined, and everything else
here under **`R16`**, the shared low-level tooling.

**The office's reading is the one recorded, and it was the office's to give.**
This page used to file every command under `R35` and say that the register and
the copy disagreed with nothing running between them. kanon's `D18` offered
either reading and said nothing turned on it; taking ours would have been koine
deciding which role it holds what under, which is not a thing this repository
gets to decide about itself. [`../docs/discussion.md`](../docs/discussion.md)
`D18` says so back.

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
$ eo_join          # join, and say so on the front page
$ eo_join --soft   # work with this ecosystem, held to none of it
```

**The answer to *should we join* is often no.** A tool with conventions of its
own, or maintainers who have agreed to none of this, is worse off adopting a
policy it did not choose — which is what `--soft` is for. Both forms open by
asking whether the repository is the runner's alone to speak for, because a
declaration on a shared tree is not one maintainer's to make, and commit access
is capability rather than voice.

### The two forms, and how they differ

**`eo_join`** declares membership on the README, adds the `anoieu / policy`
workflow the policy page gives, and runs the checker locally the way that
workflow runs it. **The page gives two forms of the workflow** — one pinning a
checker revision, one naming a policy contract — and step 3 branches rather than
choosing, because a repository on the contract form has no pinned revision and
cannot run one. Which form a member is held to is what joining costs, which is
the office's; kanon's `D16` asked for the branch and
[`../docs/discussion.md`](../docs/discussion.md) `D18` answers it.

**`eo_join --soft`** adds one README section and stops: no membership, no
workflow, no checker. The note says the repository **works with** the Eunoia
ecosystem and is **not held to** its policy — it adopts none of it, it is not
checked against it, and an assessment published by a tool here is that tool's own
work. **Naming an ecosystem and joining it are different claims**, and the
refusal is stated rather than implied: a note that named us and said nothing else
would be read as a declaration by everybody who has ever seen one.

**`--soft` is not the quiet way in, and it is not the safe thing to run on a tree
you do not own.** It puts our name on somebody else's front page, which is a
second thing to get agreement for rather than a gentler version of the first.
What such a tree can carry meanwhile is the bare `## How this repository is
maintained` heading the policy asks of everybody, naming nobody — and that needs
no command and no agent, which is why one is no longer offered for it.

### It had four forms until 2026-09-18

`--associate` wrote a footing marker, plain `--soft` wrote a note naming no other
project at all, and `--soft --affiliated` wrote the one `--soft` writes now. Four
commands for what a reader experiences as one question — *what does this
repository say about us* — and a chooser who gets it wrong writes the wrong claim
onto a front page. **The maintainer collapsed them**; both removed flags are
refused with a line saying what happened rather than *unknown option*, because
pages this repository does not own still name them.

**The soft note claims no footing, and that is deliberate.** Three of the
office's documents give `associate` two incompatible readings — `policy.md`'s
footings table has an associate *held to the policy by its own choice*, the
register's blurb has one *held to none of this*, and anoieu's checker records
that the word changed meaning under both. So the note says what the repository is
held to, which is nothing, and does not reach for a word whose meaning is
somebody else's to settle. **[`D17`](../docs/discussion.md) says all of this to
kanon**, including that the order was backwards: koine has no standing over what
joining costs, and changed the command first.

## eo_respond

```console
$ eo_respond kanon D14    # answer that one topic
```

Run it at the root of **your** repository, naming the tool whose discussion file
carries the topic. Their tree is read and never written; anything this changes is
changed in your tree and left staged.

**It pulls first.** What it stages has to apply to what is current, or the patch
is a merge for whoever reviews it — so the prompt opens on `git pull`, and on
stopping rather than untangling somebody else's merge to get started. Their tree
it reads as it stands: pulling there would be writing in a tree that is not
yours.

**The topic is required, and that is the gate.** The ecosystem's one
build-failing rule is that an agent answers a topic only where a human
instructed it and **named which topic** — and this refuses in argv rather than
asking a prompt to behave, which is strictly stronger than any wording. For *what
has anybody addressed to us*, which names nothing, run
[`eo_housekeeping`](eo_housekeeping): it sweeps every checkout at once and costs
no turn per tool.

**A run still refuses where their tree is not here**, because it answers a topic
by reading one and there is nothing to read; **the preview prints anyway** and
says which checkout it did not find, since somebody reading the prompt before
running it is the person least likely to have cloned anything.

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
$ eo_housekeeping --report    # say what it would do, changing nothing else
```

Run it at the root of the repository being tidied. **Two paragraphs.** The first
is nothing but pointers: what the ecosystem is, **who the president is** and so
where `docs/policy.md` and `docs/vision.md` are, this repository's own README and
`docs/`, the checker, and the other tools checked out on this machine. The second
is the work: `git pull` first, then the goal — documentation made true of the
tree, the topics other tools addressed to us answered, bugs in our own tooling
fixed, a topic opened in `docs/discussion.md` for anything needing somebody
else, and **CI green as the final step.**

**It pulls before it judges.** Every question a run asks — is this documentation
true of the tree, has anybody answered this topic, does CI pass — is asked of a
checkout, and a checkout that is behind answers all three wrong: work already
done reads as outstanding, and work done here comes back to somebody as a merge.
The pull is in the prompt rather than in front of the command because an agent
that cannot fast-forward is told to **say so and stop**, which a `git pull &&`
could not do. **`--report` pulls too** — a report of what is stale, computed from
a stale checkout, is the defect this command was sent to find — and that is the
one change it makes.

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

## eo_topic

```console
$ eo_topic kanon           # raise something with kanon
$ eo_topic anoieu logos    # one topic, addressed to both
```

Run it at the root of **your** repository, naming who the topic is for. It writes
`docs/discussion.md` here and stages it; their tree is read and never written.

**It does not take the topic on the command line: it asks you, and waits.** What
you want from somebody else is the one thing in a topic that cannot be read off a
tree, and correspondence typed at a shell prompt is one line long — which costs
its reader more than it saves you. `--print` is refused for the same reason:
a non-interactive run has nobody to ask.

**What it carries instead is everything mechanical**, which is the half a person
gets wrong: today's date, the commit their tree is at and whether it was dirty
when you read it, and **the next free id** — allocated above the highest this
repository ever issued, *including topics since removed*, which live in Git
history and nowhere else. Only `## Dn`, the heading of a topic we opened, counts
toward it: a `### `Dn`` inside a reply is somebody else's number being answered,
and counting those would issue one of ours twice.

**A finding is not a topic**, and the policy's test is mechanical: if what you
want to say has a file and a line number, it goes through the reporting workflow
instead. The prompt applies that test before it writes anything, and stops.

**Nothing is sent.** Addressing is not contacting: writing a topic costs us
nothing of theirs, carrying it spends somebody's afternoon, and that is a
person's decision every time.

## eo_child

```console
$ eo_child euthyna                  # start tools/euthyna/ here
$ eo_child --unadvertised euthyna   # ...and link inward to it from nothing
```

Run it at the root of **your** repository. A child project is `tools/X/`, where
`X` names a **potential tool** — an artifact that might one day be worth
building, investigated by writing it down first.

**Naming it is what starts it.** The policy's first rule for a child is that a
human starts one and a human ends one: no agent, script or workflow creates
`tools/X/` on its own initiative, because a child is a claim on attention and a
name in a shared namespace, cheap to spend and expensive to withdraw. A run with
no name is refused in argv — the person typing the name **is** the decision the
rule reserves.

**The charter is asked for, never invented.** What question the child is for and
what it will not do is the whole of what a charter says, and an assistant that
supplied them would be starting a child project on its own initiative with
somebody else's name on it. So the prompt asks and waits — and `--print` is
refused, having nobody to ask.

**It is an island, and the prompt says so before anything else.** The child reads
whatever it likes and writes only inside its own directory: nothing on the import
path, nothing in the parent's test suite, nothing in its CI. **Deleting the
directory is the test** — if removing it changes what the tool does or what CI
says, the coupling is a defect rather than something to document. A prompt that
let an assistant wire the child up would produce exactly that coupling on day one.

**The register is not written here.** Which children exist is recorded in the
president's `ecosystem.json`, that file is the office's, and a status is changed
by a person: the prompt says what the entry would say and writes nowhere but this
tree.

## eo_brainstorm

```console
$ eo_brainstorm                       # what could this tool do next?
$ eo_brainstorm proof reconstruction  # start from somewhere in particular
```

Run it at the root of your own repository. **It is the one command here that
changes nothing**: every tree on the machine is read, and the only thing written
is `brainstorm.local.md` at that root, which `*.local.md` keeps out of the
record. Nothing is staged, nothing is committed, no topic is opened.

**That is the whole of why it is worth running.** An idea is cheap and most ideas
are wrong, so the value is that being wrong costs a file somebody deletes. A
generator that edited the tree would be one nobody ran twice, and its output
would arrive mixed into a diff where an idea is indistinguishable from a fix.

**Cutting edge is a claim about somebody else's tree, so the prompt sends an
assistant to read one.** What is new is new against what cvc5 produces *now* and
against what the other tools here already do — both on this disk, neither in a
model's memory, where the state of the art is as old as the training data. So the
cvc5 checkout and the neighbours are named, every idea says what it was read out
of, and anything resting on memory or the network says it is a guess. Where cvc5
is not checked out, the prompt says so and asks for the claims about it to be
marked.

**A proposal is not an approval.** The policy breaks one composition on purpose:
notice a gap, argue a tool should exist, take a name, write a README — every step
defensible, the whole of it not, because opening a repository is irreversible and
outward-facing. Work that would be a new tool starts as a **child project** under
`tools/`, which is cheap and retirable. This proposes either and creates neither.

**It asks for the rejections too.** The vision says what the arrangement is *for*
and a README says what its tool refuses to claim, so a list of features with
nothing ruled out in it is evidence that neither page was read. That is the half
a brainstorm loses first.

**The file is the record, not the end of the run.** Writing the list and stopping
hands somebody a document at the moment they are best able to argue with it, so
the prompt carries on with them from it: which two or three it would take first,
which one it would drop, and where they want to start. **None of that costs the
guarantee above** — the conversation writes no files, and whatever they pick is
the next thing they ask for rather than something this run does. `--print` is a
non-interactive run and gets the list without the conversation, which is what it
is for.

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
