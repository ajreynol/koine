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
import shutil
import subprocess
import sys
import tempfile

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


def test_the_readme_table_agrees_with_the_manifest():
    """The manifest is the ground truth; this directory's README carries a copy.

    A register restated somewhere else needs something that runs between the
    two, or the copy is drift that has not happened yet. It had already
    happened once: the README said *every form takes `--show-prompt`* after
    programs arrived that take no such thing. This is the comparison that was
    missing, not a second description.
    """
    print("the README's table against commands.json")
    page = open(os.path.join(STORE, "README.md"), encoding="utf-8").read()
    listed = set(re.findall(r"^\| \[?`(eo_[a-z_]+|koine_[a-z_]+)`",
                            page, re.M))
    named = {c["name"] for c in manifest()["commands"]}
    check("the table names every command the manifest offers",
          sorted(named - listed), [])
    check("and offers nothing the manifest does not",
          sorted(listed - named), [])

    # A command in the directory that nobody put in the manifest installs
    # nowhere and is described nowhere; `eo_install` went that way once.
    here = {f for f in os.listdir(STORE)
            if os.access(os.path.join(STORE, f), os.X_OK)
            and not os.path.isdir(os.path.join(STORE, f))}
    check("every file in this directory is in the manifest",
          sorted(here - named), [])

    # Each one is either written up on this page or lives somewhere that has
    # its own page; a row with neither is a command with no documentation.
    for entry in manifest()["commands"]:
        where = "elsewhere" if entry.get("path") else "here"
        ok(f"{entry['name']} is written up ({where})",
           entry.get("path") or f"\n## {entry['name']}\n" in page)


def test_only_prompts_take_show_prompt():
    """The one behavioural claim the manifest makes about a `kind`."""
    print("what each kind of command answers to")
    for entry in manifest()["commands"]:
        if entry.get("kind") != "program":
            continue
        path = os.path.join(ROOT, entry.get("path")
                            or os.path.join("eo_cmd", entry["name"]))
        out = subprocess.run([path, "--show-prompt"], capture_output=True,
                             text=True)
        ok(f"{entry['name']} is a program and refuses --show-prompt",
           out.returncode != 0)


def test_every_advertised_form_runs():
    print("every form the manifest advertises")
    for name, command, args in forms():
        # `from-child` needs a directory that exists; any tree will do, and it
        # is read rather than written even when the command is not previewing.
        args = [ROOT if a == "<path>" else "kanon" if a == "<name>"
                else "D1" if a == "<Dn>" else a for a in args]
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
        args = [ROOT if a == "<path>" else "kanon" if a == "<name>"
                else "D1" if a == "<Dn>" else a for a in args]
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
    ok("asks for a README with a maintenance section",
       "How this repository is maintained" in text)
    ok("recommends the name explanation without requiring it",
       "Strongly recommended, and not required" in text)
    ok("and says that recommendation may be skipped", "Skip it freely" in text)


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


def test_the_gate_is_in_argv():
    """Naming the topic is what authorises answering it, so argv enforces it.

    The ecosystem's one build-failing rule is that an agent answers a topic only
    where a human instructed it and named which topic. `eo_respond` used to
    implement that by making the unnamed form read-only and asking the prompt
    nicely to behave -- a gate held up by prose the model was trusted to obey.
    It refuses now, before an assistant is reached, which is strictly stronger
    than any wording and is why the read-only form is gone: the survey it did is
    `eo_housekeeping`, which sweeps every checkout and costs no turn per tool.
    """
    print("the discussion gate, in argv")
    bare = subprocess.run([os.path.join(STORE, "eo_respond"), "kanon"],
                          capture_output=True, text=True)
    check("a run with no topic is refused", bare.returncode, 2)
    ok("and says naming it is the authorisation",
       "what authorises" in bare.stderr)
    ok("and sends the survey to the command that does it",
       "eo_housekeeping" in bare.stderr)
    ok("and refuses on stderr, printing no prompt", bare.stdout.strip() == "")

    worked = " ".join(show("eo_respond", "kanon", "D14").stdout.split())
    ok("naming a topic authorises that topic",
       "work D14 and no other" in worked)
    ok("and requires the two accounts to agree", "If they disagree" in worked)
    ok("and forbids the smaller safe part", "smaller safe part" in worked)
    ok("it names the repository it is run from, not a fixed one",
       "correspondence in **koine**" in worked)
    ok("the reply is drafted where an uncommitted document goes",
       "discussion-response.local.md" in worked)
    ok("and nothing is sent", "send nothing anywhere" in worked)
    ok("it stays short enough to be read", len(worked.split()) < 500)


