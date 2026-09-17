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
        ok("and the skip is explained", "did not put it there" in out.stderr)
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


def main():
    for test in (test_install, test_uninstall):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
