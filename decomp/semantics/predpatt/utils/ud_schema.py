#!/usr/bin/env python
"""Universal Dependencies schema definitions for PredPatt.

This module provides POS tags and dependency relation definitions
for both UD v1.0 and v2.0, supporting version-specific processing.
"""

from abc import ABC, abstractmethod
from typing import ClassVar


class POSTag:
    """Universal Dependencies part-of-speech tags.

    Reference: http://universaldependencies.org/u/pos/index.html
    """

    # Open class words
    ADJ: ClassVar[str] = "ADJ"
    ADV: ClassVar[str] = "ADV"
    INTJ: ClassVar[str] = "INTJ"
    NOUN: ClassVar[str] = "NOUN"
    PROPN: ClassVar[str] = "PROPN"
    VERB: ClassVar[str] = "VERB"

    # Closed class words
    ADP: ClassVar[str] = "ADP"
    AUX: ClassVar[str] = "AUX"
    CCONJ: ClassVar[str] = "CCONJ"
    DET: ClassVar[str] = "DET"
    NUM: ClassVar[str] = "NUM"
    PART: ClassVar[str] = "PART"
    PRON: ClassVar[str] = "PRON"
    SCONJ: ClassVar[str] = "SCONJ"

    # Other
    PUNCT: ClassVar[str] = "PUNCT"
    SYM: ClassVar[str] = "SYM"
    X: ClassVar[str] = "X"


class DependencyRelationsBase(ABC):
    """Base class for Universal Dependencies relation definitions."""

    # Version identifier
    VERSION: ClassVar[str]

    # Core dependency relations that must be defined by subclasses
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

    # Relation sets that must be defined by subclasses
    @property
    @abstractmethod
    def SUBJ(self) -> set[str]:
        """All subject relations."""
        pass

    @property
    @abstractmethod
    def OBJ(self) -> set[str]:
        """All object relations."""
        pass


class DependencyRelationsV1(DependencyRelationsBase):
    """Universal Dependencies v1.0 relation definitions."""

    VERSION: ClassVar[str] = "1.0"

    # Subject relations
    nsubj: ClassVar[str] = "nsubj"
    nsubjpass: ClassVar[str] = "nsubjpass"
    csubj: ClassVar[str] = "csubj"
    csubjpass: ClassVar[str] = "csubjpass"

    # Object relations
    dobj: ClassVar[str] = "dobj"
    iobj: ClassVar[str] = "iobj"

    # Copular
    cop: ClassVar[str] = "cop"

    # Auxiliary
    aux: ClassVar[str] = "aux"
    auxpass: ClassVar[str] = "auxpass"

    # Negation
    neg: ClassVar[str] = "neg"

    # Non-nominal modifier
    amod: ClassVar[str] = "amod"
    advmod: ClassVar[str] = "advmod"

    # Nominal modifiers
    nmod: ClassVar[str] = "nmod"
    nmod_poss: ClassVar[str] = "nmod:poss"
    nmod_tmod: ClassVar[str] = "nmod:tmod"
    nmod_npmod: ClassVar[str] = "nmod:npmod"
    obl: ClassVar[str] = "nmod"  # Maps to nmod in v1
    obl_npmod: ClassVar[str] = "nmod:npmod"

    # Appositional modifier
    appos: ClassVar[str] = "appos"

    # Coordination
    cc: ClassVar[str] = "cc"
    conj: ClassVar[str] = "conj"
    cc_preconj: ClassVar[str] = "cc:preconj"

    # Marker
    mark: ClassVar[str] = "mark"
    case: ClassVar[str] = "case"

    # Fixed multiword expression
    mwe: ClassVar[str] = "fixed"

    # Parataxis
    parataxis: ClassVar[str] = "parataxis"

    # Punctuation
    punct: ClassVar[str] = "punct"

    # Clausal complement
    ccomp: ClassVar[str] = "ccomp"
    xcomp: ClassVar[str] = "xcomp"

    # Relative clause
    advcl: ClassVar[str] = "advcl"
    acl: ClassVar[str] = "acl"
    aclrelcl: ClassVar[str] = "acl:relcl"

    # Unknown dependency
    dep: ClassVar[str] = "dep"

    # Relation sets for pattern matching
    SUBJ: ClassVar[set[str]] = {nsubj, csubj, nsubjpass, csubjpass}
    OBJ: ClassVar[set[str]] = {dobj, iobj}
    NMODS: ClassVar[set[str]] = {nmod, obl, nmod_npmod, nmod_tmod}
    ADJ_LIKE_MODS: ClassVar[set[str]] = {amod, appos, acl, aclrelcl}
    ARG_LIKE: ClassVar[set[str]] = {
        nmod, obl, nmod_npmod, nmod_tmod, nsubj, csubj, csubjpass, dobj, iobj
    }

    # Trivial symbols to be stripped out
    TRIVIALS: ClassVar[set[str]] = {mark, cc, punct}

    # These dependents of a predicate root shouldn't be included in the predicate phrase
    PRED_DEPS_TO_DROP: ClassVar[set[str]] = {
        ccomp, csubj, advcl, acl, aclrelcl, nmod_tmod, parataxis, appos, dep
    }

    # These dependents of an argument root shouldn't be included in the
    # argument phrase if the argument root is the gov of the predicate root
    SPECIAL_ARG_DEPS_TO_DROP: ClassVar[set[str]] = {
        nsubj, dobj, iobj, csubj, csubjpass, neg,
        aux, advcl, auxpass, ccomp, cop, mark, mwe,
        parataxis
    }

    # Predicates of these relations are hard to find arguments
    HARD_TO_FIND_ARGS: ClassVar[set[str]] = {amod, dep, conj, acl, aclrelcl, advcl}


