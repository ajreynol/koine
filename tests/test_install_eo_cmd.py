#!/usr/bin/env python3
"""The installer, and the property that makes the store trustworthy.

    python3 tests/test_install_eo_cmd.py

Two things are worth testing here and they are not the same thing.

The first is the **copy transform**: that a stored command is its original with
the command's own name changed and nothing else, and in particular that the
prompt text -- the part read by somebody outside this ecosystem -- comes through
byte for byte. That is tested against a fixture built here, so it runs in CI
with no checkout of anybody else's tree.

The second is the **installer**: that it puts files where it is told, that a
second run changes nothing, and that it refuses to overwrite a file of the same
name it did not put there. That is tested against directories made and removed
in a temporary directory.

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


RENAMES = {"join_eo": "eo_join", "init_eo": "eo_init"}

#: A script shaped like the ones this stores: a comment block, a `cat` heredoc
#: holding its own usage, and a `read` heredoc holding the prompt it hands an
#: assistant. The name appears in all three, and only two of them may move.
FIXTURE = """#!/usr/bin/env bash
# join_eo -- do the thing.
#
#   join_eo --show-prompt
#   check_join_eo <id>    # run from kanon
#   init_eo new           # the sibling

usage() {
  cat >&2 <<'USAGE'
usage: join_eo [--soft]
USAGE
  exit 2
}

read -r -d '' PROMPT <<'PROMPT_END' || true
Produced by `join_eo --soft`, a command kept in the kanon repository.

  https://github.com/ajreynol/kanon/blob/main/prompts/join_eo

`join_eo --soft --show-prompt` prints exactly this text.
PROMPT_END

echo "join_eo: $AGENT is not on PATH" >&2
"""


def test_transform():
    print("the copy transform")
    out = inst.transform(FIXTURE, RENAMES)
    lines = out.split("\n")

    check("the header comment is renamed", lines[1], "# eo_join -- do the thing.")
    check("a usage example is renamed", lines[3], "#   eo_join --show-prompt")
    check("check_join_eo is left alone", lines[4],
          "#   check_join_eo <id>    # run from kanon")
    check("the sibling is renamed", lines[5], "#   eo_init new           # the sibling")
    ok("the cat heredoc is renamed", "usage: eo_join [--soft]" in out)
    ok("the error message is renamed",
       'echo "eo_join: $AGENT is not on PATH" >&2' in out)

    prompt = out.split("<<'PROMPT_END' || true\n")[1].split("\nPROMPT_END")[0]
    original = FIXTURE.split("<<'PROMPT_END' || true\n")[1].split("\nPROMPT_END")[0]
    check("the prompt body is byte-identical", prompt, original)
    ok("the prompt still names the original command", "`join_eo --soft`" in prompt)
    ok("the prompt's URL is untouched",
       "kanon/blob/main/prompts/join_eo" in prompt)
    ok("no local alias leaks into the prompt", "eo_join" not in prompt)

    check("applying it twice changes nothing more",
          inst.transform(out, RENAMES), out)


def test_boundaries():
    print("what the rename does and does not match")
    check("a bare name moves", inst.rename("join_eo", RENAMES), "eo_join")
    check("a prefixed name does not",
          inst.rename("check_join_eo", RENAMES), "check_join_eo")
    check("a suffixed name does not",
          inst.rename("join_eot", RENAMES), "join_eot")
    check("a path moves", inst.rename("prompts/join_eo", RENAMES), "prompts/eo_join")


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
    origin = {
        "renames": RENAMES,
        "commands": [
            {"name": "eo_join", "sha256": inst.digest("#!/bin/sh\necho one\n"),
             "source": {"repo": "kanon", "path": "prompts/join_eo"}},
            {"name": "eo_init", "sha256": inst.digest("#!/bin/sh\necho two\n"),
             "source": {"repo": "kanon", "path": "prompts/init_eo"}},
        ],
    }
    with open(os.path.join(tmp, "eo_cmd", "origin.json"), "w") as handle:
        json.dump(origin, handle)
    return os.path.join(tmp, "bin")


def test_install():
    print("installing")
    tmp = tempfile.mkdtemp()
    try:
        prefix = sandbox(tmp)

        out = run(tmp, "--prefix", prefix, "--dry-run")
        ok("a dry run says what it would do", "2 installed" in out.stdout)
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


def test_check():
    print("checking the store")
    tmp = tempfile.mkdtemp()
    try:
        sandbox(tmp)
        out = run(tmp, "--check")
        check("a clean store checks out", out.returncode, 0)

        with open(os.path.join(tmp, "eo_cmd", "eo_join"), "a") as handle:
            handle.write("# edited here\n")
        out = run(tmp, "--check")
        check("an edited copy is caught", out.returncode, 1)
        ok("and the message says where it belongs",
           "a store, not a source" in out.stderr)
    finally:
        shutil.rmtree(tmp)


def test_against_kanon():
    """If a kanon checkout is beside this one, hold the store against it.

    Skipped where it is not -- CI has no kanon checkout, and a test that needs
    somebody else's tree to pass is a test that fails for reasons that are not
    about this repository.
    """
    print("against the originals, if they are here")
    kanon = os.path.join(os.path.dirname(ROOT), "kanon")
    origin_path = os.path.join(ROOT, "eo_cmd", "origin.json")
    if not os.path.isdir(kanon) or not os.path.exists(origin_path):
        print("  --   no kanon checkout beside this one; skipped")
        return

    origin = json.load(open(origin_path))
    for cmd in origin["commands"]:
        src = os.path.join(kanon, cmd["source"]["path"])
        dest = os.path.join(ROOT, "eo_cmd", cmd["name"])
        if not os.path.exists(src):
            print(f"  --   {cmd['source']['path']} is not in that checkout; skipped")
            continue
        with open(src, encoding="utf-8") as handle:
            expected = inst.transform(handle.read(), origin["renames"])
        with open(dest, encoding="utf-8") as handle:
            stored = handle.read()
        ok(f"{cmd['name']} is {cmd['source']['path']}, renamed and no more",
           stored == expected)


def main():
    for test in (test_transform, test_boundaries, test_install, test_uninstall,
                 test_check, test_against_kanon):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
