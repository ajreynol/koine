#!/usr/bin/env python3
"""Tests for the findings record.

    python3 tests/test_findings.py

The records are written inline rather than kept as fixtures, for the reason the
postmortem tests give: a parser test is readable only when the text it parses is
next to the assertion about it.

Three properties carry most of the weight. **A record round-trips** -- reading
one and writing it back produces the same bytes, which is the whole of what
canonical means; **every rule fails on something**, because a checker that only
ever passes is a checker nobody has tested; and **an absence is never reported
as agreement**, which is the one way a comparison between two producers can be
wrong in the direction that looks fine.
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from koine import findings as fd  # noqa: E402

FAILURES = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(label)


def messages(record, **kw):
    return [p.message for p in fd.check(record, **kw)]


GOOD = """\
{"type": "run", "id": "r1", "by": "program", "producer": "run_static_analysis", "when": "2026-09-16", "targets": [{"project": "cvc5", "root": "proofs/eo/cpc", "commit": "40a4bb7e4"}], "codes": ["EO0031", "DOC0011"]}
{"id": "deb8a1dbc6c6f079", "owner": "cvc5", "code": "EO0031", "where": "proofs/eo/cpc/expert/theories/ArithExt.eo:17", "what": "`@arith_vts_delta` is declared twice with the type Real", "settled": false, "run": "r1"}
{"id": "52b5ae926f12d4c9", "owner": "ethos", "code": "EO0084", "where": "tests/Builtin-rules.eo:61", "what": "rule `identity` concludes one of its own premises", "state": "declined", "settled": true, "verdict": "a no-op rule in a test signature, and re-labelling a step is what it is for", "checked_at": "9794f31"}
"""


def test_reads_a_good_record():
    print("\na record with a run and two rows:")
    r = fd.parse(GOOD, "docs/reports/findings.jsonl")
    check("both rows and the run are read", len(r) == 2 and len(r.runs) == 1)
    check("it checks clean", fd.check(r) == [], messages(r))
    check("open and settled are fields, not files",
          len(r.open()) == 1 and len(r.settled()) == 1)
    check("the path is split off `where`",
          r.findings[0].path == "proofs/eo/cpc/expert/theories/ArithExt.eo")
    check("the run says what it read",
          r.covers("cvc5", "proofs/eo/cpc/rules/Uf.eo:31") is True)
    check("and says what it did not",
          r.covers("cvc5", "src/theory/uf/theory_uf.cpp") is False)
    check("a record with no runs answers neither",
          fd.Record(findings=list(r)).covers("cvc5", "anything") is None)


def test_round_trips():
    print("\nthe canonical form:")
    r = fd.parse(GOOD)
    check("reading and writing back is byte-identical", fd.dumps(r) == GOOD,
          repr(fd.dumps(r)[:120]))
    scrambled = ('{"settled": false, "what": "x", "owner": "cvc5", '
                 '"id": "a1", "code": "C"}\n')
    once = fd.dumps(fd.parse(scrambled))
    check("a row written in another key order canonicalises",
          once == '{"id": "a1", "owner": "cvc5", "code": "C", "what": "x", '
                  '"settled": false}\n', repr(once))
    check("and is then stable", fd.dumps(fd.parse(once)) == once)
    kept = fd.parse('{"id": "a1", "what": "x", "settled": false, '
                    '"rank": "2", "issue": 4114}\n')
    check("a column this format does not name is carried and written back",
          kept.findings[0].extra == {"issue": 4114}
          and '"issue": 4114' in fd.dumps(kept))
    check("the comparison order is by id and the file's order is not touched",
          [f.id for f in fd.parse(GOOD).sorted()]
          == ["52b5ae926f12d4c9", "deb8a1dbc6c6f079"])


def test_each_rule_fails():
    print("\nevery rule fails on something:")
    def one(line, **kw):
        return messages(fd.parse(line), **kw)

    check("a row with no id",
          any("no id" in m for m in one('{"what": "x"}')))
    check("an id with whitespace in it",
          any("whitespace" in m for m in one('{"id": "a b", "what": "x"}')))
    check("the same id twice",
          any("used twice" in m for m in one(
              '{"id": "a", "what": "x"}\n{"id": "a", "what": "y"}')))
    check("a row that claims nothing",
          any("does not say what it claims" in m for m in one('{"id": "a"}')))
    check("settled, with the state left to the file it is in",
          any("inferred from where it is filed" in m for m in one(
              '{"id": "a", "what": "x", "settled": true}')))
    check("a landing with no commit",
          any("three months" in m for m in one(
              '{"id": "a", "what": "x", "landing": {"project": "cvc5", '
              '"branch": "fix"}}')))
    check("a landing that cannot be a branch query",
          any("answerable as a branch query" in m for m in one(
              '{"id": "a", "what": "x", "landing": {"commit": "abc1234"}}')))
    check("a run that names no target",
          any("cannot then be told from a file it never read" in m for m in one(
              '{"type": "run", "id": "r1", "by": "agent", "targets": []}')))
    check("a producer that is not one of the three",
          any("not one of" in m for m in one(
              '{"type": "run", "id": "r1", "by": "vibes", '
              '"targets": [{"project": "cvc5"}]}')))
    check("a row naming a run the record does not carry",
          any("does not carry" in m for m in one(
              '{"type": "run", "id": "r1", "by": "program", '
              '"targets": [{"project": "cvc5"}]}\n'
              '{"id": "a", "what": "x", "run": "r2"}')))
    check("a record with no runs at all, when the caller asks",
          any("from a file nobody scanned" in m
              for m in one('{"id": "a", "what": "x"}', require_runs=True)))
    check("and that is not a failure by default",
          one('{"id": "a", "what": "x"}') == [])
    bad = False
    try:
        fd.parse('{"id": "a"\n')
    except ValueError as exc:
        bad = "1:" in str(exc)
    check("a line that will not parse raises rather than being skipped", bad)


def test_appending_is_a_merge():
    print("\nappending is a merge:")
    base = fd.parse('{"id": "a", "owner": "cvc5", "what": "x", "settled": false}\n'
                    '{"id": "b", "owner": "cvc5", "what": "y", "settled": false}\n')
    more = fd.parse('{"id": "b", "owner": "cvc5", "what": "y", "code": "EO0031", '
                    '"settled": true, "state": "accepted and fixed"}\n'
                    '{"id": "c", "owner": "ethos", "what": "z", "settled": false}\n')
    m = fd.merge(base, more)
    check("a new id is appended, and appended last",
          m.added == ["c"] and [f.id for f in m.record] == ["a", "b", "c"])
    check("a field the other states and this one left empty is filled",
          m.record.by_id()["b"].code == "EO0031")
    check("settling is an update, not a conflict",
          m.record.by_id()["b"].settled and m.conflicts == [])
    check("the base is untouched",
          base.by_id()["b"].code == "" and len(base) == 2)

    clash = fd.merge(
        fd.parse('{"id": "a", "what": "x", "state": "declined", "settled": true}\n'),
        fd.parse('{"id": "a", "what": "x", "state": "accepted", "settled": true}\n'))
    check("a field both state differently is a conflict, not a decision",
          [(d.field, d.a, d.b) for d in clash.conflicts]
          == [("state", "declined", "accepted")])
    check("and the base keeps its value",
          clash.record.by_id()["a"].state == "declined")
    reopen = fd.merge(
        fd.parse('{"id": "a", "what": "x", "state": "declined", "settled": true}\n'),
        fd.parse('{"id": "a", "what": "x", "state": "declined", "settled": false}\n'))
    check("a merge never un-settles a row on its own",
          reopen.record.by_id()["a"].settled
          and [d.field for d in reopen.conflicts] == ["settled"])
    check("an unnamed column is merged too",
          fd.merge(fd.parse('{"id": "a", "what": "x", "settled": false}\n'),
                   fd.parse('{"id": "a", "what": "x", "settled": false, '
                            '"issue": 7}\n')).record.by_id()["a"].extra == {"issue": 7})


def test_did_the_two_producers_agree():
    print("\ndid the program and the agent agree:")
    run_a = ('{"type": "run", "id": "p", "by": "program", "targets": '
             '[{"project": "cvc5", "root": "proofs"}]}\n')
    run_b = ('{"type": "run", "id": "g", "by": "agent", "targets": '
             '[{"project": "cvc5", "root": "proofs"}]}\n')
    a = fd.parse(run_a
                 + '{"id": "1", "owner": "cvc5", "where": "proofs/a.eo:1", "what": "x", "settled": false}\n'
                 + '{"id": "2", "owner": "cvc5", "where": "proofs/b.eo:2", "what": "y", "settled": false}\n'
                 + '{"id": "3", "owner": "cvc5", "where": "src/z.cpp:3", "what": "z", "settled": false}\n')
    b = fd.parse(run_b
                 + '{"id": "1", "owner": "cvc5", "where": "proofs/a.eo:1", "what": "x", "settled": false}\n'
                 + '{"id": "2", "owner": "cvc5", "where": "proofs/b.eo:2", "what": "y CHANGED", "settled": false}\n')
    how = fd.agree(a, b)
    check("a row both produced, identically, agrees", how.same == ["1"])
    check("a row they wrote differently is reported per field",
          [(d.id, d.field) for d in how.differ] == [("2", "what")])
    check("a row b did not report, in a file b read, is `not reported`",
          how.not_reported_by_b == [])
    check("a row outside what b scanned is not counted as disagreement",
          how.not_scanned_by_b == ["3"] and how.undecidable == 1)

    wide = fd.parse(
        '{"type": "run", "id": "g", "by": "agent", "targets": '
        '[{"project": "cvc5"}]}\n'
        '{"id": "1", "owner": "cvc5", "where": "proofs/a.eo:1", "what": "x", "settled": false}\n')
    how2 = fd.agree(a, wide)
    check("a producer that scanned the whole project and stayed silent is news",
          sorted(how2.not_reported_by_b) == ["2", "3"]
          and how2.not_scanned_by_b == [])
    check("notes are not compared; two producers never phrase prose alike",
          fd.agree(
              fd.parse('{"id": "1", "what": "x", "settled": false, "notes": "one"}\n'),
              fd.parse('{"id": "1", "what": "x", "settled": false, "notes": "two"}\n')
          ).same == ["1"])


def test_a_landing_is_a_branch_query():
    print("\na landing, in the branch reporter's terms:")
    r = fd.parse('{"id": "a", "what": "x", "settled": true, "state": "accepted", '
                 '"landing": {"project": "cvc5", "branch": "fix-eo", '
                 '"commit": "abc1234"}}\n'
                 '{"id": "b", "what": "y", "settled": false}\n')
    qs = fd.landings(r, {"cvc5": "/src/cvc5"})
    check("one query, from the row that promised something",
          len(qs) == 1 and qs[0].ref == "abc1234" and qs[0].label == "a")
    check("the conservative reading of a missing ref is the default",
          qs[0].missing == "unknown")
    check("a project with no checkout on this machine is skipped, not guessed",
          fd.landings(r, {}) == [])
    check("the marker written as one string is read the same way",
          fd.parse('{"id": "a", "what": "x", "settled": true, "state": "s", '
                   '"landing": "cvc5 fix-eo abc1234"}\n'
                   ).findings[0].landing.commit == "abc1234")


LEDGER = """\
# Open findings