def test_housekeeping_points_at_the_standard_rather_than_restating_it():
    """The design of this command, which a rewrite could quietly undo.

    An earlier version paraphrased the shared policy into five areas and
    shipped the paraphrase at 1,749 words. That is a copy of somebody else's
    rules, installed on a stranger's PATH, with nothing keeping it current --
    the failure the policy's own *Copies* section is about, in the one command
    sent to find it. It also narrowed the job to whatever the paraphrase
    happened to name.

    So the first paragraph is checked for being nothing but pointers: the
    president, whose tree holds the standard, the two pages, this repository's
    own, and the checker. The word count is checked because that is how the
    regression actually looks from outside.
    """
    print("housekeeping sends the assistant to the standard")
    for args in ([], ["--report"]):
        label = " ".join(["eo_housekeeping", *args]) or "eo_housekeeping"
        flat = " ".join(show("eo_housekeeping", *args).stdout.split())
        ok(f"{label} says what the ecosystem is", "Eunoia ecosystem" in flat)
        ok(f"{label} names the president in the second sentence",
           re.match(r"[^.]+\.\s*Its \*\*president\*\*", flat) is not None)
        ok(f"{label} sends it to the policy", "policy.md" in flat)
        ok(f"{label} sends it to the vision", "vision.md" in flat)
        ok(f"{label} sends it to this repository's own pages",
           "README.md" in flat and "docs/" in flat)
        ok(f"{label} says it is not restating them",
           "restates none of it" in flat)
        ok(f"{label} names the checker without making it the job",
           "policy checker" in flat)
        # It has been 1,749 words once, which is how a prompt stops being read
        # at all. The number is a ceiling rather than a target.
        ok(f"{label} stays short enough to be read", len(flat.split()) < 500)
        ok(f"{label} is two paragraphs",
           len([p for p in show("eo_housekeeping", *args).stdout.split("\n\n")
                if p.strip()]) == 2)


def test_housekeeping_states_the_goal_and_ends_on_ci():
    """The four things a run is for, and the order the last one comes in.

    The goal is the maintainer's, quoted into the prompt rather than derived:
    documentation made true, topics other tools raised answered, bugs in our
    own tooling fixed, and a topic opened for anything needing somebody else.
    CI is last because it is the check on all of it, and a run that stops
    before it has left the tree in a state nobody verified.
    """
    print("the goal, and CI at the end")
    flat = " ".join(show("eo_housekeeping").stdout.split())
    ok("documentation", "documentation up to date" in flat)
    ok("the topics others raised", "answer the discussion items" in flat)
    ok("bugs in our own tooling", "bugs in our own tooling" in flat)
    ok("a topic for what needs somebody else",
       "opening a topic in `docs/discussion.md`" in flat)
    ok("and CI is the final step",
       flat.rstrip().endswith("**Ensure CI passes here as a final step.**"))

    report = " ".join(show("eo_housekeeping", "--report").stdout.split())
    ok("--report changes nothing", "**Change nothing**" in report)
    ok("and asks after CI rather than for it",
       "say whether CI passes here" in report)


def test_housekeeping_says_the_discussion_gate_is_overridden():
    """The prompt has to say it is overriding, or it does not work at all.

    Every discussion file opens with the ecosystem's one build-failing rule: a
    topic is answered only where a human instructed it and named the topic. A
    command run on a habit names none, so a run of this is an override rather
    than a satisfaction of it -- the maintainer's, recorded in
    `docs/maintenance.md`.

    Saying so in the prompt is not ceremony. An assistant that reads that
    banner without it stops there, correctly, and the command does nothing. So
    what is checked is that the prompt claims the instruction, that the
    narrowings which survive the override survive it, and that the record
    exists where the policy says an override is recorded.
    """
    print("the discussion gate is overridden, and says so")
    for args in ([], ["--report"]):
        label = " ".join(["eo_housekeeping", *args]) or "eo_housekeeping"
        flat = " ".join(show("eo_housekeeping", *args).stdout.split())
        ok(f"{label} claims the human instruction those files require",
           "maintainer instructs the discussion work standing" in flat)
        ok(f"{label} answers only what names us", "only what names us" in flat)
        ok(f"{label} writes in no other tree",
           "no tree but this one" in flat)
        ok(f"{label} sends nothing anywhere", "send nothing anywhere" in flat)

    # The policy's escape hatch has three properties, and the third is that an
    # override is recorded. A prompt that claims one without the record behind
    # it is an agent granting itself permission.
    notes = open(os.path.join(ROOT, "docs", "maintenance.md")).read()
    ok("the override is recorded where standing instructions live",
       "Overridden for `eo_housekeeping`" in notes)
    ok("and says what would have to be true for it not to be needed",
       "not to be needed" in notes)
    ok("and does not extend to the command that keeps the gate",
       "eo_respond" in notes)


def test_the_working_prompts_pull_before_they_work():
    """Both commands judge a tree, so both start by making the tree current.

    Every question housekeeping asks -- is this documentation true, has anybody
    answered this topic, does CI pass -- is asked of a checkout, and a checkout
    that is behind answers all three wrong: work already done reads as
    outstanding, and work done in it comes back to somebody as a merge. The same
    applies to what `eo_respond` stages, which has to apply to what is current.

    So the pull is in the prompt rather than in the shell: an agent that cannot
    fast-forward is told to say so and stop, which a `git pull ||` in front of
    the command could not do. `--report` pulls too -- a report of what is stale,
    computed from a stale checkout, is the defect the command was sent to find --
    so what is checked there is that it still forbids everything else.
    """
    print("the tree is made current before it is judged")
    for command, args in (("eo_housekeeping", []),
                          ("eo_housekeeping", ["--report"]),
                          ("eo_respond", ["kanon", "D14"])):
        label = " ".join([command, *args])
        flat = " ".join(show(command, *args).stdout.split())
        ok(f"{label} opens the work on a pull", "Begin with `git pull`" in flat)
        ok(f"{label} stops rather than resolving somebody else's merge",
           "fast-forward cleanly, say so and stop" in flat)

    report = " ".join(show("eo_housekeeping", "--report").stdout.split())
    ok("--report says the pull is the only change it makes",
       "**Change nothing** beyond that pull" in report)


