#!/usr/bin/env python3
"""Tests for the postmortem protocol.

    python3 tests/test_postmortem.py

The logs are written inline rather than kept as fixtures: a parser test is
readable only when the text it parses is next to the assertion about it.

Two properties carry most of the weight. **A log that passed the old check must
still pass `SHAPE`**, because that is the whole of what makes adoption free; and
**every rule must fail on something**, because a checker that only ever passes is
a checker nobody has tested.
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import koine_postmortem as pm  # noqa: E402

FAILURES = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


def messages(log, level=pm.PROTOCOL, **kw):
    return [p.message for p in pm.check(log, level=level, require_entries=False, **kw)]


GOOD = """# Postmortem log

Preamble, and a template that is not an entry:

```text
## <date> — <what this was>

**Kind:** round
**Summary:** not a real entry, and must never be read as one.
```

## 2026-08-31 — ethos: nineteen rows, and a decline nobody signed

**Kind:** round

**Entities:** anoieu, ethos

**Summary:** Ethos aborted on a malformed type, and three error paths reported
without a file or a line.

**Resolution:** Seven were real and are fixed on one commit; two were ours.

**Learned:** a decline is the cheapest thing an assistant can conclude and the
hardest for a reviewer to notice they have accepted.

**Debt:** seven rows closed before the change reached `main`; settles when the
landing audit reports each commit landed

### The two `Nary.eo` rows — a name that meant two things

`cons` was a parameter of the enclosing program.

**Learned:** a check that resolves a name must resolve it in the scope that
binds it.

## 2026-08-30 — the checker took dokimasia's build down

**Kind:** defect

**Entities:** anoieu, dokimasia

**Summary:** Twenty-two link failures in somebody else's tree, every one of them
caused by a rule of ours resolving from the wrong root.

**Resolution:** Fixed here, with a regression test; their build went green
without them changing anything.

