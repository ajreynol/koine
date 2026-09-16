#!/usr/bin/env python3
"""Tests for the branch-state reporter.

    python3 tests/test_branch.py

The repositories are built here rather than committed, because a git fixture
cannot be committed inside a git repository without becoming a submodule, and
because what is being tested is what git says rather than what a file contains.
Everything runs in a temporary directory and nothing touches a network.

Two properties carry most of the weight. **Every state must be reachable**, so
that a reporter which only ever says one thing is caught; and **`unknown` must
never be reported as anything else**, which is the distinction the whole piece
exists to keep.
"""

import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import koine_branch as branch  # noqa: E402

FAILURES = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


def git(repo, *args):
    """Loud on failure: a fixture that half-built would test the wrong thing."""
    subprocess.run(["git", "-C", repo, *args], check=True,
                   capture_output=True, text=True)


def commit(repo, name, text="x"):
    with open(os.path.join(repo, name), "w") as f:
        f.write(text)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", name)
    return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def build(root):
    """A checkout with a default branch, a merged branch and an unmerged one."""
    repo = os.path.join(root, "project")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "t")
    first = commit(repo, "one")

    # a branch whose work is in main
    git(repo, "checkout", "-q", "-b", "merged")
    merged_tip = commit(repo, "two")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--ff-only", "merged")

    # and one whose work is not
    git(repo, "checkout", "-q", "-b", "pending", first)
    pending_tip = commit(repo, "three")
    commit(repo, "four")
    git(repo, "checkout", "-q", "main")
    return repo, first, merged_tip, pending_tip


def test_states(repo, first, merged_tip, pending_tip):
    print("\nthe four states:")

    st = branch.ask(branch.Query(repo=repo, ref="merged"))
    check("a branch whose work is in the default branch has landed",
          st.state == branch.LANDED and st.base == "main", st.line())

    st = branch.ask(branch.Query(repo=repo, ref="pending"))
    check("a branch the default does not have is ahead, and by how much",
          st.state == branch.AHEAD and st.ahead == 2, st.line())

    st = branch.ask(branch.Query(repo=repo, ref="no-such-branch",
                                 missing=branch.ABSENT))
    check("a ref a caller calls a branch is absent, and absent is an answer",
          st.state == branch.ABSENT and st.answered, st.line())

    st = branch.ask(branch.Query(repo=repo, ref="no-such-branch"))
    check("and by default a missing ref is unknown, never a quiet answer",
          st.state == branch.UNKNOWN and not st.answered, st.line())

    st = branch.ask(branch.Query(repo=os.path.join(repo, "..", "nowhere"), ref="x"))
    check("a checkout that is not there is unknown, not absent",
          st.state == branch.UNKNOWN and not st.answered, st.line())


def test_a_commit_is_accepted_as_well_as_a_branch(repo, first, merged_tip, pending_tip):
    print("\na commit, which is the other customer's question:")

    st = branch.ask(branch.Query(repo=repo, ref=merged_tip))
    check("a commit in the default branch has landed",
          st.state == branch.LANDED and st.where == "commit", st.line())

    st = branch.ask(branch.Query(repo=repo, ref=pending_tip))
    check("a commit outside it is ahead",
          st.state == branch.AHEAD and st.where == "commit", st.line())

    st = branch.ask(branch.Query(repo=repo, ref=first[:8]))
    check("an abbreviated commit resolves",
          st.state == branch.LANDED, st.line())


def test_not_a_repository(root):
    print("\na directory that is not a checkout:")
    plain = os.path.join(root, "plain")
    os.makedirs(plain)
    st = branch.ask(branch.Query(repo=plain, ref="main"))
    check("is unknown, and says which directory",
          st.state == branch.UNKNOWN and plain in st.detail, st.line())


def test_default_branch_discovery(root):
    print("\nfinding the default branch:")
    repo = os.path.join(root, "odd")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "trunk")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "t")
    commit(repo, "one")
    check("a checkout with neither main nor master has no default to guess at",
          branch.default_branch(repo) == "", branch.default_branch(repo))

    st = branch.ask(branch.Query(repo=repo, ref="trunk"))
    check("so the ref is found and the question is still unknown",
          st.state == branch.UNKNOWN and st.where == "local"
          and "no default branch" in st.detail, st.line())

    # and with master present, the fallback order finds it
    git(repo, "branch", "master", "trunk")
    check("master is found when main is absent",
          branch.default_branch(repo) == "master", branch.default_branch(repo))


def test_local_wins_over_origin(root, repo):
    print("\nwhere a ref was found:")
    clone = os.path.join(root, "clone")
    subprocess.run(["git", "clone", "-q", repo, clone], check=True,
                   capture_output=True, text=True)
    st = branch.ask(branch.Query(repo=clone, ref="pending"))
    check("a branch only on the remote is reported as origin",
          st.where == "origin", f"{st.where!r} {st.line()}")

    git(clone, "checkout", "-q", "-b", "pending", "origin/pending")
    git(clone, "checkout", "-q", "main")
    st = branch.ask(branch.Query(repo=clone, ref="pending"))
    check("and one on both is reported as both",
          st.where == "local and origin", f"{st.where!r} {st.line()}")


def test_commits_are_carried_and_can_be_declined(repo):
    print("\nthe commits behind an ahead branch:")
    st = branch.ask(branch.Query(repo=repo, ref="pending"))
    check("are listed", len(st.commits) == 2, str(st.commits))
    st = branch.ask(branch.Query(repo=repo, ref="pending", log_limit=1))
    check("and the limit is honoured", len(st.commits) == 1, str(st.commits))
    st = branch.ask(branch.Query(repo=repo, ref="pending", log_limit=0))
    check("and a caller may decline them", st.commits == [], str(st.commits))


def test_report(repo):
    print("\nthe report:")
    queries = [
        branch.Query(repo=repo, ref="merged", label="i-1"),
        branch.Query(repo=repo, ref="pending", label="i-2"),
        branch.Query(repo="/nowhere-at-all", ref="x", label="i-3"),
    ]
    buf = io.StringIO()
    failures = branch.report(queries, out=buf)
    text = buf.getvalue()
    check("it returns only the unanswered as failures", failures == 1, str(failures))
    check("it counts the refs", "3 ref(s)" in text, text)
    check("it says the unanswered one is not a clean row",
          "unaudited row" in text, text)
    check("it carries the caller's own labels", "i-2" in text, text)

    result = branch.run(queries)
    check("run returns the same records without printing",
          len(result.of(branch.LANDED)) == 1 and result.failures == 1, text)


if __name__ == "__main__":
    root = tempfile.mkdtemp(prefix="koine-branch-")
    try:
        repo, first, merged_tip, pending_tip = build(root)
        test_states(repo, first, merged_tip, pending_tip)
        test_a_commit_is_accepted_as_well_as_a_branch(repo, first, merged_tip, pending_tip)
        test_not_a_repository(root)
        test_default_branch_discovery(root)
        test_local_wins_over_origin(root, repo)
        test_commits_are_carried_and_can_be_declined(repo)
        test_report(repo)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
