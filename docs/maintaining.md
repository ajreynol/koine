# Maintaining a protocol

> **This is koine's reading of anoieu's practice, and anoieu has not seen it.**
> Nobody handed this over. It was read off `policy.md`, `roles.md`, `board.md`,
> `reporting-workflow.md` and the postmortem log, because a repository asking to
> be handed formats ought to know how they have been maintained. **anoieu's own
> account is the ground truth and this is the copy** — `koine-D9` asks for the
> correction. Where a rule below is wrong, it is wrong because we inferred it,
> not because they told us.

Practice rather than policy: what four protocols and a handful of expensive
rounds appear to have taught the repository that has been keeping them, written
down so koine does not learn it the same way.

Each rule names the incident behind it, because *a rule with no incident behind
it is a preference* — anoieu's own standard, applied to our reading of them.
Where we could not find an incident, it says so. **The rules where we supplied
the incident ourselves are the ones most likely to be wrong.**

The principle at the head of it came from koine's maintainer, not from anoieu.

## The principle, which governs the rest

> **Redundancy is a feature. Ambiguity about which copy is right is the defect.**
>
> Copies are good: a protocol is read where somebody is working, not where it is
> decided. What makes them safe is that the document says **which copy is the
> ground truth**, and something mechanical compares the rest to it.

This looks like it contradicts why this repository exists, and it does not. koine
was approved because two tools wrote the same code twice — but **the answer was
never to leave one copy**. `scripts/` still carries the prompts, so nobody has to
paste one; the document still defines them; and the drift check is what keeps the
two the same. **koine's job is to be the ground truth and the comparison, not to
be the only copy.** That is a sharper statement of this repository's purpose than
*one implementation rather than one per member*, and it is the one to use.

It also answers the obvious objection to concentrating protocols here. A member
does not become unable to work when koine is unreachable: they hold their copy,
and koine is where the copy is *decided* and *checked*.

### The three ways it goes wrong

| failure | what it looks like | seen in |
| --- | --- | --- |
| **a copy with no declared ground truth** | two versions, both plausible, and the difference is invisible from the side that matters | dokimasia's postmortem template lost `**Learned:**` while copying anoieu's, and no page recorded a divergence |
| **a ground truth with no copies** | a document nobody reads where they are actually working | the outbound prompts before `scripts/` carried them; a person had to find and paste one |
| **a declared ground truth, copies, and no comparison** | **the worst, because it looks safe** | anoieu's standing-rules table and its own postmortem log: ten lessons, nine rules, at most three recognisable in a row, already disagreeing and nothing to notice |

The third is the one to watch for. The first two announce themselves; the third
passes every review, because the arrangement is right and only the enforcement is
missing.

## Know the scope

**koine is a servant for the protocols nobody else wants to maintain.** It does
not own the documentation of how protocols work in this ecosystem, and the
higher-level ones are not available to it:

| not koine's | held by | why not |
| --- | --- | --- |
| membership, joining, and the repository policy | `R4` | somebody is already maintaining it, and it decides who is in |
| the discussion protocol and its safety gate | `R4` | being wrong here reaches people who did not sign up |
| the inventory of who is in the ecosystem, and therefore the entity ids | `R6` | koine *uses* the vocabulary; owning it would be owning membership |
| the procedure by which a role changes hands | unowned, and anoieu's to claim | it is governance, not a format |
| the channel model — who has a wire at all | unowned, and anoieu's to claim | *only a member has a discussion file* is a membership statement wearing a format's clothes |
| what may be published about somebody else's code | `R1` | a position, and somebody signs it |

What is left is the low-level end: the shape of a reply, the shape of a
postmortem entry, the check that a script still says what its document says. Two
tools write each of them and no role holds any of them.

**The test for anything proposed for koine is not *is this a protocol*.** It is
**is anybody else maintaining this, and would they want to.** A protocol with an
owner is not available because it is well-run; a protocol without one is
available because somebody has to.

**The failure mode is generalising from the principle above.** The ground-truth
rule is good and it is true of every protocol anywhere, which makes it tempting
to conclude that koine should therefore hold them. It does not follow. A useful
rule and a narrow job are different things, and this repository has been wrong
about that once already — `D7` asked for five documents and was withdrawn, and
`D8` had to be narrowed after that.

## What koine does with the protocols it holds

Five rules, and they are mechanical on purpose.

1. **Every protocol document says where its ground truth is, in a section of its
   own.** Not in a parenthesis, not implied by which file is longer. A reader
   arriving at any copy must be able to find the authority in one hop.
2. **Every copy is named by the ground truth.** The document lists what carries a
   copy of it. A copy nobody wrote down is a copy nothing will ever check.
3. **Every copy is compared by something that runs.** If there is no check, the
   copy is drift that has not happened yet, and saying so in the document is
   better than implying the copy is fine.
4. **The comparison covers the whole of it, not an anchor part of the way down.**
   A check that starts matching at the third paragraph will not notice a stale
   one above it — which is a failure anoieu has actually had, and is why the
   drift check resolves alternatives rather than skipping past them.
5. **Where the document and the copy disagree, the document wins — and it says
   so in both.** Both existing customers write that sentence into their scripts'
   headers already. It costs a line and settles every argument in advance.

## What anoieu learned, and the incident behind each

**On changing a protocol.**

