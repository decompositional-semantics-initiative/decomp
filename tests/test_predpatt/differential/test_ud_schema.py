"""Compare standalone PredPatt UD schema with this package's UD schema."""

import pytest


# Import external predpatt for comparison
from predpatt.util.ud import dep_v1 as orig_dep_v1
from predpatt.util.ud import dep_v2 as orig_dep_v2
from predpatt.util.ud import postag as orig_postag

from decomp.semantics.predpatt.utils.ud_schema import (
    DependencyRelationsV1,
    DependencyRelationsV2,
    POSTag,
    dep_v1,
    dep_v2,
    get_dependency_relations,
    postag,
)


class TestPOSTags:
    """Test POS tag definitions match original exactly."""

    def test_postag_values(self):
        """Verify all POS tag values match original."""
        # Open class words
        assert POSTag.ADJ == orig_postag.ADJ == "ADJ"
        assert POSTag.ADV == orig_postag.ADV == "ADV"
        assert POSTag.INTJ == orig_postag.INTJ == "INTJ"
        assert POSTag.NOUN == orig_postag.NOUN == "NOUN"
        assert POSTag.PROPN == orig_postag.PROPN == "PROPN"
        assert POSTag.VERB == orig_postag.VERB == "VERB"

        # Closed class words
        assert POSTag.ADP == orig_postag.ADP == "ADP"
        assert POSTag.AUX == orig_postag.AUX == "AUX"
        assert POSTag.CCONJ == orig_postag.CCONJ == "CCONJ"
        assert POSTag.DET == orig_postag.DET == "DET"
        assert POSTag.NUM == orig_postag.NUM == "NUM"
        assert POSTag.PART == orig_postag.PART == "PART"
        assert POSTag.PRON == orig_postag.PRON == "PRON"
        assert POSTag.SCONJ == orig_postag.SCONJ == "SCONJ"

        # Other
        assert POSTag.PUNCT == orig_postag.PUNCT == "PUNCT"
        assert POSTag.SYM == orig_postag.SYM == "SYM"
        assert POSTag.X == orig_postag.X == "X"

    def test_postag_alias(self):
        """Test backwards compatibility alias."""
        assert postag is POSTag


