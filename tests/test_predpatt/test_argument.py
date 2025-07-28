"""
Tests for Argument class to document and verify current behavior.

Argument Class Documentation
============================

The Argument class represents an argument of a predicate, extracted from
a dependency parse.

Attributes
----------
root : Token
    The root token of the argument.
rules : list
    List of rules that led to this argument's extraction.
position : int
    Position of the root token (copied from root.position).
ud : module
    The Universal Dependencies module (dep_v1 or dep_v2).
tokens : list[Token]
    List of tokens that form the argument phrase.
share : bool
    Whether this argument is shared/borrowed (default: False).

Methods
-------
__init__(root, ud=dep_v1, rules=[])
    Initialize an Argument.
__repr__()
    Return string representation as 'Argument(root)'.
copy()
    Create a copy of the argument with copied rules and tokens lists.
reference()
    Create a reference (shared) copy with share=True and same tokens list.
is_reference()
    Return True if this is a reference (share=True).
isclausal()
    Check if argument is clausal (ccomp, csubj, csubjpass, xcomp).
phrase()
    Return the argument phrase as space-joined token texts.
coords()
    Get list of coordinate arguments (including self).

Token Collection and Ordering
----------------------------
1. Tokens are collected from the dependency subtree rooted at argument.root
2. The subtree is traversed breadth-first
3. Tokens are filtered by __arg_phrase() which excludes:
   - Tokens that are part of the predicate
   - Case markers (they go to predicate instead)
   - Appositives (if resolve_appos option is set)
   - Unknown dependencies (dep)
   - Special dependencies when arg root governs pred root
   - Conjunctions and coordination markers (if resolve_conj)
4. After collection, tokens are sorted by position using sort_by_position()
5. The phrase() method joins token texts with spaces in position order

Special Handling
---------------
- Clausal arguments: Identified by gov_rel in {ccomp, csubj, csubjpass, xcomp}
- Coordinated arguments: coords() expands conjunctions except for ccomp/csubj
- Reference arguments: Created with share=True for borrowed arguments
- Empty tokens list is considered broken (predicate.is_broken checks this)
"""

import pytest

from decomp.semantics.predpatt import rules
from decomp.semantics.predpatt.core.argument import Argument, sort_by_position
from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.rules import *
from decomp.semantics.predpatt.utils.ud_schema import dep_v1, dep_v2


R = rules  # Compatibility alias
from decomp.semantics.predpatt.parsing.udparse import DepTriple


class TestArgumentInitialization:
    """Test Argument initialization behavior."""

    def test_basic_initialization(self):
        """Test basic Argument creation with defaults."""
        root_token = Token(position=3, text="cat", tag="NN")
        arg = Argument(root_token)

        assert arg.root == root_token
        assert arg.rules == []
        assert arg.position == 3
        assert arg.ud == dep_v1
        assert arg.tokens == []
        assert arg.share is False

    def test_initialization_with_params(self):
        """Test Argument creation with all parameters."""
        root_token = Token(position=5, text="dog", tag="NN")
        rules = [R.g1, R.h1]

        arg = Argument(root_token, ud=dep_v2, rules=rules)

        assert arg.root == root_token
        assert arg.rules == rules
        assert arg.position == 5
        assert arg.ud == dep_v2
        assert arg.tokens == []
        assert arg.share is False

    def test_mutable_default_rules(self):
        """Test that default rules=[] doesn't cause sharing issues."""
        root1 = Token(position=1, text="one", tag="CD")
        root2 = Token(position=2, text="two", tag="CD")

        arg1 = Argument(root1)
        arg2 = Argument(root2)

        # Modify arg1's rules
        arg1.rules.append(R.g1)

        # arg2's rules should not be affected (modern implementation fixes the mutable default)
        assert len(arg1.rules) == 1
        assert len(arg2.rules) == 0  # Fixed - no sharing of mutable default


class TestArgumentRepr:
    """Test Argument string representation."""

    def test_repr_format(self):
        """Test __repr__ returns Argument(root)."""
        root = Token(position=2, text="apple", tag="NN")
        arg = Argument(root)

        assert repr(arg) == "Argument(apple/2)"

    def test_repr_with_special_tokens(self):
        """Test repr with various root tokens."""
        root1 = Token(position=0, text="", tag="PUNCT")
        arg1 = Argument(root1)
        assert repr(arg1) == "Argument(/0)"

        root2 = Token(position=-1, text="ROOT", tag="ROOT")
        arg2 = Argument(root2)
        assert repr(arg2) == "Argument(ROOT/-1)"


