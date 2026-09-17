#!/usr/bin/env python3
"""The commands themselves: every form runs, and says what it should.

    python3 tests/test_eo_cmd.py

koine took these over from kanon on 2026-09-17 under role `R35`, which makes
their text and their options this repository's to maintain — so they are tested
here rather than assumed. Nothing below launches an assistant: every form takes
`--show-prompt`, which prints what it would hand one and does nothing else.

What is checked is what a mistake here would cost. A prompt is read by somebody
outside this ecosystem, in their own repository, so a form that prints nothing,
names a command that does not exist, or points at a page that moved is a defect
that reaches a stranger. The last is why the links are extracted and looked at
rather than trusted.
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(ROOT, "eo_cmd")

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


def show(command, *args):
    """What this form would hand an assistant."""
    return subprocess.run([os.path.join(STORE, command), *args, "--show-prompt"],
                          capture_output=True, text=True)


def manifest():
    return json.load(open(os.path.join(STORE, "commands.json")))


def forms(kind="prompt"):
    """Every form the manifest advertises for commands of this kind."""
    for entry in manifest()["commands"]:
        if entry.get("kind") != kind:
            continue
        for form in entry["forms"]:
            parts = form.split()
            yield entry["name"], parts[0], parts[1:]


def test_every_advertised_form_runs():
    print("every form the manifest advertises")
    for name, command, args in forms():
        # `from-child` needs a directory that exists; any tree will do, and it
        # is read rather than written even when the command is not previewing.
        args = [a if a != "<path>" else ROOT for a in args]
        out = show(command, *args)
        label = " ".join([command, *args]) if args else command
        check(f"{label} exits 0", out.returncode, 0)
        ok(f"{label} prints a prompt", len(out.stdout.strip()) > 200)
        check(f"{label} is the command named", command, name)


def test_refusals():
    print("forms that contradict each other")
    both = subprocess.run([os.path.join(STORE, "eo_join"), "--associate", "--soft"],
                          capture_output=True, text=True)
    check("--associate with --soft is refused", both.returncode, 2)
    ok("and says why", "claims nothing" in both.stderr)

    bare = subprocess.run([os.path.join(STORE, "eo_join"), "--affiliated"],
                          capture_output=True, text=True)
    check("--affiliated without --soft is refused", bare.returncode, 2)

    mode = subprocess.run([os.path.join(STORE, "eo_init")],
                          capture_output=True, text=True)
    check("eo_init with no mode is refused", mode.returncode, 2)


def test_no_prompt_names_a_command_that_is_gone():
    """These were kanon's `join_eo` and `init_eo` until 2026-09-17.

    A prompt still naming the old command, or linking to where it used to live,
    tells a stranger to run something that exists nowhere -- and the soft form's
    text is written *into their README*, so the bad name outlives the run.
    """
    print("no prompt names a command or page that moved")
    for name, command, args in forms():
        args = [a if a != "<path>" else ROOT for a in args]
        text = show(command, *args).stdout
        label = " ".join([command, *args]) if args else command
        ok(f"{label} does not say join_eo", not re.search(r"\bjoin_eo\b", text))
        ok(f"{label} does not say init_eo", not re.search(r"\binit_eo\b", text))
        ok(f"{label} links to no kanon prompts/ page",
           "kanon/blob/main/prompts/" not in text)


def test_associate_says_what_the_footing_needs():
    """The `associate` footing, as the policy page defines it.

    The two halves are both load-bearing and the second is the one a reader
    gets wrong: an associate holds *itself* to the policy and owes this
    ecosystem nothing. A prompt that said only the first would produce a
    quieter member, which is the reading the footings table exists to refuse.
    """
    print("the associate form")
    text = show("eo_join", "--associate").stdout
    ok("names the footing", "`associate`" in text)
    ok("puts it on the maintenance page", "docs/maintenance.md" in text)
    ok("says the repository holds itself to the policy", "holds itself to" in text)
    ok("names the policy", "polic" in text.lower())
    ok("says the ecosystem is owed nothing", "owes that ecosystem nothing" in text)
    ok("says a failure is nobody's fault", "nobody's fault" in text)
    ok("distinguishes measurement from shortfall", "measurement" in text)
    ok("asks for the reason, which the checker requires", "reason" in text.lower())
    ok("forbids a README declaration",
       "add no membership declaration" in text.lower())
    ok("sends a tree held to none of this to --soft", "eo_join --soft" in text)
    ok("cites the office's page as the authority",
       "kanon/blob/main/docs/policy.md" in text)


def test_the_dictated_marker_passes_the_checker():
    """The marker this prompt dictates, read by the program that reads it.

    The prompt spells out a `**Footing:**` line for an assistant to copy. That
    line is checked by anoieu's `associate_in`, which requires an obligation
    named, the policy named, and no refusal of it -- three conditions a
    plausible-sounding sentence can miss. Testing the prompt's own example
    against the real checker is the only thing that keeps the two in step.

    Skipped where anoieu is not beside this checkout: a test that needs
    somebody else's tree to pass is a test that fails for reasons that are not
    about this repository.
    """
    print("the marker the prompt dictates")
    checker = os.path.join(os.path.dirname(ROOT), "anoieu", "scripts",
                           "policy_check.py")
    if not os.path.exists(checker):
        print("  --   no anoieu checkout beside this one; skipped")
        return

    import importlib.machinery
    import importlib.util
    spec = importlib.util.spec_from_loader(
        "policy_check", importlib.machinery.SourceFileLoader("policy_check", checker))
    pc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pc)

    text = show("eo_join", "--associate").stdout
    # The indented block the prompt tells an assistant to write.
    block = re.search(r"\n((?:       \S.*\n)+)", text)
    ok("the prompt spells out a marker", block is not None)
    if not block:
        return
    marker = "\n".join(line.strip() for line in block.group(1).splitlines())
    marker += "\nIt is not on the front page because this is one person's tree."
    problems = pc.associate_in(marker)
    check("the dictated marker satisfies associate_in", problems, [])


def test_help_says_why_and_where():
    """--help has to answer *what is this* and *where do I stand*, on stdout.

    These land on the PATH of somebody who did not install them and may not
    know what `eo` stands for. Two details matter beyond the wording: an
    explicit --help is a request rather than a mistake, so it belongs on
    stdout with an exit of 0 -- until 2026-09-17 the shell commands wrote it
    all to stderr and exited 2, which meant `eo_join --help | less` printed
    nothing at all.
    """
    print("--help answers the two questions, on stdout")
    for entry in manifest()["commands"]:
        name = entry["name"]
        if not name.startswith("eo_"):
            continue
        path = os.path.join(ROOT, entry.get("path") or os.path.join("eo_cmd", name))
        out = subprocess.run([path, "--help"], capture_output=True, text=True)
        check(f"{name} --help exits 0", out.returncode, 0)
        ok(f"{name} --help writes to stdout", len(out.stdout.strip()) > 200)
        ok(f"{name} names the ecosystem", "Eunoia ecosystem" in out.stdout)
        ok(f"{name} says where to run it", "Run it at the root" in out.stdout)
        head = [line for line in out.stdout.splitlines()[:4] if line.strip()]
        ok(f"{name} says what it is for at the top",
           any(line.startswith(f"{name} -- ") for line in head))

        bad = subprocess.run([path, "--definitely-not-a-flag"],
                             capture_output=True, text=True)
        check(f"{name} rejects a bad flag with 2", bad.returncode, 2)
        ok(f"{name} sends that to stderr", bad.stdout.strip() == "")


def main():
    for test in (test_every_advertised_form_runs, test_refusals,
                 test_no_prompt_names_a_command_that_is_gone,
                 test_associate_says_what_the_footing_needs,
                 test_the_dictated_marker_passes_the_checker,
                 test_help_says_why_and_where):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
