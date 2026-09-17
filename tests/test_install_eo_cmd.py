#!/usr/bin/env python3
"""The installer, against directories made and removed in a temporary place.

    python3 tests/test_install_eo_cmd.py

That it puts files where it is told, that a second run changes nothing, that it
says in plain terms what it is about to do, and that it refuses to overwrite a
file of the same name it did not put there.

It once also tested a copy transform: `eo_cmd/` held byte-identical copies of
kanon's joining prompts and the installer policed them. kanon handed those
commands to koine on 2026-09-17, so there is nothing left to police and those
tests went with the machinery.

No network, no checkout, nothing left behind.
"""

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "install_eo_cmd")

_spec = importlib.util.spec_from_loader(
    "install_eo_cmd",
    importlib.machinery.SourceFileLoader("install_eo_cmd", SCRIPT))
inst = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inst)

FAILS = 0


def check(name, got, want):
    global FAILS
    if got == want:
        print(f"  ok   {name}")
        return
    FAILS += 1
    print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")


def ok(name, condition):
    check(name, bool(condition), True)



def run(tmp, *args, env=None):
    """The script, against a checkout copied into a temporary directory."""
    environ = dict(os.environ)
    environ["PATH"] = environ.get("PATH", "")
    if env:
        environ.update(env)
    return subprocess.run(
        [sys.executable, os.path.join(tmp, "scripts", "install_eo_cmd"), *args],
        capture_output=True, text=True, env=environ)


def sandbox(tmp):
    """A koine checkout with two commands in its store, and nothing installed."""
    os.makedirs(os.path.join(tmp, "scripts"))
    os.makedirs(os.path.join(tmp, "eo_cmd"))
    shutil.copyfile(SCRIPT, os.path.join(tmp, "scripts", "install_eo_cmd"))
    for name, body in (("eo_join", "#!/bin/sh\necho one\n"),
                       ("eo_init", "#!/bin/sh\necho two\n")):
        with open(os.path.join(tmp, "eo_cmd", name), "w") as handle:
            handle.write(body)
    manifest = {"commands": [{"name": "eo_join", "what": "join"},
                             {"name": "eo_init", "what": "start"}]}
    with open(os.path.join(tmp, "eo_cmd", "commands.json"), "w") as handle:
        json.dump(manifest, handle)
    return os.path.join(tmp, "bin")


def test_install():
    print("installing")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)

        out = run(tmp, "--prefix", prefix, "--dry-run")
        ok("a dry run counts what it would do", "would install 2" in out.stdout)
        ok("a dry run names the verb per row", "cp " in out.stdout)
        ok("a dry run names the operation and both paths",
           f"cp eo_cmd/eo_join  {os.path.join(prefix, 'eo_join')}" in out.stdout)
        ok("a dry run says it is a copy and not a move",
           "a copy, not a move" in out.stdout)
        ok("a dry run says nothing was written",
           "nothing was written" in out.stdout)
        ok("a dry run creates nothing", not os.path.exists(prefix))

        out = run(tmp, "--prefix", prefix)
        check("installing returns 0", out.returncode, 0)
        ok("the first command is there", os.path.exists(os.path.join(prefix, "eo_join")))
        ok("the second command is there", os.path.exists(os.path.join(prefix, "eo_init")))
        ok("what is installed is executable",
           os.access(os.path.join(prefix, "eo_join"), os.X_OK))
        ok("the directory is remembered",
           json.load(open(os.path.join(tmp, "install_eo_cmd.local.json")))["prefix"]
           == prefix)

        out = run(tmp)
        ok("a second run needs no --prefix", "2 already current" in out.stdout)
        check("a second run returns 0", out.returncode, 0)

        out = run(tmp, "--status")
        ok("status says current", out.stdout.count("current") >= 2)

        # Somebody else's file, under a name we install.
        with open(os.path.join(prefix, "eo_join"), "w") as handle:
            handle.write("#!/bin/sh\necho theirs\n")
        out = run(tmp)
        ok("a file we did not install is skipped", "1 skipped" in out.stdout)
        # The reason sits in the plan beside the file it applies to, rather
        # than on stderr away from the row it explains.
        ok("and the skip is explained in the plan",
           "exists and is not ours" in out.stdout)
        ok("and every command is listed, not only the changed ones",
           out.stdout.count("eo_join") >= 1 and out.stdout.count("eo_init") >= 1)
        check("and the run reports it", out.returncode, 1)
        check("and the file is untouched",
              open(os.path.join(prefix, "eo_join")).read(), "#!/bin/sh\necho theirs\n")

        out = run(tmp, "--status")
        ok("status names it as not ours", "not ours" in out.stdout)

        out = run(tmp, "--force")
        check("--force replaces it", out.returncode, 0)
        check("and the file is ours again",
              open(os.path.join(prefix, "eo_join")).read(), "#!/bin/sh\necho one\n")
    finally:
        shutil.rmtree(tmp)


