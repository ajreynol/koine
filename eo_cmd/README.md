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
| [`eo_listen`](eo_listen) | list and summarize topics addressed to your repository, read-only |
| [`eo_respond`](eo_respond) | answer one named topic addressed to your repository |
| [`eo_brainstorm`](eo_brainstorm) | explore possibilities and discuss them with you; write only a private note |
| [`eo_housekeeping`](eo_housekeeping) | update documentation, answer incoming topics, fix local tooling, and check CI |
| `koine_append_db` | append a run's bugs to a database; implementation and usage in [`../bug_db_manager/`](../bug_db_manager/README.md) |

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
Commands for people appear first; `koine_append_db`, marked `audience: tooling`
in the manifest, appears separately. `--verbose` shows the file table;
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

**Pinned consumers keep their locators.** As checked on 2026-09-18, anoieu and
dokimasia record their koine dependency in a `koine.lock` file; anoieu's local
work places it under `config/`, and dokimasia keeps it under `scripts/`.
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
they must ask you what to write. `eo_status`, `eo_git_status` and
`koine_append_db` are programs, so they do not take `--show-prompt`.

## What koine may change here, and what it may not

As checked on 2026-09-18, [kanon's role
register](https://github.com/ajreynol/kanon/blob/main/docs/roles.md) places
`eo_init` and `eo_join` under **R35**, and the remaining commands under **R16**,
shared low-level tooling. Koine maintains their text, options, and behavior.

**What joining costs and what a member is held to belong to R4**, held by the
president. Changes to those requirements are argued there and then implemented
here. Maintaining the command does not authorize changing the rule it states.

## eo_join

```console
$ eo_join
$ eo_join --soft
```

Run in the repository making the declaration. Both forms ask whether the
repository is yours alone to speak for; commit access does not establish that.

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
$ eo_listen --print
$ eo_listen --codex
$ eo_listen --show-prompt
```

Run in the repository receiving correspondence. The assistant lists topics
whose opening `To:` field names this repository, with their source, ID, title,
kind, date, link, summary, and settlement condition. It reads appended replies
and local answers, including `discussion-response.local.md` when present,
and cites the evidence. A local draft is not evidence of delivery; a live topic
does not by itself mean an answer is owed. Notices and answered topics remain
visible. Each entry includes an `eo_respond` command selecting the source
checkout by its absolute path, for you to run separately.

Discovery searches immediate checkouts beside this repository, under
`$ANOIEU_REPOS` (colon-separated directories) and `$HOME`, and in the president's
`scripts/repos.local` map. `ANOIEU_REPOS_FILE` selects a different map. The
register identifies repositories, excluding children; map entries, registered
directory names and remote URLs resolve checkout identities. Without a register,
nearby names are explicitly unverified and ecosystem coverage is unknown.
Multiple checkouts remain visible. No network lookup is performed.

The report names the files read, the revisions and dirty state observed before
launching the assistant, and missing sources. It summarizes working files,
including local changes, and makes no claim that they match remote branches.
Missing sources are reported even when no addressed topic is found.

**This is a read-only survey.** The prompt permits no answers, implementation,
files written, messages sent, branch changes, fetches or pulls. The default
assistant receives only the built-in Read, Glob and Grep tools; `--codex` selects a
read-only sandbox with escalation disabled. `--print` prints the summary
non-interactively. `--show-prompt` prints the exact prompt without launching
an assistant and works even outside a Git repository. A real run requires one.

## eo_respond

```console
$ eo_respond kanon D14
$ eo_respond --no-main kanon D14
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
`discussion-response.local.md`, unstaged. Nothing is sent.

A real run refuses if the target checkout or its discussion file is absent;
a preview prints the prompt with that limitation. To discover and summarize
topics addressed to you, use `eo_listen`. To answer them during a maintenance
pass, use `eo_housekeeping`.

## eo_housekeeping

```console
$ eo_housekeeping
$ eo_housekeeping --no-main
$ eo_housekeeping --report
$ eo_housekeeping --report --no-main
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
```

Run in your repository. The assistant asks what you want to say and waits;
`--print` is refused. It drafts and stages one topic in `docs/discussion.md`,
addressed to the named tools, and sends nothing.

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
```

Naming the child is the human instruction to start `tools/<name>/`; a run
without a name is refused. The assistant asks for the question, goals, and
boundaries rather than inventing a charter. `--print` is refused.

A child reads other trees but writes only within its own directory. It imports
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
nothing and implements nothing.

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
```

Run in a new repository supplied by a person. The mode is required. `new`
uses the person's name and scope and checks the glossary for conflicts;
`from-child` reads the child's charter and delivered work without changing its
parent. Both write a README and leave it staged.

The prompt records its sources in `init-brief.local.md`, unstaged. Missing
scope or a conflicting name requires the person's answer. It adds no policy,
maintenance note, CI, or layout: `eo_join` is a separate step when there is
something to join with.
