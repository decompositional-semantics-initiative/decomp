#!/usr/bin/env python
"""Universal Dependencies schema definitions for PredPatt.

This module provides POS tags and dependency relation definitions
for both UD v1.0 and v2.0, supporting version-specific processing
in the PredPatt semantic extraction system.

The dependency relation classes define core syntactic relations (subject,
object, modifiers) and relation sets used by PredPatt for pattern matching
during predicate-argument extraction.

Classes
-------
POSTag
    Universal Dependencies part-of-speech tags.
DependencyRelationsBase
    Abstract base class for dependency relations.
DependencyRelationsV1
    UD v1.0 dependency relation definitions.
DependencyRelationsV2
    UD v2.0 dependency relation definitions.

Functions
---------
get_dependency_relations
    Helper to get relations for a specific version.

Constants
---------
postag
    Alias for POSTag class.
dep_v1
    Instance of DependencyRelationsV1.
dep_v2
    Instance of DependencyRelationsV2.
"""

from abc import ABC, abstractmethod
from typing import ClassVar


class POSTag:
    """Universal Dependencies part-of-speech tags.

    Reference: http://universaldependencies.org/u/pos/index.html
    """

    # open class words
    ADJ: ClassVar[str] = "ADJ"
    ADV: ClassVar[str] = "ADV"
    INTJ: ClassVar[str] = "INTJ"
    NOUN: ClassVar[str] = "NOUN"
    PROPN: ClassVar[str] = "PROPN"
    VERB: ClassVar[str] = "VERB"

    # closed class words
    ADP: ClassVar[str] = "ADP"
    AUX: ClassVar[str] = "AUX"
    CCONJ: ClassVar[str] = "CCONJ"
    DET: ClassVar[str] = "DET"
    NUM: ClassVar[str] = "NUM"
    PART: ClassVar[str] = "PART"
    PRON: ClassVar[str] = "PRON"
    SCONJ: ClassVar[str] = "SCONJ"

    # other
    PUNCT: ClassVar[str] = "PUNCT"
    SYM: ClassVar[str] = "SYM"
    X: ClassVar[str] = "X"


class DependencyRelationsBase(ABC):
    """Base class for Universal Dependencies relation definitions."""

    # version identifier
    VERSION: ClassVar[str]

    # core dependency relations that must be defined by subclasses
    @property
    @abstractmethod
    def nsubj(self) -> str:
        """Nominal subject relation."""
        pass

    @property
    @abstractmethod
    def nsubjpass(self) -> str:
        """Passive nominal subject relation."""
        pass

    @property
    @abstractmethod
    def dobj(self) -> str:
        """Direct object relation."""
        pass

    @property
    @abstractmethod
    def auxpass(self) -> str:
        """Passive auxiliary relation."""
        pass

    # relation sets that must be defined by subclasses
    @property
    @abstractmethod
    def subj(self) -> set[str]:
        """All subject relations."""
        pass

    @property
    @abstractmethod
    def obj(self) -> set[str]:
        """All object relations."""
        pass


