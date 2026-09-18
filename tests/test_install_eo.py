#!/usr/bin/env python3
"""The installer, against directories made and removed in a temporary place.

    python3 tests/test_install_eo.py

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
SCRIPT = os.path.join(ROOT, "scripts", "install_eo")

_spec = importlib.util.spec_from_loader(
    "install_eo",
    importlib.machinery.SourceFileLoader("install_eo", SCRIPT))
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


def flat(text):
    """One line, so an assertion is about the words and not where they wrap.

    Messages are wrapped to the width of a terminal, so where one breaks is a
    property of how long it is rather than of what it says. A test that asserts
    on the wrapped text fails the day somebody makes a sentence one word
    longer, which teaches the next person to stop writing sentences.
    """
    return " ".join(text.split())


def run(tmp, *args, env=None):
    """The script, against a checkout copied into a temporary directory."""
    environ = dict(os.environ)
    environ["PATH"] = environ.get("PATH", "")
    if env:
        environ.update(env)
    return subprocess.run(
        [sys.executable, os.path.join(tmp, "scripts", "install_eo"), *args],
        capture_output=True, text=True, env=environ)


def sandbox(tmp):
    """A koine checkout with two commands in its store, and nothing installed."""
    os.makedirs(os.path.join(tmp, "scripts"))
    os.makedirs(os.path.join(tmp, "eo_cmd"))
    shutil.copyfile(SCRIPT, os.path.join(tmp, "scripts", "install_eo"))
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
        ok("a dry run counts what it would do", "2 installed" in out.stdout)
        ok("and says up front that it will write nothing",
           "dry run: nothing will be written" in flat(out.stdout))
        # The directory is named once, in the sentence every count is about,
        # and each row then says only what differs: which command, and where
        # its file comes from. Repeating the destination on every row made the
        # longest string on the page the one that never changed.
        ok("a dry run names the directory once", prefix in out.stdout)
        ok("and names each command and where its file comes from",
           "install" in out.stdout and "eo_join" in out.stdout
           and "from eo_cmd/eo_join" in out.stdout)
        ok("a dry run says it is a copy and not a move",
           "a copy, not a move" in out.stdout)
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
        ok("a second run needs no --prefix",
           "2 already up to date" in flat(out.stdout))
        check("a second run returns 0", out.returncode, 0)
        ok("and does not print the file-by-file table unasked",
           "file by file" not in out.stdout)
        ok("--verbose asks for it", "file by file" in run(tmp, "--verbose").stdout)

        out = run(tmp, "--status")
        ok("status says current", out.stdout.count("current") >= 2)

        # Somebody else's file, under a name we install.
        with open(os.path.join(prefix, "eo_join"), "w") as handle:
            handle.write("#!/bin/sh\necho theirs\n")
        out = run(tmp)
        ok("a file we did not install is left alone",
           "1 left alone" in flat(out.stdout))
        # Not a word in a column for the reader to interpret: a sentence
        # naming the file, saying why it was not touched, and saying what to
        # do about it.
        ok("and the run says which file, and why",
           "eo_join was left alone" in flat(out.stdout)
           and "did not put it there" in flat(out.stdout))
        ok("and says what replaces it", "--force" in out.stdout)
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
        ok("it reports nothing to do",
           "2 already up to date" in flat(out.stdout))
        ok("and still lists every command",
           out.stdout.count("up to date  ") == 2)
        ok("and still says what each command is for",
           "eo_join" in out.stdout and "join" in out.stdout)
        ok("and names the directory it is talking about", prefix in out.stdout)
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
        # Which register a command carries is not a detail of the copy: it
        # is the difference between an answer about today's ecosystem and an
        # answer about a snapshot, so a plain run says it.
        ok("the run says which register the command now carries",
           "carries a snapshot of the register" in flat(out.stdout)
           and "from kanon" in flat(out.stdout))

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
        ok("and names the command it is about",
           "eo_join will install without a register snapshot"
           in flat(out.stderr))
        ok("and says what that command will and will not do",
           "work only in the tree that holds the register" in flat(out.stderr))
        # The warning is about one command; the run is about a directory, and
        # said so with a variable the warning had quietly taken over.
        ok("and the run still says where it installed",
           f"Installing Eunoia ecosystem scripts into {prefix}"
           in flat(out.stdout))
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
        ok("it names the clone command",
           "git clone https://example.invalid/a" in flat(out.stdout))
        ok("a child is never cloned", "kid" not in out.stdout)
        ok("an outsider is never cloned", "them" not in out.stdout)
        # One sentence naming them, not one line each: the same sentence
        # repeated per repository is a wall a reader skips.
        ok("a directory already there is left alone",
           "here is already there and left alone" in flat(out.stdout))
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


def test_a_named_president_is_used_or_refused_never_replaced():
    """Naming a tree with no register does not silently read a different one.

    `--president` and `KANON` are somebody saying *read the register there*.
    Falling through to a sibling of the checkout answers a question nobody
    asked, with a register whose age the run has no reason to trust -- and for
    `--init-clone`, which clones whatever the register names, the blast radius
    is a disk full of repositories nobody asked for. This test builds the
    fallback on purpose, in the sandbox, and checks it is not taken.
    """
    print("a president somebody named")
    tmp = tempfile.mkdtemp()
    try:
        # scripts/install_eo one level down, so the sibling the unnamed
        # case would look at -- `<parent of the checkout>/kanon` -- is inside
        # the sandbox and can be made to exist.
        checkout = os.path.join(tmp, "checkout")
        os.makedirs(checkout)
        prefix = sandbox(checkout)
        fallback = os.path.join(tmp, "kanon")
        os.makedirs(os.path.join(fallback, "scripts", "ecosystem"))
        with open(os.path.join(fallback, "scripts", "ecosystem",
                               "ecosystem.json"), "w") as handle:
            json.dump({"a": {"status": "member", "url": "https://example/a"}},
                      handle)

        ok("the fallback is there to be taken",
           run(checkout, "--init-clone", os.path.join(tmp, "eo"), "--dry-run")
           .returncode == 0)

        out = run(checkout, "--init-clone", os.path.join(tmp, "eo"),
                  "--president", os.path.join(tmp, "nowhere"))
        check("a named tree with no register refuses", out.returncode, 2)
        ok("and the refusal names the tree that was named",
           os.path.join(tmp, "nowhere") in out.stderr)
        ok("and nothing was cloned from the tree nobody named",
           not os.path.exists(os.path.join(tmp, "eo")))

        manifest = os.path.join(checkout, "eo_cmd", "commands.json")
        data = json.load(open(manifest))
        data["commands"][0]["needs"] = "register"
        json.dump(data, open(manifest, "w"))

        out = run(checkout, "--prefix", prefix, "--dry-run",
                  env={"KANON": os.path.join(tmp, "nowhere")})
        check("KANON is read the same way", out.returncode, 0)
        ok("and the fallback register is not baked in behind somebody's back",
           "work only in the tree that holds the register" in flat(out.stderr))
        ok("and the warning names the tree that was named",
           os.path.join(tmp, "nowhere") in out.stderr)
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


def test_a_finished_install_ends_by_saying_what_to_type():
    """The last thing printed is addressed to the person, not to the record.

    A run used to end on its own bookkeeping -- what was copied to which path,
    which config remembered the directory, how a copy is made atomically -- and
    the one thing a person wanted, the list of commands they now have, sat in
    the middle of it. So the run opens by saying what it is doing and where,
    and ends on the roster under a sentence saying they are ready.

    **It says ready whether or not this shell can see the directory.** The
    default is `~/bin`, which a login shell puts on PATH on every system these
    commands are meant for, so a run that withheld *ready* and explained PATH
    instead was interrupting almost everybody to fix almost nobody. The
    directory that cannot be seen gets one line, not a lecture -- and a run
    from cron or a Makefile has a PATH that says nothing about the one the
    person types in, so it is advice and never a verdict.

    A dry run is the one that does not say it: it wrote nothing, so there is
    nothing to be ready with.
    """
    print("a finished install says what to type")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)

        out = run(tmp, "--prefix", prefix, "--dry-run")
        ok("it opens by saying what it is doing and where",
           f"Installing Eunoia ecosystem scripts into {prefix}"
           in flat(out.stdout))
        ok("a dry run does not claim they are ready",
           "now ready" not in flat(out.stdout))
        ok("and still says what each command is for",
           "A real run would put these on your PATH" in flat(out.stdout)
           and "eo_join" in out.stdout)

        out = run(tmp, "--prefix", prefix)
        ok("an install says they are ready",
           "You are now ready to use the Eunoia ecosystem" in flat(out.stdout))
        ok("and offers the commands as a quick start",
           "For quick start, try these:" in flat(out.stdout))
        # One line, and the line that fixes it, rather than a paragraph about
        # shell startup files: this shell is not the shell they will use.
        ok("a directory this shell cannot see gets one quiet line",
           f'ensure that {prefix} is in your PATH: export PATH="{prefix}'
           in flat(out.stdout))
        ok("and it is one line, not a block",
           flat(out.stdout).count("in your PATH") == 1)

        out = run(tmp, env={"PATH": prefix + os.pathsep + os.environ["PATH"]})
        ok("a directory this shell can see is not mentioned at all",
           "PATH" not in out.stdout)
        ok("naming every command",
           "eo_join" in out.stdout and "eo_init" in out.stdout)
        ok("and saying where they are run, and where to read more",
           "root of the repository" in flat(out.stdout)
           and "takes --help" in flat(out.stdout))
        ok("the roster is the last thing printed, after what the run did",
           out.stdout.index("now ready")
           > out.stdout.index("Installing Eunoia ecosystem scripts"))
    finally:
        shutil.rmtree(tmp)


def test_the_roster_is_stratified_by_who_runs_it():
    """A command for machinery is listed below the line, not among the rest.

    `koine_append_db` is on somebody's PATH because another tool's CI or an
    agent has to be able to call it, and the person who has just installed the
    ecosystem has no occasion to type it. Listing it among the commands they
    are being told to try implied they would; leaving it out would hide a name
    that is on their machine. So it is listed, under a sentence saying a human
    can ignore it, and the manifest is what says which is which.
    """
    print("the roster is stratified by who runs it")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)
        manifest = os.path.join(tmp, "eo_cmd", "commands.json")
        data = json.load(open(manifest))
        data["commands"][1]["audience"] = "tooling"
        json.dump(data, open(manifest, "w"))

        out = run(tmp, "--prefix", prefix,
                  env={"PATH": prefix + os.pathsep + os.environ["PATH"]})
        ok("the machinery is still installed",
           os.path.exists(os.path.join(prefix, "eo_init")))
        ok("and still listed", "eo_init" in out.stdout)
        ok("and a human is told they can ignore it",
           "you can ignore it if you are a human" in flat(out.stdout))
        ok("it comes after the commands that are for them",
           out.stdout.index("eo_init") > out.stdout.index("eo_join"))
        ok("and after the line closing off their list",
           out.stdout.index("eo_init")
           > out.stdout.index("root of the repository"))
    finally:
        shutil.rmtree(tmp)


def test_one_sentence_however_many_files_it_is_about():
    """A message repeated once per file is a wall, and a reader skips walls.

    Uninstalling a directory somebody had edited printed the same sentence nine
    times, once per file, differing only in the name at the front. The names
    belong in one sentence.
    """
    print("one sentence, however many files")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)
        run(tmp, "--prefix", prefix)
        for name in ("eo_join", "eo_init"):
            with open(os.path.join(prefix, name), "w") as handle:
                handle.write("#!/bin/sh\necho mine now\n")

        out = run(tmp)
        ok("install says it once, naming both",
           flat(out.stdout).count("were left alone") == 1
           and "eo_join and eo_init were left alone" in flat(out.stdout))

        out = run(tmp, "--uninstall")
        ok("uninstall says it once, naming both",
           flat(out.stderr).count("were left alone") == 1
           and "eo_join and eo_init were left alone" in flat(out.stderr))
        ok("and the count is on the run's own line",
           "2 left alone" in flat(out.stdout))
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
                 test_a_finished_install_ends_by_saying_what_to_type,
                 test_one_sentence_however_many_files_it_is_about,
                 test_the_roster_is_stratified_by_who_runs_it,
                 test_help_answers_why_and_not_only_what,
                 test_init_clone_is_not_a_command_it_installs,
                 test_init_clone_refuses_without_a_register,
                 test_a_named_president_is_used_or_refused_never_replaced,
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
