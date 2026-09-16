# epidosis

*ἐπίδοσις — increase: the improvement a thing shows over what it was. In Athens
it also meant a voluntary gift to the city, and that second reading is the one
that keeps the name from sounding like a metric.*

**A register of every change made to the record of this ecosystem's history,
and whether the change improved it.** The record is one file — `docs/history.md`
— it is kept by whichever repository holds the presidency, and it travels when
the office does. This project reads it wherever it is.

**The question:** *does the record only ever get better, and on what?*

**Two axes, and a change must land on at least one.** It improves the
**meaning** of the record — something a reader who was not there can now learn
or check — or it improves the **progress** in it, the good news, meaning
technical work that actually happened and is now written down with the evidence
beside it. A change landing on neither is a **deviation**.
[`axes.md`](axes.md) is the standard in full, with the kinds of deviation and
the rule each one offends.

**The one thing to understand before using any of this.** *Good news* is a
property of the work, not of the prose. A record improves on the progress axis
because the ecosystem built something, never because somebody wrote the week up
warmly. **Removing or softening a failure is a deviation on both axes at
once** — and a change that *adds* a failure to the record is one of the best
things that can happen to it. The record's own rules already say this: an entry
with nothing under *what went wrong* is one nobody examined.

## What started it, and who decided what

**A person started this, in an explicit instruction, on 2026-09-02**, and named
its subject and its two axes. That is the only way one of these begins here.

**Two decisions in it were the maintainer's and are recorded as theirs**: that
the project lives in koine rather than in the tree that keeps the record, and
the name. The first was put to them rather than settled here on purpose. The
ecosystem has a rule about exactly this shape — *an agent asked whether a
repository should hold something will find the case for holding it, because
finding it is what it was asked to do* — and a project whose whole subject is
somebody else's record is the worst possible place to ignore it.

## Why it is here and not where the record is

**Because the alternative is the auditor sitting inside the audited.** The
record is written by the president, under laws the president wrote, and the
gates that decide whether an entry is good enough to publish are administered
by the same party. That is named as the weakest part of the arrangement by the
arrangement itself. A register of whether the record improves is worth
something only from outside it.

**And because koine already does this shape of work.** koine's subject is a
document, the thing that is supposed to say what the document says, and a
comparison that runs — the prompt-drift check is exactly that, and the
discipline it taught is that a copy is safe when the ground truth is declared
and something mechanical compares the rest to it. **This is that discipline pointed at a record instead
of a prompt**, and the parts it borrows are named where they are used rather
than imported: nothing here imports koine and koine imports nothing here.

**koine also has a reader's interest that is not borrowed.** It pins a commit of
the tree that keeps the record and must decide when to move that pin. Reading
what a stretch says it did, before adopting it, is a member's own business.

## Goals, in order

1. **Read every change to the record and say what is mechanically true of it** —
   what it touched, what it added and removed, and which questions the axes say
   to ask. Built.
2. **Carry a verdict per change, written by a person or by an agent set to work
   by one, that a later reader can disagree with.** Built, and the first pass is
   in [`ledger.md`](ledger.md): twenty changes, one deviation.
3. **Say when the record has drifted from its own laws** — a figure nobody else
   can re-derive, an earlier entry changed with nothing shown, a footing line
   quietly gone. Signals exist; the reading is a person's.
4. **Follow the record when the office moves**, without the register losing what
   it said about the previous tree.

**The wishue, which is not a commitment:** that the four self-administered gates
on a deployment — the ones nobody but the president currently reads — acquire a
reader who is not the president, and that this is what they read.

## What it is not

- **It does not write to the record, ever.** Only the president may, and this is
  not the president. Nothing here produces a patch, a suggested wording, or a
  diff against the file.
- **It does not gate anything.** No build fails on it, nothing here runs in
  anybody's CI, and a verdict is a reading somebody may take or ignore.
- **It is not the laws and does not amend them.** The laws governing the record
  are the president's, kept in the tree that holds it, and they remain the
  authority. **The two axes are not in them** — they are a second standard,
  binding nobody, and where the two disagree the laws are right.
- **It does not claim an office.** A name is reserved in this ecosystem for the
  tool that would hold those laws and check a closed entry against them. **That
  is not this**, and doing some of the work first is explicitly not a claim on
  the title.
- **It does not audit the president**, or any tool, or any person. Its subject
  is a file and the changes made to it.
- **It says nothing about a project outside this ecosystem.** The record does,
  under a banner about what that costs; this register's opinions are about the
  record's own conduct and stop there.

## The island, and what would break it

**It reads whatever it likes and writes only inside this directory.** It is not
on koine's import path, not in koine's test suite, not in koine's CI, not in any
generated document there, and **nothing in koine breaks if this directory is
deleted** — which is the test, not the intention.

**Nothing leaves by machine.** The ledger accumulates here. If anything in it
should reach the repository that keeps the record, a person carries it through
the ordinary channel, and the register has no route of its own and no lighter
standard.

## Running it

```bash
python3 epidosis.py ~/src/anoieu               # read every change, print what is true
python3 epidosis.py ~/src/anoieu --append      # add a row per change with no row yet
python3 epidosis.py ~/src/kanon --since <sha>  # wherever the record lives now
python3 test_epidosis.py                       # the evidence, against a record built here
```

No network, no dependency, and nothing written outside this directory. The test
builds a small repository in a temporary directory, changes a record in the ways
the axes name, and asserts what comes back.

## The first result, and it is the reason to keep going

**Twenty changes read, and the axes flagged one deviation the ecosystem had
already reversed on its own.** A change added a hundred and thirteen lines of
procedure to the record — how the file travels, who may write it, what an entry
must contain. Governance in the page whose subject is what was built. Eleven
changes later the same repository took ninety-one lines back out and said the
record and the rules should never have been in one file.

**That is the only kind of evidence this project can have at this stage.** The
axes were not consulted; the ecosystem reached the verdict independently and the
register agrees with it afterwards. **It says the standard is measuring
something rather than inventing it**, and it says nothing yet about whether the
standard is useful in front of a change rather than behind one.

**The second finding is about sequence and is smaller.** Figures about six
projects outside this ecosystem were published four changes before the banner
that supplies those projects their caveats. Both changes are improvements; the
order was wrong, and only a register that reads changes in order would see it.

## Is there a paper in this

**No, and stating it settles the question.** The register is a reading of one
file in one small ecosystem, and the interesting part — whether a record kept
under a standard stays honest — needs more than one office's worth of history
before it could be argued to anybody. If that changes, this line changes with it.

## How this ends

Three endings, and a person picks: it **graduates** into a repository of its
own, it is **folded** into koine, or it is **retired in place** with a line here
saying what was learned and why it stopped. **Going quiet is not one of them.**

**Folding is the least likely and the reason is worth writing down.** koine is
plumbing for the reporting loop and this is not that; if this work turns out to
be worth keeping, it belongs somewhere that is not koine.
