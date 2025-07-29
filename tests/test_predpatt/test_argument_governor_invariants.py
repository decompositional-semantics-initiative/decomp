"""
Tests for predicate type governor invariants.

These tests verify that AMOD, APPOS, and POSS predicates correctly enforce
the invariant that they must have governors, since they are created from
dependency relations (amod, appos, nmod:poss) which by definition have governors.
"""

import pytest
from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.core.predicate import Predicate, AMOD, APPOS, POSS
from decomp.semantics.predpatt.extraction.engine import PredPattEngine
from decomp.semantics.predpatt.parsing.udparse import UDParse
from decomp.semantics.predpatt.utils.ud_schema import dep_v1


class TestPredicateGovernorInvariants:
    """Test that special predicate types enforce governor invariants."""
    
    def test_amod_predicate_requires_governor(self):
        """AMOD predicates must have governors - should raise ValueError if None."""
        # Create a token without a governor
        root_token = Token(1, "big", "ADJ")
        # Manually set gov to None (simulating corrupted data)
        root_token.gov = None
        
        # Create AMOD predicate
        predicate = Predicate(root_token, type_=AMOD)
        
        # Create a minimal engine to test argument extraction
        engine = PredPattEngine.__new__(PredPattEngine)  # Create without __init__
        engine.ud = dep_v1
        engine.options = type('Options', (), {})()
        
        # Should raise ValueError when trying to extract arguments
        with pytest.raises(ValueError, match="AMOD predicate .* must have a governor but gov is None"):
            engine.argument_extract(predicate)
    
    def test_appos_predicate_requires_governor(self):
        """APPOS predicates must have governors - should raise ValueError if None."""
        # Create a token without a governor
        root_token = Token(2, "friend", "NOUN")
        root_token.gov = None
        
        # Create APPOS predicate
        predicate = Predicate(root_token, type_=APPOS)
        
        # Create a minimal engine to test argument extraction
        engine = PredPattEngine.__new__(PredPattEngine)
        engine.ud = dep_v1
        engine.options = type('Options', (), {})()
        
        # Should raise ValueError when trying to extract arguments
        with pytest.raises(ValueError, match="APPOS predicate .* must have a governor but gov is None"):
            engine.argument_extract(predicate)
    
    def test_poss_predicate_requires_governor(self):
        """POSS predicates must have governors - should raise ValueError if None."""
        # Create a token without a governor
        root_token = Token(3, "'s", "POS")
        root_token.gov = None
        
        # Create POSS predicate
        predicate = Predicate(root_token, type_=POSS)
        
        # Create a minimal engine to test argument extraction
        engine = PredPattEngine.__new__(PredPattEngine)
        engine.ud = dep_v1
        engine.options = type('Options', (), {})()
        
        # Should raise ValueError when trying to extract arguments
        with pytest.raises(ValueError, match="POSS predicate .* must have a governor but gov is None"):
            engine.argument_extract(predicate)
    
    def test_normal_predicate_allows_no_governor(self):
        """NORMAL predicates can have no governor (e.g., root of sentence)."""
        # Create a token without a governor (normal for sentence root)
        root_token = Token(0, "runs", "VERB")
        root_token.gov = None
        root_token.dependents = []
        
        # Create NORMAL predicate (default type)
        predicate = Predicate(root_token)  # type_ defaults to NORMAL
        
        # Create a minimal engine to test argument extraction
        engine = PredPattEngine.__new__(PredPattEngine)
        engine.ud = dep_v1
        engine.options = type('Options', (), {})()
        
        # Should not raise any error
        arguments = engine.argument_extract(predicate)
        assert isinstance(arguments, list)
    
    def test_amod_with_valid_governor_works(self):
        """AMOD predicates with valid governors should work normally."""
        # Create governor token
        gov_token = Token(0, "dog", "NOUN")
        
        # Create AMOD token with governor
        root_token = Token(1, "big", "ADJ")
        root_token.gov = gov_token
        root_token.dependents = []
        
        # Create AMOD predicate
        predicate = Predicate(root_token, type_=AMOD)
        
        # Create a minimal engine to test argument extraction
        engine = PredPattEngine.__new__(PredPattEngine)
        engine.ud = dep_v1
        engine.options = type('Options', (), {})()
        
        # Should work without errors and include governor as argument
        arguments = engine.argument_extract(predicate)
        assert len(arguments) >= 1
        assert any(arg.root == gov_token for arg in arguments)
    
    def test_appos_with_valid_governor_works(self):
        """APPOS predicates with valid governors should work normally."""
        # Create governor token
        gov_token = Token(0, "John", "PROPN")
        
        # Create APPOS token with governor
        root_token = Token(2, "friend", "NOUN")
        root_token.gov = gov_token
        root_token.dependents = []
        
        # Create APPOS predicate
        predicate = Predicate(root_token, type_=APPOS)
        
        # Create a minimal engine to test argument extraction
        engine = PredPattEngine.__new__(PredPattEngine)
        engine.ud = dep_v1
        engine.options = type('Options', (), {})()
        
        # Should work without errors and include governor as argument
        arguments = engine.argument_extract(predicate)
        assert len(arguments) >= 1
        assert any(arg.root == gov_token for arg in arguments)
    
    def test_poss_with_valid_governor_works(self):
        """POSS predicates with valid governors should work normally."""
        # Create governor token
        gov_token = Token(0, "car", "NOUN")
        
        # Create POSS token with governor
        root_token = Token(2, "'s", "POS")
        root_token.gov = gov_token
        root_token.dependents = []
        
        # Create POSS predicate
        predicate = Predicate(root_token, type_=POSS)
        
        # Create a minimal engine to test argument extraction
        engine = PredPattEngine.__new__(PredPattEngine)
        engine.ud = dep_v1
        engine.options = type('Options', (), {})()
        
        # Should work without errors and include both governor and self as arguments
        arguments = engine.argument_extract(predicate)
        assert len(arguments) >= 2  # W1 (governor) + W2 (self)
        assert any(arg.root == gov_token for arg in arguments)  # W1 rule
        assert any(arg.root == root_token for arg in arguments)  # W2 rule