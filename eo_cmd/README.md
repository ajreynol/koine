# eo_cmd

**Commands to run inside the repository you are working on.**
[`../scripts/install_eo`](../scripts/install_eo) puts them on your PATH.
Prompt commands hand work to an assistant; programs do the work themselves.

| command | what it does |
| --- | --- |
| [`eo_join`](eo_join) | join the Eunoia ecosystem, or add only the soft maintenance note |
| [`eo_init`](eo_init) | start a tool with a README saying what it is for |
| [`eo_status`](eo_status) | read the live register in the president's tree, or an installed snapshot elsewhere |
| [`eo_git_status`](eo_git_status) | show Git status across local checkouts and linked worktrees, without fetching |
| [`eo_topic`](eo_topic) | ask what you want to say, then draft one topic addressed to another tool |
| [`eo_child`](eo_child) | start a named child project under `tools/` |
| [`eo_listen`](eo_listen) | print topics addressed to your repository, read-only |
| [`eo_respond`](eo_respond) | answer one named topic addressed to your repository |
| [`eo_brainstorm`](eo_brainstorm) | explore possibilities and discuss them with you; write only a private note |
| [`eo_housekeeping`](eo_housekeeping) | update documentation, answer incoming topics, fix local tooling, and check CI |
| `koine_append_db` | append a run's records to a database, whatever that database calls them; implementation and usage in [`../bug_db_manager/`](../bug_db_manager/README.md) |
| `koine_window` | resolve and describe the window of another project's history a closure run reads; in [`../bug_db_manager/`](../bug_db_manager/README.md) |
| `koine_check_db` | check that a closure run changed only what it was allowed to; in [`../bug_db_manager/`](../bug_db_manager/README.md) |
| `koine_close_db` | ask an assistant what each watched project has since done about our open records; in [`../bug_db_manager/`](../bug_db_manager/README.md) |

[`commands.json`](commands.json) is the ground truth for this roster and the
installer's output. Its `short` fields supply the installation summary; `what`
carries the fuller descriptions. `test_the_readme_table_agrees_with_the_manifest`
in [`../tests/test_eo_cmd.py`](../tests/test_eo_cmd.py) compares the names and
checks that each command is documented. It cannot check whether the prose still
describes the behavior correctly.

Every installed command has an `eo_` or `koine_` prefix. The installer refuses
other names. Each command is installed as one file and imports nothing from
beside it in this checkout. Tests exercise the installed copies.

## Installing them

Run these from the koine checkout:

```console
$ scripts/install_eo --prefix ~/bin
$ scripts/install_eo                   # update using the remembered directory
$ scripts/install_eo --status
$ scripts/install_eo --dry-run          # print only the planned cp commands
$ scripts/install_eo --verbose          # show each file
$ scripts/install_eo --init-clone [DIR] # clone missing ecosystem repositories
$ scripts/install_eo --uninstall
```

The default directory is `~/bin`. The installer prints PATH advice if the
current shell cannot find it; shell configurations differ, so check that advice
before running an installed command. The chosen directory and installed-file
records live in the ignored `install_eo_cmd.local.json` at this checkout's root.
That state filename is stable, so renaming the installer preserves the chosen
directory and its installed-file ownership records.

A run reports where it installs, what changed, and what you can type next.
Commands for people appear first; the four `koine_` commands, marked
`audience: tooling` in the manifest, appear separately. `--verbose` shows the file table;
an install `--dry-run` prints only shell-quoted `cp` commands and creates
nothing, even with `--verbose`. It prints nothing when no files need copying.
Files that are current or protected from replacement are omitted. A normal
installation explains protected files; `--force` permits their replacement.
The copy list names the source and final destination; installation also makes
commands executable and embeds the register in commands that request it.

`--init-clone` reads the president's register and clones missing repositories
into `DIR`, or beside the president's checkout by default. It installs no
commands and leaves existing directories alone. `--president DIR` explicitly
selects the register checkout; an invalid selection is refused rather than
silently replaced. `--dry-run` prints the proposed clone commands.

**Pinned consumers keep their locators.** As checked on 2026-09-19, three
repositories record their koine dependency in a `koine.lock`: anoieu at
`anoieu_analyzer/reporting/config/koine.lock`, dokimasia at `scripts/koine.lock`,
and tachyon's metagraphe child at `tools/metagraphe/rewrite_db/koine.lock`.
The manifest installs the implementation in `bug_db_manager/`. Consumers must
probe and invoke `bug_db_manager/koine_append_db`; there is no `bug_db/` alias.
Installing it on PATH is for terminal use; PATH selects the installed version
and does not establish a consumer's pin.