| rule | the incident |
| --- | --- |
| **A rule with no incident behind it is a preference.** Say which one, or mark it as standing | the standing-rules table's own header; two of its nine rows cite nothing |
| **Every round leaves it shorter and more actionable. An addition says what it removes** | three rounds, three increases in prompt size, recorded each time as the number going the wrong way, with the overdue removal named and not made |
| **A protocol is procedural; technical detail is a link** | a sentence inlined in a prompt had been untrue for as long as it had existed, because nobody maintains prose that lives in two places |
| **A person approves every change.** An agent may draft one, argue for it and show the diff; it may not adopt it | a template that rewrote itself from its own experience would drift with nobody having agreed to the direction |
| **Guardrails are never traded for brevity** | standing, and deliberately exempt from the shortening rule: *fix nothing else*, *touch no issue tracker*, *leave everything staged* |
| **Weakening a claim needs nobody; strengthening one needs a person** | adding a caveat is ordinary work; asking a reader to rely on something is somebody's signature |

**On what a protocol is for.**

| rule | the incident |
| --- | --- |
| **The far end is the only place a protocol's defects are visible** | the entire first round of feedback arrived as prose in a reply with nowhere to put it, which is why the reply format has a section for it now |
| **Feedback about the record is acted on; feedback about the protocol is proposed** | the first is data; the second changes what everybody is asked, and goes to a person with the evidence attached |
| **Write it by hand before generating it** | *a board generated before anybody has kept one by hand encodes whatever the generator's author assumed*, and the assumptions are the part worth getting wrong cheaply |
| **A protocol is not a boundary until it says what it excludes** | the near miss is the expensive one: a responsibility that is *nearly* somebody's is the one acted on without anybody asking |

**On changing it safely.**

| rule | the incident |
| --- | --- |
| **A shortcut taken for tempo leaves something mechanical behind that will notice** | three rows closed as *fixed upstream* on a fix that never landed, unnoticed for three months, because a closed id is one nothing re-derives |
| **Prefer a structural answer to a promised one** | a member that pins a commit needs no undertaking from anybody about when things change, and a structural answer keeps working when nobody is paying attention |
| **Removing a piece is a decision with a burden of proof.** The pieces interlock, and the chain looks arbitrary until you know which failure each link answers | four topics came through the protocol and three changed what the ecosystem does; each link was put in by an exchange rather than designed up front |
| **Infrastructure is cheapest to delete at the moment it is most load-bearing** | the failure mode is an agent under time pressure making that trade badly and describing it as simplification |

## How a protocol moves here: three stages

**Gradually** is what we are proposing, not something agreed — no reply has come
back on any topic in this file. This is what we would mean by it. Each stage is a
different answer to *where is the ground truth*, and stage 2 is deliberately
redundant — which is the principle applied to the handoff itself rather than only
to the thing being handed over.

| stage | where the ground truth is | what koine holds | reversing it costs |
| --- | --- | --- | --- |
| **1 · referenced** | anoieu's page | a checker, and nothing else | deleting a file here |
| **2 · mirrored** | anoieu's page, **and koine's copy is compared to it** | the definition, plus the check that they agree | deleting a file here |
| **3 · held** | koine's page | the definition; anoieu's page references rather than copies | one commit, copying the text back |

**A stage advances on evidence, never on a date.**

- **1 → 2** when koine's checker reproduces the holder's own behaviour on the
  holder's real files, with no case or line of coverage lost, and a harness
  anybody can re-run says so.
- **2 → 3** when the two copies have been compared in CI across enough real
  changes that a disagreement would have been caught, and every consumer has
  pinned a commit of koine.
- **Back, from anywhere**, is one revert, and needs no permission or agreement.

**Nothing skips stage 2.** That is the whole of what redundancy buys: a period
where both copies exist, the check is running, and being wrong costs a revert
instead of an outage.

## The schedule

**What is handed off**, ordered by risk, lowest first. Three things, and each is
implemented twice today with no role holding it.

| seam | held by now | stage | advances when |
| --- | --- | ---: | --- |
| the prompt-drift check | `koine`, `R16` | **3** | done; both customers may drop their copy |
| the postmortem shape | **no role** | 2 | `koine-D4` is answered |
| the reply format | `R1`, one section | 1 | a checker here reproduces how both repositories read a reply — it is already implemented twice, which makes it next |

**What is not handed off**, and is listed so that nobody has to infer it.

| protocol | stays with | for how long |
| --- | --- | --- |
| membership, joining, the repository policy | `R4` | permanently |
| the discussion protocol, and its safety gate | `R4` | permanently |
| the inventory and the entity ids | `R6` | permanently; koine references them |
| the role handoff procedure | unowned — anoieu's to claim | not koine's to ask for |
| the channel model | unowned — anoieu's to claim | not koine's to ask for |
| every prompt template | `R1` and its counterparts | permanently |
| what may be published about somebody's code | `R1` | permanently |

**The second table is the one to keep true.** The first will get shorter as
things land; the second is the boundary, and an entry moving out of it is a
scope change that goes through the discussion file before it goes anywhere else.

## What we were not taught, and are inheriting as preference

Named so that nobody mistakes them for settled.

- **Whether a record belongs in the tree or in a tracker.** Still the open
  question on our front page, and nothing above answers it.
- **What a protocol owes a member that has stopped pinning.** The structural
  answer says a consumer on an old commit is correct rather than behind; nobody
  has been on an old commit long enough for that to have been tested.
- **Where the line between a format and a governance rule actually falls.** The
  scope table above draws it in six places and each was a judgement. *Only a
  member has a discussion file* looks like a format and is a membership rule; the
  reply format looks like governance and is a shape. We got the first one wrong
  before being corrected, and there is no test here that would have caught it —
  only somebody reading.