def test_a_dry_run_with_nothing_to_do_still_says_what_it_would_do():
    """The run somebody makes to find out what the command does.

    Listing only what would change meant that on an up-to-date machine a dry
    run printed a count and nothing else -- least informative exactly when it
    was most likely to be asked.
    """
    print("a dry run with nothing to do")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)
        run(tmp, "--prefix", prefix)
        out = run(tmp, "--dry-run")
        ok("it reports nothing to install", "would install 0" in out.stdout)
        ok("and still lists every command", out.stdout.count("skip ") == 2)
        ok("saying why each is skipped", "already current" in out.stdout)
        ok("and naming both paths",
           os.path.join(prefix, "eo_join") in out.stdout)
    finally:
        shutil.rmtree(tmp)


def test_uninstall():
    print("uninstalling")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)
        run(tmp, "--prefix", prefix)

        # One of the two has been edited by the person since.
        with open(os.path.join(prefix, "eo_init"), "w") as handle:
            handle.write("#!/bin/sh\necho mine now\n")

        out = run(tmp, "--uninstall", "--dry-run")
        ok("a dry uninstall names the rm and the path",
           f"rm {os.path.join(prefix, 'eo_join')}" in out.stdout)
        ok("and removes nothing", os.path.exists(os.path.join(prefix, "eo_join")))

        out = run(tmp, "--uninstall")
        ok("what we installed is removed",
           not os.path.exists(os.path.join(prefix, "eo_join")))
        ok("what changed under us is left alone",
           os.path.exists(os.path.join(prefix, "eo_init")))
        ok("and the run says so", "left alone" in out.stdout)
        check("and it did not rewrite their file",
              open(os.path.join(prefix, "eo_init")).read(), "#!/bin/sh\necho mine now\n")
    finally:
        shutil.rmtree(tmp)


def president(tmp, entries, commit=True, edit_after=False):
    """A git repository holding the register, standing in for the president."""
    root = os.path.join(tmp, "kanon")
    os.makedirs(os.path.join(root, "scripts", "ecosystem"))
    path = os.path.join(root, inst.REGISTER)
    with open(path, "w") as handle:
        json.dump(entries, handle)
    run = lambda *a: subprocess.run(["git", "-C", root, *a], capture_output=True)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@example.invalid")
    run("config", "user.name", "t")
    if commit:
        run("add", "-A")
        run("commit", "-qm", "the register")
    if edit_after:
        with open(path, "w") as handle:
            json.dump({**entries, "late": {"status": "member"}}, handle)
    return root


def test_the_register_is_baked_in():
    """An installed command carries the register, and says it is a snapshot.

    The point is usability away from the president's tree without the lie that
    would otherwise come with it. What is baked in is what the register said at
    a moment, so the moment travels with it.
    """
    print("baking the register into an installed command")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)
        office = president(tmp, {"a": {"status": "member", "url": "u"}})

        # only a command that asks for it gets it
        manifest = os.path.join(tmp, "eo_cmd", "commands.json")
        data = json.load(open(manifest))
        data["commands"][0]["needs"] = "register"
        json.dump(data, open(manifest, "w"))
        with open(os.path.join(tmp, "eo_cmd", "eo_join"), "w") as handle:
            handle.write("#!/usr/bin/env python3\nEMBEDDED = None\n"
                         'EMBEDDED_FROM = ""\nprint(EMBEDDED, EMBEDDED_FROM)\n')

        out = run(tmp, "--prefix", prefix, "--president", office)
        check("installing returns 0", out.returncode, 0)
        ok("the plan says the register was baked in",
           "register baked in" in out.stdout)

        installed = open(os.path.join(prefix, "eo_join")).read()
        ok("the data is in the installed file",
           "'status': 'member'" in installed)
        ok("and it is grouped rather than dumped", "# -- member --" in installed)
        ok("and the source is untouched",
           "EMBEDDED = None" in open(os.path.join(tmp, "eo_cmd", "eo_join")).read())
        ok("the provenance names the tree", "from kanon" in installed)
        ok("and the date", "2026-" in installed or "20" in installed)

        # the command that did not ask for it gets nothing
        other = open(os.path.join(prefix, "eo_init")).read()
        ok("a command that did not ask carries no register",
           "status" not in other)
    finally:
        shutil.rmtree(tmp)