class TestDependencyRelationsV1:
    """Test UD v1 dependency relations match original exactly."""

    def test_version(self):
        """Test version identifier."""
        assert DependencyRelationsV1.VERSION == orig_dep_v1.VERSION == "1.0"

    def test_all_relations(self):
        """Test all individual relation values."""
        # Subject relations
        assert DependencyRelationsV1.nsubj == orig_dep_v1.nsubj == "nsubj"
        assert DependencyRelationsV1.nsubjpass == orig_dep_v1.nsubjpass == "nsubjpass"
        assert DependencyRelationsV1.csubj == orig_dep_v1.csubj == "csubj"
        assert DependencyRelationsV1.csubjpass == orig_dep_v1.csubjpass == "csubjpass"

        # Object relations
        assert DependencyRelationsV1.dobj == orig_dep_v1.dobj == "dobj"
        assert DependencyRelationsV1.iobj == orig_dep_v1.iobj == "iobj"

        # Other relations
        assert DependencyRelationsV1.cop == orig_dep_v1.cop == "cop"
        assert DependencyRelationsV1.aux == orig_dep_v1.aux == "aux"
        assert DependencyRelationsV1.auxpass == orig_dep_v1.auxpass == "auxpass"
        assert DependencyRelationsV1.neg == orig_dep_v1.neg == "neg"
        assert DependencyRelationsV1.amod == orig_dep_v1.amod == "amod"
        assert DependencyRelationsV1.advmod == orig_dep_v1.advmod == "advmod"
        assert DependencyRelationsV1.nmod == orig_dep_v1.nmod == "nmod"
        assert DependencyRelationsV1.nmod_poss == orig_dep_v1.nmod_poss == "nmod:poss"
        assert DependencyRelationsV1.nmod_tmod == orig_dep_v1.nmod_tmod == "nmod:tmod"
        assert DependencyRelationsV1.nmod_npmod == orig_dep_v1.nmod_npmod == "nmod:npmod"
        assert DependencyRelationsV1.obl == orig_dep_v1.obl == "nmod"  # Maps to nmod in v1
        assert DependencyRelationsV1.obl_npmod == orig_dep_v1.obl_npmod == "nmod:npmod"
        assert DependencyRelationsV1.appos == orig_dep_v1.appos == "appos"
        assert DependencyRelationsV1.cc == orig_dep_v1.cc == "cc"
        assert DependencyRelationsV1.conj == orig_dep_v1.conj == "conj"
        assert DependencyRelationsV1.cc_preconj == orig_dep_v1.cc_preconj == "cc:preconj"
        assert DependencyRelationsV1.mark == orig_dep_v1.mark == "mark"
        assert DependencyRelationsV1.case == orig_dep_v1.case == "case"
        assert DependencyRelationsV1.mwe == orig_dep_v1.mwe == "fixed"
        assert DependencyRelationsV1.parataxis == orig_dep_v1.parataxis == "parataxis"
        assert DependencyRelationsV1.punct == orig_dep_v1.punct == "punct"
        assert DependencyRelationsV1.ccomp == orig_dep_v1.ccomp == "ccomp"
        assert DependencyRelationsV1.xcomp == orig_dep_v1.xcomp == "xcomp"
        assert DependencyRelationsV1.advcl == orig_dep_v1.advcl == "advcl"
        assert DependencyRelationsV1.acl == orig_dep_v1.acl == "acl"
        assert DependencyRelationsV1.aclrelcl == orig_dep_v1.aclrelcl == "acl:relcl"
        assert DependencyRelationsV1.dep == orig_dep_v1.dep == "dep"

    def test_relation_sets(self):
        """Test relation sets match exactly."""
        # Note: We use lowercase properties, external uses uppercase
        v1_instance = DependencyRelationsV1()
        assert v1_instance.subj == orig_dep_v1.SUBJ
        assert v1_instance.obj == orig_dep_v1.OBJ
        assert DependencyRelationsV1.NMODS == orig_dep_v1.NMODS
        assert DependencyRelationsV1.ADJ_LIKE_MODS == orig_dep_v1.ADJ_LIKE_MODS
        assert DependencyRelationsV1.ARG_LIKE == orig_dep_v1.ARG_LIKE
        assert DependencyRelationsV1.TRIVIALS == orig_dep_v1.TRIVIALS
        assert DependencyRelationsV1.PRED_DEPS_TO_DROP == orig_dep_v1.PRED_DEPS_TO_DROP
        assert DependencyRelationsV1.SPECIAL_ARG_DEPS_TO_DROP == orig_dep_v1.SPECIAL_ARG_DEPS_TO_DROP
        assert DependencyRelationsV1.HARD_TO_FIND_ARGS == orig_dep_v1.HARD_TO_FIND_ARGS

    def test_dep_v1_alias(self):
        """Test backwards compatibility alias."""
        assert dep_v1 is DependencyRelationsV1


