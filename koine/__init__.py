"""koine -- the shared half of the reporting loop.

A tool in this ecosystem reports findings about somebody else's project, and the
trip a finding takes is the same shape no matter which tool raised it. This
package holds the parts of that trip that are identical, so they have one
implementation rather than one per tool.

There is nothing general here. Every module answers to a piece that two
customers -- anoieu and dokimasia -- had already written twice, and the second
copy is what justifies the module existing.

Nothing installs. Put the directory containing this package on `sys.path` and
import it; the package is pure standard library and reads nothing but the files
a caller hands it.

    import sys; sys.path.insert(0, "/tmp/koine")
    from koine import drift
"""

__all__ = ["drift"]
