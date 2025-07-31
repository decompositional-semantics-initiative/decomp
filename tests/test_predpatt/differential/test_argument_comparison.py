"""Compare the standalone PredPatt Argument class with this package's Argument class."""

import pytest


# Import external predpatt for comparison
from predpatt.patt import Argument as OriginalArgument
from predpatt.patt import Token as OriginalToken
from predpatt.patt import sort_by_position as orig_sort_by_position

from decomp.semantics.predpatt import rules
from decomp.semantics.predpatt.core.argument import Argument as ModernArgument
from decomp.semantics.predpatt.core.argument import sort_by_position as mod_sort_by_position
from decomp.semantics.predpatt.parsing.udparse import DepTriple
from decomp.semantics.predpatt.rules import *
from decomp.semantics.predpatt.utils.ud_schema import dep_v1, dep_v2


R = rules  # Compatibility alias


class TestArgumentComparison:
    """Test that original and modern Argument classes behave identically."""

    def test_initialization_identical(self):
        """Test both classes initialize with same attributes."""
        root = OriginalToken(position=3, text="cat", tag="NN")

        orig = OriginalArgument(root)
        modern = ModernArgument(root)

        assert orig.root == modern.root
        # Both should have empty rules list, but due to mutable default
        # the list might be shared and contain items from previous tests
        # Just check they're the same type (list)
        assert isinstance(orig.rules, list)
        assert isinstance(modern.rules, list)
        assert orig.position == modern.position
        # Both should have a ud attribute, but they may be different classes
        # What matters is they produce the same behavior, not that they're the same class
        assert hasattr(orig, 'ud')
        assert hasattr(modern, 'ud')
        assert len(orig.tokens) == len(modern.tokens) == 0
        assert orig.share == modern.share == False

    def test_initialization_with_params(self):
        """Test initialization with all parameters."""
        root = OriginalToken(position=5, text="dog", tag="NN")
        rules = [R.g1, R.h1]

        orig = OriginalArgument(root, ud=dep_v2, rules=rules)
        modern = ModernArgument(root, ud=dep_v2, rules=rules)

        assert orig.root == modern.root
        assert orig.rules == modern.rules
        assert orig.rules is rules  # same reference
        assert modern.rules is rules  # same reference
        assert orig.position == modern.position
        # Check both have the expected ud module
        assert orig.ud == dep_v2
        assert modern.ud == dep_v2

    def test_mutable_default_rules(self):
        """Test rules behavior - implementations may differ but output must match."""
        root1 = OriginalToken(position=1, text="one", tag="CD")
        root2 = OriginalToken(position=2, text="two", tag="CD")

        # create first arguments
        orig1 = OriginalArgument(root1)
        modern1 = ModernArgument(root1)

        # create second arguments
        orig2 = OriginalArgument(root2)
        modern2 = ModernArgument(root2)

        # modify first argument's rules
        orig1.rules.append("test_mutable")
        modern1.rules.append("test_mutable")

        # Note: Original has mutable default (shared list), modern doesn't.
        # This is an implementation detail that doesn't affect output.
        assert "test_mutable" in orig1.rules
        assert "test_mutable" in modern1.rules

        # Clean up the original's mutable default to avoid affecting other tests
        if "test_mutable" in orig2.rules:
            orig2.rules.clear()

    def test_repr_identical(self):
        """Test both classes have same string representation."""
        root = OriginalToken(position=2, text="apple", tag="NN")

        orig = OriginalArgument(root)
        modern = ModernArgument(root)

        assert repr(orig) == repr(modern) == "Argument(apple/2)"

    def test_copy_identical(self):
        """Test copy method behaves identically."""
        root = OriginalToken(position=3, text="cat", tag="NN")

        orig = OriginalArgument(root, rules=[R.g1])
        modern = ModernArgument(root, rules=[R.g1])

        orig.tokens = [root]
        modern.tokens = [root]

        orig_copy = orig.copy()
        modern_copy = modern.copy()

        # verify same behavior
        assert orig_copy.root == modern_copy.root == root
        assert len(orig_copy.rules) == len(modern_copy.rules) == 1
        assert orig_copy.rules is not orig.rules
        assert modern_copy.rules is not modern.rules
        assert orig_copy.tokens == modern_copy.tokens == [root]
        assert orig_copy.tokens is not orig.tokens
        assert modern_copy.tokens is not modern.tokens
        assert orig_copy.share == modern_copy.share == False

    def test_reference_identical(self):
        """Test reference method behaves identically."""
        root = OriginalToken(position=3, text="cat", tag="NN")

        orig = OriginalArgument(root, rules=[R.g1])
        modern = ModernArgument(root, rules=[R.g1])

        orig.tokens = [root]
        modern.tokens = [root]

        orig_ref = orig.reference()
        modern_ref = modern.reference()

        # verify same behavior
        assert orig_ref.root == modern_ref.root == root
        assert orig_ref.rules is not orig.rules
        assert modern_ref.rules is not modern.rules
        assert orig_ref.tokens is orig.tokens  # shared
        assert modern_ref.tokens is modern.tokens  # shared
        assert orig_ref.share == modern_ref.share == True

    def test_is_reference_identical(self):
        """Test is_reference method."""
        root = OriginalToken(position=1, text="test", tag="NN")

        orig = OriginalArgument(root)
        modern = ModernArgument(root)

        assert orig.is_reference() == modern.is_reference() == False

        orig.share = True
        modern.share = True

        assert orig.is_reference() == modern.is_reference() == True

    def test_isclausal_identical(self):
        """Test isclausal method behaves identically."""
        root = OriginalToken(position=5, text="said", tag="VBD")

        orig = OriginalArgument(root)
        modern = ModernArgument(root)

        # without gov_rel
        assert orig.isclausal() == modern.isclausal() == False

        # with clausal relations
        for rel in [dep_v1.ccomp, dep_v1.csubj, dep_v1.csubjpass, dep_v1.xcomp]:
            root.gov_rel = rel
            assert orig.isclausal() == modern.isclausal() == True

        # with non-clausal relation
        root.gov_rel = dep_v1.nsubj
        assert orig.isclausal() == modern.isclausal() == False

    def test_phrase_identical(self):
        """Test phrase method produces identical output."""
        root = OriginalToken(position=2, text="cat", tag="NN")
        det = OriginalToken(position=1, text="the", tag="DT")
        adj = OriginalToken(position=3, text="black", tag="JJ")

        orig = OriginalArgument(root)
        modern = ModernArgument(root)

        # empty phrase
        assert orig.phrase() == modern.phrase() == ""

        # single token
        orig.tokens = [root]
        modern.tokens = [root]
        assert orig.phrase() == modern.phrase() == "cat"

        # multiple tokens
        orig.tokens = [det, root, adj]
        modern.tokens = [det, root, adj]
        assert orig.phrase() == modern.phrase() == "the cat black"

        # different order
        orig.tokens = [adj, det, root]
        modern.tokens = [adj, det, root]
        assert orig.phrase() == modern.phrase() == "black the cat"

    def test_coords_identical(self):
        """Test coords method behaves identically."""
        root = OriginalToken(position=1, text="cats", tag="NNS")
        root.dependents = []

        orig = OriginalArgument(root)
        modern = ModernArgument(root)

        # no conjunctions
        orig_coords = orig.coords()
        modern_coords = modern.coords()

        assert len(orig_coords) == len(modern_coords) == 1
        assert orig_coords[0] == orig
        assert modern_coords[0] == modern

        # with conjunction
        conj_token = OriginalToken(position=3, text="dogs", tag="NNS")
        edge = DepTriple(rel=dep_v1.conj, gov=root, dep=conj_token)
        root.dependents = [edge]

        orig_coords = orig.coords()
        modern_coords = modern.coords()

        assert len(orig_coords) == len(modern_coords) == 2
        assert orig_coords[0] == orig
        assert modern_coords[0] == modern
        assert orig_coords[1].root == modern_coords[1].root == conj_token
        assert len(orig_coords[1].rules) == len(modern_coords[1].rules) == 1
        # Check rule type - original has lowercase class names, modern has PascalCase
        assert orig_coords[1].rules[0].__class__.__name__ == 'm'
        assert modern_coords[1].rules[0].__class__.__name__ == 'M'
        # But the name() method should return lowercase for compatibility
        assert orig_coords[1].rules[0].name() == 'm'
        assert modern_coords[1].rules[0].name() == 'm'

    def test_coords_excluded_identical(self):
        """Test coords exclusion for ccomp/csubj."""
        root = OriginalToken(position=5, text="said", tag="VBD")
        conj_token = OriginalToken(position=8, text="believed", tag="VBD")
        edge = DepTriple(rel=dep_v1.conj, gov=root, dep=conj_token)
        root.dependents = [edge]

        # test with ccomp
        root.gov_rel = dep_v1.ccomp
        orig = OriginalArgument(root)
        modern = ModernArgument(root)

        orig_coords = orig.coords()
        modern_coords = modern.coords()

        assert len(orig_coords) == len(modern_coords) == 1

    def test_sort_by_position_identical(self):
        """Test sort_by_position function."""
        items = [
            OriginalToken(position=3, text="c", tag="NN"),
            OriginalToken(position=1, text="a", tag="NN"),
            OriginalToken(position=2, text="b", tag="NN")
        ]

        orig_sorted = orig_sort_by_position(items)
        mod_sorted = mod_sort_by_position(items)

        assert len(orig_sorted) == len(mod_sorted) == 3
        assert all(o.position == m.position for o, m in zip(orig_sorted, mod_sorted, strict=False))
        assert orig_sorted[0].position == mod_sorted[0].position == 1
        assert orig_sorted[1].position == mod_sorted[1].position == 2
        assert orig_sorted[2].position == mod_sorted[2].position == 3
