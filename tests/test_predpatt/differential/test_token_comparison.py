"""
Compare the original Token class with the modernized Token class.

This test ensures that both implementations have identical behavior.
"""

import pytest


# Skip these tests if external predpatt is not installed
predpatt = pytest.importorskip("predpatt")
from predpatt.patt import Token as OriginalToken

from decomp.semantics.predpatt.core.token import Token as ModernToken
from decomp.semantics.predpatt.parsing.udparse import DepTriple
from decomp.semantics.predpatt.utils.ud_schema import dep_v1, dep_v2, postag


class TestTokenComparison:
    """Test that original and modern Token classes behave identically."""

    def test_initialization_identical(self):
        """Test both classes initialize with same attributes."""
        orig = OriginalToken(position=5, text="hello", tag="NN")
        modern = ModernToken(position=5, text="hello", tag="NN")

        assert orig.position == modern.position
        assert orig.text == modern.text
        assert orig.tag == modern.tag
        assert orig.dependents == modern.dependents  # both None
        assert orig.gov == modern.gov  # both None
        assert orig.gov_rel == modern.gov_rel  # both None
        # Both should have a ud attribute, but they may be different classes
        # What matters is they produce the same behavior, not that they're the same class
        assert hasattr(orig, 'ud')
        assert hasattr(modern, 'ud')

    def test_repr_identical(self):
        """Test both classes have same string representation."""
        orig = OriginalToken(position=3, text="cat", tag="NN")
        modern = ModernToken(position=3, text="cat", tag="NN")

        assert repr(orig) == repr(modern) == "cat/3"

    def test_isword_identical(self):
        """Test isword property behaves identically."""
        # non-punctuation
        orig1 = OriginalToken(position=0, text="word", tag="NN")
        modern1 = ModernToken(position=0, text="word", tag="NN")
        assert orig1.isword == modern1.isword == True

        # punctuation
        orig2 = OriginalToken(position=1, text=".", tag=postag.PUNCT)
        modern2 = ModernToken(position=1, text=".", tag=postag.PUNCT)
        assert orig2.isword == modern2.isword == False

    def test_argument_like_identical(self):
        """Test argument_like method behaves identically."""
        orig = OriginalToken(position=0, text="cat", tag="NN")
        modern = ModernToken(position=0, text="cat", tag="NN")

        # without gov_rel
        assert orig.argument_like() == modern.argument_like() == False

        # with subject relation
        orig.gov_rel = dep_v1.nsubj
        modern.gov_rel = dep_v1.nsubj
        assert orig.argument_like() == modern.argument_like() == True

        # with non-argument relation
        orig.gov_rel = dep_v1.aux
        modern.gov_rel = dep_v1.aux
        assert orig.argument_like() == modern.argument_like() == False

    def test_hard_to_find_arguments_identical(self):
        """Test hard_to_find_arguments method behaves identically."""
        orig = OriginalToken(position=0, text="helpful", tag="JJ")
        modern = ModernToken(position=0, text="helpful", tag="JJ")

        # Both should raise TypeError with None dependents
        orig.gov_rel = dep_v1.amod
        modern.gov_rel = dep_v1.amod

        with pytest.raises(TypeError):
            orig.hard_to_find_arguments()
        with pytest.raises(TypeError):
            modern.hard_to_find_arguments()

        # with empty dependents
        orig.dependents = []
        modern.dependents = []
        assert orig.hard_to_find_arguments() == modern.hard_to_find_arguments() == True

        # with subject dependent
        dep_token = OriginalToken(position=1, text="cat", tag="NN")
        edge = DepTriple(rel=dep_v1.nsubj, gov=orig, dep=dep_token)
        orig.dependents = [edge]
        modern.dependents = [edge]
        assert orig.hard_to_find_arguments() == modern.hard_to_find_arguments() == False

    def test_with_dep_v2_identical(self):
        """Test both classes work identically with dep_v2."""
        orig = OriginalToken(position=0, text="test", tag="NN", ud=dep_v2)
        modern = ModernToken(position=0, text="test", tag="NN", ud=dep_v2)

        assert orig.ud == modern.ud == dep_v2

        # test methods work with dep_v2
        orig.gov_rel = dep_v2.nsubj
        modern.gov_rel = dep_v2.nsubj
        assert orig.argument_like() == modern.argument_like() == True

    def test_no_equality_methods(self):
        """Test that neither class defines equality methods."""
        orig1 = OriginalToken(position=0, text="same", tag="NN")
        orig2 = OriginalToken(position=0, text="same", tag="NN")
        modern1 = ModernToken(position=0, text="same", tag="NN")
        modern2 = ModernToken(position=0, text="same", tag="NN")

        # neither defines __eq__, so different instances are not equal
        assert orig1 != orig2
        assert modern1 != modern2
        assert orig1 != modern1  # different classes

    def test_edge_cases_identical(self):
        """Test edge cases behave identically."""
        # negative position
        orig1 = OriginalToken(position=-1, text="ROOT", tag="ROOT")
        modern1 = ModernToken(position=-1, text="ROOT", tag="ROOT")
        assert repr(orig1) == repr(modern1) == "ROOT/-1"

        # empty text
        orig2 = OriginalToken(position=0, text="", tag="PUNCT")
        modern2 = ModernToken(position=0, text="", tag="PUNCT")
        assert repr(orig2) == repr(modern2) == "/0"

        # special characters
        orig3 = OriginalToken(position=1, text="$100", tag="CD")
        modern3 = ModernToken(position=1, text="$100", tag="CD")
        assert repr(orig3) == repr(modern3) == "$100/1"
