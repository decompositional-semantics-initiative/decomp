"""
Run all original Token tests against the modernized Token class.

This file contains a copy of all tests from test_token.py but imports
the modernized Token to verify identical behavior.
"""

import pytest
from decomp.semantics.predpatt.core.token import Token  # Modern Token
from decomp.semantics.predpatt.util.ud import dep_v1, dep_v2, postag
from decomp.semantics.predpatt.UDParse import DepTriple


class TestTokenInitialization:
    """Test Token initialization behavior."""
    
    def test_basic_initialization(self):
        """Test basic Token creation with required parameters."""
        token = Token(position=0, text="hello", tag="NN")
        
        assert token.position == 0
        assert token.text == "hello"
        assert token.tag == "NN"
        assert token.dependents is None
        assert token.gov is None
        assert token.gov_rel is None
        assert token.ud == dep_v1  # default
    
    def test_initialization_with_dep_v2(self):
        """Test Token creation with explicit UD version."""
        token = Token(position=5, text="world", tag="NN", ud=dep_v2)
        
        assert token.position == 5
        assert token.text == "world"
        assert token.tag == "NN"
        assert token.ud == dep_v2
    
    def test_initialization_with_various_types(self):
        """Test Token handles various input types."""
        # position can be any integer
        token1 = Token(position=-1, text="ROOT", tag="ROOT")
        assert token1.position == -1
        
        # text can be empty string
        token2 = Token(position=0, text="", tag="PUNCT")
        assert token2.text == ""
        
        # tag can be any string
        token3 = Token(position=1, text="test", tag="CUSTOM_TAG")
        assert token3.tag == "CUSTOM_TAG"


class TestTokenRepr:
    """Test Token string representation."""
    
    def test_repr_format(self):
        """Test __repr__ returns text/position format."""
        token = Token(position=3, text="cat", tag="NN")
        assert repr(token) == "cat/3"
    
    def test_repr_with_special_characters(self):
        """Test __repr__ with special characters in text."""
        token1 = Token(position=0, text="hello/world", tag="NN")
        assert repr(token1) == "hello/world/0"
        
        token2 = Token(position=1, text="", tag="PUNCT")
        assert repr(token2) == "/1"
        
        token3 = Token(position=2, text="$100", tag="CD")
        assert repr(token3) == "$100/2"


class TestTokenIsWord:
    """Test the isword property."""
    
    def test_isword_true_for_non_punct(self):
        """Test isword returns True for non-punctuation."""
        token = Token(position=0, text="word", tag="NN")
        assert token.isword is True
        
        token2 = Token(position=1, text="run", tag="VB")
        assert token2.isword is True
    
    def test_isword_false_for_punct(self):
        """Test isword returns False for punctuation."""
        token = Token(position=0, text=".", tag=postag.PUNCT)
        assert token.isword is False
        
        token2 = Token(position=1, text=",", tag="PUNCT")
        assert token2.isword is False
    
    def test_isword_with_different_ud_versions(self):
        """Test isword works with both UD versions."""
        token1 = Token(position=0, text="word", tag="NN", ud=dep_v1)
        assert token1.isword is True
        
        token2 = Token(position=0, text="word", tag="NN", ud=dep_v2)
        assert token2.isword is True


class TestTokenArgumentLike:
    """Test the argument_like method."""
    
    def test_argument_like_without_gov_rel(self):
        """Test argument_like when gov_rel is None."""
        token = Token(position=0, text="cat", tag="NN")
        # gov_rel is None, so it won't be in ARG_LIKE set
        assert token.argument_like() is False
    
    def test_argument_like_with_arg_like_relations(self):
        """Test argument_like with various argument-like relations."""
        token = Token(position=0, text="cat", tag="NN")
        
        # test subject relations
        token.gov_rel = dep_v1.nsubj
        assert token.argument_like() is True
        
        token.gov_rel = dep_v1.csubj
        assert token.argument_like() is True
        
        # test object relations
        token.gov_rel = dep_v1.dobj
        assert token.argument_like() is True
        
        token.gov_rel = dep_v1.iobj
        assert token.argument_like() is True
        
        # test nmod relations
        token.gov_rel = dep_v1.nmod
        assert token.argument_like() is True
    
    def test_argument_like_with_non_arg_relations(self):
        """Test argument_like with non-argument relations."""
        token = Token(position=0, text="cat", tag="NN")
        
        token.gov_rel = "root"  # root is not a constant in dep_v1
        assert token.argument_like() is False
        
        token.gov_rel = dep_v1.aux
        assert token.argument_like() is False
        
        token.gov_rel = dep_v1.cop
        assert token.argument_like() is False