def test_a_snapshot_says_when_it_came_from_a_dirty_tree():
    """A snapshot from a half-edited working tree is a different fact.

    Baking one in is fine -- that is often exactly what somebody wants while
    they are working -- but a reader who later wonders why the numbers disagree
    with the register is owed the reason, and `at <commit>` alone would not
    give it.
    """
    print("a snapshot from an edited register")
    tmp = tempfile.mkdtemp()
    try:
        office = president(tmp, {"a": {"status": "member"}}, edit_after=True)
        _, where = inst.snapshot(office)
        ok("it says the register was edited", "edited and not committed" in where)
        ok("and still names the commit", " at " in where)
    finally:
        shutil.rmtree(tmp)


def test_no_president_is_a_warning_not_a_failure():
    print("installing with no president to read")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)
        manifest = os.path.join(tmp, "eo_cmd", "commands.json")
        data = json.load(open(manifest))
        data["commands"][0]["needs"] = "register"
        json.dump(data, open(manifest, "w"))
        os.environ["KANON"] = os.path.join(tmp, "nowhere")
        try:
            out = run(tmp, "--prefix", prefix)
        finally:
            del os.environ["KANON"]
        check("it still installs", out.returncode, 0)
        ok("and says what the commands will and will not do",
           "work only where the register is" in out.stderr)
    finally:
        shutil.rmtree(tmp)


def test_the_snapshot_is_readable_python():
    """What is baked in is source somebody can read, and it round-trips.

    A command carrying the register is a file people open. A single line of
    JSON in the middle of one cannot be checked against anything by eye, which
    would waste the provenance line printed beside it.
    """
    print("the shape of what is baked in")
    data = {
        "kanon": {"status": "president", "url": "u1", "short": "the office",
                  "vetted": "2026-01-01", "why": "reasons nobody else needs"},
        "anoieu": {"status": "member", "url": "u2", "what": "the checker"},
        "kid": {"status": "child", "parent": "kanon", "short": "a child"},
        "odd": {"status": "brand-new-footing", "url": "u3"},
        "prose": ["not an entry"],
    }
    text = inst.as_source(data, "from kanon at abc1234, on 2026-09-17")

    ok("it is grouped by footing", "# -- president --" in text)
    ok("and says where it came from", "from kanon at abc1234" in text)
    ok("one entry per line", text.count("'status':") == 4)
    ok("a footing it does not know is kept, and flagged",
       "did not know" in text and "'odd'" in text)
    ok("prose is left out", "not an entry" not in text)
    ok("the office's own reasoning is left out",
       "vetted" not in text and "reasons nobody else needs" not in text)

    scope = {}
    exec(compile(text, "<embedded>", "exec"), scope)
    got = scope["EMBEDDED"]
    check("it round-trips to the entries a command reads",
          sorted(got), ["anoieu", "kanon", "kid", "odd"])
    check("with the footing intact", got["anoieu"]["status"], "member")
    check("and `what` normalised to the field the readers use",
          got["anoieu"]["short"], "the checker")
    check("a child keeps its parent", got["kid"]["parent"], "kanon")


def test_init_clone_is_not_a_command_it_installs():
    """Cloning the ecosystem lives here, not in an installed command.

    A command for it would have to be installed by this script first, so
    putting the ecosystem on a machine would depend on having already set up
    the thing that puts the ecosystem on a machine. It belongs where somebody
    already is.
    """
    print("--init-clone")
    tmp = tempfile.mkdtemp()
    try:
        sandbox(tmp)
        office = president(tmp, {
            "a": {"status": "member", "url": "https://example.invalid/a"},
            "kid": {"status": "child", "parent": "a"},
            "them": {"status": "outsider", "url": "https://example.invalid/them"},
            "here": {"status": "member", "url": "https://example.invalid/here"},
        })
        into = os.path.join(tmp, "eo")
        os.makedirs(os.path.join(into, "here"))

        out = run(tmp, "--init-clone", into, "--president", office, "--dry-run")
        check("a dry run returns 0", out.returncode, 0)
        ok("it names the clone command", "git clone https://example.invalid/a" in out.stdout)
        ok("a child is never cloned", "kid" not in out.stdout)
        ok("an outsider is never cloned", "them" not in out.stdout)
        ok("a directory already there is left alone",
           "here: already there, left alone" in out.stdout)
        ok("and it says where the register came from", "from kanon" in out.stdout)
        ok("nothing was cloned", not os.path.exists(os.path.join(into, "a")))

        ok("no command called eo_install is installed",
           not any(c["name"] == "eo_install"
                   for c in json.load(open(os.path.join(ROOT, "eo_cmd",
                                                        "commands.json")))["commands"]))
    finally:
        shutil.rmtree(tmp)