Prose, and a table that is a legend rather than rows:

| code | what it is |
| --- | --- |
| `EO` | a check read something out of a signature |

## Open

| id | owner | code | where | what | notes |
| --- | --- | --- | --- | --- | --- |
| `deb8a1dbc6c6f079` | cvc5 | EO0031 | `x/ArithExt.eo:17` | `@a` is declared twice |  |
| `52b5ae926f12d4c9` | ethos | EO0084 | `tests/B.eo:61` | rule `identity` concludes a premise | declined by ethos as deliberate |
"""


def test_reads_the_table_a_customer_already_has():
    print("\nthe ledger a customer already keeps:")
    found = fd.tables(LEDGER)
    check("every table is found, legend included", len(found) == 2)
    rows = fd.from_table(found[1], {"id": "id", "owner": "owner", "code": "code",
                                    "where": "where", "what": "what",
                                    "notes": "notes"})
    check("two rows, with the backticks taken off the id and the location",
          [r.id for r in rows] == ["deb8a1dbc6c6f079", "52b5ae926f12d4c9"]
          and rows[0].where == "x/ArithExt.eo:17")
    check("a cell that is empty stays empty", rows[0].notes == "")
    check("the row's line in the document is kept", rows[0].line == 13,
          str(rows[0].line))
    unmapped = fd.from_table(found[1], {"id": "id", "what": "what"})
    check("a column the map does not name is carried rather than dropped",
          unmapped[0].extra.get("owner") == "cvc5"
          and unmapped[0].extra.get("code") == "EO0031")
    defaulted = fd.from_table(found[1], {"id": "id", "what": "what"},
                             defaults={"settled": True, "owner": "cvc5"})
    check("a default fills a column the ledger states by being a file",
          defaulted[0].settled and defaulted[0].owner == "cvc5")


def test_the_verdict_word_becomes_a_field():
    print("\nthe verdict word, and the two spellings of its separator:")
    em = fd.split_verdict("not audited — the file is a copy of cvc5's")
    dd = fd.split_verdict("intentional -- the rule is a no-op on purpose")
    check("an em-dash splits", em == ("not audited", "the file is a copy of cvc5's"))
    check("and so does a double dash, and neither is blessed",
          dd == ("intentional", "the rule is a no-op on purpose"))
    check("a verdict with no reason is a word and an empty reason",
          fd.split_verdict("withdrawn") == ("withdrawn", ""))
    check("only the first separator splits",
          fd.split_verdict("declined — a — b") == ("declined", "a — b"))


def test_renders_the_page_a_reader_is_pointed_at():
    print("\nthe generated table:")
    r = fd.parse(GOOD)
    cols = [fd.Column("id", "id", code=True), fd.Column("owner", "owner"),
            fd.Column("code", "code"), fd.Column("where", "where", code=True),
            fd.Column("what", "what"), fd.Column("notes", "notes")]
    out = fd.render(r.findings, cols)
    check("a header, a divider and a row each", len(out) == 4)
    check("the id and the location keep their backticks",
          out[2].startswith("| `deb8a1dbc6c6f079` | cvc5 | EO0031 | "
                            "`proofs/eo/cpc/expert/theories/ArithExt.eo:17` |"))
    check("an empty cell renders empty rather than as None",
          out[2].endswith("|  |"), out[2][-20:])
    back = fd.from_table(fd.tables("\n".join(out))[0],
                         {"id": "id", "owner": "owner", "code": "code",
                          "where": "where", "what": "what", "notes": "notes"})
    check("and the table reads back as the rows it was rendered from",
          [b.id for b in back] == [f.id for f in r.findings]
          and back[0].where == r.findings[0].where)


def test_report():
    print("\nthe report:")
    buf = io.StringIO()
    n = fd.report(fd.parse(GOOD, "docs/reports/findings.jsonl"), out=buf)
    check("it returns the failure count", n == 0, str(n))
    check("it names the record and counts what is settled",
          "docs/reports/findings.jsonl" in buf.getvalue()
          and "2 row(s), 1 settled, 1 run(s)" in buf.getvalue(), buf.getvalue())
    buf = io.StringIO()
    n = fd.report(fd.parse('{"id": "a"}\n'), out=buf)
    check("and prints what is wrong", n == 1 and "FAIL" in buf.getvalue())


def test_writes_a_file():
    print("\nwriting one:")
    import tempfile
    r = fd.parse(GOOD)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "findings.jsonl")
        n = fd.write(r, path)
        check("it returns the number of rows", n == 2)
        check("and what it wrote reads back the same",
              fd.dumps(fd.read(path)) == GOOD)


if __name__ == "__main__":
    for fn in (test_reads_a_good_record, test_round_trips, test_each_rule_fails,
               test_appending_is_a_merge, test_did_the_two_producers_agree,
               test_a_landing_is_a_branch_query,
               test_reads_the_table_a_customer_already_has,
               test_the_verdict_word_becomes_a_field,
               test_renders_the_page_a_reader_is_pointed_at,
               test_report, test_writes_a_file):
        fn()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)}: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")