class TestArgumentCopy:
    """Test Argument copy and reference methods."""

    def test_copy_basic(self):
        """Test copying an argument."""
        root = Token(position=3, text="cat", tag="NN")
        arg = Argument(root, rules=[R.g1])
        arg.tokens = [root, Token(position=2, text="the", tag="DT")]

        copy = arg.copy()

        # verify attributes are copied
        assert copy.root == arg.root  # same token reference
        assert copy.rules == arg.rules
        assert copy.rules is not arg.rules  # different list
        assert copy.position == arg.position
        assert copy.ud == arg.ud
        assert copy.tokens == arg.tokens
        assert copy.tokens is not arg.tokens  # different list
        assert copy.share is False  # not set by copy()

    def test_reference_creation(self):
        """Test creating a reference (shared) argument."""
        root = Token(position=3, text="cat", tag="NN")
        arg = Argument(root, rules=[R.g1])
        arg.tokens = [root]

        ref = arg.reference()

        # verify reference attributes
        assert ref.root == arg.root
        assert ref.rules == arg.rules
        assert ref.rules is not arg.rules  # different list
        assert ref.tokens == arg.tokens
        assert ref.tokens is arg.tokens  # SAME list (not copied)
        assert ref.share is True  # marked as shared

    def test_is_reference(self):
        """Test is_reference method."""
        root = Token(position=1, text="test", tag="NN")

        arg = Argument(root)
        assert arg.is_reference() is False

        ref = arg.reference()
        assert ref.is_reference() is True

        # manually setting share
        arg.share = True
        assert arg.is_reference() is True


class TestArgumentIsClausal:
    """Test isclausal method."""

    def test_clausal_relations(self):
        """Test clausal dependency relations."""
        root = Token(position=5, text="said", tag="VBD")
        arg = Argument(root)

        # not clausal without gov_rel
        assert arg.isclausal() is False

        # clausal relations
        for rel in [dep_v1.ccomp, dep_v1.csubj, dep_v1.csubjpass, dep_v1.xcomp]:
            root.gov_rel = rel
            assert arg.isclausal() is True

    def test_non_clausal_relations(self):
        """Test non-clausal dependency relations."""
        root = Token(position=3, text="cat", tag="NN")
        arg = Argument(root)

        # non-clausal relations
        for rel in [dep_v1.nsubj, dep_v1.dobj, dep_v1.nmod, dep_v1.amod]:
            root.gov_rel = rel
            assert arg.isclausal() is False

    def test_with_dep_v2(self):
        """Test isclausal with dep_v2."""
        root = Token(position=5, text="said", tag="VBD", ud=dep_v2)
        arg = Argument(root, ud=dep_v2)

        root.gov_rel = dep_v2.ccomp
        assert arg.isclausal() is True


class TestArgumentPhrase:
    """Test phrase generation."""

    def test_empty_phrase(self):
        """Test phrase with no tokens."""
        root = Token(position=2, text="cat", tag="NN")
        arg = Argument(root)

        assert arg.phrase() == ""

    def test_single_token_phrase(self):
        """Test phrase with one token."""
        root = Token(position=2, text="cat", tag="NN")
        arg = Argument(root)
        arg.tokens = [root]

        assert arg.phrase() == "cat"

    def test_multi_token_phrase(self):
        """Test phrase with multiple tokens."""
        root = Token(position=2, text="cat", tag="NN")
        det = Token(position=1, text="the", tag="DT")
        adj = Token(position=3, text="black", tag="JJ")

        arg = Argument(root)
        arg.tokens = [root, det, adj]

        # tokens are joined by space in the order they appear in the list
        assert arg.phrase() == "cat the black"

    def test_phrase_with_special_characters(self):
        """Test phrase with punctuation and special tokens."""
        root = Token(position=2, text="said", tag="VBD")
        quote1 = Token(position=1, text='"', tag="``")
        word = Token(position=3, text="hello", tag="UH")
        quote2 = Token(position=4, text='"', tag="''")

        arg = Argument(root)
        arg.tokens = [quote1, root, word, quote2]

        assert arg.phrase() == '" said hello "'

    def test_phrase_order_matters(self):
        """Test that token order in list affects phrase."""
        t1 = Token(position=1, text="A", tag="DT")
        t2 = Token(position=2, text="B", tag="NN")
        t3 = Token(position=3, text="C", tag="NN")

        arg = Argument(t2)

        # different orders produce different phrases
        arg.tokens = [t1, t2, t3]
        assert arg.phrase() == "A B C"

        arg.tokens = [t3, t1, t2]
        assert arg.phrase() == "C A B"

        arg.tokens = [t2, t3, t1]
        assert arg.phrase() == "B C A"