**Learned:** the first outside run of a checker finds defects in the checker.
"""


def test_reads_a_good_log():
    print("a log that keeps the protocol:")
    log = pm.parse(GOOD, "docs/postmortem.md")
    check("two entries, and the template is not one", len(log.entries) == 2,
          f"{len(log.entries)}")
    a, b = log.entries
    check("the date is the heading's", a.date == "2026-08-31", a.date)
    check("the title drops the date and the dash",
          a.title == "ethos: nineteen rows, and a decline nobody signed", a.title)
    check("the kind is read", (a.kind, b.kind) == ("round", "defect"))
    check("entities are split", a.entities == ["anoieu", "ethos"], str(a.entities))
    check("a wrapped field is joined into one line",
          a.summary.endswith("without a file or a line."), a.summary)
    check("the entry's Learned is the entry's", "cheapest thing" in a.learned)
    check("a section is read with its own Learned",
          len(a.sections) == 1 and "resolves a name" in a.sections[0].learned)
    check("the second entry has no sections", b.sections == [])
    check("it keeps SHAPE", messages(log, pm.SHAPE) == [], str(messages(log, pm.SHAPE)))
    check("it keeps PROTOCOL", messages(log) == [], str(messages(log)))


def test_debts():
    print("\ndebts:")
    log = pm.parse(GOOD)
    debts = pm.open_debts(log)
    check("one debt is booked", len(debts) == 1, str(debts))
    check("its discharge condition is read",
          debts[0].settles.startswith("the landing audit reports"), str(debts[0].settles))
    check("a debt named as discharged drops out",
          pm.open_debts(log, discharged=[debts[0].text]) == [])
    bad = pm.parse("## 2026-01-01 — x\n\n**Kind:** debt\n**Entities:** koine\n"
                   "**Summary:** s.\n**Resolution:** r.\n**Learned:** l.\n"
                   "**Debt:** we took a shortcut and nothing watches it\n")
    check("a debt with no settles-when clause fails",
          any("settles when" in m for m in messages(bad)), str(messages(bad)))


def test_lessons():
    print("\nlessons:")
    got = pm.lessons(pm.parse(GOOD))
    check("every Learned line is collected, entry and section", len(got) == 3,
          f"{len(got)}")
    check("a section lesson carries its section",
          any(l.section and "Nary.eo" in l.section for l in got))
    check("an entry lesson carries none",
          any(l.section is None for l in got))
    check("each arrives with the incident that produced it",
          all(l.entry and l.date for l in got))


# -- every rule fails on something -------------------------------------------

def entry(**over):
    f = {"Kind": "round", "Entities": "anoieu, ethos", "Summary": "A thing. ",
         "Resolution": "It came out.", "Learned": "Something general."}
    f.update(over)
    body = "\n\n".join(f"**{k}:** {v}" for k, v in f.items() if v is not None)
    return pm.parse(f"## 2026-01-01 — a title\n\n{body}\n")


def test_each_rule_fails():
    print("\nevery rule fails on something:")
    cases = [
        ("a missing Summary is a SHAPE failure",
         entry(Summary=None), pm.SHAPE, "no **Summary:** line"),
        ("a missing Resolution is a SHAPE failure",
         entry(Resolution=None), pm.SHAPE, "no **Resolution:** line"),
        ("a missing Kind is a PROTOCOL failure only",
         entry(Kind=None), pm.PROTOCOL, "no **Kind:** line"),
        ("a missing Learned is a PROTOCOL failure only",
         entry(Learned=None), pm.PROTOCOL, "no **Learned:** line"),
        ("a kind outside the vocabulary is named",
         entry(Kind="vibes"), pm.PROTOCOL, "not one of"),
        ("an over-long summary is measured",
         entry(Summary="x" * 260 + "."), pm.SHAPE, "characters"),
        ("a summary of too many sentences is counted",
         entry(Summary="One. Two. Three."), pm.SHAPE, "sentences"),
        ("an entity that is not an id is named",
         entry(Entities="Some Project"), pm.PROTOCOL, "is not an id"),
        ("Entities naming nobody fails",
         entry(Entities=""), pm.PROTOCOL, "names nobody"),
    ]
    for label, log, level, want in cases:
        got = messages(log, level)
        check(label, any(want in m for m in got), f"{got}")

    check("a missing Kind is not a SHAPE failure",
          messages(entry(Kind=None), pm.SHAPE) == [])
    check("a missing Learned is not a SHAPE failure",
          messages(entry(Learned=None), pm.SHAPE) == [])


def test_summary_limit_cannot_be_evaded():
    """The one place the two copies disagreed. A blank line inside the field
    does not end it, so carrying on past one is measured rather than ignored."""
    print("\nthe summary limit:")
    log = pm.parse("## 2026-01-01 — a title\n\n**Kind:** round\n\n"
                   "**Entities:** anoieu\n\n**Summary:** Short.\n\n"
                   + "and then a great deal more prose. " * 12
                   + "\n\n**Resolution:** r.\n\n**Learned:** l.\n")
    check("prose after a blank line still counts against the field",
          any("characters" in m for m in messages(log)), str(messages(log)))


def test_repeated_and_stray_fields():
    print("\nfields in the wrong place:")
    twice = pm.parse("## 2026-01-01 — t\n\n**Kind:** round\n\n**Entities:** a\n\n"
                     "**Summary:** One.\n\n**Summary:** Two.\n\n"
                     "**Resolution:** r.\n\n**Learned:** l.\n")
    check("two Summary lines are counted",
          any("2 **Summary:** lines" in m for m in messages(twice)), str(messages(twice)))
    stray = pm.parse("## 2026-01-01 — t\n\n**Kind:** round\n\n**Entities:** a\n\n"
                     "**Summary:** s.\n\n**Resolution:** r.\n\n**Learned:** l.\n\n"
                     "### a finding\n\n**Summary:** this belongs to the entry.\n")
    check("a field belonging to the entry is not allowed on a section",
          any("on a section beneath it" in m for m in messages(stray)),
          str(messages(stray)))
    check("Learned on a section is fine",
          not any("on a section" in m for m in messages(pm.parse(GOOD))))


def test_tool_is_accepted_as_an_entity():
    """Both logs predate the protocol and write `Tool:`. An existing log is read,
    not rewritten in order to be read."""
    print("\nlogs written before the protocol:")
    log = pm.parse("## 2026-01-01 — t\n\n**Tool:** ethos\n\n**Summary:** s.\n\n"
                   "**Resolution:** r.\n")
    check("Tool: is read as one entity", log.entries[0].entities == ["ethos"],
          str(log.entries[0].entities))
    check("and satisfies SHAPE untouched", messages(log, pm.SHAPE) == [],
          str(messages(log, pm.SHAPE)))
    check("PROTOCOL still wants Kind and Learned",
          sorted(messages(log)) == ["no **Kind:** line", "no **Learned:** line"],
          str(messages(log)))


def test_registry():
    print("\nthe entity registry:")
    log = entry(Entities="anoieu, atlantis")
    check("an id in no registry is named",
          any("atlantis" in m and "registry" in m
              for m in messages(log, registry=["anoieu", "ethos"])))
    check("without a registry, existence is not checked",
          messages(log) == [], str(messages(log)))


def test_scaffold():
    print("\nthe scaffold:")
    text = pm.scaffold(date="2026-01-01", title="t", kind="round",
                       entities=["anoieu", "ethos"],
                       debts=["a shortcut; settles when the audit says so"])
    log = pm.parse(text)
    check("what it writes parses", len(log.entries) == 1)
    check("and it carries every field the level requires",
          [m for m in messages(log) if m.startswith("no **")] == [],
          str(messages(log)))
    try:
        pm.scaffold(kind="vibes")
        check("a kind outside the vocabulary is refused", False, "it returned")
    except ValueError as exc:
        check("a kind outside the vocabulary is refused", "vibes" in str(exc))


def test_empty_log():
    print("\na log with no entries:")
    log = pm.parse("# Postmortem log\n\nNothing has been worked yet.\n")
    check("by default that is a failure",
          len(pm.check(log)) == 1 and "no entries" in pm.check(log)[0].message)
    check("and a caller may say it is expected",
          pm.check(log, require_entries=False) == [])


def test_report():
    print("\nthe report:")
    buf = io.StringIO()
    n = pm.report(pm.parse(GOOD, "docs/postmortem.md"), pm.PROTOCOL, out=buf)
    check("it returns the failure count", n == 0, str(n))
    check("it names the log and counts the entries",
          "docs/postmortem.md" in buf.getvalue()
          and "2 entry(s)" in buf.getvalue(), buf.getvalue())
    check("an unknown level is refused",
          _raises(lambda: pm.check(pm.parse(GOOD), level="deep"), ValueError))


def _raises(fn, exc):
    try:
        fn()
    except exc:
        return True
    return False


if __name__ == "__main__":
    for fn in (test_reads_a_good_log, test_debts, test_lessons, test_each_rule_fails,
               test_summary_limit_cannot_be_evaded, test_repeated_and_stray_fields,
               test_tool_is_accepted_as_an_entity, test_registry, test_scaffold,
               test_empty_log, test_report):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
