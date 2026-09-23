#!/usr/bin/env python3
"""Tests for koine_window.

    python3 tests/test_window.py

Everything runs against git repositories built in a temporary directory, so a
test reads as a history: here is what the project did, here is what the window
says about it. Nothing fetches, and no repository outside the scratch directory
is read.

**The three properties that carry the weight are the three ways a window lies.**
A shallow clone carries no history and its empty window says nothing about the
project. A diverged branch is not a history, and `base..HEAD` on one is what a
branch has done since the merge-base. A checkout parked at the baseline has an
empty window by construction. Each is reported, in the facts and in the prose,
because a window that lies quietly is worse than no window at all.

A fourth property is about the prose rather than the git: **a command is never
re-wrapped**, and a paragraph always is. The prose carries paths and project
names of every length, so wrapping it by hand would mean a paragraph whose shape
depends on how long somebody's checkout path happens to be.
"""

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "bug_db_manager", "koine_window")

_spec = importlib.util.spec_from_loader(
    "koine_window",
    importlib.machinery.SourceFileLoader("koine_window", SCRIPT))
win = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(win)

FAILURES = []

URL = "https://github.com/cvc5/cvc5.git"


def said(text, phrase):
    """Whether the prose says that, wherever the wrapping happened to break it.

    The prose is wrapped at the end rather than written pre-wrapped, so where a
    sentence breaks depends on the length of a path somebody chose. A test that
    matched the raw text would be a test of this machine's temporary directory
    names.
    """
    return " ".join(phrase.split()) in " ".join(text.split())


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


class Project:
    """A git repository with a history, standing in for somebody else's project."""

    def __init__(self):
        self._temp = tempfile.TemporaryDirectory(prefix="koine-window-")
        self.dir = self._temp.name
        self.root = os.path.join(self.dir, "src")
        os.makedirs(self.root)
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "Test")

    def git(self, *args, root=None):
        p = subprocess.run(["git", "-C", root or self.root, *args],
                           capture_output=True, text=True)
        if p.returncode:
            raise RuntimeError(f"git {' '.join(args)}: {p.stderr}")
        return p.stdout.strip()

    def commit(self, subject):
        name = subject.replace(" ", "-")
        with open(os.path.join(self.root, name), "w") as fh:
            fh.write(subject)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", subject)
        return self.git("rev-parse", "HEAD")

    def run(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *args],
                              capture_output=True, text=True, timeout=60)

    def facts(self, *args):
        r = self.run(*args, "--json")
        if r.returncode:
            raise RuntimeError(r.stderr)
        return json.loads(r.stdout)


def test_a_local_window_is_the_commits_after_the_baseline():
    print("\na checkout somebody already has:")
    p = Project()
    base = p.commit("one")
    p.commit("two")
    head = p.commit("three")
    w = p.facts("--baseline", base, "--local", p.root, "--project", "demo")
    check("it is read from the checkout", w["where"] == "local")
    check("HEAD is where that checkout is", w["head"] == head)
    check("the window is what landed after the baseline", w["count"] == 2, str(w))
    check("newest first", [c["subject"] for c in w["commits"]] == ["three", "two"],
          str(w["commits"]))
    check("the baseline itself is not in it",
          base not in [c["sha"] for c in w["commits"]])
    check("nothing is behind and nothing has diverged",
          w["behind"] == 0 and w["diverged"] is False, str(w))

    text = p.run("--baseline", base, "--local", p.root, "--project", "demo").stdout
    check("the prose names the project",
          said(text, "A checkout of demo is on this machine"), text)
    check("it lists the commits", "three" in text and "two" in text)
    check("it gives the full window as a command",
          f"log --no-merges --format='%h %s' {base}..HEAD" in text, text)
    check("and it says the checkout is on loan",
          said(text, "**Read that checkout; never write it.**"), text)


def test_a_cut_listing_says_how_much_it_cut():
    print("\na window longer than the prose will list:")
    p = Project()
    base = p.commit("base")
    for n in range(6):
        p.commit(f"landed {n}")
    text = p.run("--baseline", base, "--local", p.root, "--listed", "2").stdout
    check("it lists as many as it was told to",
          text.count("landed ") >= 2 and "landed 5" in text and "landed 4" in text)
    check("it says how many it left out", said(text, "... and 4 more"), text)
    # A prompt is not a substitute for `git log`. The list is cut and the
    # commands are not, and an assistant that needs the rest is told how.
    check("and that the commands below it are not cut",
          said(text, "the commands below are not, and the window is all of them"),
          text)
    check("the cut notice is a wrapped paragraph, not a line in the commit list",
          all(len(line) <= 79 for line in text.splitlines()
              if "and 4 more" in line or "window is all of them" in line), text)


