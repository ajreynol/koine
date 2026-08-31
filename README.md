# koine

A tool in the Eunoia ecosystem raises findings about projects that are not its
own: the analyzer reads somebody else's repository, the scrutineer reads
somebody else's proof, and each has to get what it found to the people who own
it. The trip is always the same shape. A script runs in the project the finding
is about and leaves a question; somebody answers it in a file; a second script
runs back at home and reads the answer; and a check confirms that the wording
the scripts use still matches the document that defines it.

**koine is that trip, held once instead of once per tool.** It is the shared
half of the reporting loop — the part that is identical no matter which tool is
at one end or which project is at the other.

## The question it answers

*How does a finding get from the tool that raised it to the people it is about,
and an answer back, in a form both ends read the same way?*

That is a narrow, mechanical question, and it is the whole of the job. Two
tools in this ecosystem have now built the loop separately and arrived at the
same code for these parts — not similar code, the same code. koine exists
because the second one had to be written at all.

## The question it does not answer

*Whether the finding is any good.*

koine has no opinion on what is worth reporting, what makes a report correct,
or what settles one. Those belong to the tool that raised it, and they differ
because the subjects differ — the analyzer's questions are not the
scrutineer's. koine carries the envelope and never writes the letter.

The name invites a larger reading, so it is worth refusing in the open: koine
is not a shared standard for how members track issues, keep registers, or agree
on what counts as a problem. Those formats are still being discovered, and
fixing them now would fix them before anybody has evidence about which is
right. Nor does using koine enrol a repository in anything; a tool somebody
depends on is not thereby a member of this ecosystem.

## Running it

Nothing runs. This README is the only file here.

There is no code, no command, no package, and no interface — how a consumer
would fetch and call this has not been designed, and saying so is more useful
than a plan. If that changes, it will arrive the way this ecosystem shares
anything else: a consumer pins a commit and fetches it. That describes the
mechanism, not a release.

## The name

κοινή — *koinē*, the common dialect. The Greek that spread after Alexander and
became the tongue people whose Greek differed used to understand each other. It
is here because what two tools running this loop actually share is not code but
a dialect they must both speak; the code is only what keeps them speaking it.

The objection, which belongs in the same paragraph as the claim: κοινή is a
word about communication in general, fastened to a tool about reporting in
particular, and a reader can fairly hear it as *the common one* — the drawer
where shared odds and ends go. That reading is wrong today and would become
right the moment this repository accepts its first piece of code that is merely
shared rather than spoken by both ends of a report. The name is a test as much
as a label, and it can be failed.

`koine` was reserved in the ecosystem's
[register of names](https://github.com/ajreynol/anoieu/blob/main/tools/ynoia/names.md)
and approved on 2026-08-31 as proposal `P1`, awaiting a repository. This is the
repository. Taking the name commits this repository to the description written
there, or to changing it.