class DependencyRelationsV1(DependencyRelationsBase):
    """Universal Dependencies v1.0 relation definitions."""

    VERSION: ClassVar[str] = "1.0"

    # subject relations
    nsubj: ClassVar[str] = "nsubj"
    nsubjpass: ClassVar[str] = "nsubjpass"
    csubj: ClassVar[str] = "csubj"
    csubjpass: ClassVar[str] = "csubjpass"

    # object relations
    dobj: ClassVar[str] = "dobj"
    iobj: ClassVar[str] = "iobj"

    # copular
    cop: ClassVar[str] = "cop"

    # auxiliary
    aux: ClassVar[str] = "aux"
    auxpass: ClassVar[str] = "auxpass"

    # negation
    neg: ClassVar[str] = "neg"

    # non-nominal modifier
    amod: ClassVar[str] = "amod"
    advmod: ClassVar[str] = "advmod"

    # nominal modifiers
    nmod: ClassVar[str] = "nmod"
    nmod_poss: ClassVar[str] = "nmod:poss"
    nmod_tmod: ClassVar[str] = "nmod:tmod"
    nmod_npmod: ClassVar[str] = "nmod:npmod"
    obl: ClassVar[str] = "nmod"  # maps to nmod in v1
    obl_npmod: ClassVar[str] = "nmod:npmod"

    # appositional modifier
    appos: ClassVar[str] = "appos"

    # coordination
    cc: ClassVar[str] = "cc"
    conj: ClassVar[str] = "conj"
    cc_preconj: ClassVar[str] = "cc:preconj"

    # marker
    mark: ClassVar[str] = "mark"
    case: ClassVar[str] = "case"

    # fixed multiword expression
    mwe: ClassVar[str] = "fixed"

    # parataxis
    parataxis: ClassVar[str] = "parataxis"

    # punctuation
    punct: ClassVar[str] = "punct"

    # clausal complement
    ccomp: ClassVar[str] = "ccomp"
    xcomp: ClassVar[str] = "xcomp"

    # relative clause
    advcl: ClassVar[str] = "advcl"
    acl: ClassVar[str] = "acl"
    aclrelcl: ClassVar[str] = "acl:relcl"

    # unknown dependency
    dep: ClassVar[str] = "dep"

    # relation sets for pattern matching
    SUBJ: ClassVar[set[str]] = {nsubj, csubj, nsubjpass, csubjpass}
    OBJ: ClassVar[set[str]] = {dobj, iobj}
    NMODS: ClassVar[set[str]] = {nmod, obl, nmod_npmod, nmod_tmod}
    ADJ_LIKE_MODS: ClassVar[set[str]] = {amod, appos, acl, aclrelcl}
    ARG_LIKE: ClassVar[set[str]] = {
        nmod, obl, nmod_npmod, nmod_tmod, nsubj, csubj, csubjpass, dobj, iobj
    }

    # trivial symbols to be stripped out
    TRIVIALS: ClassVar[set[str]] = {mark, cc, punct}

    # these dependents of a predicate root shouldn't be included in the predicate phrase
    PRED_DEPS_TO_DROP: ClassVar[set[str]] = {
        ccomp, csubj, advcl, acl, aclrelcl, nmod_tmod, parataxis, appos, dep
    }

    # these dependents of an argument root shouldn't be included in the
    # argument phrase if the argument root is the gov of the predicate root
    SPECIAL_ARG_DEPS_TO_DROP: ClassVar[set[str]] = {
        nsubj, dobj, iobj, csubj, csubjpass, neg,
        aux, advcl, auxpass, ccomp, cop, mark, mwe,
        parataxis
    }

    # predicates of these relations are hard to find arguments
    HARD_TO_FIND_ARGS: ClassVar[set[str]] = {amod, dep, conj, acl, aclrelcl, advcl}

    @property
    def subj(self) -> set[str]:
        """All subject relations."""
        return self.SUBJ

    @property
    def obj(self) -> set[str]:
        """All object relations."""
        return self.OBJ