def test_a_diverged_branch_is_not_a_history():
    print("\na checkout whose branch the baseline is not on:")
    p = Project()
    p.commit("shared")
    p.git("checkout", "--quiet", "-b", "topic")
    p.commit("on the topic branch")
    p.git("checkout", "--quiet", "main")
    base = p.commit("on main, and the rows were measured here")
    p.git("checkout", "--quiet", "topic")

    w = p.facts("--baseline", base, "--local", p.root, "--project", "demo")
    check("it is reported as diverged", w["diverged"] is True, str(w))
    check("and the commits are still listed, because they are still commits",
          w["count"] == 1, str(w))
    check("with the distance back to the baseline", w["behind"] == 1, str(w))

    text = p.run("--baseline", base, "--local", p.root, "--project", "demo").stdout
    check("the prose says the window is not a history",
          said(text, "the window is not a history"), text)
    check("it names what is not an ancestor of what",
          said(text, f"{base} is not an ancestor"), text)
    # The failure this prevents: an assistant handed a list of commits with no
    # warning reads a branch difference as a change somebody made.
    check("and it says plainly not to close a row on the difference",
          said(text, "do not close a row because this branch looks different"), text)


def test_the_owners_remeasure_command_is_pointed_at_never_invented():
    print("\nwhat a reading is told to do instead of re-measuring:")
    p = Project()
    p.commit("shared")
    p.git("checkout", "--quiet", "-b", "topic")
    p.commit("elsewhere")
    p.git("checkout", "--quiet", "main")
    base = p.commit("measured here")
    p.git("checkout", "--quiet", "topic")

    plain = p.run("--baseline", base, "--local", p.root).stdout
    check("without one, the prose still says a reading is not a run",
          said(plain, "**Re-measuring is a run and not a reading**"), plain)
    check("and invents no command", "re-measuring, which is the run" not in plain)

    named = p.run("--baseline", base, "--local", p.root,
                  "--remeasure", "python3 scripts/run.py").stdout
    check("given one, it is printed as a command", "python3 scripts/run.py" in named)
    check("on its own line, not run into the paragraph",
          "  python3 scripts/run.py" in named.splitlines()[-1] or
          any(line == "  python3 scripts/run.py" for line in named.splitlines()),
          named)


def test_a_shallow_clone_is_refused():
    print("\na clone made for an analysis rather than a history:")
    p = Project()
    base = p.commit("one")
    p.commit("two")
    shallow = os.path.join(p.dir, "shallow")
    subprocess.run(["git", "clone", "--quiet", "--depth", "1",
                    "file://" + p.root, shallow], capture_output=True, check=True)
    r = p.run("--baseline", base, "--local", shallow)
    # The alternative is an empty window, which reads as *the project did
    # nothing* and is a fact about the clone.
    check("it refuses rather than reporting an empty window", r.returncode == 1)
    check("and says why", "shallow clone and carries no history" in r.stderr, r.stderr)


def test_a_baseline_the_checkout_does_not_have_is_refused():
    print("\na baseline that checkout never fetched:")
    p = Project()
    p.commit("one")
    r = p.run("--baseline", "0" * 40, "--local", p.root)
    check("it refuses", r.returncode == 1)
    check("and does not offer to fetch it",
          "this never fetches" in r.stderr, r.stderr)


def test_an_empty_window_says_where_else_to_look():
    print("\na checkout parked at the baseline:")
    p = Project()
    p.commit("one")
    parked = p.commit("two")
    p.commit("three")
    p.commit("four")
    p.git("checkout", "--quiet", "-B", "parked", parked)

    w = p.facts("--baseline", parked, "--local", p.root, "--project", "demo")
    check("the window is empty", w["count"] == 0)
    check("and the refs that are ahead are named",
          any(r["ref"] == "main" and r["ahead"] == 2 for r in w["elsewhere"]),
          str(w["elsewhere"]))

    text = p.run("--baseline", parked, "--local", p.root, "--project", "demo").stdout
    check("the prose says nothing landed",
          said(text, "**No commit landed between the baseline and that "
                     "checkout's HEAD**"), text)
    # The useful answer is almost never *the project did nothing*: it is that
    # the history is on a ref nobody checked out.
    check("and names the ref that does carry the history",
          "main in this checkout is 2 commit(s) ahead of HEAD" in text, text)
    check("and offers the remote as the way on",
          said(text, "read the history on the remote instead"), text)


def test_a_remote_window_is_pointed_at_and_never_fetched():
    print("\na project nobody has checked out:")
    p = Project()
    r = p.run("--baseline", "aee8742", "--url", URL, "--ref", "main",
              "--project", "cvc5")
    check("it needs no checkout and no network", r.returncode == 0, r.stderr)
    text = r.stdout
    check("it gives the compare view",
          "https://github.com/cvc5/cvc5/compare/aee8742...main" in text, text)
    check("and the gh recipes, for the cheaper route",
          'gh api "repos/cvc5/cvc5/compare/aee8742...main"' in text, text)
    check("including the one that says whether the baseline is on the ref at all",
          "whether the baseline is on main at all" in text, text)
    check("it warns that the compare view pages",
          said(text, "**That compare view pages at 250 commits.**"), text)
    check("and asks which revision was actually read",
          said(text, "**Say which revision of `main` you read**"), text)
    check("and what a `diverged` answer means",
          said(text, "If that first command says `diverged`, the window is not "
                     "a history."), text)

    w = p.facts("--baseline", "aee8742", "--url", URL, "--ref", "main")
    check("the facts say it was pointed at, not read", w["where"] == "remote")
    # `null` and not `[]`. An empty list is a claim that nothing landed, and
    # this did not look.
    check("and claim nothing about what landed",
          w["commits"] is None and w["count"] is None and w["diverged"] is None,
          str(w))