def test_init_clone_refuses_without_a_register():
    print("--init-clone with no register to read")
    tmp = tempfile.mkdtemp()
    try:
        sandbox(tmp)
        os.environ["KANON"] = os.path.join(tmp, "nowhere")
        try:
            out = run(tmp, "--init-clone", os.path.join(tmp, "eo"))
        finally:
            del os.environ["KANON"]
        check("it refuses", out.returncode, 2)
        ok("and says the register is what names who to clone",
           "register" in out.stderr)
    finally:
        shutil.rmtree(tmp)


def test_an_orphan_is_noticed():
    """A command dropped from the manifest leaves a file behind.

    Dropping it stops it being installed; it does not remove the copy already
    on somebody's path, which then goes stale forever with nothing pointing at
    it. That happened to `eo_install` on 2026-09-17 and nothing said so.
    """
    print("a command that is no longer offered")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)
        run(tmp, "--prefix", prefix)

        manifest = os.path.join(tmp, "eo_cmd", "commands.json")
        data = json.load(open(manifest))
        dropped = data["commands"].pop()["name"]
        json.dump(data, open(manifest, "w"))

        out = run(tmp, "--status")
        ok("status names it as orphaned",
           f"{dropped}" in out.stdout and "orphaned" in out.stdout)
        ok("and says it can be removed", "--uninstall removes it" in out.stdout)
        ok("the file is still there",
           os.path.exists(os.path.join(prefix, dropped)))

        run(tmp, "--uninstall")
        ok("and --uninstall takes it", not os.path.exists(os.path.join(prefix, dropped)))
    finally:
        shutil.rmtree(tmp)


def test_help_answers_why_and_not_only_what():
    """--help has to say why somebody would run this, not just what it accepts.

    An option list cannot answer it. `--prefix DIR  install here` tells a reader
    who does not already know what `eo_cmd/` is that something gets installed
    somewhere, which is the part they could guess. The two reasons are that
    these commands are written to run inside *somebody else's* repository and so
    are useless in a checkout, and that the ecosystem is a set of sibling
    checkouts somebody has to get onto the disk first.

    The second was invisible from the option list, which listed `--init-clone`
    among seven flags and nowhere said that cloning is half of what this is for.
    """
    print("--help says why, not only what")
    out = subprocess.run([sys.executable, SCRIPT, "--help"],
                         capture_output=True, text=True)
    check("--help exits 0", out.returncode, 0)
    ok("and writes to stdout", len(out.stdout.strip()) > 400)
    flat = " ".join(out.stdout.split())
    ok("it names the ecosystem", "Eunoia ecosystem" in flat)
    ok("it says the commands run in somebody else's repository",
       "INSIDE somebody else's repository" in flat)
    ok("it says what a PATH is for here", "onto a PATH" in flat)
    ok("it names the other job, which the option list hid",
       "the repositories, onto the disk" in flat)
    ok("and says cloning installs nothing", "installs no commands" in flat)
    ok("it gives examples", "examples:" in out.stdout)


def main():
    for test in (test_install, test_the_register_is_baked_in,
                 test_help_answers_why_and_not_only_what,
                 test_init_clone_is_not_a_command_it_installs,
                 test_init_clone_refuses_without_a_register,
                 test_an_orphan_is_noticed,
                 test_the_snapshot_is_readable_python,
                 test_a_snapshot_says_when_it_came_from_a_dirty_tree,
                 test_no_president_is_a_warning_not_a_failure,
                 test_a_dry_run_with_nothing_to_do_still_says_what_it_would_do,
                 test_uninstall):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