class TestDependencyRelationsV2:
    """Test UD v2 dependency relations match original exactly."""

    def test_version(self):
        """Test version identifier."""
        assert DependencyRelationsV2.VERSION == orig_dep_v2.VERSION == "2.0"

    def test_all_relations(self):
        """Test all individual relation values."""
        # Subject relations
        assert DependencyRelationsV2.nsubj == orig_dep_v2.nsubj == "nsubj"
        assert DependencyRelationsV2.nsubjpass == orig_dep_v2.nsubjpass == "nsubj:pass"
        assert DependencyRelationsV2.csubj == orig_dep_v2.csubj == "csubj"
        assert DependencyRelationsV2.csubjpass == orig_dep_v2.csubjpass == "csubj:pass"

        # Object relations
        assert DependencyRelationsV2.dobj == orig_dep_v2.dobj == "obj"
        assert DependencyRelationsV2.iobj == orig_dep_v2.iobj == "iobj"

        # Other relations
        assert DependencyRelationsV2.aux == orig_dep_v2.aux == "aux"
        assert DependencyRelationsV2.auxpass == orig_dep_v2.auxpass == "aux:pass"
        assert DependencyRelationsV2.neg == orig_dep_v2.neg == "neg"
        assert DependencyRelationsV2.cop == orig_dep_v2.cop == "cop"
        assert DependencyRelationsV2.amod == orig_dep_v2.amod == "amod"
        assert DependencyRelationsV2.advmod == orig_dep_v2.advmod == "advmod"
        assert DependencyRelationsV2.nmod == orig_dep_v2.nmod == "nmod"
        assert DependencyRelationsV2.nmod_poss == orig_dep_v2.nmod_poss == "nmod:poss"
        assert DependencyRelationsV2.nmod_tmod == orig_dep_v2.nmod_tmod == "nmod:tmod"
        assert DependencyRelationsV2.nmod_npmod == orig_dep_v2.nmod_npmod == "nmod:npmod"
        assert DependencyRelationsV2.obl == orig_dep_v2.obl == "obl"
        assert DependencyRelationsV2.obl_npmod == orig_dep_v2.obl_npmod == "obl:npmod"
        assert DependencyRelationsV2.appos == orig_dep_v2.appos == "appos"
        assert DependencyRelationsV2.cc == orig_dep_v2.cc == "cc"
        assert DependencyRelationsV2.conj == orig_dep_v2.conj == "conj"
        assert DependencyRelationsV2.cc_preconj == orig_dep_v2.cc_preconj == "cc:preconj"
        assert DependencyRelationsV2.mark == orig_dep_v2.mark == "mark"
        assert DependencyRelationsV2.case == orig_dep_v2.case == "case"
        assert DependencyRelationsV2.mwe == orig_dep_v2.mwe == "fixed"
        assert DependencyRelationsV2.parataxis == orig_dep_v2.parataxis == "parataxis"
        assert DependencyRelationsV2.punct == orig_dep_v2.punct == "punct"
        assert DependencyRelationsV2.ccomp == orig_dep_v2.ccomp == "ccomp"
        assert DependencyRelationsV2.xcomp == orig_dep_v2.xcomp == "xcomp"
        assert DependencyRelationsV2.advcl == orig_dep_v2.advcl == "advcl"
        assert DependencyRelationsV2.acl == orig_dep_v2.acl == "acl"
        assert DependencyRelationsV2.aclrelcl == orig_dep_v2.aclrelcl == "acl:relcl"
        assert DependencyRelationsV2.dep == orig_dep_v2.dep == "dep"

    def test_relation_sets(self):
        """Test relation sets match exactly."""
        # Note: We use lowercase properties, external uses uppercase
        v2_instance = DependencyRelationsV2()
        assert v2_instance.subj == orig_dep_v2.SUBJ
        assert v2_instance.obj == orig_dep_v2.OBJ
        assert DependencyRelationsV2.NMODS == orig_dep_v2.NMODS
        assert DependencyRelationsV2.ADJ_LIKE_MODS == orig_dep_v2.ADJ_LIKE_MODS
        assert DependencyRelationsV2.ARG_LIKE == orig_dep_v2.ARG_LIKE
        assert DependencyRelationsV2.TRIVIALS == orig_dep_v2.TRIVIALS
        assert DependencyRelationsV2.PRED_DEPS_TO_DROP == orig_dep_v2.PRED_DEPS_TO_DROP
        assert DependencyRelationsV2.SPECIAL_ARG_DEPS_TO_DROP == orig_dep_v2.SPECIAL_ARG_DEPS_TO_DROP
        assert DependencyRelationsV2.HARD_TO_FIND_ARGS == orig_dep_v2.HARD_TO_FIND_ARGS

    def test_dep_v2_alias(self):
        """Test backwards compatibility alias."""
        assert dep_v2 is DependencyRelationsV2


class TestVersionSpecificBehavior:
    """Test version-specific differences between v1 and v2."""

    def test_version_differences(self):
        """Verify the key differences between v1 and v2."""
        # Passive subject
        assert DependencyRelationsV1.nsubjpass == "nsubjpass"
        assert DependencyRelationsV2.nsubjpass == "nsubj:pass"

        # Clausal passive subject
        assert DependencyRelationsV1.csubjpass == "csubjpass"
        assert DependencyRelationsV2.csubjpass == "csubj:pass"

        # Direct object
        assert DependencyRelationsV1.dobj == "dobj"
        assert DependencyRelationsV2.dobj == "obj"

        # Passive auxiliary
        assert DependencyRelationsV1.auxpass == "auxpass"
        assert DependencyRelationsV2.auxpass == "aux:pass"

        # Oblique nominal (v1 maps to nmod)
        assert DependencyRelationsV1.obl == "nmod"
        assert DependencyRelationsV2.obl == "obl"

    def test_get_dependency_relations(self):
        """Test version selection function."""
        v1_class = get_dependency_relations("1.0")
        assert v1_class is DependencyRelationsV1
        assert v1_class.VERSION == "1.0"

        v2_class = get_dependency_relations("2.0")
        assert v2_class is DependencyRelationsV2
        assert v2_class.VERSION == "2.0"

        # Default is v2
        default_class = get_dependency_relations()
        assert default_class is DependencyRelationsV2

        # Invalid version
        with pytest.raises(ValueError, match="Unsupported UD version"):
            get_dependency_relations("3.0")