def test_a_project_hosted_somewhere_gh_does_not_reach():
    print("\na project that is not on github:")
    p = Project()
    text = p.run("--baseline", "abc1234", "--project", "demo", "--ref", "trunk",
                 "--url", "https://git.example.invalid/demo/demo.git").stdout
    check("it still gives the compare view",
          "https://git.example.invalid/demo/demo/compare/abc1234...trunk" in text,
          text)
    check("and promises no gh api that would not work", "gh api" not in text, text)
    check("it still asks which revision was read",
          said(text, "**Say which revision of `trunk` you read**"), text)
    check("and still explains divergence",
          said(text, "the window is not a history"), text)


def test_a_window_nobody_said_where_to_find_is_refused():
    print("\nwhat it will not guess:")
    p = Project()
    r = p.run("--baseline", "abc1234")
    check("no checkout and no remote is refused", r.returncode == 1)
    check("and says which two it wanted", "--url and --ref" in r.stderr, r.stderr)
    r = p.run("--baseline", "abc1234", "--url", URL)
    check("half a remote is refused too", r.returncode == 1, r.stdout)
    r = p.run("--baseline", "abc", "--local", p.root, "--listed", "0")
    check("and a listing of nothing", r.returncode == 1)


def test_a_provenance_that_looks_like_a_flag():
    print("\nwhere the checkout came from, when that is the name of a flag:")
    p = Project()
    base = p.commit("one")
    p.commit("two")
    # A launcher's provenance string is routinely the flag it came from, and
    # argparse reads `--via --use-local` as two flags. Callers build argv lists,
    # so this has to work without them knowing to write `--via=`.
    text = p.run("--baseline", base, "--local", p.root, "--via", "--use-local").stdout
    check("it is taken as the value it is", "(from --use-local)" in text, text)


def test_a_paragraph_is_wrapped_and_a_command_is_not():
    print("\nwhat is re-wrapped and what is left alone:")
    p = Project()
    base = p.commit("one")
    p.commit("two")
    # A path nobody would choose, standing in for one somebody did.
    deep = os.path.join(p.dir, "a" * 60)
    subprocess.run(["git", "clone", "--quiet", p.root, deep], capture_output=True,
                   check=True)
    text = p.run("--baseline", base, "--local", deep,
                 "--project", "a-project-with-a-long-name").stdout
    prose = [line for line in text.splitlines()
             if line and not line.startswith("  ")]
    over = [line for line in prose if len(line) > win.WIDTH]
    check("no paragraph runs long, whatever it was handed",
          all(len(line.split()) == 1 for line in over), "\n".join(over))
    # The one exception, and it is not wrapping failing: a path is a single
    # token, and a token broken across two lines is not a path any more.
    check("except where one unbreakable word is longer than the width, kept whole",
          any(deep in line for line in over), "\n".join(over))
    check("the git command is whole, however long that makes it",
          any(line.startswith(f"  git -C {deep} log --no-merges") and
              line.endswith(f"{base}..HEAD") for line in text.splitlines()), text)
    check("and the commit subjects are not re-flowed either",
          any(line.startswith("  ") and line.endswith(" two")
              for line in text.splitlines()), text)


def test_it_writes_nothing_and_fetches_nothing():
    print("\nwhat it leaves behind:")
    p = Project()
    base = p.commit("one")
    p.commit("two")
    before = p.git("status", "--porcelain=v1", "--untracked-files=all")
    head = p.git("rev-parse", "HEAD")
    reflog = p.git("reflog", "--format=%H")
    p.run("--baseline", base, "--local", p.root)
    p.run("--baseline", base, "--local", p.root, "--json")
    check("the checkout is where it was", p.git("rev-parse", "HEAD") == head)
    check("nothing was added to it",
          p.git("status", "--porcelain=v1", "--untracked-files=all") == before)
    # No fetch, no checkout, no branch: all three would show here.
    check("and nothing moved a ref", p.git("reflog", "--format=%H") == reflog)


if __name__ == "__main__":
    for fn in (test_a_local_window_is_the_commits_after_the_baseline,
               test_a_cut_listing_says_how_much_it_cut,
               test_a_diverged_branch_is_not_a_history,
               test_the_owners_remeasure_command_is_pointed_at_never_invented,
               test_a_shallow_clone_is_refused,
               test_a_baseline_the_checkout_does_not_have_is_refused,
               test_an_empty_window_says_where_else_to_look,
               test_a_remote_window_is_pointed_at_and_never_fetched,
               test_a_project_hosted_somewhere_gh_does_not_reach,
               test_a_window_nobody_said_where_to_find_is_refused,
               test_a_provenance_that_looks_like_a_flag,
               test_a_paragraph_is_wrapped_and_a_command_is_not,
               test_it_writes_nothing_and_fetches_nothing):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