## Prompt commands

Every form of a prompt command takes `--show-prompt`: it prints exactly what
would reach the assistant and launches nothing. Previews work without sibling
checkouts and say what cannot be read. A real run may require those checkouts.
`test_every_form_previews_on_a_machine_with_nothing_on_it` exercises every
advertised form with an empty home directory and no neighboring repositories.

`--print` runs non-interactively. `eo_topic` and `eo_child` refuse it because
they must ask you what to write. `eo_status`, `eo_git_status`, `eo_listen`,
`koine_append_db`, `koine_window` and `koine_check_db` are programs, so they
do not take `--show-prompt`. `koine_close_db` is a prompt and does; it is `audience:
tooling` all the same, because a consumer's own launcher calls it with that
consumer's config rather than a person typing it.

## How the work is left

**Every command here that changes a tree leaves the work staged and not
committed.** The prompts say so in the same words, because the diff is the
review: a person reads what an assistant did before any of it is in a history
somebody has to undo. `*.local.md` files — `init-brief.local.md`,
`discussion-response.local.md`, `brainstorm.local.md`, `housekeeping.local.md` —
are not staged at all.

**`--push` is the one thing that changes that.** It tells the assistant to
commit the work with a message saying what changed and why, and to `git push`.
Where there is no upstream, or the push is rejected, the run says so and stops;
it does not force a push or rewrite history. `eo_housekeeping --push` commits
after CI passes, which is still the final step of the work.

| command | `--push` |
| --- | --- |
| `eo_join` | yes. It publishes a declaration made on a front page in that repository's own voice |
| `eo_init` | yes, after the mode: `eo_init new --push` |
| `eo_topic` | yes. It pushes to your own remote and still sends the topic to nobody |
| `eo_child` | yes |
| `eo_respond` | yes, for the change; the reply draft stays an unstaged `*.local.md` |
| `eo_housekeeping` | yes, unless `--report`, which is refused with that pair |
| `eo_brainstorm` | refused: it changes nothing, so there is nothing to push |

The programs — `eo_status`, `eo_git_status`, `eo_listen` — write nothing and
reject the flag as an unknown argument.

## What koine may change here, and what it may not

