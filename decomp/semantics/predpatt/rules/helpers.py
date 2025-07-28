"""Helper functions for rule application.

This module contains utility functions used by rules to determine
when certain rules should be applied.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..parsing.udparse import DepTriple
    from ..utils.ud_schema import DependencyRelationsV1 as UniversalDependencies


def gov_looks_like_predicate(e: DepTriple, ud: UniversalDependencies) -> bool:
    """Check if the governor of an edge looks like a predicate.

    A token "looks like" a predicate if it has potential arguments based on
    its POS tag and the dependency relations it participates in.

    Parameters
    ----------
    e : DepTriple
        The dependency edge to check.
    ud : UniversalDependencies
        The UD schema containing relation definitions.

    Returns
    -------
    bool
        True if the governor looks like a predicate.
    """
    # import here to avoid circular dependency
    from ..utils.ud_schema import postag

    # if e.gov "looks like" a predicate because it has potential arguments
    if e.gov.tag in {postag.VERB} and e.rel in {
            ud.nmod, ud.nmod_npmod, ud.obl, ud.obl_npmod}:
        return True
    return e.rel in {ud.nsubj, ud.nsubjpass, ud.csubj, ud.csubjpass,
                     ud.dobj, ud.iobj,
                     ud.ccomp, ud.xcomp, ud.advcl}