class TestTokenHardToFindArguments:
    """Test the hard_to_find_arguments method."""
    
    def test_hard_to_find_arguments_with_none_dependents(self):
        """Test method handles None dependents gracefully."""
        token = Token(position=0, text="helpful", tag="JJ")
        token.gov_rel = dep_v1.amod
        
        # This should raise TypeError because dependents is None
        with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
            token.hard_to_find_arguments()
    
    def test_hard_to_find_arguments_with_empty_dependents(self):
        """Test with empty dependents list."""
        token = Token(position=0, text="helpful", tag="JJ")
        token.dependents = []
        token.gov_rel = dep_v1.amod
        
        # No dependents with SUBJ/OBJ, and gov_rel is in HARD_TO_FIND_ARGS
        assert token.hard_to_find_arguments() is True
    
    def test_hard_to_find_arguments_with_subj_dependent(self):
        """Test returns False when dependent has subject relation."""
        token = Token(position=0, text="helpful", tag="JJ")
        token.dependents = []
        
        # create a mock dependent edge with subject relation
        dep_token = Token(position=1, text="cat", tag="NN")
        edge = DepTriple(rel=dep_v1.nsubj, gov=token, dep=dep_token)
        token.dependents = [edge]
        
        token.gov_rel = dep_v1.amod
        assert token.hard_to_find_arguments() is False
    
    def test_hard_to_find_arguments_with_obj_dependent(self):
        """Test returns False when dependent has object relation."""
        token = Token(position=0, text="helpful", tag="JJ")
        token.dependents = []
        
        # create a mock dependent edge with object relation
        dep_token = Token(position=1, text="thing", tag="NN")
        edge = DepTriple(rel=dep_v1.dobj, gov=token, dep=dep_token)
        token.dependents = [edge]
        
        token.gov_rel = dep_v1.amod
        assert token.hard_to_find_arguments() is False
    
    def test_hard_to_find_arguments_various_gov_rels(self):
        """Test with various governor relations."""
        token = Token(position=0, text="test", tag="NN")
        token.dependents = []
        
        # test relations in HARD_TO_FIND_ARGS
        for rel in [dep_v1.amod, dep_v1.dep, dep_v1.conj, dep_v1.acl, 
                    dep_v1.aclrelcl, dep_v1.advcl]:
            token.gov_rel = rel
            assert token.hard_to_find_arguments() is True
        
        # test relations not in HARD_TO_FIND_ARGS
        token.gov_rel = dep_v1.nsubj
        assert token.hard_to_find_arguments() is False
        
        token.gov_rel = "root"  # root is not a constant in dep_v1
        assert token.hard_to_find_arguments() is False


class TestTokenWithDependencies:
    """Test Token behavior when integrated with dependency structure."""
    
    def test_token_as_governor(self):
        """Test token with dependents."""
        gov_token = Token(position=1, text="eat", tag="VB")
        dep_token1 = Token(position=0, text="I", tag="PRP")
        dep_token2 = Token(position=2, text="apples", tag="NNS")
        
        # set up dependency edges
        edge1 = DepTriple(rel=dep_v1.nsubj, gov=gov_token, dep=dep_token1)
        edge2 = DepTriple(rel=dep_v1.dobj, gov=gov_token, dep=dep_token2)
        
        gov_token.dependents = [edge1, edge2]
        
        # verify structure
        assert len(gov_token.dependents) == 2
        assert gov_token.dependents[0].dep == dep_token1
        assert gov_token.dependents[1].dep == dep_token2
    
    def test_token_as_dependent(self):
        """Test token with governor."""
        gov_token = Token(position=1, text="eat", tag="VB")
        dep_token = Token(position=0, text="I", tag="PRP")
        
        # set up governor relationship
        dep_token.gov = gov_token
        dep_token.gov_rel = dep_v1.nsubj
        
        assert dep_token.gov == gov_token
        assert dep_token.gov_rel == dep_v1.nsubj
        assert dep_token.argument_like() is True


class TestTokenEdgeCases:
    """Test edge cases and unusual behaviors."""
    
    def test_dependents_none_vs_empty_list(self):
        """Test the quirk where dependents is None instead of []."""
        token = Token(position=0, text="test", tag="NN")
        
        # initially None, not empty list
        assert token.dependents is None
        assert token.dependents != []
    
    def test_no_equality_methods(self):
        """Test that Token doesn't define __eq__ or __hash__."""
        token1 = Token(position=0, text="same", tag="NN")
        token2 = Token(position=0, text="same", tag="NN")
        
        # tokens with same attributes are not equal (object identity)
        assert token1 != token2
        assert token1 is not token2
        
        # can be used in sets/dicts (uses object id for hash)
        token_set = {token1, token2}
        assert len(token_set) == 2
    
    def test_position_can_be_negative(self):
        """Test that position can be negative (e.g., for ROOT)."""
        token = Token(position=-1, text="ROOT", tag="ROOT")
        assert token.position == -1
        assert repr(token) == "ROOT/-1"