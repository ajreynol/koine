"""The postmortem protocol: a uniform record of what happened to a repository.

A significant thing happens to a repository — a reply is worked, a check of ours
takes somebody else's build down, a number is retracted, a shortcut is taken on
purpose — and four questions are worth answering while anybody still remembers:
**what happened, who was involved, how it came out, and what we learned.**

This module is the protocol's implementation: it reads a log, checks it, derives
what the log knows, and writes a blank entry so nobody has to invent the shape.
[`docs/postmortem-protocol.md`](docs/postmortem-protocol.md) is the
definition, and where the two disagree the document is right.

## Two levels, so adoption is free on the first day

`SHAPE` is what anoieu and dokimasia already check, and nothing more: one field
block per entry, no stray fields on the sections beneath, and a summary short
enough to still be a summary. A customer at this level deletes their copy and
changes no other file.

`PROTOCOL` adds the fields that make the log answerable rather than merely
readable — what kind of event this was, who it involved, what was learned, and
what debt it booked. It is what the document recommends and what a customer moves
to when they choose.

Nothing here is binding on anybody. koine ships a definition and a checker; which
level a repository runs, and when, is the repository's.

## Calling it

    import koine_postmortem as postmortem

    log = postmortem.read(path)
    problems = postmortem.check(log, level=postmortem.PROTOCOL)
    for lesson in postmortem.lessons(log): ...
    for debt in postmortem.open_debts(log): ...
    print(postmortem.scaffold(kind="round", entities=["anoieu", "ethos"]))

`report` prints and returns a count, the way `koine_drift.report` does, so a
customer's test runner calls one and the other the same way.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

__all__ = [
    "SHAPE", "PROTOCOL", "KINDS", "FIELDS", "SUMMARY_CHARS", "SUMMARY_SENTENCES",
    "Entry", "Section", "Log", "Problem", "Debt", "Lesson",
    "read", "parse", "check", "report", "lessons", "open_debts", "scaffold",
]

SHAPE = "shape"
PROTOCOL = "protocol"

# Both customers arrived at these two limits independently. They are the only
# numbers in the protocol and they are not koine's to move.
SUMMARY_CHARS = 250
SUMMARY_SENTENCES = 2

#: The kinds of event an entry may record. Closed, and short, because a
#: vocabulary nobody can enumerate is prose with extra steps. Every one of these
#: has an incident behind it; see the document.
KINDS = {
    "round": "a reply from the project a finding was reported to was worked",
    "defect": "something here was wrong, and somebody else paid for it",
    "retraction": "we published something and withdrew it",
    "debt": "a shortcut was taken deliberately, and something was left to notice",
    "adoption": "something was taken up, or dropped: a tool, a policy, a member",
}

#: The one-per-entry fields, and whether each level requires them. `Tool:` is
#: what both customers wrote before there was a protocol; it is accepted as one
#: entity so that an existing log is not rewritten to be read.
FIELDS = {
    "Kind": PROTOCOL,
    "Entities": PROTOCOL,
    "Tool": None,
    "Summary": SHAPE,
    "Resolution": SHAPE,
    "Learned": PROTOCOL,
}

#: A field that may appear more than once, and is therefore never counted.
REPEATABLE = ("Debt",)

_FIELD = re.compile(r"^\*\*([A-Za-z][A-Za-z ]*):\*\*[ \t]*(.*)$", re.M)
_ENTRY = re.compile(r"^## (?=\d{4}-\d{2}-\d{2}\b)", re.M)
_SECTION = re.compile(r"^### ", re.M)
_FENCE = re.compile(r"```.*?```", re.S)
_SETTLES = re.compile(r"\bsettles when\b", re.I)


# -- the record --------------------------------------------------------------

@dataclass
class Debt:
    """A shortcut taken on purpose, and what will notice that it is outstanding.

    A debt with no discharge condition is a regret, so the protocol requires the
    clause and this carries it. `settles` is the text after *settles when*.
    """
    text: str
    settles: Optional[str] = None

    @property
    def discharged_by(self) -> str:
        return self.settles or ""


@dataclass
class Section:
    """One finding, row or thread inside an entry."""
    title: str
    body: str
    learned: Optional[str] = None
    fields: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class Entry:
    date: str
    title: str
    fields: Dict[str, List[str]] = field(default_factory=dict)
    sections: List[Section] = field(default_factory=list)
    line: int = 0

    def one(self, name: str) -> Optional[str]:
        got = self.fields.get(name) or []
        return got[0] if got else None

    @property
    def kind(self) -> Optional[str]:
        return (self.one("Kind") or "").strip().lower() or None

    @property
    def summary(self) -> Optional[str]:
        return self.one("Summary")

    @property
    def resolution(self) -> Optional[str]:
        return self.one("Resolution")

    @property
    def learned(self) -> Optional[str]:
        return self.one("Learned")

    @property
    def entities(self) -> List[str]:
        """Who was involved, by the ids the ecosystem already uses.

        `Entities:` if it is there; otherwise `Tool:`, which is what the logs
        that predate the protocol wrote and means the same thing for one party.
        """
        raw = self.one("Entities")
        if raw is None:
            raw = self.one("Tool")
        if not raw:
            return []
        return [p.strip() for p in re.split(r"[,;]| and ", raw) if p.strip()]

    @property
    def debts(self) -> List[Debt]:
        out = []
        for text in self.fields.get("Debt", []):
            m = _SETTLES.search(text)
            out.append(Debt(text, text[m.end():].strip(" -—:") if m else None))
        return out

    @property
    def heading(self) -> str:
        return f"{self.date} — {self.title}" if self.title else self.date


@dataclass
class Log:
    path: Optional[str]
    preamble: str
    entries: List[Entry] = field(default_factory=list)

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)


@dataclass
class Problem:
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.where}: {self.message}"


@dataclass
class Lesson:
    """A `Learned:` line, and the entry it was learned in.

    A rule with no incident behind it is a preference; this is what lets the
    standing-rules table be derived from the log instead of kept beside it.
    """
    text: str
    entry: str
    date: str
    section: Optional[str] = None


# -- reading -----------------------------------------------------------------

def _fields(text: str) -> Dict[str, List[str]]:
    """Every `**Name:**` field in a chunk, in the order written.

    A field's value runs to the next field or to a blank line — whichever comes
    first is *not* how this reads it. It runs to the next field, so that a limit
    on a field's length cannot be evaded by inserting a blank line and carrying
    on. That is the one place the two copies of this check disagreed, and the
    document says why this side was taken.
    """
    out: Dict[str, List[str]] = {}
    hits = list(_FIELD.finditer(text))
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        value = (m.group(2) + "\n" + text[m.end():end]).strip()
        out.setdefault(m.group(1).strip(), []).append(" ".join(value.split()))
    return out


def parse(text: str, path: Optional[str] = None) -> Log:
    """Read a log. Fenced blocks are templates and are never entries."""
    clean = _FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    chunks = _ENTRY.split(clean)
    preamble, rest = chunks[0], chunks[1:]

    line_of = {}
    offset = 0
    for i, chunk in enumerate(chunks):
        line_of[i] = clean[:offset].count("\n") + 1
        offset += len(chunk) + (3 if i else 0)

    entries = []
    for i, chunk in enumerate(rest, start=1):
        head, _, body = chunk.partition("\n")
        head = head.strip()
        date = head[:10]
        title = head[10:].strip().lstrip("\u2014-").strip()
        parts = _SECTION.split(body)
        entry = Entry(date=date, title=title, fields=_fields(parts[0]),
                      line=line_of[i])
        for part in parts[1:]:
            stitle, _, sbody = part.partition("\n")
            sfields = _fields(sbody)
            entry.sections.append(Section(
                title=stitle.strip().lstrip("—-").strip(),
                body=sbody.strip(),
                learned=(sfields.get("Learned") or [None])[0],
                fields=sfields))
        entries.append(entry)
    return Log(path=path, preamble=preamble, entries=entries)


def read(path: str) -> Log:
    with open(path, encoding="utf-8") as fh:
        return parse(fh.read(), path)


# -- checking ----------------------------------------------------------------

def _sentences(text: str) -> int:
    return len(re.findall(r"[.!?](?:\s|$)", text))


def check(log: Log, level: str = SHAPE,
          registry: Optional[Iterable[str]] = None,
          require_entries: bool = True) -> List[Problem]:
    """What the log gets wrong, at the level asked for.

    `registry` is the set of entity ids that exist — the ecosystem's own list,
    where a caller has one. Without it the ids are checked for shape and not for
    existence, which keeps this module from depending on anybody's file.
    """
    if level not in (SHAPE, PROTOCOL):
        raise ValueError(f"level is {SHAPE!r} or {PROTOCOL!r}, not {level!r}")
    known = set(registry) if registry is not None else None
    problems: List[Problem] = []

    def bad(where, message):
        problems.append(Problem(where, message))

    if require_entries and not log.entries:
        bad(log.path or "the log", "no entries, and no run has said why")
        return problems

    for entry in log.entries:
        where = f"{entry.heading!r}"

        for name, needed in FIELDS.items():
            n = len(entry.fields.get(name, []))
            if n > 1:
                bad(where, f"{n} **{name}:** lines, expected at most 1")
            if needed is None or n:
                continue
            if needed == SHAPE or level == PROTOCOL:
                if name == "Entities" and entry.fields.get("Tool"):
                    continue
                bad(where, f"no **{name}:** line")

        strays = sorted({n for s in entry.sections for n in s.fields
                         if n in FIELDS and n != "Learned"})
        if strays:
            bad(where, f"{strays} on a section beneath it; those fields belong "
                       "to the entry, not to one finding")

        summary = entry.summary
        if summary is not None:
            if len(summary) > SUMMARY_CHARS:
                bad(where, f"the summary is {len(summary)} characters, "
                           f"at most {SUMMARY_CHARS}")
            if _sentences(summary) > SUMMARY_SENTENCES:
                bad(where, f"the summary is {_sentences(summary)} sentences, "
                           f"at most {SUMMARY_SENTENCES}")

        for debt in entry.debts:
            if debt.settles is None:
                bad(where, "a **Debt:** with no *settles when* clause; a debt "
                           "nothing discharges is a regret")

        if level != PROTOCOL:
            continue

        if entry.kind and entry.kind not in KINDS:
            bad(where, f"kind {entry.kind!r} is not one of "
                       f"{', '.join(sorted(KINDS))}")
        if not entry.entities:
            bad(where, "**Entities:** names nobody")
        for name in entry.entities:
            if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
                bad(where, f"entity {name!r} is not an id")
            elif known is not None and name not in known:
                bad(where, f"entity {name!r} is in no registry")
        if entry.learned is not None and not entry.learned.strip():
            bad(where, "**Learned:** is empty; an entry that learned nothing "
                       "is a log line")

    return problems


def report(log: Log, level: str = SHAPE, registry=None, out=None) -> int:
    """Print it and return the count, the way `koine_drift.report` does."""
    import sys
    stream = sys.stdout if out is None else out
    problems = check(log, level=level, registry=registry)
    name = log.path or "the log"
    for problem in problems:
        print(f"FAIL {problem}", file=stream)
    if not problems:
        print(f"ok   {name}: {len(log.entries)} entry(s) keep the "
              f"{level}", file=stream)
    print(f"-- the postmortem log: {len(log.entries)} entry(s), "
          f"{len(problems)} failure(s)", file=stream)
    return len(problems)


# -- what the log knows ------------------------------------------------------

def lessons(log: Log) -> List[Lesson]:
    """Every `Learned:` line, entry-level and section-level, newest first.

    This is the standing-rules table derived rather than maintained: each rule
    arrives with the incident that produced it, because that is the difference
    between a rule and a preference.
    """
    out = []
    for entry in log.entries:
        if entry.learned:
            out.append(Lesson(entry.learned, entry.heading, entry.date))
        for section in entry.sections:
            if section.learned:
                out.append(Lesson(section.learned, entry.heading, entry.date,
                                  section.title))
    return out


def open_debts(log: Log, discharged: Sequence[str] = ()) -> List[Debt]:
    """Debts the log has booked and not written off.

    `discharged` is the text of debts a caller knows to be settled — an audit's
    answer. Nothing here decides that: whether a debt is paid is a fact about
    the world, and this module reads files.
    """
    done = set(discharged)
    return [d for e in log.entries for d in e.debts if d.text not in done]


# -- writing one -------------------------------------------------------------

def scaffold(date: str = "", title: str = "", kind: str = "",
             entities: Sequence[str] = (), debts: Sequence[str] = ()) -> str:
    """A blank entry, so that nobody writes the shape from memory.

    The prompts that produce these run in a session that has never read the
    protocol; handing them the skeleton is cheaper than describing it, and it is
    the one place a protocol can be enforced before the fact rather than after.
    """
    if kind and kind not in KINDS:
        raise ValueError(f"kind {kind!r} is not one of {', '.join(sorted(KINDS))}")
    if not date:
        import datetime
        date = datetime.date.today().isoformat()
    lines = [
        f"## {date} — {title or '<what this was, in a phrase>'}",
        "",
        f"**Kind:** {kind or ' | '.join(sorted(KINDS))}",
        "",
        f"**Entities:** {', '.join(entities) or '<who was involved, by id>'}",
        "",
        "**Summary:** <what happened, for somebody who works on neither project: "
        f"no ids, no counts, no procedure. {SUMMARY_SENTENCES} sentences, "
        f"{SUMMARY_CHARS} characters at most.>",
        "",
        "**Resolution:** <how it came out, and what changed here as a result. "
        "Counts and links belong in this field, not in the summary.>",
        "",
        "**Learned:** <the general fact, stated so it applies to the next one "
        "rather than to this one. An entry that learned nothing is a log line.>",
    ]
    for debt in debts or ():
        lines += ["", f"**Debt:** {debt}"]
    if not debts:
        lines += ["", "<!-- **Debt:** <a shortcut taken on purpose>; settles when "
                      "<what discharges it> -->"]
    return "\n".join(lines) + "\n"