def test_housekeeping_names_the_president_it_was_told_of():
    """Who holds the office is read, never written in.

    The president's tree is where the policy and the vision are, so the prompt
    has to name it -- and naming one in the text would be a claim about who
    holds an office, going stale the moment it changes, in a file installed on
    somebody else's path. The register says who holds it and the register lives
    in the office's tree, so finding the file is finding the president.

    Skipped where no register is beside this checkout: a test that needs
    somebody else's tree to pass is one that fails for reasons that are not
    about this repository.
    """
    print("the president is looked up, not written in")
    register = os.path.join(os.path.dirname(ROOT), "kanon", "scripts",
                            "ecosystem", "ecosystem.json")
    if not os.path.exists(register):
        print("  --   no register beside this one; skipped")
        return

    data = json.load(open(register))
    holders = [k for k, v in data.items()
               if isinstance(v, dict) and v.get("status") == "president"]
    check("the register names exactly one president", len(holders), 1)
    if not holders:
        return

    text = " ".join(show("eo_housekeeping").stdout.split())
    ok("the prompt names the one the register names",
       f"**{holders[0]}**" in text)

    source = open(os.path.join(STORE, "eo_housekeeping")).read()
    body = source[source.index("read -r -d '' PROMPT"):]
    ok("and the prompt text itself names no president",
       holders[0] not in body)


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
        # The wording differs by command -- "at the root of the repository
        # being declared", "in the repository that holds the register" -- so
        # what is checked is that the question is answered, not one phrasing.
        ok(f"{name} says where to run it",
           re.search(r"\bRun (it|this)\b[^.]*\brepositor", out.stdout) is not None)
        head = [line for line in out.stdout.splitlines()[:4] if line.strip()]
        ok(f"{name} says what it is for at the top",
           any(line.startswith(f"{name} -- ") for line in head))

        bad = subprocess.run([path, "--definitely-not-a-flag"],
                             capture_output=True, text=True)
        check(f"{name} rejects a bad flag with 2", bad.returncode, 2)
        ok(f"{name} sends that to stderr", bad.stdout.strip() == "")


def test_runs_as_an_installed_copy():
    """Every command has to work as a lone file on somebody's PATH.

    `install_eo_cmd` copies one file per command. Anything a command needs from
    beside it in this tree is simply not there once installed, and the failure
    is invisible from inside the repository -- every test passes, and the first
    person to run the installed copy gets a traceback.

    That happened on 2026-09-17: `eo_status` imported a sibling module and, from
    ~/bin, went looking for it one directory up from the bin directory. This
    copies each command somewhere with none of this tree beside it and runs it.
    """
    print("as an installed copy, with none of this tree beside it")
    tmp = tempfile.mkdtemp()
    try:
        for entry in manifest()["commands"]:
            name = entry["name"]
            src = os.path.join(ROOT, entry.get("path") or os.path.join("eo_cmd", name))
            dest = os.path.join(tmp, name)
            shutil.copyfile(src, dest)
            os.chmod(dest, 0o755)
            # --help for everything: it needs no arguments and no git
            # repository, and for a Python command it still runs every line of
            # module scope -- which is where the import of a sibling file that
            # is not installed beside it would blow up.
            out = subprocess.run([dest, "--help"], capture_output=True,
                                 text=True, cwd=tmp)
            ok(f"{name} runs from outside the tree", out.returncode == 0)
            ok(f"{name} raises nothing", "Traceback" not in out.stderr)
    finally:
        shutil.rmtree(tmp)


def main():
    for test in (test_the_readme_table_agrees_with_the_manifest,
                 test_only_prompts_take_show_prompt,
                 test_every_advertised_form_runs, test_refusals,
                 test_no_prompt_names_a_command_that_is_gone,
                 test_associate_says_what_the_footing_needs,
                 test_the_dictated_marker_passes_the_checker,
                 test_the_gate_is_in_argv,
                 test_housekeeping_points_at_the_standard_rather_than_restating_it,
                 test_housekeeping_states_the_goal_and_ends_on_ci,
                 test_housekeeping_says_the_discussion_gate_is_overridden,
                 test_the_working_prompts_pull_before_they_work,
                 test_housekeeping_names_the_president_it_was_told_of,
                 test_help_says_why_and_where,
                 test_runs_as_an_installed_copy):
        test()
    print()
    if FAILS:
        print(f"-- {FAILS} failure(s)")
        return 1
    print("-- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
