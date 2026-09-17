#!/usr/bin/env python3
"""The register, read only where the register actually is.

**kanon keeps the register; koine keeps the programs that read it.** A footing
is a decision somebody made, so `scripts/ecosystem/ecosystem.json` stays with
the office and nothing here ever writes to it.

## Why this does not go looking

An earlier version of this module found kanon three ways -- `$KANON`, a sibling
checkout, then a clone at a pinned commit -- in the shape anoieu uses to find
koine. **That was wrong for this file**, and the difference is what the data is
for. anoieu pins koine because it wants *the same program every run*, and an
old one is fine so long as it is the one recorded. The register is the opposite:
it is the answer to **who is in this ecosystem right now**, and a copy is only
ever as true as the moment it was taken.

So a read of a sibling working tree, or of a clone at a pin, is a report about
a register that may since have changed -- printed with all the authority of the
real one, and with nothing in the output saying which it was. **Rather than
caveat that, this refuses it.** The register is read in the tree that holds it
or not at all.
"""

import json
import os

#: The register, relative to the root of the repository that holds it. Its
#: presence is what makes a directory the one this may be run in.
REGISTER = os.path.join("scripts", "ecosystem", "ecosystem.json")
CHECKOUTS = os.path.join("scripts", "ecosystem", "checkouts.json")

#: Every footing the policy defines. A value outside this set is a register
#: that has drifted from the page that defines it, which `--check` reports and
#: this module does not silently accept.
FOOTINGS = {"member", "associate", "candidate", "foundation", "president",
            "child", "outsider"}

WHERE = ("Run this in the repository that holds the register -- the tree with\n"
         "scripts/ecosystem/ecosystem.json in it, which today is kanon. The\n"
         "register is the ground truth for who is in this ecosystem, and a copy\n"
         "of it read from anywhere else is only true as of whenever it was\n"
         "taken. This does not read one.")


def holds_register(root):
    """Is this the repository the register lives in?"""
    return bool(root) and os.path.isfile(os.path.join(root, REGISTER))


def require(root="."):
    """The register in this tree, or a refusal that says where to stand."""
    root = os.path.abspath(os.path.expanduser(root))
    if not holds_register(root):
        raise SystemExit(
            f"-- refused: {root} does not hold {REGISTER}\n\n{WHERE}")
    with open(os.path.join(root, REGISTER), encoding="utf-8") as handle:
        return json.load(handle)


def checkouts(root="."):
    """The recorded checkout locations, where the tree has them. `{}` if not."""
    path = os.path.join(os.path.abspath(os.path.expanduser(root)), CHECKOUTS)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def entries(data):
    """The register's tools, as `(id, entry)`. Anything else is not a tool.

    The file carries prose alongside the entries -- a key whose value is a list
    of strings documenting the footings, for instance. A tool is a mapping with
    a `status`, and nothing here infers one that is missing.
    """
    return [(k, v) for k, v in data.items()
            if isinstance(v, dict) and "status" in v]


def problems(data):
    """What is wrong with the register, structurally. Offline, and no opinions.

    It never says a footing is the wrong one to have given somebody: that is a
    decision and not a defect. It says a footing is not one the policy defines,
    an entry is missing what every entry carries, or two entries claim the same
    repository -- each of which is a fact about the file.
    """
    bad = []
    seen = {}
    for name, entry in entries(data):
        footing = entry["status"]
        if footing not in FOOTINGS:
            bad.append(f"{name}: footing `{footing}` is not one the policy defines")
        if footing == "child":
            if not entry.get("parent"):
                bad.append(f"{name}: a child records no parent")
        elif not entry.get("url"):
            bad.append(f"{name}: no url, so nothing can be checked against it")
        repo = entry.get("url") or entry.get("repo")
        if repo:
            if repo in seen:
                bad.append(f"{name}: claims {repo}, which {seen[repo]} also claims")
            seen[repo] = name
    return bad