class TestArgumentCoords:
    """Test coords method for coordinated arguments."""

    def test_coords_no_conjunctions(self):
        """Test coords with no conjunctions returns just self."""
        root = Token(position=3, text="cat", tag="NN")
        root.dependents = []  # must initialize to empty list
        arg = Argument(root)

        coords = arg.coords()

        assert len(coords) == 1
        assert coords[0] == arg

    def test_coords_with_conjunction(self):
        """Test coords with conjunction."""
        # Setup: "cats and dogs"
        root = Token(position=1, text="cats", tag="NNS")
        conj_token = Token(position=3, text="dogs", tag="NNS")

        # create conjunction edge
        edge = DepTriple(rel=dep_v1.conj, gov=root, dep=conj_token)
        root.dependents = [edge]

        arg = Argument(root)
        coords = arg.coords()

        assert len(coords) == 2
        assert coords[0] == arg  # original argument
        assert coords[1].root == conj_token  # conjunction argument
        assert len(coords[1].rules) == 1
        assert isinstance(coords[1].rules[0], R.m)  # m() rule applied

    def test_coords_excluded_for_clausal(self):
        """Test coords doesn't expand ccomp/csubj arguments."""
        root = Token(position=5, text="said", tag="VBD")
        conj_token = Token(position=8, text="believed", tag="VBD")

        # create conjunction edge
        edge = DepTriple(rel=dep_v1.conj, gov=root, dep=conj_token)
        root.dependents = [edge]

        # test with ccomp
        root.gov_rel = dep_v1.ccomp
        arg = Argument(root)
        coords = arg.coords()

        assert len(coords) == 1  # no expansion
        assert coords[0] == arg

        # test with csubj
        root.gov_rel = dep_v1.csubj
        coords = arg.coords()

        assert len(coords) == 1  # no expansion
        assert coords[0] == arg

    def test_coords_sorted_by_position(self):
        """Test coords are sorted by position."""
        # "apples, oranges and bananas"
        root = Token(position=1, text="apples", tag="NNS")
        conj1 = Token(position=3, text="oranges", tag="NNS")
        conj2 = Token(position=5, text="bananas", tag="NNS")

        # create edges (order matters to test sorting)
        edge1 = DepTriple(rel=dep_v1.conj, gov=root, dep=conj2)  # add bananas first
        edge2 = DepTriple(rel=dep_v1.conj, gov=root, dep=conj1)  # then oranges
        root.dependents = [edge1, edge2]

        arg = Argument(root)
        coords = arg.coords()

        assert len(coords) == 3
        # verify sorted by position
        assert coords[0].position == 1  # apples
        assert coords[1].position == 3  # oranges
        assert coords[2].position == 5  # bananas
        # verify all conjuncts have m() rule
        assert all(isinstance(c.rules[0], R.m) for c in coords[1:])

    def test_coords_with_no_dependents(self):
        """Test coords when root has None dependents."""
        root = Token(position=1, text="test", tag="NN")
        root.dependents = None  # quirk: can be None instead of []

        arg = Argument(root)

        # should raise TypeError since None is not iterable
        with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
            arg.coords()


class TestArgumentTokenOrdering:
    """Test how tokens are ordered in phrases."""

    def test_tokens_join_order(self):
        """Test that phrase joins tokens in list order, not position order."""
        # Create tokens with positions: 1, 3, 2
        t1 = Token(position=1, text="the", tag="DT")
        t2 = Token(position=3, text="cat", tag="NN")
        t3 = Token(position=2, text="big", tag="JJ")

        arg = Argument(t2)  # root is "cat"

        # Add tokens in non-position order
        arg.tokens = [t2, t3, t1]  # cat, big, the

        # phrase joins in list order, NOT position order
        assert arg.phrase() == "cat big the"

        # If tokens were sorted by position first
        arg.tokens = sort_by_position(arg.tokens)
        assert arg.phrase() == "the big cat"

    def test_empty_text_tokens(self):
        """Test phrase with empty text tokens."""
        t1 = Token(position=1, text="", tag="PUNCT")
        t2 = Token(position=2, text="word", tag="NN")
        t3 = Token(position=3, text="", tag="PUNCT")

        arg = Argument(t2)
        arg.tokens = [t1, t2, t3]

        # empty texts are included (with spaces)
        assert arg.phrase() == " word "


class TestArgumentEdgeCases:
    """Test edge cases and unusual behaviors."""

    def test_mutable_tokens_list(self):
        """Test that tokens list is mutable and shared references matter."""
        root = Token(position=1, text="test", tag="NN")
        arg1 = Argument(root)
        arg2 = Argument(root)

        # each has its own tokens list
        arg1.tokens.append(root)
        assert len(arg1.tokens) == 1
        assert len(arg2.tokens) == 0

        # but reference() shares the list
        ref = arg1.reference()
        ref.tokens.append(Token(position=2, text="more", tag="JJR"))

        assert len(arg1.tokens) == 2  # affected!
        assert len(ref.tokens) == 2  # same list

    def test_position_from_root(self):
        """Test that position is always copied from root."""
        root = Token(position=42, text="answer", tag="NN")
        arg = Argument(root)

        assert arg.position == 42

        # changing root position doesn't affect argument
        root.position = 0
        assert arg.position == 42  # unchanged

    def test_rules_modification(self):
        """Test modifying rules list."""
        root = Token(position=1, text="test", tag="NN")
        initial_rules = [R.g1]
        arg = Argument(root, rules=initial_rules)

        # modify argument's rules
        arg.rules.append(R.h1)

        # original list is also modified (same reference)
        assert len(initial_rules) == 2
        assert initial_rules[1] == R.h1
