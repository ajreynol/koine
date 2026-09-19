#!/usr/bin/env python3
"""The commands themselves: every form runs, and says what it should.

    python3 tests/test_eo_cmd.py

Koine maintains these commands under R35 for eo_init and eo_join, and R16
for the remaining commands. Nothing below launches a real assistant: prompt
forms use `--show-prompt` or a stub that prints its arguments.

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


def concrete(args):
    """A manifest form's placeholders, as arguments a run can actually take.

    `<path>` wants a tree that exists and is read even when not previewing;
    `<name>` a repository beside this one; `<Dn>` a topic id; `<focus>` free
    text. One place decides these because both tests below need the same
    answer, and the mapping was written twice before there was a third
    placeholder to get wrong.
    """
    return [ROOT if a == "<path>" else "kanon" if a == "<name>"
            else "D1" if a == "<Dn>" else "proofs" if a == "<focus>" else a
            for a in args]


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
        args = concrete(args)
        out = show(command, *args)
        label = " ".join([command, *args]) if args else command
        check(f"{label} exits 0", out.returncode, 0)
        ok(f"{label} prints a prompt", len(out.stdout.strip()) > 200)
        check(f"{label} is the command named", command, name)


def test_refusals():
    """Runs that are refused, and the two kinds of refusal.

    A form that never existed gets *unknown option*. **A form that did exist
    gets an explanation**: `--associate` and `--soft --affiliated` were
    `eo_join` until 2026-09-18, they are named in pages this repository does not
    own, and a person who read one of those pages and typed what it says is owed
    more than a usage block.
    """
    print("runs that are refused")
    for flag, said in (("--associate", "is gone"), ("--affiliated", "is gone")):
        out = subprocess.run([os.path.join(STORE, "eo_join"), flag],
                             capture_output=True, text=True)
        check(f"eo_join {flag} is refused", out.returncode, 2)
        ok(f"and says what happened to it", said in out.stderr)
        ok(f"and says what to run instead", "eo_join --soft" in out.stderr)
        ok(f"and prints no prompt", out.stdout.strip() == "")

    mode = subprocess.run([os.path.join(STORE, "eo_init")],
                          capture_output=True, text=True)
    check("eo_init with no mode is refused", mode.returncode, 2)

    for command, args, why in (
            ("eo_topic", [], "addressed to nobody"),
            ("eo_child", [], "A human starts a child project"),
            ("eo_child", ["tools/x"], "one path segment")):
        out = subprocess.run([os.path.join(STORE, command), *args],
                             capture_output=True, text=True)
        label = " ".join([command, *args])
        check(f"{label} is refused", out.returncode, 2)
        ok(f"and says why", why in out.stderr)

    # Both ask a person something before they write, so both refuse the form
    # that has nobody to ask.
    for command in ("eo_topic", "eo_child"):
        out = subprocess.run([os.path.join(STORE, command), "x", "--print"],
                             capture_output=True, text=True)
        check(f"{command} --print is refused", out.returncode, 2)
        ok(f"{command} says it has nobody to ask", "nobody to ask" in out.stderr)


def test_no_prompt_names_a_command_that_is_gone():
    """These were kanon's `join_eo` and `init_eo` until 2026-09-17.

    A prompt still naming the old command, or linking to where it used to live,
    tells a stranger to run something that exists nowhere -- and the soft form's
    text is written *into their README*, so the bad name outlives the run.
    """
    print("no prompt names a command or page that moved")
    for name, command, args in forms():
        args = concrete(args)
        text = show(command, *args).stdout
        label = " ".join([command, *args]) if args else command
        ok(f"{label} does not say join_eo", not re.search(r"\bjoin_eo\b", text))
        ok(f"{label} does not say init_eo", not re.search(r"\binit_eo\b", text))
        ok(f"{label} links to no kanon prompts/ page",
           "kanon/blob/main/prompts/" not in text)


def test_the_soft_form_names_us_and_claims_nothing():
    """The one soft form, and the two claims it has to keep apart.

    It says the repository **works with** this ecosystem and is **held to none
    of** its policy. A note that named us and said nothing else would be read as
    a declaration by everybody who has ever seen one, so the refusal is stated
    rather than implied -- and the note claims no footing at all, because
    `associate` means two incompatible things across the office's own pages and
    this command does not get to settle which.

    It also may not be sold as the safe option for a tree somebody else owns:
    it writes our name onto that tree's front page.
    """
    print("the soft form")
    text = show("eo_join", "--soft").stdout
    low = text.lower()
    ok("names the ecosystem", "eunoia ecosystem" in low)
    ok("says it is held to none of the policy", "not held to" in text)
    ok("says it is joining nothing", "joining nothing" in text)
    ok("declares no membership", "declare membership of nothing" in text)
    ok("adds no workflow and runs no checker",
       "add no workflow file, run no checker" in low)
    ok("claims no footing", "claims no footing" in text)
    ok("and forbids writing the word in", "Do not write `associate`" in text)
    ok("asks whether the tree is the runner's to speak for",
       "solely\nthe runner's to speak for" in text or
       "solely the runner's to speak for" in " ".join(text.split()))
    ok("and does not offer itself as the way around agreement",
       "How this repository is maintained` heading" in text)
    ok("cites the office's page as the authority",
       "kanon/blob/main/docs/policy.md" in text)
    ok("and says where the command itself can be read",
       "koine/blob/main/eo_cmd/eo_join" in text)


def test_the_soft_note_the_prompt_asks_for_passes_the_checker():
    """What the prompt asks for, read by the program that reads such notes.

    anoieu's `affiliation_in` decides whether a maintenance note names this
    ecosystem and says the repository is not held to the policy -- the two
    halves that keep it from reading as a declaration. The prompt does not
    dictate the paragraph, because the office's page owns that template and a
    copy here would be the drift this ecosystem is built to notice; what is
    checked instead is that **what the prompt asks for satisfies the reader**,
    by building the minimal note it describes and putting it through the real
    checker.

    Skipped where anoieu is not beside this checkout: a test that needs
    somebody else's tree to pass is one that fails for reasons that are not
    about this repository.
    """
    print("the note the prompt asks for, through anoieu's reader")
    anoieu = os.path.join(os.path.dirname(ROOT), "anoieu")
    # Recent anoieu separates the implementation from its CLI launcher.
    checker = next((path for path in (
        os.path.join(anoieu, "policy_check", "checker.py"),
        os.path.join(anoieu, "scripts", "policy_check.py"),
    ) if os.path.isfile(path)), None)
    if checker is None:
        print("  --   no anoieu checkout beside this one; skipped")
        return

    import importlib.machinery
    import importlib.util
    spec = importlib.util.spec_from_loader(
        "policy_check", importlib.machinery.SourceFileLoader("policy_check", checker))
    pc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pc)

    text = show("eo_join", "--soft").stdout
    ok("the prompt asks for the section the reader looks in",
       "How this repository is maintained" in text)
    note = ("# A tool\n\n## How this repository is maintained\n\n"
            "It is written and maintained by people.\n\n"
            "It works with the Eunoia ecosystem and is not held to that\n"
            "ecosystem's repository policy: it adopts none of it, it is not\n"
            "checked against it, and it speaks only for itself.\n")
    check("a note of what it asks for satisfies affiliation_in",
          pc.affiliation_in(note), [])
    # The half a note gets wrong: naming us and stopping there. Every refusal
    # goes, not just the words *not held to* -- `adopts none of it` is one of
    # the phrasings the reader accepts, which is why this is built rather than
    # edited down.
    named_only = ("# A tool\n\n## How this repository is maintained\n\n"
                  "It is written and maintained by people.\n\n"
                  "It works with the Eunoia ecosystem.\n")
    ok("and naming us without the refusal does not",
       pc.affiliation_in(named_only) != [])


def test_the_gate_is_in_argv():
    """Naming the topic is what authorises answering it, so argv enforces it.

    The ecosystem's one build-failing rule is that an agent answers a topic only
    where a human instructed it and named which topic. `eo_respond` used to
    implement that by making the unnamed form read-only and asking the prompt
    nicely to behave -- a gate held up by prose the model was trusted to obey.
    It refuses now, before an assistant is reached, which is strictly stronger
    than any wording. `eo_listen` surveys incoming topics without answering
    them; housekeeping handles them as part of a maintenance pass.
    """
    print("the discussion gate, in argv")
    bare = subprocess.run([os.path.join(STORE, "eo_respond"), "kanon"],
                          capture_output=True, text=True)
    check("a run with no topic is refused", bare.returncode, 2)
    ok("and says naming it is the authorisation",
       "what authorises" in bare.stderr)
    ok("and sends the survey to the command that does it",
       "eo_listen" in bare.stderr)
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


def test_topic_asks_for_the_topic_and_computes_the_id():
    """The two halves of `eo_topic`: it asks for one, and it counts.

    What we want from somebody else cannot be read off a tree, so the prompt
    asks the person and waits -- and carries nothing of its own, because a
    command that arrived with a topic in it would be this repository writing
    correspondence nobody asked for.

    What it does carry is the mechanical half, which is where a person goes
    wrong: **the next id is above the highest this repository ever issued,
    including topics since removed**, which are in Git history and nowhere
    else. Only `## Dn` counts -- a `### `Dn`` inside a reply is somebody else's
    number being answered, and counting those issues one of ours twice. The
    number is recomputed here from the same two sources, because a prompt that
    hands over a wrong id is worse than one that hands over none.
    """
    print("eo_topic asks, and counts")
    flat = " ".join(show("eo_topic", "kanon").stdout.split())
    ok("it asks the person and waits",
       "Ask the person running this what they want to say, and wait" in flat)
    ok("and carries no topic of its own", "You carry no topic of your own" in flat)
    ok("a finding is not a topic", "it is a finding, not a topic" in flat)
    ok("Settles when is required and answerable",
       "required\nand has to be answerable" in show("eo_topic", "kanon").stdout
       or "required and has to be answerable" in flat)
    ok("when in doubt it is a request", "in doubt it is a `request`" in flat)
    ok("never about somebody else's discussion file",
       "Never open a topic about somebody else's discussion file" in flat)
    ok("it stages and sends nothing", "nothing is sent anywhere" in flat)
    ok("addressing is not contacting", "addressing is\nnot contacting" in
       show("eo_topic", "kanon").stdout or "addressing is not contacting" in flat)
    ok("it stays short enough to be read", len(flat.split()) < 500)

    # The same two sources the command reads, read again here.
    ever = set()
    history = subprocess.run(["git", "log", "-p", "--all", "--", "docs/discussion.md"],
                             capture_output=True, text=True, cwd=ROOT).stdout
    page = ""
    if os.path.exists(os.path.join(ROOT, "docs", "discussion.md")):
        page = open(os.path.join(ROOT, "docs", "discussion.md"), encoding="utf-8").read()
    for line in (history + "\n" + page).splitlines():
        m = re.match(r"\+?## D(\d+)", line)
        if m:
            ever.add(int(m.group(1)))
    check("the id offered is the next one above every id ever issued",
          f"`D{max(ever) + 1}`" in flat, True)
    cited = {int(n) for n in re.findall(r"^### `D(\d+)`", page, re.M)}
    ok("and the ids quoted in replies are not counted as ours",
       bool(cited - ever))


def test_child_is_started_by_a_human_and_stays_an_island():
    """A child project is somebody's decision and nobody's dependency.

    The policy's first rule is that a human starts one and a human ends one:
    naming it in argv is that decision, and the charter -- the question it is
    for, and what it will not do -- is asked of the person rather than written
    by the assistant, which would be the same rule broken with a person's name
    on it.

    The second rule is the island. A child writes inside its own directory and
    nothing else imports it, in the tree or in CI, and **deleting it is the
    test**. A prompt that let an assistant wire the child up would produce
    exactly the coupling the rule forbids, on day one.
    """
    print("eo_child: a person starts it, and it is an island")
    flat = " ".join(show("eo_child", "euthyna").stdout.split())
    ok("the name is the person's and not the assistant's",
       "that name is theirs and not yours to improve" in flat)
    ok("a strained name stops the run", "say so and stop" in flat)
    ok("the charter is asked for", "ask them what question this child is for"
       in flat)
    ok("and never invented",
       "a charter you wrote yourself is you starting a child project" in flat)
    ok("it names what a charter must carry",
       "out of scope" in flat and "wishue" in flat)
    ok("it writes in the child's directory and nowhere else",
       "and nowhere else in this tree" in flat)
    ok("nothing imports it, and CI does not see it",
       "nothing in the test suite, nothing in CI" in flat)
    ok("deleting it must change nothing",
       "deleting the directory must change nothing" in flat)
    ok("the register entry is a person's", "a person writes that entry" in flat)
    ok("and it opens nothing anywhere", "open nothing anywhere" in flat)
    ok("it stays short enough to be read", len(flat.split()) < 500)

    advertised = " ".join(show("eo_child", "euthyna").stdout.split())
    ok("advertised is the default and declares nothing",
       "Advertised is the default and declares nothing" in advertised)
    unadv = " ".join(show("eo_child", "--unadvertised", "euthyna").stdout.split())
    ok("--unadvertised records the footing the readers read",
       "`unadvertised-child`" in unadv)
    ok("and asks for the reason with it", "with the reason" in unadv)


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
        for branch_args in ([], ["--no-main"]):
            variant = " ".join([label, *branch_args])
            out = show(command, *args, *branch_args)
            check(f"{variant} previews successfully", out.returncode, 0)
            flat = " ".join(out.stdout.split())
            ok(f"{variant} requires a fast-forward-only pull",
               "`git pull --ff-only`" in flat)
            ok(f"{variant} stops rather than resolving somebody else's merge",
               "fast-forward cleanly, say so and stop" in flat)
            if branch_args:
                ok(f"{variant} keeps the current branch",
                   "on the current branch; do not switch branches" in flat)
                ok(f"{variant} has no instruction to switch to main",
                   "`main`" not in flat and "git switch" not in flat)
            else:
                ok(f"{variant} checks main before pulling",
                   "verify the branch is `main`" in flat
                   and flat.index("git switch main") < flat.index("git pull"))
                ok(f"{variant} stops if switching fails",
                   "If switching fails, say so and stop" in flat)
                ok(f"{variant} preserves existing work",
                   "do not discard, stash, or reset changes" in flat)

    report = " ".join(show("eo_housekeeping", "--report").stdout.split())
    ok("--report allows the branch switch and pull before reporting",
       "**Change nothing** beyond switching to `main` and that pull" in report)
    report = " ".join(show("eo_housekeeping", "--report", "--no-main").stdout.split())
    ok("--report --no-main allows only the pull before reporting",
       "**Change nothing** beyond that pull" in report)


def test_branch_options_reach_the_assistant_without_changing_the_checkout():
    """Branch preparation is an instruction, including for installed copies."""
    print("branch options reach the assistant without changing the checkout")
    with tempfile.TemporaryDirectory() as tmp:
        here = os.path.join(tmp, "work", "alone")
        other = os.path.join(tmp, "other")
        installed = os.path.join(tmp, "bin")
        home = os.path.join(tmp, "home")
        for directory in (here, os.path.join(other, "docs"), installed, home):
            os.makedirs(directory)
        subprocess.run(["git", "init", "-q", "-b", "feature", here], check=True)
        with open(os.path.join(other, "docs", "discussion.md"), "w") as f:
            f.write("## D1 — request\n\n**To:** alone\n")
        for agent in ("claude", "codex"):
            path = os.path.join(installed, agent)
            with open(path, "w") as f:
                f.write('#!/bin/sh\nfor arg do printf "%s\\n" "$arg"; done\n')
            os.chmod(path, 0o755)
        env = dict(os.environ, HOME=home, ANOIEU_REPOS="",
                   PATH=installed + os.pathsep + os.environ["PATH"])
        for command, args in (("eo_housekeeping", []),
                              ("eo_housekeeping", ["--report"]),
                              ("eo_respond", [other, "D1"])):
            dest = os.path.join(installed, command)
            shutil.copy2(os.path.join(STORE, command), dest)
            for extra in ([], ["--no-main"]):
                for mode in ([], ["--print"], ["--codex", "--print"]):
                    out = subprocess.run([dest, *args, *extra, *mode], cwd=here,
                                         env=env, capture_output=True, text=True)
                    check(f"{command} launches the stub assistant", out.returncode, 0)
                    flat = " ".join(out.stdout.split())
                    ok("the assistant receives the selected branch instruction",
                       ("do not switch branches" if extra else "git switch main") in flat)
            preview = subprocess.run([dest, *args, "--show-prompt"], cwd=here,
                                     env=env, capture_output=True, text=True)
            check("an installed preview works without main or a remote",
                  preview.returncode, 0)
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=here,
                                capture_output=True, text=True, check=True)
        check("the launchers leave branch preparation to the assistant",
              branch.stdout.strip(), "feature")
        ok("no pull runs before the assistant", not os.path.exists(
            os.path.join(here, ".git", "FETCH_HEAD")))


def test_housekeeping_takes_in_the_child_projects():
    """A child project is this tree's code, so it is this run's work.

    `tools/<name>/` holds child projects, which are not repositories: they open
    no topic and answer none, so a run that tidied only the top level would
    leave pages nobody else is going to make true and requests nobody else is
    going to make. The register is what says which children are ours -- a
    directory under `tools/` it does not name is not a child project -- and it
    also gives the branch a child's work is on, which is how a child can be ours
    and not in this checkout.

    Checked against a tree that has children, because this repository has none:
    the fragment is empty here by design, since a sentence about the children of
    a repository with none is words a prompt pays for and gets nothing back.
    """
    print("child projects are part of the job")
    flat = " ".join(show("eo_housekeeping").stdout.split())
    ok("a repository with no children gets no sentence about children",
       "child project" not in flat)

    parent = os.path.join(os.path.dirname(ROOT), "eudaimonia")
    if not os.path.isdir(parent):
        print("  --   no checkout with child projects beside this one; skipped")
        return
    out = subprocess.run([os.path.join(STORE, "eo_housekeeping"), "--show-prompt"],
                         capture_output=True, text=True, cwd=parent)
    flat = " ".join(out.stdout.split())
    ok("the children are named where there are any",
       "**child projects** are" in flat)
    ok("as this tree's own code rather than repositories",
       "rather than repositories of their own" in flat)
    ok("and they are part of the work", "part of all three" in flat)
    ok("and a child opens no topic, so we open it",
       "a child opens no topic and answers none" in flat)
    ok("it is still two paragraphs",
       len([p for p in out.stdout.split("\n\n") if p.strip()]) == 2)
    ok("and still short enough to be read", len(flat.split()) < 500)


def test_brainstorm_changes_nothing_and_says_what_new_is_measured_against():
    """The command that looks forward, and the two ways it goes wrong.

    An idea is cheap and most are wrong, so the whole value of this one is that
    being wrong in it costs a file somebody deletes: the deliverable is
    `brainstorm.local.md`, which `*.local.md` keeps out of the record, and
    nothing else is touched. A generator that edited the tree would be one
    nobody ran twice.

    The other failure is subtler. *Cutting edge* is a claim about somebody
    else's tree, and a model asked for one from memory answers as of its
    training data -- so the prompt names the cvc5 checkout and the neighbours,
    and asks each idea what it was read out of. And because the policy breaks
    the path from *a tool should exist* to *a repository exists* on purpose, the
    prompt proposes and creates neither.

    **The file is the record and not the end of the run.** A run that writes the
    list and stops hands somebody a document at the moment they are most able to
    argue with it, so the prompt carries on with them from it -- which two it
    would take, which it would drop, and where they want to start. That costs
    nothing of the guarantee above: the conversation writes no files, and
    anything built out of it is the next thing they ask for.
    """
    print("brainstorm: reads everything, writes one ignored file")
    for args in ([], ["proof", "reconstruction"]):
        label = " ".join(["eo_brainstorm", *args]) or "eo_brainstorm"
        flat = " ".join(show("eo_brainstorm", *args).stdout.split())
        ok(f"{label} writes the list where the record does not keep it",
           "`brainstorm.local.md`" in flat)
        ok(f"{label} changes nothing else",
           "change nothing else**: nothing staged, nothing committed, "
           "no topic opened" in flat)
        ok(f"{label} sends nothing anywhere", "send nothing anywhere" in flat
           or "nothing sent anywhere" in flat)
        ok(f"{label} sends it to the vision", "vision.md" in flat)
        ok(f"{label} measures new against cvc5 as it is now", "cvc5" in flat)
        ok(f"{label} asks what each idea was read out of",
           "read it out of" in flat)
        ok(f"{label} asks what is ruled out too", "rule out" in flat)
        ok(f"{label} proposes a repository and opens none",
           "propose either, create neither" in flat)
        # The file is the record, not the end of the run. A list written and
        # abandoned is one nobody opens twice, and the person ran this to
        # decide something -- so the session carries on from it, and what gets
        # built is still the next thing they ask for.
        ok(f"{label} carries on with the person from the list",
           "carry on with the person from it" in flat)
        ok(f"{label} asks them where to start", "where they want to start" in flat)
        ok(f"{label} still builds nothing on its own",
           "the next thing they ask for and not this" in flat)
        ok(f"{label} stays short enough to be read", len(flat.split()) < 500)
        ok(f"{label} is two paragraphs",
           len([p for p in show("eo_brainstorm", *args).stdout.split("\n\n")
                if p.strip()]) == 2)

    focused = " ".join(show("eo_brainstorm", "proof", "reconstruction").stdout.split())
    ok("a focus is quoted back whole", '"proof reconstruction"' in focused)
    ok("and may honestly come back empty",
       "nothing there worth building" in focused)


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


def test_every_form_previews_on_a_machine_with_nothing_on_it():
    """The suite has to answer the same on a runner as on a developer's disk.

    Every command here looks for the other checkouts of this ecosystem beside
    its own and under $HOME, which on the machine these are written on finds all
    of them and on a CI runner finds none. That made the suite's answer a fact
    about the disk it ran on rather than about the tree: `eo_respond` refused
    `--show-prompt` without a checkout of the tool named, so ten checks passed
    here and failed in CI for eight consecutive pushes -- red for a reason that
    was not in the tree, which is the one thing a check must never be.

    So every advertised form is previewed a second time with $HOME and
    $ANOIEU_REPOS pointed at an empty directory, from a repository with no
    siblings. A preview is what somebody reads *before* they run anything, and
    that somebody has cloned nothing.
    """
    print("every form previews with no other checkout on the machine")
    # The commands that resolve somebody else's tree. `eo_join` and `eo_init`
    # write into the tree they are run in and look nothing up, so there is
    # nothing for them to report not finding.
    SAYS_WHAT_IT_COULD_NOT_READ = ("eo_topic", "eo_respond", "eo_housekeeping", "eo_listen")
    tmp = tempfile.mkdtemp()
    try:
        home = os.path.join(tmp, "home")
        here = os.path.join(tmp, "work", "alone")
        os.makedirs(home)
        os.makedirs(here)
        subprocess.run(["git", "init", "-q", here], check=True)
        bare = dict(os.environ, HOME=home, ANOIEU_REPOS="")

        for name, command, args in forms():
            args = concrete(args)
            label = " ".join([command, *args]) if args else command
            out = subprocess.run(
                [os.path.join(STORE, command), *args, "--show-prompt"],
                capture_output=True, text=True, cwd=here, env=bare)
            check(f"{label} exits 0 with nothing beside it", out.returncode, 0)
            ok(f"{label} still prints a prompt", len(out.stdout.strip()) > 200)
            # Saying so is the whole of what a preview may do differently. A
            # prompt that quietly leaves out the tree it could not read hands an
            # assistant a checkout that is not there, which is worse than the
            # refusal this replaced.
            if command in SAYS_WHAT_IT_COULD_NOT_READ:
                ok(f"{label} says which checkout it did not find",
                   re.search(r"no checkout|not checked out|"
                             r"no other tool of this ecosystem is checked out",
                             out.stdout, re.I) is not None)
    finally:
        shutil.rmtree(tmp)

    # And the real run still refuses, because it answers a topic by reading
    # one. The preview is what was widened; the gate is not.
    gone = subprocess.run([os.path.join(STORE, "eo_respond"),
                           "definitely-not-a-checkout", "D1"],
                          capture_output=True, text=True)
    check("eo_respond refuses a run it cannot read a topic for", gone.returncode, 2)
    ok("and says the preview is still available",
       "--show-prompt still prints" in gone.stderr)
    ok("and prints no prompt", gone.stdout.strip() == "")


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

    `install_eo` copies one file per command. Anything a command needs from
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
                 test_the_soft_form_names_us_and_claims_nothing,
                 test_the_soft_note_the_prompt_asks_for_passes_the_checker,
                 test_the_gate_is_in_argv,
                 test_topic_asks_for_the_topic_and_computes_the_id,
                 test_child_is_started_by_a_human_and_stays_an_island,
                 test_housekeeping_points_at_the_standard_rather_than_restating_it,
                 test_housekeeping_states_the_goal_and_ends_on_ci,
                 test_housekeeping_says_the_discussion_gate_is_overridden,
                 test_the_working_prompts_pull_before_they_work,
                 test_branch_options_reach_the_assistant_without_changing_the_checkout,
                 test_housekeeping_takes_in_the_child_projects,
                 test_brainstorm_changes_nothing_and_says_what_new_is_measured_against,
                 test_housekeeping_names_the_president_it_was_told_of,
                 test_every_form_previews_on_a_machine_with_nothing_on_it,
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