class DependencyRelationsV2(DependencyRelationsBase):
    """Universal Dependencies v2.0 relation definitions."""

    VERSION: ClassVar[str] = "2.0"

    # Subject relations
    nsubj: ClassVar[str] = "nsubj"
    nsubjpass: ClassVar[str] = "nsubj:pass"  # Changed in v2
    csubj: ClassVar[str] = "csubj"
    csubjpass: ClassVar[str] = "csubj:pass"  # Changed in v2

    # Object relations
    dobj: ClassVar[str] = "obj"  # Changed in v2
    iobj: ClassVar[str] = "iobj"

    # Auxiliary
    aux: ClassVar[str] = "aux"
    auxpass: ClassVar[str] = "aux:pass"  # Changed in v2

    # Negation
    neg: ClassVar[str] = "neg"

    # Copular
    cop: ClassVar[str] = "cop"

    # Non-nominal modifier
    amod: ClassVar[str] = "amod"
    advmod: ClassVar[str] = "advmod"

    # Nominal modifiers
    nmod: ClassVar[str] = "nmod"
    nmod_poss: ClassVar[str] = "nmod:poss"
    nmod_tmod: ClassVar[str] = "nmod:tmod"
    nmod_npmod: ClassVar[str] = "nmod:npmod"
    obl: ClassVar[str] = "obl"  # Separate relation in v2
    obl_npmod: ClassVar[str] = "obl:npmod"

    # Appositional modifier
    appos: ClassVar[str] = "appos"

    # Coordination
    cc: ClassVar[str] = "cc"
    conj: ClassVar[str] = "conj"
    cc_preconj: ClassVar[str] = "cc:preconj"

    # Marker
    mark: ClassVar[str] = "mark"
    case: ClassVar[str] = "case"

    # Fixed multiword expression
    mwe: ClassVar[str] = "fixed"

    # Parataxis
    parataxis: ClassVar[str] = "parataxis"

    # Punctuation
    punct: ClassVar[str] = "punct"

    # Clausal complement
    ccomp: ClassVar[str] = "ccomp"
    xcomp: ClassVar[str] = "xcomp"

    # Relative clause
    advcl: ClassVar[str] = "advcl"
    acl: ClassVar[str] = "acl"
    aclrelcl: ClassVar[str] = "acl:relcl"

    # Unknown dependency
    dep: ClassVar[str] = "dep"

    # Relation sets for pattern matching
    SUBJ: ClassVar[set[str]] = {nsubj, csubj, nsubjpass, csubjpass}
    OBJ: ClassVar[set[str]] = {dobj, iobj}
    NMODS: ClassVar[set[str]] = {nmod, obl, nmod_npmod, nmod_tmod}
    ADJ_LIKE_MODS: ClassVar[set[str]] = {amod, appos, acl, aclrelcl}
    ARG_LIKE: ClassVar[set[str]] = {
        nmod, obl, nmod_npmod, nmod_tmod, nsubj, csubj, csubjpass, dobj, iobj
    }

    # Trivial symbols to be stripped out
    TRIVIALS: ClassVar[set[str]] = {mark, cc, punct}

    # These dependents of a predicate root shouldn't be included in the predicate phrase
    PRED_DEPS_TO_DROP: ClassVar[set[str]] = {
        ccomp, csubj, advcl, acl, aclrelcl, nmod_tmod, parataxis, appos, dep
    }

    # These dependents of an argument root shouldn't be included in the
    # argument phrase if the argument root is the gov of the predicate root
    SPECIAL_ARG_DEPS_TO_DROP: ClassVar[set[str]] = {
        nsubj, dobj, iobj, csubj, csubjpass, neg,
        aux, advcl, auxpass, ccomp, cop, mark, mwe,
        parataxis
    }

    # Predicates of these relations are hard to find arguments
    HARD_TO_FIND_ARGS: ClassVar[set[str]] = {amod, dep, conj, acl, aclrelcl, advcl}


# Convenience aliases for backwards compatibility
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
