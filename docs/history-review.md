# Reviewing the history record

[`koine_history`](../koine_history) reads every change to a repository's
`docs/history.md`, reports what changed, and flags questions for a reviewer.
With `--append`, it adds unreviewed changes to Koine's
[`history-ledger.md`](history-ledger.md). A person, or an agent a person set to
work, supplies the verdict. The script never supplies one.

## Running it

From the Koine repository root:

```bash
./koine_history /path/to/record-repository
./koine_history /path/to/record-repository --since <sha> --append
./koine_history /path/to/record-repository --file history.md
python3 tests/test_history.py
```

The repository is a local Git checkout. `--since` excludes that commit and reads
through `HEAD`; `--file` selects a different record path within the checkout.
Without `--append`, the script only prints its report. With it, rows go to
`docs/history-ledger.md` in the Koine checkout containing the script, regardless
of the current working directory. No network or third-party Python packages are
needed; Git must be installed.

## Design decisions

**Keep the record and its review separate.** The repository that holds the
record is an argument, so the review can live in Koine while the record moves
between repositories. The script never writes to the source record and never
produces proposed edits to it.

**Preserve earlier readings.** Each commit gets a row only once. Rows are
appended oldest first, and a repeated run leaves existing rows, including their
handwritten verdicts, untouched. Reviews from earlier repositories remain in the
same ledger when a later run reads another tree.

**Separate mechanical evidence from judgement.** Signals identify such things
as figures without nearby evidence, removed failure language, and changes to
earlier entries. They are questions to investigate, not findings of wrongdoing.
The review is advisory: it does not gate deployments, amend the record's rules,
claim an office, or evaluate the projects described in the record. Nothing sends
the ledger anywhere; a person may carry a reading through the ordinary channel.

## The two axes

**The standard Koine uses when reviewing the record.** It is not the law — the laws
governing `history.md` are the president's, kept in the tree that holds the
record, and nothing here amends them or is binding on anybody. This is a second
reading, and where the two disagree the laws are right.

## The rule

**Every change to the record improves it on at least one of two axes, and never
deviates from both.**

| axis | the question |
| --- | --- |
| **meaning** | does a reader who was not there now learn, or now check, something they could not before? |
| **progress** | does the record now hold technical progress that actually happened? |

A change landing on either is an **improvement**. A change landing on neither is a
**deviation**, and deviations are named by kind rather than counted.

## The inversion, which is the first thing to get right

**The progress axis is an invitation to launder, and reading it that way
destroys the record it was meant to improve.**

*Good news* is a property of the **work**, arriving in the record because it
happened. It is never a property of the **prose**, arriving because somebody
wrote the week up warmly. The distance between those two readings is the whole
risk in the axis: one of them asks the ecosystem to build more, and the other
asks it to say the same things better.

**So the record's own rules point the other way, and they win.** A stretch entry
carries what went wrong, and an entry with nothing in that field is one nobody
examined; a stretch is not deployable while that field is empty. **Removing,
softening or reframing a failure is therefore a deviation on both axes at
once** — it costs meaning, because a reader loses the thing they could not have
reconstructed from the commits, and it fakes progress, because the news improved
while the work did not.

**A change that adds a failure to the record is an improvement on the meaning
axis.** It is the commonest one worth recording, and a register that could not
say so would be measuring the wrong thing.

## What counts on the meaning axis

A change lands here when it does one of these, and the list is closed until
somebody argues it open:

- **a figure arrives with the way to re-derive it** — the repository, the
  commit, the run history, anything that lets a reader take the measurement
  again without asking;
- **a claim is narrowed to what the evidence supports**, including a claim
  about this ecosystem's own reach;
- **something a reader could not reconstruct from the commits is written
  down** — how long a build was red, what nobody was watching, what a status
  meant on the day rather than in hindsight;
- **an entry becomes followable by somebody who was not there**;
- **an attribution is corrected**, or a statement about a project outside this
  ecosystem gains the caveats the record's own banner requires;
- **prose goes and nothing checkable goes with it.**

## What counts on the progress axis

- **a thing was built, and the record now says so with the evidence beside it**;
- **a check exists that did not, and it can go red**;
- **somebody outside took something we made**, or was offered it;
- **a piece of work moved from claimed to demonstrated.**

**Governance is not progress.** A protocol written, a register added, a role
allocated, an office moved — these are real work and they are not what this axis
measures. They land on meaning when they make the record checkable, and on
nothing at all when they only make it longer.

## The kinds of deviation

Each names the rule it offends, in words rather than by number, because a
citation a reader has to go and look up is not a citation.

| kind | what it looks like | why it is one |
| --- | --- | --- |
| **laundering** | a failure removed, softened, or rewritten as a lesson learned | the record's own rules require what went wrong, and an entry without it was not examined |
| **unre-derivable** | a figure only its author can produce | every number on the page has to be recomputable by somebody else, or it does not go on the page |
| **silent revision** | an earlier stretch's text changed with no demonstration attached | correcting the past is allowed and is meant to cost something: the burden is on the editor to show the old wording was wrong |
| **membership erosion** | a line of who joined, when, and on what footing demoted, summarised away, or dropped | that part of the record survives every clean-up; when space has to be found it is found somewhere else |
| **padding** | volume without a new claim; a paragraph restating the one above it | the shortest arguable form is the standard, and a page that only grows is one people learn to distrust |
| **defence** | the record arguing for the party it describes | it is a record and not a defence, and the party writing it is the party being described |
| **ceremony** | procedure recorded as though it were achievement | governance about governance, in an arrangement that already has more of that than of the thing it governs |
| **uncaveated outsider** | something said about a project outside this ecosystem without the caveats the page's own banner requires | those projects did not ask to be measured and have not seen the page |
| **placeholder** | a `FIXME` shipped in the entry | it is worse than an empty section, because an empty section does not pretend |

## What this register may never do

**It may not write to the record.** Only the president may, and this is not the
president. Nothing here produces a patch, a suggested wording, or a diff against
the file.

**It may not gate a deployment.** The gates belong to the build system in the
tree that holds it. A verdict here is a reading somebody may take or ignore.

**It may not decide a verdict on its own.** The signals below the line are
mechanical; the verdict is written by a person or by an agent a person set to
work, and the generator never overwrites one that has been written.

## Limits and evidence

The signals are heuristics, and no automatic check proves that they implement
every rule above. Where they disagree, the written standard is the authority.
Renames are followed when enumerating commits, but content is read only at the
requested path. A change the script cannot read under that path is flagged
`unreadable`. Reading a new repository does not recover history absent from that
checkout; it preserves the rows already in the ledger.

The tests construct a temporary Git repository and check the signals, repeated
appends, preservation of written verdicts, and the command's ledger location.
They run as part of Koine's normal test suite and CI; CI does not judge the
ecosystem's actual record.

This work began on 2026-09-02 as the child project **epidosis**, at a person's
instruction. The maintainer chose its name and its home in Koine. On 2026-09-16,
the maintainer asked to fold it into Koine and remove the child project. Its
review standard and existing ledger are retained here.

The first review covered twenty changes and recorded one deviation: procedure
had been added to the history record, then removed eleven changes later by the
repository itself. It also noted that figures about outside projects preceded
their caveat banner by four changes. These are retrospective readings preserved
in the ledger, not evidence of usefulness before a change is made. That first
pass did not establish a basis for a paper or a deployment gate.