class DependencyRelationsV2(DependencyRelationsBase):
    """Universal Dependencies v2.0 relation definitions."""

    VERSION: ClassVar[str] = "2.0"

    # subject relations
    nsubj: ClassVar[str] = "nsubj"
    nsubjpass: ClassVar[str] = "nsubj:pass"  # changed in v2
    csubj: ClassVar[str] = "csubj"
    csubjpass: ClassVar[str] = "csubj:pass"  # changed in v2

    # object relations
    dobj: ClassVar[str] = "obj"  # changed in v2
    iobj: ClassVar[str] = "iobj"

    # auxiliary
    aux: ClassVar[str] = "aux"
    auxpass: ClassVar[str] = "aux:pass"  # changed in v2

    # negation
    neg: ClassVar[str] = "neg"

    # copular
    cop: ClassVar[str] = "cop"

    # non-nominal modifier
    amod: ClassVar[str] = "amod"
    advmod: ClassVar[str] = "advmod"

    # nominal modifiers
    nmod: ClassVar[str] = "nmod"
    nmod_poss: ClassVar[str] = "nmod:poss"
    nmod_tmod: ClassVar[str] = "nmod:tmod"
    nmod_npmod: ClassVar[str] = "nmod:npmod"
    obl: ClassVar[str] = "obl"  # separate relation in v2
    obl_npmod: ClassVar[str] = "obl:npmod"

    # appositional modifier
    appos: ClassVar[str] = "appos"

    # coordination
    cc: ClassVar[str] = "cc"
    conj: ClassVar[str] = "conj"
    cc_preconj: ClassVar[str] = "cc:preconj"

    # marker
    mark: ClassVar[str] = "mark"
    case: ClassVar[str] = "case"

    # fixed multiword expression
    mwe: ClassVar[str] = "fixed"

    # parataxis
    parataxis: ClassVar[str] = "parataxis"

    # punctuation
    punct: ClassVar[str] = "punct"

    # clausal complement
    ccomp: ClassVar[str] = "ccomp"
    xcomp: ClassVar[str] = "xcomp"

    # relative clause
    advcl: ClassVar[str] = "advcl"
    acl: ClassVar[str] = "acl"
    aclrelcl: ClassVar[str] = "acl:relcl"

    # unknown dependency
    dep: ClassVar[str] = "dep"

    # relation sets for pattern matching
    SUBJ: ClassVar[set[str]] = {nsubj, csubj, nsubjpass, csubjpass}
    OBJ: ClassVar[set[str]] = {dobj, iobj}
    NMODS: ClassVar[set[str]] = {nmod, obl, nmod_npmod, nmod_tmod}
    ADJ_LIKE_MODS: ClassVar[set[str]] = {amod, appos, acl, aclrelcl}
    ARG_LIKE: ClassVar[set[str]] = {
        nmod, obl, nmod_npmod, nmod_tmod, nsubj, csubj, csubjpass, dobj, iobj
    }

    # trivial symbols to be stripped out
    TRIVIALS: ClassVar[set[str]] = {mark, cc, punct}

    # these dependents of a predicate root shouldn't be included in the predicate phrase
    PRED_DEPS_TO_DROP: ClassVar[set[str]] = {
        ccomp, csubj, advcl, acl, aclrelcl, nmod_tmod, parataxis, appos, dep
    }

    # these dependents of an argument root shouldn't be included in the
    # argument phrase if the argument root is the gov of the predicate root
    SPECIAL_ARG_DEPS_TO_DROP: ClassVar[set[str]] = {
        nsubj, dobj, iobj, csubj, csubjpass, neg,
        aux, advcl, auxpass, ccomp, cop, mark, mwe,
        parataxis
    }

    # predicates of these relations are hard to find arguments
    HARD_TO_FIND_ARGS: ClassVar[set[str]] = {amod, dep, conj, acl, aclrelcl, advcl}

    @property
    def subj(self) -> set[str]:
        """All subject relations."""
        return self.SUBJ

    @property
    def obj(self) -> set[str]:
        """All object relations."""
        return self.OBJ


# convenience aliases for backwards compatibility
postag = POSTag
dep_v1 = DependencyRelationsV1
dep_v2 = DependencyRelationsV2


def get_dependency_relations(version: str = "2.0") -> type[DependencyRelationsBase]:
    """Get dependency relations for a specific UD version.

    Parameters
    ----------
    version : str, optional
        The UD version ("1.0" or "2.0"), by default "2.0"

    Returns
    -------
    type[DependencyRelationsBase]
        The dependency relations class for the specified version

    Raises
    ------
    ValueError
        If an unsupported version is specified
    """
    if version == "1.0":
        return DependencyRelationsV1
    elif version == "2.0":
        return DependencyRelationsV2
    else:
        raise ValueError(f"Unsupported UD version: {version}. Use '1.0' or '2.0'.")
