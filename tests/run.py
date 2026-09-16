#!/usr/bin/env python3
"""koine's own tests. No dependencies, no network, no customer checked out.

    python3 tests/run.py

Everything runs against `tests/fixtures/customer/` -- a miniature repository
with one document and one script, shaped like a real customer and small enough
to read. A check that only ever passes proves nothing, so every piece of the
comparison is tested against a script that has drifted as well as one that has
not.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import koine_drift as drift  # noqa: E402

CUSTOMER = os.path.join(HERE, "fixtures", "customer")
ONE = "-- or, for one row --"
POSTM = "-- or, with --no-postm --"

FAILURES = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


def spec(cases):
    return drift.Spec(
        root=CUSTOMER,
        document="docs/protocol.md",
        prompts={"one": drift.Prompt("## Prompt one", "## Prompt two"),
                 "two": drift.Prompt("## Prompt two", "## Keeping them in step")},
        cases=cases,
    )


def case(name, argv, prompt="one", forms=None, rules=()):
    return drift.Case(name, prompt, ["bash", "scripts/say", "--show-prompt"] + argv,
                      forms={ONE: False} if forms is None else forms, rules=rules)


# -- the two forms of each prompt, in agreement ------------------------------

def test_agreement():
    print("a script that says what the document says:")
    r = drift.run(spec([
        case("prompt one, one row", ["ID"], forms={ONE: True},
             rules=[drift.sub("example-ID", "BRANCH")]),
        case("prompt one, the sweep", [], forms={ONE: False},
             rules=[drift.sub("example-findings", "BRANCH")]),
        case("prompt two, with a postmortem", ["--two"], prompt="two",
             forms={POSTM: False}),
        case("prompt two, --no-postm", ["--two", "--no-postm"], prompt="two",
             forms={POSTM: True}),
    ]))
    for c in r.cases:
        check(c.name, c.ok, c.error or "\n".join(c.diff))
    check("no failures reported", r.failures == 0, f"{r.failures}")


# -- and the same script once it has drifted ---------------------------------

def test_drift_is_caught():
    print("\na script that has drifted:")
    r = drift.run(spec([
        case("an added sentence", ["--drift"], forms={ONE: False},
             rules=[drift.sub("example-findings", "BRANCH")]),
    ]))
    c = r.cases[0]
    check("the case fails", not c.ok)
    check("the diff names the added text",
          any("whatever else seems useful" in l for l in c.diff),
          "\n".join(c.diff))
    check("the diff is labelled document/script",
          any(l.startswith("--- document") for l in c.diff)
          and any(l.startswith("+++ script") for l in c.diff),
          "\n".join(c.diff[:2]))


def test_wrong_form_is_caught():
    """Taking the wrong side of an alternative is drift like any other, and is
    the failure a check anchored part way down a prompt would miss."""
    print("\na case that resolves the alternative the wrong way:")
    r = drift.run(spec([
        case("sweep output against the one-row form", [], forms={ONE: True},
             rules=[drift.sub("example-findings", "BRANCH")]),
    ]))
    check("the case fails", not r.cases[0].ok)


# -- the failures that are the customer's spec, not their script -------------

def test_unchosen_marker():
    """A document that grows an alternative no case chooses between is an error,
    not a silent half-check: the new text would go uncompared in every case."""
    print("\na prompt whose alternatives a case does not choose between:")
    r = drift.run(spec([case("nothing chosen", [], forms={})]))
    c = r.cases[0]
    check("the case fails", not c.ok)
    check("it says which marker", c.error is not None and ONE in c.error,
          str(c.error))


def test_missing_pieces():
    print("\na spec that does not match the document:")
    r = drift.run(drift.Spec(
        root=CUSTOMER, document="docs/protocol.md",
        prompts={"one": drift.Prompt("## Prompt nine", "## Prompt ten")},
        cases=[drift.Case("no such heading", "one", ["bash", "scripts/say"],
                          forms={ONE: False}),
               drift.Case("no such prompt", "three", ["bash", "scripts/say"])],
    ))
    check("a heading that is not there is named",
          not r.cases[0].ok and "Prompt nine" in (r.cases[0].error or ""),
          str(r.cases[0].error))
    check("a prompt the spec never defined is named",
          not r.cases[1].ok and "three" in (r.cases[1].error or ""),
          str(r.cases[1].error))


def test_script_failure_is_visible():
    """A script that exits non-zero must not read as a script that printed
    nothing -- that is the one failure that could quietly stop checking."""
    print("\na script that fails:")
    r = drift.run(spec([case("it exits 3", ["--fail"], forms={ONE: False})]))
    c = r.cases[0]
    check("the case fails", not c.ok)
    check("its own message reaches the diff",
          any("something went wrong" in l for l in c.diff), "\n".join(c.diff))


# -- the rules ---------------------------------------------------------------

def test_rules():
    print("\nthe normalising rules:")
    check("sub applies to both sides by default",
          drift.sub("a", "b").apply("a", drift.DOCUMENT) == "b"
          and drift.sub("a", "b").apply("a", drift.SCRIPT) == "b")
    check("a one-sided rule leaves the other side alone",
          drift.sub("a", "b", side=drift.SCRIPT).apply("a", drift.DOCUMENT) == "a")
    check("after keeps from the marker on",
          drift.after("X").apply("junk\nX tail", drift.BOTH) == "X tail")
    check("after leaves text without the marker alone",
          drift.after("X").apply("!! say: died", drift.BOTH) == "!! say: died")
    check("drop_paragraphs drops by prefix and keeps the rest",
          drift.drop_paragraphs(["Scope"]).apply("Scope: x\n\nkeep", drift.BOTH)
          == "keep")
    check("drop_paragraphs ignores leading whitespace",
          drift.drop_paragraphs(["Scope"]).apply("  Scope: x\n\nkeep", drift.BOTH)
          == "keep")


def test_resolve():
    """The alternatives resolver, which is the function both customers wrote."""
    print("\nthe alternatives resolver:")
    text = "head\n\nabove\n-- or --\nbelow\n\ntail"
    check("false keeps what is above the marker",
          drift.resolve(text, "-- or --", False) == "head\n\nabove\n\ntail")
    check("true keeps what is below it",
          drift.resolve(text, "-- or --", True) == "head\n\nbelow\n\ntail")
    check("a multi-line side is kept whole",
          drift.resolve("a\n-- or --\nb\nc\n\nz", "-- or --", True) == "b\nc\n\nz")
    try:
        drift.resolve(text, "-- nope --", False)
        check("an absent marker is an error", False, "it returned")
    except LookupError as exc:
        check("an absent marker is an error", "-- nope --" in str(exc))


def test_report_is_printable():
    print("\nthe report:")
    import io
    buf = io.StringIO()
    n = drift.report(spec([case("prompt one, the sweep", [], forms={ONE: False},
                                rules=[drift.sub("example-findings", "BRANCH")])]),
                     out=buf)
    text = buf.getvalue()
    check("it returns the failure count", n == 0, str(n))
    check("it names the document", "docs/protocol.md" in text, text)
    check("it counts the cases", "1 case(s)" in text, text)


if __name__ == "__main__":
    for fn in (test_agreement, test_drift_is_caught, test_wrong_form_is_caught,
               test_unchosen_marker, test_missing_pieces,
               test_script_failure_is_visible, test_rules, test_resolve,
               test_report_is_printable):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