As checked on 2026-09-19, [kanon's role
register](https://github.com/ajreynol/kanon/blob/main/docs/roles.md) places
`eo_init` and `eo_join` under **R35**, and the remaining commands under **R16**,
shared low-level tooling. Koine maintains their text, options, and behavior.
R16's list of commands names all but `eo_listen` and `eo_git_status`; both are in
[`commands.json`](commands.json) and in the register's own tooling inventory, so
the split is not in question and the list is one paragraph behind.

**What joining costs and what a member is held to belong to R4**, held by the
president. Changes to those requirements are argued there and then implemented
here. Maintaining the command does not authorize changing the rule it states.

## eo_join

```console
$ eo_join
$ eo_join --soft
$ eo_join --push
```

Run in the repository making the declaration. Both forms ask whether the
repository is yours alone to speak for; commit access does not establish that.
Both leave the work staged. `--push` publishes the declaration instead, which is
a decision to make before typing it rather than one a run makes.

`eo_join` points to the president's joining policy, adds the membership note
and the policy workflow it specifies, and runs the corresponding checker
locally. For a pinned workflow, run the pinned revision. For a workflow naming
a policy contract, run a current checker against that contract. The prompt
states neither workflow itself; the policy and anoieu's checker guide define
those interfaces.

`--soft` adds one maintenance section: the repository works with the Eunoia
ecosystem and is held to none of its policy. It adds no membership, workflow,
checker, or footing marker. Putting the ecosystem's name on a shared front page
still requires agreement. A bare maintenance heading naming nobody needs no
command.

`--associate` and `--affiliated` are withdrawn flags and refuse with an
explanation. The associate marker and an independent maintenance note are
written by hand, as the policy specifies.

## eo_listen

```console
$ eo_listen
$ eo_listen | less
```

Run in the repository receiving correspondence. This program prints each
complete `## Dn` topic whose opening `To:` field lists this repository as a
comma-separated recipient. It accepts `**To:**` and plain `To:` fields.
Each topic is preceded by its source repository, file path and line number.
The original fields, body and appended replies are printed together. Mentions
in prose, quoted or fenced examples, and addresses in replies do not select a
topic. Notices and answered topics remain visible.

Discovery searches immediate checkouts beside this repository, under
`$ANOIEU_REPOS` (colon-separated directories) and `$HOME`, and in the president's
`scripts/repos.local` map. `ANOIEU_REPOS_FILE` selects a different map. The
register identifies repositories, excluding children; map entries, registered
directory names and remote URLs resolve checkout identities. Without a register,
nearby names are explicitly unverified and ecosystem coverage is unknown.
Multiple checkouts remain visible. No network lookup is performed.

Topics go to stdout; counts, missing sources and read failures go to stderr.
It reads working files, including local changes. No matches is a successful
result; a present discussion file that cannot be read gives exit status 1,
while invalid arguments, configuration or a run outside Git give status 2.

Requires Python 3 and Git. It launches no assistant, accepts no prompt or agent
options, and performs no writes, branch changes, fetches or pulls.

## eo_respond

```console
$ eo_respond kanon D14
$ eo_respond --no-main kanon D14
$ eo_respond --push kanon D14
```

Run at the root of **your** repository. The prompt first asks the assistant to
inspect the branch, switch to `main` if needed, verify it, and run
`git pull --ff-only`. If switching or pulling fails, stop and report it; do not
force the switch by discarding, stashing, or resetting work. **`--no-main` keeps
the current branch and still requires a fast-forward-only pull.** These are
instructions to the assistant; a preview switches no branch and performs no pull.

The topic is required before an assistant can be launched. The prompt checks
that the human's instruction and the named topic agree; disagreement stops the
work. The other repository is read as it stands and never pulled or written.
Changes here are left staged, and the reply is drafted in
`discussion-response.local.md`, unstaged. `--push` commits and pushes the
change; the reply draft stays unstaged either way. Nothing is sent.

A real run refuses if the target checkout or its discussion file is absent;
a preview prints the prompt with that limitation. To print
topics addressed to you, use `eo_listen`. To answer them during a maintenance
pass, use `eo_housekeeping`.

## eo_housekeeping

```console
$ eo_housekeeping
$ eo_housekeeping --no-main
$ eo_housekeeping --report
$ eo_housekeeping --report --no-main
$ eo_housekeeping --push
```

Run at the root of the repository being tidied. The first paragraph points to
the president's policy and vision, the local README and docs, the checker, and
neighboring tools. The president and tool names come from the register. Without
a register, the prompt reports the missing source and points to the local
README's policy link.

The second paragraph asks the assistant to **ensure `main` and run
`git pull --ff-only` first**, with the same stop-on-failure rules as
`eo_respond`. `--no-main` keeps the current branch. Then it updates documentation,
answers topics whose `To:` names this repository, fixes its tooling, opens local
topics for requests to others, and ensures CI passes as the final step. Children
are included in their parent's work; they open no correspondence of their own.

The work is left staged and not committed; `--push` commits it and pushes it
once CI has passed. `--report --push` is refused, because a report writes only
an ignored file.

**`--report` also switches to `main` and pulls**, unless `--no-main` suppresses
the switch. Beyond that preparation it writes only `housekeeping.local.md`,
unstaged, describing the work and whether CI passes. Neither preview form
changes branches or pulls.

The discussion work uses the maintainer's standing override recorded in
[`../docs/maintenance.md`](../docs/maintenance.md#the-two-rules-that-cut-across-both).
The prompt says so explicitly. It answers only what names this repository,
writes in no other tree, and sends nothing. This override does not extend to
`eo_respond`, which requires a named topic.

## eo_topic

```console
$ eo_topic kanon
$ eo_topic anoieu logos
$ eo_topic --push kanon
```

Run in your repository. The assistant asks what you want to say and waits;
`--print` is refused. It drafts and stages one topic in `docs/discussion.md`,
addressed to the named tools, and sends nothing. `--push` commits and pushes it
to your own remote, which is still not sending it to anybody.

The prompt supplies the date, the target checkout's commit and dirty state,
and the next available topic ID. IDs are allocated above every ID in this
repository's discussion history, including removed topics. Only `## Dn`
headings count; a reply's `### Dn` reference does not allocate a topic.

The prompt applies the policy's distinction between a finding and a topic
before drafting. Other repositories are read and never written.

## eo_child

```console
$ eo_child euthyna
$ eo_child --unadvertised euthyna
$ eo_child --push euthyna
```

Naming the child is the human instruction to start `tools/<name>/`; a run
without a name is refused. The assistant asks for the question, goals, and
boundaries rather than inventing a charter. `--print` is refused.

The work is left staged; `--push` commits and pushes it. A child reads other
trees but writes only within its own directory. It imports
nothing from its parent and participates in none of the parent's tests or CI.
`--unadvertised` records that preference and adds no inward links. The register
is the president's to update; this command writes only in the current tree.

## eo_brainstorm

```console
$ eo_brainstorm
$ eo_brainstorm proof reconstruction
```

Run in your repository. The assistant reads the local tools and cvc5 checkout,
records ideas and rejected ideas in `brainstorm.local.md`, then discusses the
list with you. `--print` produces the list without that conversation. It stages
nothing and implements nothing, and `--push` is refused with that reason.

Each idea identifies the evidence it uses. Missing checkouts and claims resting
on memory or the network are marked as limitations. A proposed tool or child is
not an approval to create one.

## eo_status

```console
$ eo_status
$ eo_status --check
$ eo_status --children
```

In the president's tree, it reads the live register. Elsewhere an installed
copy reads the snapshot baked into it by the installer, printing its source
commit and date. Reinstall to refresh that snapshot. Without either source it
refuses; it does not search for an unlabelled substitute.

`--check` validates the register's structure: footings, URLs, parents, and
unique repository claims. `--children` includes child projects. It runs no
checker against other repositories and makes no membership decisions. Auditing
the register against the world belongs to the president's `eo_status_audit`.

## eo_git_status

```console
$ eo_git_status
$ eo_git_status ~/projects ~/other-checkout
$ eo_git_status --president /path/to/president
$ eo_git_status --repos-file /path/to/repos.local
```

Shows one row per local checkout: path, branch, staged and unstaged changes,
untracked paths, conflicts, and ahead/behind counts against its upstream.
Detached and unborn branches are labelled. Counts describe Git status entries;
an untracked directory counts once, and conflicts are counted separately from
staged and unstaged changes. An em dash means there is no upstream; an upstream
with a missing local ref has unavailable counts. **It does not fetch**, so
remote tracking refs reflect the last fetch. It changes no branch, file or index.

Discovery reads the current checkout, its siblings (or the current directory
outside a checkout), `$HOME`, and the colon-separated roots in `$ANOIEU_REPOS`.
Each root and its immediate children are searched. Positional directories add
checkouts or search roots; there is no recursive disk scan. Linked Git worktrees
are included even outside those roots. Multiple clones and worktrees remain
separate rows; repeated paths and symlinks to the same checkout do not.

When a discovered checkout holds `scripts/ecosystem/ecosystem.json`, the command
reads that register and its `scripts/repos.local` map of `ID PATH` lines.
`--president DIR` selects that checkout explicitly. `--repos-file FILE` or
`$ANOIEU_REPOS_FILE` replaces the automatic path map; paths may contain spaces,
and relative paths are relative to the directory running the command. A
repository is matched by mapped ID, directory name or remote URL. Every found
checkout is shown, including ones outside the register.

The register's source path and repositories not found in the searched locations
follow the table; child projects do not count as missing checkouts. Without a
register the command still shows status and says that missing-repository
coverage is unavailable. Missing repositories are informational. An unreadable
checkout is reported without stopping the remaining checks and gives exit 1;
invalid arguments or configuration give exit 2. No assistant is launched.

## eo_init

```console
$ eo_init new
$ eo_init from-child <path>
$ eo_init new --push
```

Run in a new repository supplied by a person. The mode is required and comes
first, so `--push` follows it. `new`
uses the person's name and scope and checks the glossary for conflicts;
`from-child` reads the child's charter and delivered work without changing its
parent. Both write a README and leave it staged.

The prompt records its sources in `init-brief.local.md`, unstaged, **and the
commit of the tree it read each at** — in both modes, because the register moves
and the version read is the only thing that explains what was written. Missing
scope or a conflicting name requires the person's answer. It adds no policy,
maintenance note, CI, or layout: `eo_join` is a separate step when there is
something to join with.
