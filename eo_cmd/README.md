# eo_cmd

**The Eunoia ecosystem's commands, kept in one place.** Scripts useful across
the ecosystem rather than inside any one repository, stored here and put on a
person's path by [`../scripts/install_eo_cmd`](../scripts/install_eo_cmd).

**koine keeps these and does not write them.** The repository each one comes
from is the authority for every word of it, and
[`origin.json`](origin.json) records which repository, which path, which role
and which commit. The rule is enforced rather than promised: see [Their content
is not koine's to modify](#their-content-is-not-koines-to-modify).

```console
$ scripts/install_eo_cmd --prefix ~/bin   # install, and remember the directory
$ scripts/install_eo_cmd                  # later runs need no arguments
$ scripts/install_eo_cmd --status         # what is installed, and whether it is current
```

**`--dry-run` names every operation, both paths and nothing else**, so what will
happen is read rather than inferred:

```console
$ scripts/install_eo_cmd --dry-run
-- would install 2, 0 already current, 0 skipped  ->  /home/you/bin
   cp eo_cmd/eo_join  /home/you/bin/eo_join   (new)
   cp eo_cmd/eo_init  /home/you/bin/eo_init   (new)
-- a copy, not a move: eo_cmd/ keeps every file, and each one is written
   to a temporary file beside the target, made executable, and renamed over
   it, so an interrupted run leaves the old file in place
-- dry run: nothing was written, and /home/you/bin is unchanged
```

A real run prints the same lines under `installed` rather than `would install`,
so the two are compared by reading them. `--uninstall --dry-run` lists `rm` and
its path; `--sync --dry-run` lists each file it would write and where it reads
it from.

Some commands in this ecosystem are meant to be run **in a repository that is
not the one they live in** — the tree that is joining, the tree being started.
Reaching those by typing a path into somebody else's checkout is the wrong shape
for them, and nothing here put them anywhere better. `eo_cmd/` holds them, and
this installs them.

The chosen directory is remembered in `install_eo_cmd.local.json`, which the
repository ignores. **It never overwrites a file it did not install**: a name
already taken in the target directory is reported and skipped, and `--force` is
how a person overrides that, because the file being replaced is theirs.
`--uninstall` removes what it put there and leaves anything that has changed
since. `--dry-run` says what would happen and writes nothing.

Today there are two, and both are kanon's:

| installed as | copied from | what it does |
| --- | --- | --- |
| `eo_join` | [`prompts/join_eo`](https://github.com/ajreynol/kanon/blob/main/prompts/join_eo) | join the Eunoia ecosystem, run from inside the repository that is joining |
| `eo_init` | [`prompts/init_eo`](https://github.com/ajreynol/kanon/blob/main/prompts/init_eo) | start a tool: write a README saying what it is for, complying with nothing |

They carry the ecosystem's prefix rather than koine's, because they are not
koine's. Everything at this repository's root is named `koine_<piece>`; nothing
in `eo_cmd/` is, and that is the distinction the directory exists to draw.

## Their content is not koine's to modify

**koine stores these and installs them. It does not own a word of them.** kanon
does — they are part of its `R4`, the ecosystem's policy and joining it — and
kanon's copy is the authority for every line. A question about what `eo_join`
asks of a repository is a question for kanon, and an argument about whether it
should ask it is an argument to have there.

What this repository provides is the service: keeping the copies honest, and
putting them where a person can run them.

So the copies are held to a rule a program can check.
[`origin.json`](origin.json) records where each one came from and
at which commit, and a stored command must be its original with **one** change —
the command's own name, which differs here because the installed names are
prefixed:

```console
$ scripts/install_eo_cmd --check ../kanon
-- eo_join: is prompts/join_eo in /path/to/kanon, renamed and otherwise unchanged
-- eo_init: is prompts/init_eo in /path/to/kanon, renamed and otherwise unchanged
```

`--sync ../kanon` re-copies them, and is the only sanctioned way a file in
`eo_cmd/` changes. Editing one by hand is caught by `--check` and overwritten by
the next `--sync`, which is the intended outcome rather than a hazard: the store
is a copy, and a copy that has been improved locally is just a copy that is
wrong.

**The rename stops at the wrapper.** It is applied to each script's comments,
usage text, error messages and banner, and **not** to the prompt it hands an
assistant. That exception is the point of the rule rather than an edge of it.
Those prompts are read by somebody outside this ecosystem, in their own
repository, and they name the command so that a person handed one can check it
against what the command actually says. The name that survives that check is the
one in the tree they can read, which is kanon's. A local alias would name a
command that exists on one machine and in no repository anywhere.
